#!/usr/bin/env python3
"""
Reproducible article figures, generated ONLY from frozen evidence:
  evidence/phase6-adaptive-full-inference/final/PHASE6_SUMMARY.json

fig1_kernel_speedup_vs_generic.svg  — D/G and P/G full-inference speedup per
    workload, small multiples per environment (the ranking flip).
fig2_turn_latency.svg               — representative turn (p128 + decode64)
    latency per kernel per environment (the Phase 7 baseline view).

Palette: validated categorical slots (light surface) — D = slot 1 blue,
P = slot 2 orange, G = slot 3 aqua; colors follow the kernel in every figure.
Static vector figures for print/publication (no interaction layer).
"""

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SUMMARY = REPO / "evidence/phase6-adaptive-full-inference/final/PHASE6_SUMMARY.json"
OUT = REPO / "figures"

SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e3e2de"
COL = {"dot": "#2a78d6", "pairwise": "#eb6834", "generic": "#1baf7a"}
NAME = {"generic": "G · generic (autovectorized)", "dot": "D · i32x4.dot_i16x8_s",
        "pairwise": "P · i16x8.mul + extadd_pairwise"}
WL = ["p32", "p64", "p128", "p256", "decode64"]
FONT = "font-family='system-ui, -apple-system, Segoe UI, Roboto, sans-serif'"


def bar(x, y0, w, h, color):
    """Vertical bar anchored at baseline y0 (SVG y grows down), 4px rounded data-end."""
    r = min(4, h / 2, w / 2)
    top = y0 - h
    return (f"<path d='M{x},{y0} L{x},{top + r} Q{x},{top} {x + r},{top} "
            f"L{x + w - r},{top} Q{x + w},{top} {x + w},{top + r} L{x + w},{y0} Z' fill='{color}'/>")


def hbar(x0, y, w, h, color):
    """Horizontal bar anchored at x0, 4px rounded data-end on the right."""
    r = min(4, w / 2, h / 2)
    end = x0 + w
    return (f"<path d='M{x0},{y} L{end - r},{y} Q{end},{y} {end},{y + r} "
            f"L{end},{y + h - r} Q{end},{y + h} {end - r},{y + h} L{x0},{y + h} Z' fill='{color}'/>")


def text(x, y, s, size=13, color=INK, anchor="start", weight="400"):
    return (f"<text x='{x}' y='{y}' {FONT} font-size='{size}' fill='{color}' "
            f"text-anchor='{anchor}' font-weight='{weight}'>{s}</text>")


def fig1(envs):
    W, panel_w, panel_h, top, left, gap = 1060, 300, 260, 150, 64, 34
    ymax = 2.0
    H = top + panel_h + 90
    out = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>",
           f"<rect width='100%' height='100%' fill='{SURFACE}'/>",
           text(left - 40, 34, "Same WASM SIMD strategy, different winner per engine", 20, INK, weight="600"),
           text(left - 40, 58, "Full-inference speedup over the compiler-autovectorized generic kernel (dashed line, G = 1.0).", 13, INK2),
           text(left - 40, 77, "Median of 6 retained runs; BitNet b1.58 2B4T, CPU-only, single thread, inside the browser.", 13, INK2)]
    # legend (2 series)
    lx = left - 40
    for k in ("dot", "pairwise"):
        out.append(f"<rect x='{lx}' y='96' width='12' height='12' rx='2' fill='{COL[k]}'/>")
        out.append(text(lx + 18, 107, NAME[k], 13, INK))
        lx += 270
    for i, e in enumerate(envs):
        x0 = left + i * (panel_w + gap)
        base = top + panel_h
        sy = lambda v: base - v / ymax * panel_h
        # grid + axis labels
        for v in (0, 0.5, 1.0, 1.5, 2.0):
            y = sy(v)
            stroke = INK2 if v == 1.0 else GRID
            dash = "" if v != 1.0 else " stroke-dasharray='4 3'"
            out.append(f"<line x1='{x0}' x2='{x0 + panel_w}' y1='{y}' y2='{y}' stroke='{stroke}' stroke-width='1'{dash}/>")
            if i == 0:
                out.append(text(x0 - 8, y + 4, f"{v:.1f}×", 11, INK2, "end"))
        out.append(text(x0, top - 10, e["label"], 14, INK, weight="600"))
        slot = panel_w / len(WL)
        bw = (slot - 14) / 2
        med = e["canonical_static_median_ms"]
        for j, w in enumerate(WL):
            bx = x0 + j * slot + 6
            for m, k in enumerate(("dot", "pairwise")):
                sp = med["generic"][w] / med[k][w]
                out.append(bar(bx + m * (bw + 2), base, bw, sp / ymax * panel_h, COL[k]))
            out.append(text(x0 + j * slot + slot / 2, base + 18, w, 11, INK2, "middle"))
        best = sorted({e["oracle"][w]["best_kernel"] for w in WL})
        out.append(text(x0, base + 42, "fastest on all 5 workloads: " + "/".join(best), 12, INK))
    out.append(text(left - 40, H - 14, "Source: frozen Phase 6 evidence (PHASE6_SUMMARY.json). "
                    "Safari 17.4.1 omitted: performance not collected (correctness only).", 11, INK2))
    out.append("</svg>")
    return "\n".join(out)


def fig2(envs):
    W, left, top, rowh, bh = 980, 210, 100, 108, 24
    H = top + rowh * len(envs) + 50
    maxv = max(sum(e["canonical_static_median_ms"][k][w] for w in ("p128", "decode64")) / 1000
               for e in envs for k in COL)
    span = W - left - 120
    sx = lambda v: v / (maxv * 1.05) * span
    out = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>",
           f"<rect width='100%' height='100%' fill='{SURFACE}'/>",
           text(24, 34, "One interactive turn takes about 34–75 s on the best kernel", 20, INK, weight="600"),
           text(24, 58, "Representative turn = prefill 128 tokens + decode 64 tokens (seconds, median of 6 retained runs; "
                "model load excluded).", 13, INK2)]
    lx = 24
    for k in ("generic", "dot", "pairwise"):
        out.append(f"<rect x='{lx}' y='70' width='12' height='12' rx='2' fill='{COL[k]}'/>")
        out.append(text(lx + 18, 81, NAME[k], 13, INK))
        lx += 290
    for v in range(0, int(maxv * 1.05) + 1, 20):
        x = left + sx(v)
        out.append(f"<line x1='{x}' x2='{x}' y1='{top - 6}' y2='{H - 40}' stroke='{GRID}' stroke-width='1'/>")
        out.append(text(x, H - 24, f"{v} s", 11, INK2, "middle"))
    for i, e in enumerate(envs):
        y0 = top + i * rowh
        out.append(text(24, y0 + 44, e["label"], 14, INK, weight="600"))
        for m, k in enumerate(("generic", "dot", "pairwise")):
            v = sum(e["canonical_static_median_ms"][k][w] for w in ("p128", "decode64")) / 1000
            y = y0 + m * (bh + 4)
            out.append(hbar(left, y, sx(v), bh, COL[k]))
            out.append(text(left + sx(v) + 6, y + bh - 7, f"{v:.1f} s", 12, INK))
    out.append(text(24, H - 6, "Source: frozen Phase 6 evidence (PHASE6_SUMMARY.json). Safari 17.4.1 omitted: "
                    "performance not collected.", 11, INK2))
    out.append("</svg>")
    return "\n".join(out)


def main():
    s = json.loads(SUMMARY.read_text())
    envs = [e for e in s["environments"] if e["phase6_environment_pass"] is not None]
    OUT.mkdir(exist_ok=True)
    (OUT / "fig1_kernel_speedup_vs_generic.svg").write_text(fig1(envs))
    (OUT / "fig2_turn_latency.svg").write_text(fig2(envs))
    print("wrote", sorted(p.name for p in OUT.iterdir()))


if __name__ == "__main__":
    main()
