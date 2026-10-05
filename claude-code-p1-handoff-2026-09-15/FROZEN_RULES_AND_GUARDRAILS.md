# Frozen rules and guardrails

1. Never retune Phase 5D. Never alter Phase 6 thresholds after canonical measurement started.
2. Never rerun a noisy canonical measurement just to improve the result.
3. Retain all measured samples. No outlier removal.
4. Generic baseline is NOT scalar. Call it: generic C++ I2_S compatibility implementation -> Clang/Emscripten -O3 -msimd128 -> compiler-autovectorized WASM SIMD128.
5. Do not claim universal 2x full-inference speedup. The original >=2x end-to-end gate was broadly not passed.
6. Edge p32 was 1.9918x, not >2x.
7. Do not use the old Node ~2.239x microbenchmark as a final browser claim; it was provisional/superseded due possible hoisting concerns.
8. Do not say V8 dot is broken, Safari dot is broken, or ARM causes the effect.
9. Do not attribute exact JIT native lowering causality without native JIT inspection.
10. Pairwise is a controlled instruction-sequence substitution, not proof of a specific JIT bug.
11. The linked pairwise full runtime is not globally dot-free; only the target I2_S object replaced all 16 target dot instructions.
12. Model load is excluded from kernel/inference timing claims.
13. Same browser family on Windows and Mac uses different versions here; do not make CPU-only causal claims from that comparison.
14. Phase 5D microkernel selector success and Phase 6 full-inference transfer are separate questions.
15. Phase 6 regret is based on the selected kernel's canonical static time divided by the independently frozen best static time. Adaptive measured times are retained/reported but do not redefine the oracle.
16. Both adaptive sessions are evaluated independently.
17. Do not change the canonical static aggregation: pool 3+3 retained samples across the two static sessions, median of all six.
18. Do not alter G/D/P mappings or artifact hashes.
19. `crossOriginIsolated=false` is acceptable because the experiment is single-threaded and does not use pthreads/SAB.
20. Never replace the historical good GGUF with the current broken upstream file.
21. If an expected frozen file is missing, locate/copy the original artifact. Do not reconstruct a supposedly frozen artifact from memory unless you explicitly create a new version and label it as such.
22. All result freezes must include raw JSON, evaluator output, protocol/evaluation docs, SHA256 manifest, and a concise RESULT.md.
