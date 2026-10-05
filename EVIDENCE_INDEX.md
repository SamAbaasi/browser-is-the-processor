# P1 — The Browser Is the Processor: final evidence index

Closed: 2026-10-05. P1 experimentation is STOPPED (Phase 8 hardware stop).
Every number below comes from frozen evidence in this repository. The data
tables at the end are generated from the frozen JSON.

## 1. Research question and framing
Can a ternary matrix kernel designed around WebAssembly SIMD128 make CPU-only
browser inference practically useful on devices without a viable WebGPU path?
The framing is reach, fallback and always-on capability. It does not claim
universal speed superiority.

## 2. Artifact identities
| Artifact | SHA256 |
|---|---|
| Historical GGUF (microsoft/bitnet-b1.58-2B-4T-gguf @ 6e8c386a…, 1,844,472,032 bytes; verified externally) | 13939ce5030319a35db346e5dba7a3a3bd599dfc18b113a2a97446ff964714c5 |
| G — generic C++ I2_S → Clang/Emscripten -O3 -msimd128 (compiler-autovectorized WASM SIMD128; NOT scalar) | 76317e0043e1468d35f81d8df18650c4d50d6d363983027463f9eb6abdb52ebf |
| D — handwritten i32x4.dot_i16x8_s | 756a9e2230caa9a653fddb12c0ea9e3d12fb551345982c180cfb5c06aefbca9d |
| P — handwritten i16x8.mul + i32x4.extadd_pairwise_i16x8 | 69d125579180e84c796d9d3a6039d53451df9415c3a2225cc2db20b5e360e624 |
| Phase 5D selector WASM | 944fc9f7818d34383a012328525243b069bf77fd147aa4ce22a08f657b720561 |
| PHASE6_PROTOCOL.md | 5431b9c769d08b1bb5fbc0e7c9c0d04a4e569c573ad07ab0b2c64c9afda8a728 |
| CORRECTNESS_PROTOCOL_V2.md | 23450db07389011fcae5dec72c22dd966304e65018364d3dfd8d6a62bac0de78 |
| PHASE8_PROTOCOL.md (frozen, not executed) | bcd231f02eddb618dacbf62d66dd9c496c60ef9a7c3744092b0a53c1366a41f9 |

## 3. Phase status and gates
| Phase | Status | Gate result |
|---|---|---|
| 4D controlled instruction isolation | closed (frozen before this index) | Direction depends on the environment. Canonical v6.2 ratios: Windows Chrome 152 D/G≈1.933, P/G≈1.632, P/D≈0.844; M1 Chrome 153 D/G≈0.824, P/G≈1.125, P/D≈1.366; M1 Firefox 155 D/G≈1.296, P/G≈1.513, P/D≈1.167; M1 Safari 17.4.1 D/G≈0.868, P/G≈1.013, P/D≈1.166 |
| 5D runtime selector (microkernel) | closed, not retuned | 8/8 runs selector wall < 200 ms (max ≈182 ms); max regret vs frozen microkernel oracle ≈1.01266 |
| 6 adaptive full inference | **closed — FAIL** | Windows Chrome 152 FAIL (session 1 GM regret 1.3143); M1 Chrome 153 PASS; M1 Firefox 155 PASS; M1 Safari 17.4.1 INCOMPLETE (correctness only) |
| 7 break-even | closed (3 environments) | universal static = pairwise; 5 of 6 adaptive sessions: no finite break-even; Windows session 2 saves 19.8%/turn (break-even pending raw Windows Phase 5D wall) |
| 8 generalization | protocol frozen, **not executed** | hardware stop; see experiments/phase8-generalization/HARDWARE_REQUIRED.md |

## 4. Evidence locations
| Evidence | Path | Archive SHA256 |
|---|---|---|
| Windows Chrome 152 raw + evaluation | claude-code-p1-handoff-2026-09-15/current-results/windows-chrome152/ (verified against handoff SHA256SUMS) | — |
| M1 Chrome 153 freeze | evidence/phase6-adaptive-full-inference/m1-chrome153-freeze-2026-09-15/ | 6651635450c5bff51a3693f8d78763613ffa554030939176a501025ea99589dd |
| M1 Firefox 155 freeze | evidence/phase6-adaptive-full-inference/m1-firefox155-freeze-2026-10-05/ | 42aa1db72a7560e326f9ceba7bf51537d614390ad93bbfa12f42b466f5fbadb5 |
| M1 Safari 17.4.1 (INCOMPLETE) | evidence/phase6-adaptive-full-inference/m1-safari17-4-1-INCOMPLETE-2026-10-05/ | 66d87b1cdef773d28557d2436ca55b82fd8b90e0a56bf32495a09b14dc89b546 |
| Correctness-v2 (all environments + frozen harness hashes) | evidence/phase6-adaptive-full-inference/correctness/v2/ | — |
| Phase 6 consolidated summary | evidence/phase6-adaptive-full-inference/final/ (SHA256SUMS inside) | — |
| Phase 7 break-even | evidence/phase7-break-even/ (SHA256SUMS inside) | — |
| Phase 8 protocol + hardware list | experiments/phase8-generalization/ (SHA256SUMS inside) | — |

## 5. Negative results and protocol deviations (all disclosed)
1. **Phase 6 FAIL on Windows Chrome 152.** Adaptive session 1 selected pairwise while the oracle was dot for every workload. This is preserved and was not rerun.
2. **M1 Chrome 153 correctness ran post-hoc**, after canonical performance. This is an ordering deviation; performance was not rerun.
3. **M1 Safari 17.4.1 is INCOMPLETE.** Correctness-v2 passed. Performance was not collected: the first static attempt was aborted at the owner's request and was never observed.
4. **M1 Firefox 155 attempts that produced no evidence:**
   - correctness attempt 1 was not captured (driver bug);
   - static2 attempt 1 was killed by a tool time limit;
   - static2 attempt 2 was lost to a battery-forced sleep.

   None was observed. All are in DRIVER_LOG.jsonl.
5. **Firefox static1 ran on battery** (Low Power Mode off). It was retained per frozen rule 2.
6. **Firefox and Safari were operated by W3C WebDriver** on the real installed browsers. Firefox 155.0 was the official Mozilla build. On Safari, native clicks did not reach page handlers, so the page's own element.click() was used and logged.
7. **The Windows Chrome 152 Phase 5D raw runs are not on the Mac,** so the Windows Phase 7 selector wall is pending. No substitute was used.
8. **The Phase 7 calculator had a logic error** (zero saving marked "pending"). It was fixed before freezing.
9. **The original ≥2x end-to-end gate was broadly not passed.**
   - Edge p32 was 1.9918x, not above 2x.
   - The old Node ≈2.239x microbenchmark is superseded and is not a browser claim.
   - In Phase 6 full inference, the highest kernel-vs-generic speedup is 1.914x (Windows, dot, p64).

## 6. Supported claims
- **Ternary inference works across all four environments.** BitNet b1.58 2B4T (I2_S) runs CPU-only, single-threaded, fully inside desktop browsers. G/D/P produce bit-identical final logits for the canonical input (top1 12366, cosine 1, relL2 0, max |diff| 0).
- **The same WASM SIMD instruction strategy ranks differently across browser/platform environments.** dot is best on Windows Chrome 152; pairwise is best on M1 Chrome 153 and Firefox 155. A controlled substitution implicates instruction selection, lowering or optimization paths.
- **Full-inference speedups over the generic kernel were measured:**
  - up to 1.914x on Windows Chrome 152 (dot, p64);
  - up to 1.522x on M1 Firefox 155 (pairwise);
  - up to 1.152x on M1 Chrome 153 (pairwise).
- **Absolute throughput is low for interactive use.**
  - Best decode is 1.67 tok/s (Windows), 3.58 tok/s (M1 Chrome) and 2.62 tok/s (M1 Firefox).
  - A p128 prefill takes 16–37 s.
- **The frozen selector transferred to full inference in 2 of 3 evaluated environments** and failed in 1. In this matrix, a single static kernel (pairwise) matched the selector's steady-state turn latency in 5 of 6 adaptive sessions.

## 7. Explicitly unsupported claims (do not make)
- A universal 2x full-inference speedup, or that the selector generally pays off.
- That V8, Safari or SpiderMonkey "dot is broken", or that ARM causes the effect.
- Any specific JIT lowering cause without native JIT inspection.
- That the linked pairwise runtime is globally dot-free. Only the target I2_S object replaced its 16 target dot instructions.
- CPU-only causality from same-family browsers on different OS/hardware.
- Any Safari full-inference performance conclusion.
- Any generalization to unseen devices (Phase 8 not executed).
- Selector microbenchmark timings as canonical inference performance.
- That inference including model load was measured: model load is excluded from all inference timings.

## Generated data tables (from frozen JSON; do not edit by hand)

### Phase 6 canonical static medians (ms; median of 6 retained samples)

**Windows / Chrome 152** — oracle best: p32=dot, p64=dot, p128=dot, p256=dot, decode64=dot

| workload | generic (G) | dot (D) | pairwise (P) | D/G speedup | P/G speedup |
|---|---|---|---|---|---|
| p32 | 12,830.9 | 7,243.2 | 9,814.2 | 1.771x | 1.307x |
| p64 | 29,460.2 | 15,394.2 | 20,693.9 | 1.914x | 1.424x |
| p128 | 59,786.2 | 36,630.6 | 41,443.8 | 1.632x | 1.443x |
| p256 | 117,395.6 | 62,872.9 | 88,173.6 | 1.867x | 1.331x |
| decode64 | 49,277.9 | 38,402.8 | 52,103.4 | 1.283x | 0.946x |

Best decode throughput: 1.67 tok/s (decode64, dot). Best p128 prefill: 3.49 tok/s.

**Apple M1 / Chrome 153** — oracle best: p32=pairwise, p64=pairwise, p128=pairwise, p256=pairwise, decode64=pairwise

| workload | generic (G) | dot (D) | pairwise (P) | D/G speedup | P/G speedup |
|---|---|---|---|---|---|
| p32 | 4,477.0 | 5,189.2 | 3,913.9 | 0.863x | 1.144x |
| p64 | 8,968.5 | 10,330.6 | 7,784.9 | 0.868x | 1.152x |
| p128 | 18,338.4 | 21,199.8 | 16,165.5 | 0.865x | 1.134x |
| p256 | 38,700.4 | 44,674.8 | 34,624.1 | 0.866x | 1.118x |
| decode64 | 18,861.5 | 20,464.7 | 17,863.4 | 0.922x | 1.056x |

Best decode throughput: 3.58 tok/s (decode64, pairwise). Best p128 prefill: 7.92 tok/s.

**Apple M1 / Firefox 155** — oracle best: p32=pairwise, p64=pairwise, p128=pairwise, p256=pairwise, decode64=pairwise

| workload | generic (G) | dot (D) | pairwise (P) | D/G speedup | P/G speedup |
|---|---|---|---|---|---|
| p32 | 6,805.0 | 5,353.5 | 4,470.0 | 1.271x | 1.522x |
| p64 | 13,630.5 | 10,425.0 | 8,954.5 | 1.307x | 1.522x |
| p128 | 27,138.0 | 21,378.5 | 18,637.5 | 1.269x | 1.456x |
| p256 | 57,157.0 | 46,832.0 | 41,022.5 | 1.220x | 1.393x |
| decode64 | 27,478.0 | 25,487.5 | 24,402.5 | 1.078x | 1.126x |

Best decode throughput: 2.62 tok/s (decode64, pairwise). Best p128 prefill: 6.87 tok/s.

### Phase 6 adaptive sessions

| environment | session | selected | selector wall (ms) | GM regret | pass |
|---|---|---|---|---|---|
| windows-chrome152 | 1 | pairwise | 152.8 | 1.3143 | False |
| windows-chrome152 | 2 | dot | 157.3 | 1.0000 | True |
| m1-chrome153 | 1 | pairwise | 161.1 | 1.0000 | True |
| m1-chrome153 | 2 | pairwise | 151.2 | 1.0000 | True |
| m1-firefox155 | 1 | pairwise | 188.0 | 1.0000 | True |
| m1-firefox155 | 2 | pairwise | 161.0 | 1.0000 | True |

### Correctness-v2 (all four environments)

| environment | pass | ordering | top1 ids G/D/P | result SHA256 |
|---|---|---|---|---|
| windows-chrome152 | True | before canonical performance (frozen reference result) | 12366/12366/12366 | `1f52d7ba0df6c4c6…` |
| m1-chrome153 | True | POST-HOC: run after canonical performance (protocol-ordering deviation, disclosed; performance not rerun) | 12366/12366/12366 | `8835997a8413893c…` |
| m1-firefox155 | True | before canonical performance | 12366/12366/12366 | `7db35b3bebac31f1…` |
| m1-safari17-4-1 | True | before any performance session | 12366/12366/12366 | `ee6cb066a15d8301…` |

### Phase 7 break-even (3 completed environments; universal static = pairwise)

| environment | session | selected | saving/turn (ms) | selector wall used (ms) | break-even |
|---|---|---|---|---|---|
| windows-chrome152 | 1 | pairwise | 0.0 | unavailable | no finite break-even |
| windows-chrome152 | 2 | dot | 18,513.9 | unavailable | pending: canonical Phase 5D selector wall unavailable (= 1 turn for any wall <= 18513.9 ms) |
| m1-chrome153 | 1 | pairwise | 0.0 | 172.40000000037253 | no finite break-even |
| m1-chrome153 | 2 | pairwise | 0.0 | 172.40000000037253 | no finite break-even |
| m1-firefox155 | 1 | pairwise | 0.0 | 173 | no finite break-even |
| m1-firefox155 | 2 | pairwise | 0.0 | 173 | no finite break-even |
