# M1 Chrome 153 — correctness-v2 (POST-HOC environment validation)

Date processed: 2026-09-15
Result file: m1-chrome153-correctness-v2.json
SHA256: 8835997a8413893c51b090e03c8f39a260d1fd4f6b9627b039757bd05d24761c

## Status: PASS (post-hoc)

All frozen correctness-v2 thresholds satisfied:
- schema p1-phase6-correctness-v2, canonical input [128000,791,6864,315,9822,374]
- same_vocab = true (128256), finite_pass = true
- every pair (G/D/P) cosine = 1.0 (>= 0.99), relative_l2 = 0.0 (<= 0.05), max_abs_diff = 0
- all three variants top1 = 12366 (matches Windows Chrome 152 reference); NO token-ordering deviation

## PROTOCOL-ORDERING DEVIATION (must not be hidden)

The frozen Phase 6 protocol requires correctness to pass BEFORE canonical
performance measurement for each environment. For M1 Chrome 153 the
canonical PERFORMANCE data was collected FIRST (already frozen at
evidence/phase6-adaptive-full-inference/m1-chrome153-freeze-2026-09-15/),
and this correctness-v2 run was performed AFTERWARD as post-hoc
environment validation.

- The performance result was NOT rerun to fix protocol appearance.
- Strict ordering compliance would require a new phase/version, not a
  silent replacement (per CURRENT_RESEARCH_STATE.md).
- This deviation is temporal (step ordering) only; the correctness
  result itself is a clean PASS.

Actual browser confirmed by user_agent: Chrome/153.0.0.0 on Mac
(actual Chrome 153, not a substitute engine).
