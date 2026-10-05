# Phase 6 — M1 Firefox 155

Correctness-v2: PASS (run before canonical performance; SHA256 7db35b3bebac31f1fe737ec066b114964e26ddd0b166a204a764d8dc556e6c56)
Performance environment gate: PASS

Canonical pooled static oracle (median of 6 retained samples):
p32      -> pairwise 4470.000 ms  (ranking pairwise < dot < generic)
p64      -> pairwise 8954.500 ms  (ranking pairwise < dot < generic)
p128     -> pairwise 18637.500 ms  (ranking pairwise < dot < generic)
p256     -> pairwise 41022.500 ms  (ranking pairwise < dot < generic)
decode64 -> pairwise 24402.500 ms  (ranking pairwise < dot < generic)

Canonical static medians (ms):
| workload | generic | dot | pairwise |
|---|---|---|---|
| p32 | 6805.000 | 5353.500 | 4470.000 |
| p64 | 13630.500 | 10425.000 | 8954.500 |
| p128 | 27138.000 | 21378.500 | 18637.500 |
| p256 | 57157.000 | 46832.000 | 41022.500 |
| decode64 | 27478.000 | 25487.500 | 24402.500 |

Adaptive Session 1:
selected: pairwise
selector wall: 188.000 ms
decision mode: clear-winner-stage1
GM regret: 1.000000
gate <= 1.05: PASS

Adaptive Session 2:
selected: pairwise
selector wall: 161.000 ms
decision mode: bounded-confirmation-pair
GM regret: 1.000000
gate <= 1.05: PASS

Environment result: PASS

No retained sample was removed. No threshold, ordering, or selector
parameter was changed. Aborted/uncaptured attempts and all environment
conditions are disclosed in METHODOLOGY_NOTES.md and DRIVER_LOG.jsonl.
