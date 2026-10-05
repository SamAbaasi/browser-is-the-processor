#!/usr/bin/env python3
"""Descriptive, non-canonical stability analysis of the frozen Phase 6 static samples.
Reads raw retained samples only; changes nothing; canonical values are not redefined."""
import json, statistics as st
from pathlib import Path
R = Path(__file__).resolve().parents[3]
P6 = R / "evidence/phase6-adaptive-full-inference"
ENVS = {"Windows Chrome 152": R / "claude-code-p1-handoff-2026-09-15/current-results/windows-chrome152",
        "M1 Chrome 153": P6 / "m1-chrome153-freeze-2026-09-15",
        "M1 Firefox 155": P6 / "m1-firefox155-freeze-2026-10-05",
        "M1 Safari 17.4.1": P6 / "m1-safari17-4-1-freeze-2026-10-05"}
W = ["p32", "p64", "p128", "p256", "decode64"]; K = ["generic", "dot", "pairwise"]
out = {}
for env, d in ENVS.items():
    sess = {}
    for i in (1, 2):
        j = json.loads((d / f"static-session{i}.json").read_text())
        for v in j["variants"]:
            for w in v["workloads"]:
                s = [x["wall_ms"] for x in w["samples"] if x["type"] == "measurement"]
                sess.setdefault((v["kernel_key"], w["workload"]), {})[i] = s
        out.setdefault(env, {})["order%d" % i] = j["static_order"]
    cells = {}
    for k in K:
        for w in W:
            a, b = sess[(k, w)][1], sess[(k, w)][2]; s = a + b
            cells[f"{k}/{w}"] = dict(n=len(s), median=st.median(s), min=min(s), max=max(s),
                                     cv=st.pstdev(s) / st.mean(s), s1_median=st.median(a), s2_median=st.median(b))
    # winner separation: winner max < runner-up min
    sep = {}
    for w in W:
        med = sorted(K, key=lambda k: cells[f"{k}/{w}"]["median"])
        win, ru = med[0], med[1]
        sep[w] = dict(winner=win, runner_up=ru, separated=cells[f"{win}/{w}"]["max"] < cells[f"{ru}/{w}"]["min"])
    out[env].update(cells=cells, separation=sep)
print(json.dumps(out, indent=1)[:200])
Path(__file__).with_name("stability.json").write_text(json.dumps(out, indent=1))
for env in out:
    c = out[env]["cells"]; cvs = [v["cv"] for v in c.values()]
    print(f"\n== {env}  order1={out[env]['order1']} order2={out[env]['order2']}")
    print("  CV median %.4f max %.4f (%s)" % (st.median(cvs), max(cvs), max(c, key=lambda x: c[x]["cv"])))
    for w, s in out[env]["separation"].items(): print("  ", w, s)
    for k in K:
        r = [c[f"{k}/{w}"]["s2_median"] / c[f"{k}/{w}"]["s1_median"] for w in W]
        print("   s2/s1", k, " ".join("%.3f" % x for x in r))

# per-session winners and within-session best-handwritten/G ratio
print("\n--- per-session winners (median of 3) ---")
for env, d in ENVS.items():
    per = {}
    for i in (1, 2):
        j = json.loads((d / f"static-session{i}.json").read_text())
        for v in j["variants"]:
            for w in v["workloads"]:
                s = [x["wall_ms"] for x in w["samples"] if x["type"] == "measurement"]
                per.setdefault(i, {})[(v["kernel_key"], w["workload"])] = st.median(s)
    agree = 0
    rows = []
    for w in W:
        wins = [min(K, key=lambda k: per[i][(k, w)]) for i in (1, 2)]
        agree += wins[0] == wins[1]
        rows.append(f"{w}:{wins[0][0]}{wins[1][0]}")
    canon = {w: min(K, key=lambda k: out[env]["cells"][f"{k}/{w}"]["median"]) for w in W}
    print(f"{env}: same winner both sessions {agree}/5  ", " ".join(rows))
    out[env]["session_winners_agree"] = agree
    # outliers: samples > 1.5x the cell's median
    outl = []
    for kw, c in out[env]["cells"].items():
        pass
Path(__file__).with_name("stability.json").write_text(json.dumps(out, indent=1))
