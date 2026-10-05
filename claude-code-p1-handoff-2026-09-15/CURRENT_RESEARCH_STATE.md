# Current research state — P1 Ternary WASM Kernel

## Research question

Can a ternary matrix kernel designed specifically around WebAssembly SIMD128 make CPU-only browser inference practically useful on devices that do not have a viable WebGPU path?

Framing: reach / fallback / always-on capability, not universal speed superiority.

## Historical model

Microsoft BitNet b1.58 2B4T historical GGUF I2_S.

- revision: `6e8c386a5609ebd6ef546dc3cb89d684be5c08d4`
- bytes: `1844472032`
- SHA256: `13939ce5030319a35db346e5dba7a3a3bd599dfc18b113a2a97446ff964714c5`

Do not use the currently broken upstream GGUF.

## Frozen kernel identities

Phase 6 full runtime WASM:

- G generic: `76317e0043e1468d35f81d8df18650c4d50d6d363983027463f9eb6abdb52ebf`
- D handwritten dot: `756a9e2230caa9a653fddb12c0ea9e3d12fb551345982c180cfb5c06aefbca9d`
- P handwritten pairwise: `69d125579180e84c796d9d3a6039d53451df9415c3a2225cc2db20b5e360e624`

Frozen selector WASM:

- `944fc9f7818d34383a012328525243b069bf77fd147aa4ce22a08f657b720561`

Frozen Phase 6 protocol SHA256:

- `5431b9c769d08b1bb5fbc0e7c9c0d04a4e569c573ad07ab0b2c64c9afda8a728`

Frozen Windows correctness-v2 result SHA referenced by the canonical harness:

- `1f52d7ba0df6c4c6cd7c9d241a52d72e1831b92820c9fa37c8e8a7d506a0df14`

## Phase 4D final controlled instruction isolation

The experimental change replaces the two target dot expressions in the I2_S source path with `i16x8.mul + i32x4.extadd_pairwise_i16x8` only. Do not describe the whole linked pairwise runtime as dot-free; it still has 8 unrelated/common linked dot instructions elsewhere.

Canonical v6.2 direction:

- Windows Chrome 152: D/G ~1.933, P/G ~1.632, P/D ~0.844
- M1 Chrome 153: D/G ~0.824, P/G ~1.125, P/D ~1.366
- M1 Firefox 155: D/G ~1.296, P/G ~1.513, P/D ~1.167
- M1 Safari 17.4.1: D/G ~0.868, P/G ~1.013, P/D ~1.166

Interpretation only: same exact WASM instruction strategy behaves differently across browser/platform environments. Controlled substitution implicates instruction-selection/lowering/optimization path. It does NOT prove a specific JIT bug or native lowering cause.

## Phase 5D final selector

Frozen and CLOSED. Do not retune.

- 8/8 original Phase 5D runs: selector wall <200 ms
- max wall ~182 ms
- max regret vs frozen microkernel oracle ~1.01266
- no UA/browser/OS/CPU hardcoding

Phase 6 may show transfer failure; that does not invalidate the original Phase 5D result against its own microkernel oracle.

## Phase 6 — current status

### Windows Chrome 152 — COMPLETE / CLOSED / FAIL

Canonical pooled static oracle winner: D for all five workloads.

Canonical static medians:

- p32: D `7243.200 ms`
- p64: D `15394.200 ms`
- p128: D `36630.550 ms`
- p256: D `62872.950 ms`
- decode64: D `38402.800 ms`

Adaptive session 1:

- selected P
- selector wall `152.8 ms`
- GM regret `1.314259815...`
- FAIL

Adaptive session 2:

- selected D
- selector wall `157.3 ms`
- GM regret `1.0`
- PASS

Environment result: FAIL because both adaptive sessions are evaluated independently and every session must satisfy the frozen `<=1.05` environment-level regret gate.

Do not rerun Windows canonical data. Do not remove noisy samples.

### Apple M1 Chrome 153 — PERFORMANCE COMPLETE / PASS

Canonical pooled static oracle winner: P for all five workloads.

Canonical static medians:

- p32: P `3913.950 ms`
- p64: P `7784.850 ms`
- p128: P `16165.450 ms`
- p256: P `34624.050 ms`
- decode64: P `17863.450 ms`

Adaptive session 1:

- selected P
- selector wall `161.1 ms`
- GM regret `1.0`
- PASS

Adaptive session 2:

- selected P
- selector wall `151.2 ms`
- GM regret `1.0`
- PASS

Performance environment result: PASS.

Important protocol caveat: the frozen Phase 6 document states correctness must pass for every tested environment and before canonical performance measurement. The M1 Chrome performance data was already collected before a per-environment correctness-v2 run was performed. Do NOT erase or hide this ordering deviation. Locate the exact frozen correctness-v2 harness from the local Windows repo, run it unchanged on M1 Chrome as post-hoc environment validation, and label it explicitly as post-hoc validation. Do not rerun the canonical performance merely to improve protocol appearance; if strict ordering compliance is required, that would need a new version/phase, not silent replacement.

### M1 Firefox 155 — NOT STARTED in Phase 6 canonical matrix

Required order from now on:

1. exact unchanged correctness-v2 in Firefox 155
2. Static Session 1: G -> D -> P
3. Static Session 2: P -> D -> G
4. Adaptive Session 1
5. Adaptive Session 2
6. exact frozen evaluator
7. freeze raw evidence and hashes

### M1 Safari 17.4.1 — NOT STARTED in Phase 6 canonical matrix

Same sequence as Firefox, with correctness first.

## Phase 7 — frozen analysis concept

No new benchmark.

Representative interactive turn:

`p128 + decode64`

Choose ONE universal static kernel G/D/P by lowest cross-environment geometric-mean representative-turn latency across the completed Phase 6 environments.

For each environment:

- `turn_selected = p128_selected + decode64_selected`
- `turn_universal = p128_universal + decode64_universal`
- `saving = turn_universal - turn_selected`
- use maximum canonical Phase 5D selector wall for that environment conservatively
- if `saving <= 0`: no finite break-even
- else `ceil(selector_wall / saving)`

Report steady-state and first-use cost. Do not invent a benefit if saving <= 0.

## Phase 8 — generalization

Goal: test on genuinely unseen environment/device(s), then STOP P1 experimentation.

Phase 8 protocol has not yet been frozen. Before any Phase 8 measurement, write a protocol that preserves the core semantics and clearly defines unseen-device selection, correctness, static/adaptive runs, aggregation, and stop rule. Freeze/hash it before measurement.

Do not call an already-used Windows Chrome 152 or M1 browser environment an unseen device.
