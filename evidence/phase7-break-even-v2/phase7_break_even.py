#!/usr/bin/env python3
"""
Phase 7 break-even calculator (analysis only, no new benchmark).

Implements the frozen Phase 7 definition in PHASE6_PROTOCOL.md:

  representative interactive turn = prefill128 + decode64
  universal-static kernel = the ONE kernel in {generic, dot, pairwise} with the
      lowest cross-environment geometric mean of the representative-turn latency
      (canonical static medians). Offline baseline only.
  turn_selected(e)  = p128_selected(e)  + decode64_selected(e)
  turn_universal(e) = p128_universal(e) + decode64_universal(e)
  saving_per_turn(e) = turn_universal(e) - turn_selected(e)
  selector_wall(e) = MAXIMUM canonical Phase 5D selector wall observed for that
      environment (from the frozen Phase 5D result JSONs, NOT the Phase 6
      adaptive sessions)
  saving <= 0 -> no finite break-even; else ceil(selector_wall / saving)
  first_use_cost(e) = selector_wall + first inference turn

Resolution of "selected kernel" when an environment's two adaptive sessions
selected different kernels (Windows Chrome 152): each adaptive session is
evaluated independently, mirroring frozen Phase 6 rule 16 ("Both adaptive
sessions are evaluated independently"). No tie-break policy is invented.

Inputs:
  --env NAME=evaluation.json            (frozen Phase 6 evaluation per environment)
  --phase5d NAME=run1.json,run2.json    (frozen canonical Phase 5D runs per environment)

An environment without Phase 5D runs is reported with break-even "pending:
Phase 5D wall unavailable"; no substitute wall is used. The output is marked
provisional unless all 4 environments have both inputs.

first_use_cost note: canonical static medians exclude the discarded warm-up and
model load, so "first inference turn" here is the canonical steady-state turn.
Cold-start effects (model load, first-run JIT) are not measured canonically
and are excluded; this is stated in the output.
"""

import argparse
import json
import math
from pathlib import Path

TURN = ["p128", "decode64"]
KERNELS = ["generic", "dot", "pairwise"]
EXPECTED = 4


def gm(xs):
    return math.exp(sum(math.log(x) for x in xs) / len(xs))


def turn(ev, k):
    return sum(ev["canonical_static"][k][w]["median_ms"] for w in TURN)


def kv(specs):
    out = {}
    for s in specs or []:
        name, val = s.split("=", 1)
        out[name] = val
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--env", action="append", required=True)
    ap.add_argument("--phase5d", action="append")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    evs = {n: json.loads(Path(p).read_text()) for n, p in kv(a.env).items()}
    for n, ev in evs.items():
        assert ev.get("schema") == "p1-phase6-environment-evaluation-v1", n
    p5 = {}
    for n, files in kv(a.phase5d).items():
        runs = [json.loads(Path(f).read_text()) for f in files.split(",")]
        p5[n] = {"files": files.split(","),
                 "walls_ms": [r["selector"]["selector_wall_ms"] for r in runs],
                 "selected": [r["selector"]["selected_variant"] for r in runs],
                 "max_wall_ms": max(r["selector"]["selector_wall_ms"] for r in runs)}

    universal_gm = {k: gm([turn(ev, k) for ev in evs.values()]) for k in KERNELS}
    universal = min(universal_gm, key=universal_gm.get)

    per_env = {}
    for n, ev in evs.items():
        tu = turn(ev, universal)
        wall = p5[n]["max_wall_ms"] if n in p5 else None
        sessions = []
        for s in ev["adaptive_sessions"]:
            k = s["selected_kernel"]
            ts = turn(ev, k)
            saving = tu - ts
            if saving <= 0:
                # independent of the selector wall: no positive saving can ever repay it
                be = "no finite break-even"
                first = (wall + ts) if wall is not None else None
            elif wall is None:
                be = (f"pending: canonical Phase 5D selector wall unavailable "
                      f"(= 1 turn for any wall <= {saving:.1f} ms)")
                first = None
            else:
                be = math.ceil(wall / saving)
                first = wall + ts
            sessions.append({"adaptive_session": s["session_index"], "selected_kernel": k,
                             "turn_selected_ms": ts, "saving_per_turn_ms": saving,
                             "break_even_turns": be, "first_use_cost_ms": first})
        per_env[n] = {"environment_pass_phase6": ev["environment_pass"],
                      "universal_kernel": universal, "turn_universal_ms": tu,
                      "turn_by_kernel_ms": {k: turn(ev, k) for k in KERNELS},
                      "phase5d": p5.get(n), "selector_wall_used_ms": wall,
                      "sessions": sessions}

    complete = len(evs) == EXPECTED and all(n in p5 for n in evs)
    res = {"schema": "p1-phase7-break-even-v2",
           "provisional": not complete,
           "representative_turn": "p128 + decode64 (canonical static medians)",
           "universal_static": {"kernel": universal, "cross_env_gm_turn_ms": universal_gm},
           "selector_wall_source": "max canonical Phase 5D selector_wall_ms per environment",
           "selection_rule": "each Phase 6 adaptive session evaluated independently (rule 16)",
           "first_use_note": "selector wall + canonical steady-state turn; model load and cold-start JIT excluded (not canonically measured)",
           "per_environment": per_env}
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(res, indent=2) + "\n")

    print(f"=== Phase 7 break-even [{'FINAL INPUTS' if complete else 'PROVISIONAL'}] ===")
    print(f"universal static kernel: {universal}  " +
          "  ".join(f"{k}={v:.1f}" for k, v in universal_gm.items()))
    for n, r in per_env.items():
        print(f"\n[{n}] turn_universal={r['turn_universal_ms']:.1f} ms  wall={r['selector_wall_used_ms']}")
        for s in r["sessions"]:
            print(f"  A{s['adaptive_session']} {s['selected_kernel']}: turn={s['turn_selected_ms']:.1f} "
                  f"saving={s['saving_per_turn_ms']:.1f} break_even={s['break_even_turns']} first_use={s['first_use_cost_ms']}")
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
