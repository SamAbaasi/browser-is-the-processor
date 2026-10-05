# Phase 6 correctness sub-protocol v2

Status: FROZEN BEFORE SUCCESSFUL CORRECTNESS MEASUREMENT
Date: 2026-09-15

Supersedes:
CORRECTNESS_PROTOCOL.md / harness v1

Reason:
Harness v1 aborted during model tensor loading before logits were
produced. The historical logit probe did not disable mmap for browser
WORKERFS execution.

No numerical threshold was changed.

Purpose:
Verify numerical compatibility of the three full browser inference
kernel variants before Phase 6 canonical performance measurements.

Variants:
G = generic compiler-autovectorized SIMD128 runtime
D = handwritten dot runtime
P = handwritten pairwise runtime

Canonical input:
128000,791,6864,315,9822,374

Configuration:
- historical BitNet GGUF
- CPU-only browser execution
- one thread
- n_ctx = 128
- mmap disabled
- no forced continuation tokens
- full final-logit vector dumped as float32
- correctness runs are NOT performance measurements

Required checks:
1. all three probes execute successfully
2. identical vocabulary size
3. zero NaN logits
4. zero infinite logits

Numerical comparisons:
- G vs D
- G vs P
- D vs P

Correctness gate for every pair:
- cosine >= 0.99
- relative_l2 <= 0.05

Top-1 token IDs and top-1/top-2 margins are reported.
Top-1 disagreement alone is not a failure condition because previously
documented numerical validation contained near-tie top-1 flips.

No thresholds may be changed after v2 correctness measurement begins.

If correctness fails:
STOP before canonical Phase 6 performance measurement.
