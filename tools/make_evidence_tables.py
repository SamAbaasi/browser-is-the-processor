#!/usr/bin/env python3
"""Generate the data tables of EVIDENCE_INDEX.md from frozen JSON (never edit them by hand).

Usage: python3 tools/make_evidence_tables.py <PHASE6_SUMMARY.json> <phase7-break-even.json> > tables.md
"""
import json
import math
import sys

W = ["p32", "p64", "p128", "p256", "decode64"]
gm = lambda xs: math.exp(sum(map(math.log, xs)) / len(xs))


def main():
    S = json.load(open(sys.argv[1]))
    P7 = json.load(open(sys.argv[2]))
    L = ["## Generated data tables (from frozen JSON; do not edit by hand)", "",
         f"Sources: `{sys.argv[1]}`, `{sys.argv[2]}`.", "",
         "### Phase 6 canonical static medians (ms; median of 6 retained samples)", ""]
    for e in S["environments"]:
        if e["phase6_environment_pass"] is None:
            continue
        L.append(f"**{e['label']}** — oracle best: " + ", ".join(f"{w}={e['oracle'][w]['best_kernel']}" for w in W) + "\n")
        L += ["| workload | generic (G) | dot (D) | pairwise (P) | D/G speedup | P/G speedup |", "|---|---|---|---|---|---|"]
        m = e["canonical_static_median_ms"]
        for w in W:
            g, d, p = (m[k][w] for k in ("generic", "dot", "pairwise"))
            L.append(f"| {w} | {g:,.1f} | {d:,.1f} | {p:,.1f} | {g/d:.3f}x | {g/p:.3f}x |")
        best_dec = e["oracle"]["decode64"]
        L.append(f"\nBest decode throughput: {64000/best_dec['best_ms']:.2f} tok/s (decode64, {best_dec['best_kernel']}). "
                 f"Best p128 prefill: {128000/e['oracle']['p128']['best_ms']:.2f} tok/s. "
                 f"Full-inference GM ratios: D/G {gm([m['generic'][w]/m['dot'][w] for w in W]):.3f}, "
                 f"P/G {gm([m['generic'][w]/m['pairwise'][w] for w in W]):.3f}, "
                 f"P/D {gm([m['dot'][w]/m['pairwise'][w] for w in W]):.3f}.\n")
    L += ["### Phase 6 adaptive sessions", "", "| environment | session | selected | selector wall (ms) | GM regret | pass |", "|---|---|---|---|---|---|"]
    for e in S["environments"]:
        for s in e.get("adaptive_sessions", []):
            L.append(f"| {e['environment']} | {s['session_index']} | {s['selected_kernel']} | {s['selector_wall_ms']:.1f} | "
                     f"{s['environment_gm_regret']:.4f} | {s['pass']} |")
    L += ["", "### Correctness-v2", "", "| environment | pass | ordering | top1 ids G/D/P | result SHA256 |", "|---|---|---|---|---|"]
    for e in S["environments"]:
        c = e["correctness_v2"]; t = c["top1_ids"]
        L.append(f"| {e['environment']} | {c['pass']} | {c['ordering']} | {t['generic']}/{t['dot']}/{t['pairwise']} | `{c['sha256'][:16]}…` |")
    u = P7["universal_static"]
    L += ["", f"### Phase 7 break-even (universal static = {u['kernel']}; "
              + ", ".join(f"{k} GM turn {v/1000:.1f} s" for k, v in u["cross_env_gm_turn_ms"].items()) + ")", "",
          "| environment | session | selected | saving/turn (ms) | selector wall used (ms) | break-even |", "|---|---|---|---|---|---|"]
    for n, r in P7["per_environment"].items():
        w = r["selector_wall_used_ms"]
        for s in r["sessions"]:
            L.append(f"| {n} | {s['adaptive_session']} | {s['selected_kernel']} | {s['saving_per_turn_ms']:,.1f} | "
                     f"{'unavailable' if w is None else f'{w:.1f}'} | {s['break_even_turns']} |")
    print("\n".join(L))


if __name__ == "__main__":
    main()
