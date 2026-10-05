# Phase 8 — Generalization to Unseen Environments

Status: **FROZEN 2026-10-05 — NOT EXECUTED (hardware stop).**
No qualifying unseen environment was available when P1 closed. This
protocol is frozen so that any future execution follows it unchanged.
Any change creates a new version (Phase 8 v2) with a new hash.

It preserves the frozen Phase 6 semantics (PHASE6_PROTOCOL.md, SHA256
`5431b9c769d08b1bb5fbc0e7c9c0d04a4e569c573ad07ab0b2c64c9afda8a728`) and
the frozen Phase 7 break-even definition. It reuses the frozen artifacts,
harnesses and evaluator unchanged.

## Research question

The frozen Phase 5D selector's full-inference transfer result was:
- FAIL on Windows Chrome 152
- PASS on Apple M1 Chrome 153
- PASS on Apple M1 Firefox 155
- INCOMPLETE on Apple M1 Safari 17.4.1 (correctness only)

Does that result generalize to genuinely **unseen** environments that
played no role in designing or tuning the selector? What does the frozen
Phase 7 break-even look like there?

## What counts as an unseen environment (hard gate)

An environment qualifies only if ALL of the following hold.

1. It is NOT any environment already used in P1:
   - Windows Chrome 152
   - Apple M1 Chrome 153
   - Apple M1 Firefox 155
   - Apple M1 Safari 17.4.1 (correctness was run there, so it is not unseen)
2. Its CPU microarchitecture family is materially different from every
   environment above, OR its browser engine/version is. A new browser
   version on the same M1 machine is the weakest form and must be labeled
   "weak". A different CPU family or vendor is preferred.
3. It was not used to tune Phase 5D or to choose any Phase 6 threshold.
4. No per-environment hardcoding is introduced. The selector WASM is
   byte-identical (`944fc9f7818d34383a012328525243b069bf77fd147aa4ce22a08f657b720561`).

For each environment, record:
- OS and version
- CPU model and microarchitecture family
- RAM
- browser and exact version
- power source
- why it is unseen relative to the four prior environments

## Frozen inputs (verified before any measurement)

- Historical GGUF I2_S: 1844472032 bytes, SHA256
  `13939ce5030319a35db346e5dba7a3a3bd599dfc18b113a2a97446ff964714c5`
  (verified externally)
- Full-inference runtimes:
  - G `76317e0043e1468d35f81d8df18650c4d50d6d363983027463f9eb6abdb52ebf`
  - D `756a9e2230caa9a653fddb12c0ea9e3d12fb551345982c180cfb5c06aefbca9d`
  - P `69d125579180e84c796d9d3a6039d53451df9415c3a2225cc2db20b5e360e624`
- Selector WASM `944fc9f7…20561`
- Correctness-v2 harness, verified against
  `evidence/phase6-adaptive-full-inference/correctness/v2/FROZEN_HARNESS_SHA256.txt`
- Phase 5D harness and protocol (reference bundle `phase5d-mac-harness.zip`)
- Evaluator `tools/evaluate_phase6_environment.py`
- Break-even calculator `tools/phase7_break_even.py`, as frozen in
  `evidence/phase7-break-even/`

## Operational rules (learned in Phase 6; mandatory)

- Exactly one browser measurement at a time on the machine. Nothing else
  heavy may run concurrently.
- AC power is required for every measured session. The power state is
  recorded at each session start.
- Each session starts in a fresh browser process with a clean profile.
- The person operating the browser, or the automation driver (e.g. W3C
  WebDriver on the real installed browser), must be disclosed. The frozen
  harness pages are used byte-identical.
- Every attempt that produced no evidence (aborts, capture failures,
  infrastructure failures) is logged and disclosed. It is never silently
  replaced.

## Per-environment sequence (correctness first)

1. **Correctness-v2** before any performance measurement. Thresholds are
   unchanged:
   - all logits finite
   - same vocabulary (128256)
   - pairwise cosine >= 0.99
   - relative L2 <= 0.05

   A top-1 disagreement alone is not a failure, but it must be recorded. Any
   integration correctness failure stops performance testing for that
   environment.
2. **Phase 5D canonical runs** ×2 with the frozen Phase 5D harness. They
   record the selector wall, which Phase 7 break-even needs.
3. **Static Session 1:** G → D → P.
   - Workloads run in order p32 → p64 → p128 → p256 → decode64.
   - One discarded warm-up, then three retained measurements.
   - Fresh worker per workload.
   - Model load is excluded from medians.
   - No outlier removal.
4. **Static Session 2:** P → D → G, with the same rules.
5. **Adaptive Session 1:**
   - Run the frozen selector once and verify the selector SHA.
   - Map the selection to its runtime and verify the runtime identity.
   - One discarded warm-up, then three retained measurements per workload.
   - Record the selector wall separately.
6. **Adaptive Session 2:** same as Adaptive Session 1.
7. Run the frozen evaluator to produce `evaluation.json`.
8. Run frozen Phase 7 break-even. Use the universal kernel frozen in
   `evidence/phase7-break-even/RESULT.md` (pairwise) as the baseline, and
   report separately what the universal kernel would be if this
   environment were included.
9. Freeze:
   - raw JSON and evaluator output
   - protocol docs
   - MODEL/RUNTIME SHA files
   - DRIVER_LOG
   - METHODOLOGY_NOTES
   - SHA256SUMS
   - RESULT.md

## Aggregation, oracle, gate (unchanged from Phase 6)

- canonical_static = median of 6 retained samples (3 per static session),
  with no outlier removal
- best_static = min over G, D and P
- adaptive_regret = canonical_static(selected) / best_static
- environment regret = geometric mean over p32, p64, p128, p256 and decode64
- **Gate: correctness passes AND environment GM regret <= 1.05 in each
  adaptive session, evaluated independently.**

## Interpretation constraints

- A FAIL is a legitimate result and is preserved. No retuning.
- No universal-transfer claim may rest on one unseen environment. Report
  per environment and give the count of passes.
- Follow all P1 interpretation constraints:
  - no CPU-only causality claims
  - no JIT-bug attribution without native JIT inspection
  - no universal 2x claim

## Stop rule

- No qualifying environment available: freeze this protocol, list the
  required hardware (see HARDWARE_REQUIRED.md), and STOP. Never substitute
  prior environments or fabricate data.
- If qualifying environments are available: execute this protocol on each,
  freeze the evidence, then STOP P1 experimentation.
