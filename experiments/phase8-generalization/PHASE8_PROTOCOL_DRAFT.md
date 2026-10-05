# Phase 8 — Generalization to Unseen Environments (DRAFT)

Status: **DRAFT — NOT FROZEN, NOT HASHED.** No measurement may begin
until this document is reviewed, finalized, and its SHA256 recorded.
Date drafted: 2026-09-15

This draft preserves the frozen Phase 6 semantics (PHASE6_PROTOCOL.md,
SHA256 `5431b9c769d08b1bb5fbc0e7c9c0d04a4e569c573ad07ab0b2c64c9afda8a728`)
and reuses the frozen artifacts and evaluator unchanged. It changes
nothing about kernels, thresholds, workloads, aggregation, or the
selector. Its only new content is the definition of an *unseen*
environment and the generalization stop rule.

## Research question

Does the Phase 5D runtime kernel-selection signal — which chose a
near-best static kernel under full BitNet browser inference in the
Phase 6 matrix — continue to hold on a genuinely **unseen** device /
environment that played no role in designing or tuning the selector?

## What counts as an unseen environment (hard gate)

An environment qualifies for Phase 8 only if ALL hold:

1. It is NOT any environment already used anywhere in P1:
   - NOT Windows Chrome 152
   - NOT Apple M1 Chrome 153
   - NOT Apple M1 Firefox 155
   - NOT Apple M1 Safari 17.4.1
2. Its (CPU microarchitecture family) is materially different from, OR
   its browser engine/version is materially different from, every
   environment above. A new browser version on the *same* M1 machine is
   the weakest possible form and must be labeled as such; prefer a
   different CPU family (e.g. non-Apple-Silicon, or a different vendor).
3. It was not used to tune Phase 5D or select any Phase 6 threshold.
4. No per-environment hardcoding of any kind is introduced to make it
   pass. The selector WASM is byte-identical
   (`944fc9f7818d34383a012328525243b069bf77fd147aa4ce22a08f657b720561`).

Record for each Phase 8 environment: OS + version, CPU model/family,
browser + exact version, RAM, and why it is unseen relative to the four
prior environments.

## Frozen inputs (unchanged, verified before measurement)

- Historical GGUF I2_S: bytes `1844472032`, SHA256
  `13939ce5030319a35db346e5dba7a3a3bd599dfc18b113a2a97446ff964714c5`
- Kernels: G `76317e00…52ebf`, D `756a9e22…bca9d`, P `69d12557…0e624`
- Selector WASM: `944fc9f7…20561`
- Correctness-v2 harness + `CORRECTNESS_PROTOCOL_V2.md` (frozen)
- Phase 6 evaluator `tools/evaluate_phase6_environment.py` (unchanged)

## Per-environment sequence (identical to Phase 6, correctness first)

1. **Correctness-v2** on this environment, BEFORE any performance.
   Thresholds unchanged: all logits finite / same vocab `128256` /
   pairwise cosine >= .99 / relL2 <= .05. A top1 ordering disagreement
   alone is NOT a failure but MUST be recorded. Any integration
   correctness failure stops Phase 8 performance testing for that
   environment.
2. **Static Session 1**: G -> D -> P; within each kernel workloads run
   p32 -> p64 -> p128 -> p256 -> decode64; one discarded warmup, three
   retained measurements; fresh worker per workload; model load excluded
   from inference medians; no outlier removal.
3. **Static Session 2**: P -> D -> G, same rules.
4. **Adaptive Session 1**: run the frozen Phase 5D selector once, verify
   selector WASM SHA, map selection -> full runtime, verify runtime
   identity, one discarded warmup, three retained measurements per
   workload; selector wall recorded separately.
5. **Adaptive Session 2**: same.
6. Run the frozen evaluator to produce `evaluation.json`
   (schema `p1-phase6-environment-evaluation-v1`).
7. Freeze: raw JSON, evaluator output, protocol/eval docs, MODEL_SHA256,
   RUNTIME_SHA256, SHA256SUMS manifest, and a concise RESULT.md.

## Aggregation, oracle, gate (unchanged from Phase 6)

- canonical_static(kernel, workload) = median of the 6 retained samples
  (3 per static session), no outlier removal.
- best_static(workload) = min over G/D/P.
- adaptive_regret(workload) = canonical_static(selected, workload) /
  best_static(workload). Adaptive measured times are retained/reported
  but do NOT redefine the oracle.
- environment-level regret = geometric mean over p32,p64,p128,p256,
  decode64.
- **Gate: correctness passes AND environment-level GM regret <= 1.05,
  each adaptive session evaluated independently.**

## Generalization interpretation

- PASS on an unseen environment = the selector signal transferred there.
- FAIL is a legitimate scientific result and is preserved (as Windows
  Chrome 152 FAIL was preserved). Do not retune to convert a FAIL.
- No claim of universal transfer may be made from a single unseen
  environment; report per-environment and, if multiple unseen
  environments exist, report the count that passed with full raw data.

## Stop rule

- If NO qualifying unseen environment is available: finalize + freeze
  this protocol, then STOP with a precise list of the hardware/browser
  environments still required. Do NOT substitute any of the four prior
  environments and do NOT fabricate generalization data.
- If unseen environment(s) are available: execute the frozen protocol on
  each, freeze evidence, then STOP P1 experimentation. No selector or
  measurement-setting changes. Any changed protocol becomes a new
  phase/version.

## Freeze procedure for THIS protocol

Before any Phase 8 measurement:
1. Finalize this text (remove DRAFT status).
2. Compute its SHA256 and record it in the Phase 8 freeze + evidence
   index as the frozen Phase 8 protocol hash.
3. Only then begin correctness-v2 on the first unseen environment.
