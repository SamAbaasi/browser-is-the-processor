# Stability analysis of retained static samples (descriptive, NON-CANONICAL)

This folder reads the frozen Phase 6 static-session JSONs (90 retained samples per
environment, 360 in total). It changes nothing and does not redefine any canonical
value, oracle or gate.

- `analyze_stability.py` writes `stability.json`. For each kernel–workload cell it
  records the median, min, max and coefficient of variation (CV), plus the median of
  each session. It also records the winner per workload, whether the winner's slowest
  sample beats the runner-up's fastest ("separated"), and whether each reversed-order
  session alone picks the same winner.
- `make_fig_samples.py` writes `fig_samples.tex`, a pgfplots strip plot of every
  sample divided by its cell median.

Summary:

| Environment | Median cell CV | Max cell CV | Same winner in both sessions | Winner separated | Samples > 1.5× cell median |
|---|---|---|---|---|---|
| Windows Chrome 152 | 0.142 | 0.258 | 4/5 | 1/5 | 0 |
| M1 Chrome 153 | 0.004 | 0.018 | 5/5 | 5/5 | 0 |
| M1 Firefox 155 | 0.027 | 0.153 | 4/5 | 4/5 | 0 |
| M1 Safari 17.4.1 | 0.038 | 0.843 | 4/5 | 4/5 | 8 |

Safari's 8 slow samples:
- 6 come from G's first static session: all three p32 samples, the first p64 sample,
  and two p256 samples.
- 2 come from P's p64 in session 2.

Six-sample medians absorb all of them except the p32 cell.
