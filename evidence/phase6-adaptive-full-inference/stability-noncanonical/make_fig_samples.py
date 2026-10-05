#!/usr/bin/env python3
"""Generate fig_samples.tex: every retained static sample divided by its cell median (descriptive)."""
import json, statistics as st
from pathlib import Path
R = Path(__file__).resolve().parents[3]
P6 = R / "evidence/phase6-adaptive-full-inference"
ENVS = [("Windows\\\\Chrome 152", R / "claude-code-p1-handoff-2026-09-15/current-results/windows-chrome152"),
        ("Apple M1\\\\Chrome 153", P6 / "m1-chrome153-freeze-2026-09-15"),
        ("Apple M1\\\\Firefox 155", P6 / "m1-firefox155-freeze-2026-10-05"),
        ("Apple M1\\\\Safari 17.4.1", P6 / "m1-safari17-4-1-freeze-2026-10-05")]
W = ["p32", "p64", "p128", "p256", "decode64"]; K = ["generic", "dot", "pairwise"]
COL = {"generic": "kG", "dot": "kD", "pairwise": "kP"}
out = [r"""\definecolor{kD}{HTML}{2A78D6}
\definecolor{kP}{HTML}{EB6834}
\definecolor{kG}{HTML}{1BAF7A}
\begin{tikzpicture}
\begin{groupplot}[group style={group size=4 by 1, horizontal sep=0.35cm, y descriptions at=edge left},
  width=0.27\textwidth, height=4.2cm, ymode=log, ymin=0.22, ymax=6.5, ytick={0.25,0.5,1,2,4},
  yticklabels={0.25$\times$,0.5$\times$,1$\times$,2$\times$,4$\times$}, ymajorgrids, grid style={black!8},
  xmin=0.3, xmax=5.7, xtick={1,2,3,4,5}, xticklabels={p32,p64,p128,p256,dec64},
  x tick label style={rotate=45, anchor=east, font=\scriptsize}, y tick label style={font=\scriptsize},
  title style={font=\footnotesize\bfseries, align=center}, ylabel style={font=\small},
  axis line style={black!40}, tick style={black!40}]"""]
for ei, (label, d) in enumerate(ENVS):
    cells = {}
    for i in (1, 2):
        j = json.loads((d / f"static-session{i}.json").read_text())
        for v in j["variants"]:
            for w in v["workloads"]:
                cells.setdefault((v["kernel_key"], w["workload"]), []).extend(
                    (i, x["wall_ms"]) for x in w["samples"] if x["type"] == "measurement")
    opts = f"title={{{label}}}"
    if ei == 0:
        opts += ", ylabel={Sample / cell median}, legend to name=sampleslegend, legend columns=6, legend style={draw=none, font=\\small, column sep=6pt}"
    out.append(f"\\nextgroupplot[{opts}]")
    for ki, k in enumerate(K):
        for sess, mark in ((1, "o"), (2, "triangle")):
            pts = []
            for wi, w in enumerate(W):
                s = cells[(k, w)]; m = st.median([x for _, x in s])
                for n, (i, x) in enumerate([p for p in s if p[0] == sess]):
                    pts.append(f"({wi + 1 + (ki - 1) * 0.25 + (n - 1) * 0.05:.3f},{x / m:.4f})")
            out.append(f"\\addplot[only marks, mark={mark}, mark size=1.1pt, draw={COL[k]}, fill={COL[k]}!40] coordinates {{{' '.join(pts)}}};")
            if ei == 0:
                lbl = {"generic": "G", "dot": "D", "pairwise": "P"}[k]
                out.append(f"\\addlegendentry{{{lbl}, session {sess}}}" if k != "pairwise" or True else "")
    out.append(r"\draw[densely dashed, black!50] (axis cs:0.3,1) -- (axis cs:5.7,1);")
out.append(r"""\end{groupplot}
\end{tikzpicture}

\vspace{2pt}\ref{sampleslegend}""")
Path(__file__).with_name("fig_samples.tex").write_text("\n".join(out) + "\n")
print("ok")
