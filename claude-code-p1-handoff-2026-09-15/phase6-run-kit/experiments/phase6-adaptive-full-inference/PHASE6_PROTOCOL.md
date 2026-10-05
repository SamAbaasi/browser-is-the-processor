# Phase 6 — Adaptive Full Browser Inference + Break-even

Status: FROZEN BEFORE CANONICAL MEASUREMENT
Date: 2026-09-15

## Research question

Can the frozen Phase 5D runtime kernel selector choose a SIMD kernel
that remains near the best static kernel during full BitNet browser
inference, and when is the startup tuning cost amortized?

## Frozen upstream evidence

Phase 4D:
Controlled generic / dot / pairwise kernel comparison.

Phase 5D:
Budget-bounded runtime selector.

Frozen selector WASM SHA256:

944fc9f7818d34383a012328525243b069bf77fd147aa4ce22a08f657b720561

Historical BitNet GGUF SHA256:

13939ce5030319a35db346e5dba7a3a3bd599dfc18b113a2a97446ff964714c5

## Static full-inference variants

G = generic SIMD compatibility implementation

D = handwritten wasm SIMD using i32x4.dot_i16x8_s

P = handwritten wasm SIMD using
    i16x8.mul + i32x4.extadd_pairwise_i16x8

Only the kernel implementation may differ.

## Adaptive variant

A runs the frozen Phase 5D selector once per session.

The selector chooses G, D, or P from measurement only.

No browser-name, user-agent, operating-system, or CPU-specific
hardcoded selection rule is permitted.

## Environments

1. Windows / Chrome 152
2. Apple M1 / Chrome 153
3. Apple M1 / Firefox 155
4. Apple M1 / Safari 17.4.1

## Inference configuration

- CPU-only browser inference
- one inference thread
- no pthreads
- mmap disabled
- same historical GGUF
- same tokenizer and inference settings
- model loading excluded from kernel-performance claims
- fresh worker/runtime session for independent runs

## Workloads

Prefill:
- 32 tokens
- 64 tokens
- 128 tokens
- 256 tokens

Decode:
- 64 generated tokens

## Correctness

Before canonical performance measurement, verify that G/D/P and the
adaptive-selected runtime preserve expected deterministic inference
behavior for the canonical test prompt.

Any integration correctness failure stops Phase 6 performance testing.

## Static measurement protocol

Two independent sessions per static variant per environment.

Variant order:

Session set 1:
G -> D -> P

Session set 2:
P -> D -> G

Each session:

- model/runtime load excluded
- one discarded warm-up
- three measured inference repetitions per workload
- retain all measurements
- no outlier removal

Primary per-workload statistic:
median measured inference time.

## Adaptive measurement protocol

Two independent adaptive sessions per environment.

Each adaptive session:

1. run the exact frozen Phase 5D selector
2. record selector wall time and decision path
3. instantiate/select the chosen full-inference kernel runtime
4. verify chosen variant identity
5. one discarded inference warm-up
6. three measured repetitions per workload

Selector time and inference time MUST be reported separately.

## Full-inference oracle

For each environment and workload:

best_static =
min(G, D, P median inference time)

adaptive_regret =
selected_static_time / best_static_time

Primary environment-level regret:

geometric mean of workload regrets across:

p32, p64, p128, p256, decode64

## Phase 6 success gate

For every tested environment:

1. correctness passes
2. adaptive environment-level full-inference regret <= 1.05x

Selector wall time is reported but its Phase 5D <200 ms gate is not
redefined here.

No threshold changes are allowed after canonical measurement starts.

## Phase 7 break-even analysis

Phase 7 requires no new benchmark.

It is calculated from frozen Phase 6 full-inference measurements and
the frozen Phase 5D selector cost.

Primary representative interactive turn:

prefill128 + decode64

The universal-static baseline is the ONE static kernel among G/D/P
with the lowest cross-environment geometric-mean interactive-turn
latency.

This universal baseline is selected only for offline comparison.
It is not used by the runtime selector.

For environment e:

turn_selected(e) =
p128_selected(e) + decode64_selected(e)

turn_universal(e) =
p128_universal(e) + decode64_universal(e)

saving_per_turn(e) =
turn_universal(e) - turn_selected(e)

For conservative break-even, use the maximum canonical Phase 5D
selector wall time observed for that environment.

If saving_per_turn <= 0:

break_even = no finite break-even

Otherwise:

break_even_turns =
ceil(selector_wall / saving_per_turn)

Report both:

- steady-state inference performance
- first-use cost = selector wall + first inference turn

## Interpretation constraints

Do not claim:
- universal 2x full-inference speedup
- CPU-only causality for browser differences
- a specific JIT lowering bug without native JIT inspection
- selector microbench timings as canonical inference performance

Phase 4D remains the kernel-performance oracle.

Phase 6 tests whether that kernel-selection signal transfers to
full browser inference.

## Stop rule

After two canonical adaptive sessions per environment and the complete
static matrix are collected:

STOP Phase 6 measurement.

Do not tune selector parameters or measurement settings.

Any changed protocol becomes a new phase/version.
