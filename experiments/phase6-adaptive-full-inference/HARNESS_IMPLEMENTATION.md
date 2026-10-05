# Phase 6 canonical harness implementation

Status: FROZEN BEFORE CANONICAL PERFORMANCE MEASUREMENT
Date: 2026-09-15

Protocol:
PHASE6_PROTOCOL.md
SHA256:
5431b9c769d08b1bb5fbc0e7c9c0d04a4e569c573ad07ab0b2c64c9afda8a728

Correctness prerequisite:
Windows Chrome 152 correctness v2 PASS
result SHA256:
1f52d7ba0df6c4c6cd7c9d241a52d72e1831b92820c9fa37c8e8a7d506a0df14

Static sessions:

Session 1:
G -> D -> P

Session 2:
P -> D -> G

Within each kernel, workloads run in fixed order:
p32 -> p64 -> p128 -> p256 -> decode64

Each workload execution uses:
- a fresh Web Worker
- the frozen full-inference runtime for that kernel
- the user-selected historical GGUF through WORKERFS
- one model load
- exactly one discarded warmup
- exactly three retained inference measurements

Model loading is recorded but excluded from inference medians.

All three retained measurements are preserved.
No outlier removal is performed.

Adaptive sessions:

Each adaptive session:
1. runs the exact frozen Phase 5D selector once
2. verifies schema and frozen selector WASM SHA
3. maps the selected kernel to its frozen full-inference runtime
4. executes the five workloads using that selected runtime
5. uses a fresh inference worker per workload
6. preserves selector wall time separately from inference time

Selector mapping:

generic  -> G -> browser/dist/generic
dot      -> D -> browser/dist/handwritten
pairwise -> P -> browser/dist/pairwise

Frozen full-runtime WASM identities:

G:
76317e0043e1468d35f81d8df18650c4d50d6d363983027463f9eb6abdb52ebf

D:
756a9e2230caa9a653fddb12c0ea9e3d12fb551345982c180cfb5c06aefbca9d

P:
69d125579180e84c796d9d3a6039d53451df9415c3a2225cc2db20b5e360e624

Frozen Phase 5D selector WASM:
944fc9f7818d34383a012328525243b069bf77fd147aa4ce22a08f657b720561

Historical model:
bytes = 1844472032
SHA256 =
13939ce5030319a35db346e5dba7a3a3bd599dfc18b113a2a97446ff964714c5

The browser harness checks model byte size.
The historical model SHA is verified externally, not recomputed in-browser.

No Phase 6 thresholds or ordering may be changed after the first
canonical measurement.
