# Phase 6 — M1 Chrome 153

Performance environment gate: PASS

Canonical pooled static oracle:
p32      -> pairwise 3913.950 ms
p64      -> pairwise 7784.850 ms
p128     -> pairwise 16165.450 ms
p256     -> pairwise 34624.050 ms
decode64 -> pairwise 17863.450 ms

Adaptive Session 1:
selected: pairwise
selector wall: 161.100 ms
GM regret: 1.000000
gate <= 1.05: PASS

Adaptive Session 2:
selected: pairwise
selector wall: 151.200 ms
GM regret: 1.000000
gate <= 1.05: PASS

Environment result:
PASS

No canonical run was rerun.
No retained samples were removed.
No selector threshold was changed.
