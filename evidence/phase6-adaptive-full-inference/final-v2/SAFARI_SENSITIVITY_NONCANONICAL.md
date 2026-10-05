# M1 Safari 17.4.1: anomaly report and sensitivity analysis (NON-CANONICAL)

This file does NOT change any canonical result. The frozen aggregation (median
of all 6 retained samples, no removal) and the frozen gate apply unchanged:
**Safari 17.4.1 Phase 6 = FAIL** (adaptive 1: generic, GM regret 1.3531;
adaptive 2: pairwise, GM regret 1.1404). The analysis below is reported for
transparency only.

## Anomaly 1: first-session start effect (generic p32)
- generic p32 samples: static session 1 = 28,599 / 29,947 / 27,860 ms;
  static session 2 = 4,674 / 4,512 / 4,521 ms.
- Static session 1 ran in order G→D→P. generic p32 was its very first workload
  in a freshly launched Safari process (the discarded warm-up preceded these
  samples). generic p64 in session 1 shows the same effect on its first sample
  only (23,517 then 8,954 / 9,002 ms).
- The canonical median of the six bimodal samples is 16,267 ms, which is in
  neither cluster. No cause is claimed.

## Anomaly 2: pairwise decode is slow and unstable in Safari
- pairwise decode64 samples: 28,303 / 42,862 / 45,144 (session 1);
  27,840 / 64,710 / 45,550 (session 2). Coefficient of variation 0.32.
- generic decode64 samples: 22,615–23,214 ms, coefficient of variation 0.011.
- Even the fastest pairwise decode sample (27,840 ms) is slower than the slowest
  generic sample (23,214 ms). The ordering is therefore not an artefact of
  variance. No cause is claimed.

## Sensitivity (environment GM regret per selection; gate ≤ 1.05)
| Scenario | generic-selected (adaptive 1) | pairwise-selected (adaptive 2) | Safari verdict |
|---|---|---|---|
| Canonical: all 6 samples | 1.3531 FAIL | 1.1404 FAIL | FAIL |
| S1: drop session-1 generic p32 samples only | 1.0474 pass | 1.1404 FAIL | FAIL |
| S2: static session 2 samples only, every cell | 1.0167 pass | 1.2229 FAIL | FAIL |

## Supported reading
- The Safari FAIL is robust. Adaptive session 2's selection (pairwise) fails
  under every scenario, because pairwise decode is genuinely slower there.
- Adaptive session 1's failure depends on the session-1 start anomaly in a
  single cell. This must be stated whenever that session is discussed.
- In Safari the full-inference winner depends on the workload: pairwise is
  fastest for all four prefill sizes, and generic is fastest for decode. This
  holds in all scenarios above. It is the only environment of the four where
  the winner splits by workload.
