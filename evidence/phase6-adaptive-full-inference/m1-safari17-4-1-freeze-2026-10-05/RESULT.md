# Phase 6 — M1 Safari 17.4.1

Correctness-v2: PASS (run before canonical performance; SHA256 ee6cb066a15d830172cedea66d7f2627d2469aeed5d1430ea1fc83fd2b6acacf)
Performance environment gate: FAIL

Canonical pooled static oracle (median of 6 retained samples):
p32      -> pairwise 4374.000 ms  (ranking pairwise < dot < generic)
p64      -> pairwise 8767.500 ms  (ranking pairwise < generic < dot)
p128     -> pairwise 18147.000 ms  (ranking pairwise < generic < dot)
p256     -> pairwise 39553.000 ms  (ranking pairwise < generic < dot)
decode64 -> generic 22811.000 ms  (ranking generic < dot < pairwise)

Canonical static medians (ms):
| workload | generic | dot | pairwise |
|---|---|---|---|
| p32 | 16267.000 | 5036.000 | 4374.000 |
| p64 | 9280.000 | 10076.000 | 8767.500 |
| p128 | 18979.000 | 21033.500 | 18147.000 |
| p256 | 43572.500 | 45769.500 | 39553.000 |
| decode64 | 22811.000 | 23844.500 | 44003.000 |

Adaptive Session 1:
selected: generic
selector wall: 141.000 ms
decision mode: clear-winner-stage1
GM regret: 1.353071
gate <= 1.05: FAIL

Adaptive Session 2:
selected: pairwise
selector wall: 163.000 ms
decision mode: clear-winner-stage1
GM regret: 1.140427
gate <= 1.05: FAIL

Environment result: FAIL

No retained sample was removed. No threshold, ordering, or selector
parameter was changed. Aborted/uncaptured attempts and all environment
conditions are disclosed in METHODOLOGY_NOTES.md and DRIVER_LOG.jsonl.
