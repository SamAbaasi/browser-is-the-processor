#!/usr/bin/env python3
"""
Phase 6 final consolidation (analysis only; reads frozen evidence, changes nothing).

Every environment's numbers are recomputed with the UNCHANGED frozen
evaluator from its raw static/adaptive JSONs, then cross-checked against
that environment's stored evaluation.json. Any mismatch aborts.

Outputs (refuses to overwrite):
  PHASE6_SUMMARY.json  — per environment: correctness status + ordering,
                         performance gate, oracle, canonical medians,
                         per-session selection / selector wall / regrets / GM regret
  PHASE6_SUMMARY.csv   — one row per (environment, adaptive session)
  PHASE6_RESULT.md     — human summary; does not reinterpret the frozen gate
"""

import csv
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
P6 = REPO / "evidence/phase6-adaptive-full-inference"
HANDOFF = REPO / "claude-code-p1-handoff-2026-09-15/current-results"
COR = P6 / "correctness/v2"
WORKLOADS = ["p32", "p64", "p128", "p256", "decode64"]

ENVS = [
    {"env": "windows-chrome152", "label": "Windows / Chrome 152",
     "raw": HANDOFF / "windows-chrome152", "stored_eval": HANDOFF / "windows-chrome152/evaluation.json",
     "correctness": COR / "windows-chrome152-correctness-v2.json",
     "correctness_order": "before canonical performance (frozen reference result)",
     "driver": "manual (person operated Chrome)"},
    {"env": "m1-chrome153", "label": "Apple M1 / Chrome 153",
     "raw": P6 / "m1-chrome153-freeze-2026-09-15", "stored_eval": P6 / "m1-chrome153-freeze-2026-09-15/evaluation.json",
     "correctness": COR / "m1-chrome153-correctness-v2.json",
     "correctness_order": "POST-HOC: run after canonical performance (protocol-ordering deviation, disclosed; performance not rerun)",
     "driver": "manual (person operated Chrome)"},
    {"env": "m1-firefox155", "label": "Apple M1 / Firefox 155",
     "raw": P6 / "m1-firefox155-freeze-2026-10-05", "stored_eval": P6 / "m1-firefox155-freeze-2026-10-05/evaluation.json",
     "correctness": COR / "m1-firefox155-correctness-v2.json",
     "correctness_order": "before canonical performance",
     "driver": "W3C WebDriver (geckodriver 0.37.1) on real Firefox 155.0"},
    {"env": "m1-safari17-4-1", "label": "Apple M1 / Safari 17.4.1",
     "raw": None, "stored_eval": None, "incomplete": True,
     "status_dir": P6 / "m1-safari17-4-1-INCOMPLETE-2026-10-05",
     "correctness": COR / "m1-safari17-4-1-correctness-v2.json",
     "correctness_order": "before any performance session",
     "driver": "W3C WebDriver (safaridriver) on real Safari 17.4.1"},
]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def evaluate(raw):
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "e.json"
        subprocess.run([sys.executable, str(REPO / "tools/evaluate_phase6_environment.py"),
                        "--static1", str(raw / "static-session1.json"),
                        "--static2", str(raw / "static-session2.json"),
                        "--adaptive1", str(raw / "adaptive-session1.json"),
                        "--adaptive2", str(raw / "adaptive-session2.json"),
                        "--out", str(out)], check=True, capture_output=True)
        return json.loads(out.read_text())


def main():
    out_dir = P6 / "final"
    if out_dir.exists():
        sys.exit(f"refusing to overwrite {out_dir}")

    summary = {"schema": "p1-phase6-final-summary-v1",
               "gate": "per environment: correctness-v2 PASS AND every adaptive session GM regret <= 1.05",
               "regret_definition": "canonical static time of selected kernel / best canonical static time",
               "static_aggregation": "median of 6 retained samples (3 per static session), no outlier removal",
               "environments": []}
    rows = []
    for e in ENVS:
        if e.get("incomplete"):
            c = json.loads(Path(e["correctness"]).read_text())
            summary["environments"].append({
                "environment": e["env"], "label": e["label"], "driver": e["driver"],
                "status": "INCOMPLETE: correctness-v2 only; no canonical performance data",
                "correctness_v2": {"pass": c["overall_pass"], "ordering": e["correctness_order"],
                                   "file": str(Path(e["correctness"]).relative_to(REPO)),
                                   "sha256": sha(e["correctness"]), "user_agent": c["user_agent"],
                                   "top1_ids": {k: v["top"]["top1_id"] for k, v in c["variants"].items()}},
                "performance_environment_pass": None, "phase6_environment_pass": None,
                "evidence_dir": str(Path(e["status_dir"]).relative_to(REPO))})
            continue
        ev = evaluate(e["raw"])
        stored = json.loads(Path(e["stored_eval"]).read_text())
        if ev != stored:
            sys.exit(f"{e['env']}: recomputed evaluation differs from stored evaluation.json")
        c = json.loads(Path(e["correctness"]).read_text())
        rec = {"environment": e["env"], "label": e["label"], "driver": e["driver"],
               "correctness_v2": {"pass": c["overall_pass"], "ordering": e["correctness_order"],
                                  "file": str(Path(e["correctness"]).relative_to(REPO)),
                                  "sha256": sha(e["correctness"]),
                                  "user_agent": c["user_agent"],
                                  "top1_ids": {k: v["top"]["top1_id"] for k, v in c["variants"].items()}},
               "performance_environment_pass": ev["environment_pass"],
               "phase6_environment_pass": bool(c["overall_pass"] and ev["environment_pass"]),
               "oracle": {w: {"best_kernel": ev["oracle"][w]["best_kernel"],
                              "best_ms": ev["oracle"][w]["best_ms"],
                              "ranking": ev["oracle"][w]["ranking"]} for w in WORKLOADS},
               "canonical_static_median_ms": {k: {w: ev["canonical_static"][k][w]["median_ms"] for w in WORKLOADS}
                                              for k in ("generic", "dot", "pairwise")},
               "adaptive_sessions": ev["adaptive_sessions"],
               "evidence_dir": str(Path(e["raw"]).relative_to(REPO))}
        summary["environments"].append(rec)
        for s in ev["adaptive_sessions"]:
            rows.append({"environment": e["env"], "session": s["session_index"],
                         "correctness_pass": c["overall_pass"], "correctness_ordering": e["correctness_order"],
                         "selected_kernel": s["selected_kernel"],
                         "selector_wall_ms": s["selector_wall_ms"],
                         "selector_decision_mode": s["selector_decision_mode"],
                         **{f"regret_{w}": s["regret_by_workload"][w] for w in WORKLOADS},
                         "gm_regret": s["environment_gm_regret"], "session_pass": s["pass"],
                         **{f"oracle_{w}": ev["oracle"][w]["best_kernel"] for w in WORKLOADS},
                         "environment_pass": rec["phase6_environment_pass"]})

    evaluated = [x for x in summary["environments"] if x["phase6_environment_pass"] is not None]
    summary["environments_evaluated"] = [x["environment"] for x in evaluated]
    summary["environments_incomplete"] = [x["environment"] for x in summary["environments"] if x["phase6_environment_pass"] is None]
    summary["all_evaluated_environments_pass"] = all(x["phase6_environment_pass"] for x in evaluated)
    summary["phase6_gate_verdict"] = ("FAIL: the frozen gate requires every tested environment to pass; "
                                      + ", ".join(x["environment"] for x in evaluated if not x["phase6_environment_pass"])
                                      + " failed") if not summary["all_evaluated_environments_pass"] else "PASS on all evaluated environments"
    out_dir.mkdir(parents=True)
    (out_dir / "PHASE6_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n")
    with open(out_dir / "PHASE6_SUMMARY.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    md = ["# Phase 6 — final result (4 environments)", "",
          "Gate (frozen): correctness-v2 PASS and EVERY adaptive session GM regret <= 1.05.", "",
          "| Environment | Correctness-v2 | Oracle (all workloads) | Adaptive 1 | Adaptive 2 | Phase 6 |",
          "|---|---|---|---|---|---|"]
    for x in summary["environments"]:
        if x["phase6_environment_pass"] is None:
            md.append(f"| {x['label']} | {'PASS' if x['correctness_v2']['pass'] else 'FAIL'} | not measured | not collected | not collected | **INCOMPLETE** |")
            continue
        best = sorted({x["oracle"][w]["best_kernel"] for w in WORKLOADS})
        a = x["adaptive_sessions"]
        cell = lambda s: f"{s['selected_kernel']}, {s['selector_wall_ms']:.1f} ms, GM {s['environment_gm_regret']:.4f}"
        corr = ("PASS" if x["correctness_v2"]["pass"] else "FAIL") + (" (post-hoc)" if "POST-HOC" in x["correctness_v2"]["ordering"] else "")
        md.append(f"| {x['label']} | {corr} | {'/'.join(best)} | {cell(a[0])} | {cell(a[1])} | "
                  f"{'PASS' if x['phase6_environment_pass'] else 'FAIL'} |")
    md += ["", f"Phase 6 gate verdict: {summary['phase6_gate_verdict']}",
           f"Evaluated: {', '.join(summary['environments_evaluated'])}. Incomplete: {', '.join(summary['environments_incomplete']) or 'none'}.", "",
           "Notes:",
           "- Windows Chrome 152 FAIL is preserved: adaptive session 1 selected pairwise (GM regret 1.3143) "
           "while the canonical static oracle was dot for every workload. Later passes do not erase it.",
           "- M1 Chrome 153 correctness-v2 was run AFTER its canonical performance data (post-hoc validation). "
           "This protocol-ordering deviation is disclosed; performance was not rerun.",
           "- Firefox and Safari were operated by W3C WebDriver on the real installed browsers; see each freeze's METHODOLOGY_NOTES.md.",
           "- Safari 17.4.1 is INCOMPLETE: correctness-v2 PASS only; performance sessions were not collected (first attempt aborted at the owner's request). No Safari performance claim is made. Whether Phase 5D's Safari choice (generic) transfers to full inference is an open question.",
           "- Phase 5D selector success against its microkernel oracle and Phase 6 full-inference transfer are separate questions.",
           ""]
    (out_dir / "PHASE6_RESULT.md").write_text("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
