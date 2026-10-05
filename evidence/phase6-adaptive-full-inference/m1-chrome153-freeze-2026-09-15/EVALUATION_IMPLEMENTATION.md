# Phase 6 evaluation implementation

Status: FROZEN BEFORE ADAPTIVE SESSION 2
Date: 2026-09-15

This document clarifies deterministic aggregation of the already
frozen Phase 6 protocol. It does not modify any threshold, workload,
kernel, ordering, or measurement procedure.

Static aggregation:

For each environment, kernel, and workload:

1. take the 3 retained measurements from Static Session 1
2. take the 3 retained measurements from Static Session 2
3. concatenate all 6 measurements
4. remove no samples
5. compute the median of the 6 wall-clock measurements

This value is canonical_static_time(kernel, workload).

Full-inference static oracle:

best_static_time(workload) =
min(
  canonical_static_time(G, workload),
  canonical_static_time(D, workload),
  canonical_static_time(P, workload)
)

Adaptive regret:

The adaptive session's measured inference timings are retained and
reported, but are not used to redefine the static oracle.

For each adaptive session and workload:

adaptive_regret(workload) =
canonical_static_time(selected_kernel, workload)
/
best_static_time(workload)

Environment-level regret:

geometric mean of the five workload regrets:
p32, p64, p128, p256, decode64

Success gate:

environment-level regret <= 1.05

Both adaptive sessions are evaluated independently.

No threshold or aggregation rule may be changed after this document
is frozen.
