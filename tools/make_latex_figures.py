#!/usr/bin/env python3
"""
Emit pgfplots figure sources (for the LaTeX papers) generated ONLY from frozen
evidence: evidence/phase6-adaptive-full-inference/final/PHASE6_SUMMARY.json.

fig_speedup.tex — full-inference speedup of D and P over G, per workload,
                  one panel per fully-measured environment.
fig_turn.tex    — representative turn (p128 + decode64) latency per kernel and
                  environment, with value labels.

Environments without Phase 6 performance data are omitted automatically.
Colors follow the kernel (validated categorical palette): D blue, P orange,
G aqua.

Usage: python3 tools/make_latex_figures.py <output_dir>
"""

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SUMMARY = Path(__import__("os").environ.get("P6_SUMMARY", REPO / "evidence/phase6-adaptive-full-inference/final/PHASE6_SUMMARY.json"))
WL = ["p32", "p64", "p128", "p256", "decode64"]
SHORT = {"windows-chrome152": "Windows\\\\Chrome 152", "m1-chrome153": "Apple M1\\\\Chrome 153",
         "m1-firefox155": "Apple M1\\\\Firefox 155", "m1-safari17-4-1": "Apple M1\\\\Safari 17.4.1"}

COLORS = r"""\definecolor{kD}{HTML}{2A78D6}
\definecolor{kP}{HTML}{EB6834}
\definecolor{kG}{HTML}{1BAF7A}
"""


def coords(vals):
    return " ".join(f"({i + 1},{v:.3f})" for i, v in enumerate(vals))


def fig_speedup(envs):
    n = len(envs)
    out = [COLORS, r"\begin{tikzpicture}",
           r"\begin{groupplot}[group style={group size=%d by 1, horizontal sep=0.35cm, "
           r"y descriptions at=edge left}," % n,
           r"  width=%.2f\textwidth, height=4.6cm, ybar=0.6pt, /pgf/bar width=4.2pt," % (1.02 / n),
           r"  ymin=0, ymax=2.05, ytick={0,0.5,1,1.5,2}, ymajorgrids, grid style={black!8},",
           r"  yticklabel={\pgfmathprintnumber{\tick}$\times$}, ylabel style={font=\small},",
           r"  xmin=0.4, xmax=5.6, xtick={1,2,3,4,5},",
           r"  xticklabels={p32,p64,p128,p256,dec64},",
           r"  x tick label style={rotate=45, anchor=east, font=\scriptsize},",
           r"  y tick label style={font=\scriptsize}, title style={font=\footnotesize\bfseries, align=center},",
           r"  axis line style={black!40}, tick style={black!40}, enlarge x limits=false]"]
    for i, e in enumerate(envs):
        m = e["canonical_static_median_ms"]
        d = [m["generic"][w] / m["dot"][w] for w in WL]
        p = [m["generic"][w] / m["pairwise"][w] for w in WL]
        extra = ", ylabel={Speedup over G}, legend to name=speeduplegend, legend columns=2, " \
                "legend style={draw=none, font=\\small, column sep=8pt}" if i == 0 else ""
        out.append(r"\nextgroupplot[title={%s}%s]" % (SHORT.get(e["environment"], e["label"]), extra))
        out.append(r"\addplot[fill=kD, draw=none] coordinates {%s};" % coords(d))
        out.append(r"\addplot[fill=kP, draw=none] coordinates {%s};" % coords(p))
        if i == 0:
            out.append(r"\addlegendentry{D: \texttt{i32x4.dot\_i16x8\_s}}")
            out.append(r"\addlegendentry{P: \texttt{i16x8.mul} + \texttt{extadd\_pairwise}}")
        out.append(r"\draw[densely dashed, black!60] (axis cs:0.4,1) -- (axis cs:5.6,1);")
        for j, w in enumerate(WL):  # values beyond the axis are clipped by pgfplots: print them
            over = [(lbl, v) for lbl, v in (("D", d[j]), ("P", p[j])) if v > 2.05]
            if over:
                txt = "/".join(f"{lbl} {v:.2f}" for lbl, v in over)
                out.append(r"\node[font=\tiny, anchor=north west, align=left, inner sep=1pt] "
                           r"at (axis cs:%.2f,1.98) {%s$\times$\textsuperscript{\dag}};" % (j + 1.3, txt.replace("/", "\\\\")))
    out += [r"\end{groupplot}", r"\end{tikzpicture}", "",
            r"\vspace{2pt}\ref{speeduplegend}", ""]
    return "\n".join(out)


def fig_turn(envs):
    rows = []
    for e in envs:
        m = e["canonical_static_median_ms"]
        rows.append((SHORT.get(e["environment"], e["label"]).replace("\\\\", " / "),
                     {k: (m[k]["p128"] + m[k]["decode64"]) / 1000 for k in ("generic", "dot", "pairwise")}))
    n = len(rows)
    ymax = n + 0.5
    xmax = max(v for _, r in rows for v in r.values()) * 1.18
    out = [COLORS, r"\begin{tikzpicture}",
           r"\begin{axis}[xbar=0.8pt, /pgf/bar width=6pt, width=0.80\textwidth, height=%.1fcm," % (1.6 + 1.6 * n),
           r"  xmin=0, xmax=%.0f, xlabel={Seconds per turn (prefill 128 + decode 64)}," % xmax,
           r"  ymin=0.5, ymax=%.1f, ytick={%s}, yticklabels={%s}," % (
               ymax, ",".join(str(i + 1) for i in range(n)), ",".join("{%s}" % r[0] for r in rows)),
           r"  y dir=reverse, xmajorgrids, grid style={black!8}, axis line style={black!40},",
           r"  tick style={black!40}, tick label style={font=\scriptsize}, label style={font=\small},",
           r"  nodes near coords, nodes near coords style={font=\scriptsize, anchor=west},",
           r"  point meta=x, every node near coord/.append style={/pgf/number format/.cd, fixed, fixed zerofill, precision=1},",
           r"  legend style={draw=none, font=\small, at={(0.5,1.02)}, anchor=south, legend columns=3},",
           r"  reverse legend]"]
    for k, color, label in (("pairwise", "kP", "P (pairwise)"), ("dot", "kD", "D (dot)"),
                            ("generic", "kG", "G (generic)")):
        pts = " ".join(f"({r[1][k]:.1f},{i + 1})" for i, r in enumerate(rows))
        out.append(r"\addplot[fill=%s, draw=none] coordinates {%s};" % (color, pts))
        out.append(r"\addlegendentry{%s}" % label)
    out += [r"\end{axis}", r"\end{tikzpicture}", ""]
    return "\n".join(out)


def main():
    outdir = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    outdir.mkdir(parents=True, exist_ok=True)
    s = json.loads(SUMMARY.read_text())
    envs = [e for e in s["environments"] if e["phase6_environment_pass"] is not None]
    (outdir / "fig_speedup.tex").write_text(fig_speedup(envs))
    (outdir / "fig_turn.tex").write_text(fig_turn(envs))
    print(f"wrote fig_speedup.tex, fig_turn.tex for {len(envs)} environments -> {outdir}")


if __name__ == "__main__":
    main()
