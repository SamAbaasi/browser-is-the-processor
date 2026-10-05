#!/usr/bin/env python3
"""
Freeze one completed Phase 6 environment (frozen rule 22).

Copies, never rewrites, the raw evidence into a freeze directory:
  raw static/adaptive JSON, frozen evaluator output (evaluation.json +
  evaluator-output.txt), correctness-v2 JSON, protocol/evaluation/harness
  docs, driver script + DRIVER_LOG.jsonl, MODEL/RUNTIME SHA files,
  METHODOLOGY_NOTES.md (supplied by the caller), a generated RESULT.md,
  SHA256SUMS over every file, and a zip archive.

Refuses to overwrite an existing freeze directory.
"""

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
P6 = REPO / "evidence/phase6-adaptive-full-inference"
WORKLOADS = ["p32", "p64", "p128", "p256", "decode64"]
RUNTIMES = [
    "browser/dist/generic/p1-browser-workload-bench.wasm",
    "browser/dist/handwritten/p1-browser-workload-bench.wasm",
    "browser/dist/pairwise/p1-browser-workload-bench.wasm",
    "browser/dist/triple-v6/p1-triple-v6.wasm",
]
DOCS = [
    "experiments/phase6-adaptive-full-inference/PHASE6_PROTOCOL.md",
    "experiments/phase6-adaptive-full-inference/EVALUATION_IMPLEMENTATION.md",
    "experiments/phase6-adaptive-full-inference/HARNESS_IMPLEMENTATION.md",
    "experiments/phase6-adaptive-full-inference/CORRECTNESS_PROTOCOL_V2.md",
]
MODEL_SHA = "13939ce5030319a35db346e5dba7a3a3bd599dfc18b113a2a97446ff964714c5"


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--env", required=True)
    ap.add_argument("--title", required=True, help="e.g. 'M1 Firefox 155'")
    ap.add_argument("--date", required=True, help="freeze date YYYY-MM-DD")
    ap.add_argument("--notes", required=True, help="METHODOLOGY_NOTES.md source file")
    a = ap.parse_args()

    res = P6 / "results" / a.env
    out = P6 / f"{a.env}-freeze-{a.date}"
    if out.exists():
        sys.exit(f"refusing to overwrite {out}")
    names = ["static-session1.json", "static-session2.json",
             "adaptive-session1.json", "adaptive-session2.json"]
    for n in names:
        if not (res / n).exists():
            sys.exit(f"missing {res / n}")
    out.mkdir(parents=True)

    for n in names + ["DRIVER_LOG.jsonl"]:
        shutil.copy2(res / n, out / n)
    cor = P6 / "correctness/v2" / f"{a.env}-correctness-v2.json"
    shutil.copy2(cor, out / cor.name)
    for d in DOCS:
        shutil.copy2(REPO / d, out / Path(d).name)
    for t in ["tools/evaluate_phase6_environment.py", "tools/phase6_webdriver_driver.py"]:
        shutil.copy2(REPO / t, out / Path(t).name)
    shutil.copy2(a.notes, out / "METHODOLOGY_NOTES.md")

    ev = subprocess.run(
        [sys.executable, str(REPO / "tools/evaluate_phase6_environment.py"),
         "--static1", str(out / names[0]), "--static2", str(out / names[1]),
         "--adaptive1", str(out / names[2]), "--adaptive2", str(out / names[3]),
         "--out", str(out / "evaluation.json")],
        capture_output=True, text=True, check=True)
    (out / "evaluator-output.txt").write_text(ev.stdout)

    (out / "MODEL_SHA256.txt").write_text(
        f"{MODEL_SHA}  /Users/saman/Downloads/ggml-model-i2_s.gguf (verified externally)\n")
    (out / "RUNTIME_SHA256.txt").write_text(
        "".join(f"{sha(REPO / r)}  {r}\n" for r in RUNTIMES))

    e = json.loads((out / "evaluation.json").read_text())
    c = json.loads((out / cor.name).read_text())
    lines = [f"# Phase 6 — {a.title}", "",
             f"Correctness-v2: {'PASS' if c['overall_pass'] else 'FAIL'} "
             f"(run before canonical performance; SHA256 {sha(out / cor.name)})",
             f"Performance environment gate: {'PASS' if e['environment_pass'] else 'FAIL'}",
             "", "Canonical pooled static oracle (median of 6 retained samples):"]
    for w in WORKLOADS:
        o = e["oracle"][w]
        lines.append(f"{w:8s} -> {o['best_kernel']} {o['best_ms']:.3f} ms  (ranking {' < '.join(o['ranking'])})")
    lines += ["", "Canonical static medians (ms):", "| workload | generic | dot | pairwise |", "|---|---|---|---|"]
    for w in WORKLOADS:
        lines.append(f"| {w} | " + " | ".join(f"{e['canonical_static'][k][w]['median_ms']:.3f}"
                                             for k in ("generic", "dot", "pairwise")) + " |")
    for s in e["adaptive_sessions"]:
        lines += ["", f"Adaptive Session {s['session_index']}:",
                  f"selected: {s['selected_kernel']}",
                  f"selector wall: {s['selector_wall_ms']:.3f} ms",
                  f"decision mode: {s['selector_decision_mode']}",
                  f"GM regret: {s['environment_gm_regret']:.6f}",
                  f"gate <= {s['gate']}: {'PASS' if s['pass'] else 'FAIL'}"]
    lines += ["", f"Environment result: {'PASS' if e['environment_pass'] else 'FAIL'}", "",
              "No retained sample was removed. No threshold, ordering, or selector",
              "parameter was changed. Aborted/uncaptured attempts and all environment",
              "conditions are disclosed in METHODOLOGY_NOTES.md and DRIVER_LOG.jsonl.", ""]
    (out / "RESULT.md").write_text("\n".join(lines))

    files = sorted(p for p in out.iterdir() if p.is_file() and p.name != "SHA256SUMS")
    (out / "SHA256SUMS").write_text("".join(f"{sha(p)}  {p.name}\n" for p in files))

    z = P6 / f"phase6-{a.env}-freeze-{a.date}.zip"
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(out.iterdir()):
            zf.write(p, f"{out.name}/{p.name}")
    print(ev.stdout)
    print(f"froze {out}\narchive {z}  sha256 {sha(z)}")


if __name__ == "__main__":
    main()
