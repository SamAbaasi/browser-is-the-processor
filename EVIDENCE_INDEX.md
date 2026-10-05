# P1 — The Browser Is the Processor: final evidence index (v2)

Closed: 2026-10-05. P1 experimentation is STOPPED (Phase 8 hardware stop).
This index is v2: it covers the complete 4-environment Phase 6 matrix, after
M1 Safari 17.4.1 was resumed and completed. v1 (Safari incomplete) is in git
history. Every number comes from frozen evidence. The data tables at the end are
generated from the frozen JSON by `tools/make_evidence_tables.py`.

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
| 4D controlled instruction isolation | closed | Direction depends on environment. Canonical v6.2 ratios: Windows Chrome 152 D/G≈1.933, P/G≈1.632, P/D≈0.844; M1 Chrome 153 D/G≈0.824, P/G≈1.125, P/D≈1.366; M1 Firefox 155 D/G≈1.296, P/G≈1.513, P/D≈1.167; M1 Safari 17.4.1 D/G≈0.868, P/G≈1.013, P/D≈1.166 |
| 5D runtime selector (microkernel) | closed, not retuned | 8/8 runs selector wall < 200 ms (max ≈182 ms); max regret vs frozen microkernel oracle ≈1.01266 |
| 6 adaptive full inference | **closed — FAIL** | Windows Chrome 152 **FAIL** (A1 GM regret 1.3143); M1 Chrome 153 PASS; M1 Firefox 155 PASS; M1 Safari 17.4.1 **FAIL** (A1 generic 1.3531, A2 pairwise 1.1404; robust under sensitivity, see §5) |
| 7 break-even | **v2 closed (4 environments)**; v1 superseded | universal static = dot; the selector pays off within 1 turn in 5 of 8 sessions, ties in 1, and is slower in 2 (Windows A1, Safari A2); Windows walls unavailable |
| 8 generalization | protocol frozen, **not executed** | hardware stop; see experiments/phase8-generalization/HARDWARE_REQUIRED.md |

## 4. Evidence locations
| Evidence | Path | Archive SHA256 |
|---|---|---|
| Windows Chrome 152 raw + evaluation | claude-code-p1-handoff-2026-09-15/current-results/windows-chrome152/ (verified against handoff SHA256SUMS) | — |
| M1 Chrome 153 freeze | evidence/phase6-adaptive-full-inference/m1-chrome153-freeze-2026-09-15/ | 6651635450c5bff51a3693f8d78763613ffa554030939176a501025ea99589dd |
| M1 Firefox 155 freeze | evidence/phase6-adaptive-full-inference/m1-firefox155-freeze-2026-10-05/ | 42aa1db72a7560e326f9ceba7bf51537d614390ad93bbfa12f42b466f5fbadb5 |
| M1 Safari 17.4.1 freeze (complete) | evidence/phase6-adaptive-full-inference/m1-safari17-4-1-freeze-2026-10-05/ | afd3f0bde6ca9d329f96af0af48e14e3d3f5a64299a9e18aa1542bf5e217ddda |
| M1 Safari 17.4.1 INCOMPLETE record (history, superseded) | evidence/phase6-adaptive-full-inference/m1-safari17-4-1-INCOMPLETE-2026-10-05/ | 66d87b1cdef773d28557d2436ca55b82fd8b90e0a56bf32495a09b14dc89b546 |
| Correctness-v2 (all environments + frozen harness hashes) | evidence/phase6-adaptive-full-inference/correctness/v2/ | — |
| Phase 6 summary v2 (4 environments) + Safari sensitivity (non-canonical) | evidence/phase6-adaptive-full-inference/final-v2/ (SHA256SUMS inside) | — |
| Phase 6 summary v1 (Safari incomplete; superseded) | evidence/phase6-adaptive-full-inference/final/ | — |
| Phase 7 v2 break-even (canonical) | evidence/phase7-break-even-v2/ (SHA256SUMS inside) | — |
| Phase 7 v1 (3 environments; superseded) | evidence/phase7-break-even/ | — |
| Phase 8 protocol + hardware list | experiments/phase8-generalization/ (SHA256SUMS inside) | — |

## 5. Negative results and protocol deviations (all disclosed)
1. **Phase 6 FAIL on Windows Chrome 152.** Adaptive session 1 selected pairwise while the oracle was dot for every workload. Preserved; not rerun.
2. **Phase 6 FAIL on M1 Safari 17.4.1, in both adaptive sessions.**
   - Pairwise decode is genuinely slower and unstable in Safari: decode64 samples 27.8–64.7 s (CV 0.32), versus generic 22.6–23.2 s (CV 0.011).
   - A2 (pairwise) therefore fails under every scenario.
   - A1 (generic) fails canonically, but only because of a first-session start anomaly: generic p32 took 28–30 s in session 1 and 4.5 s in session 2.
   - The non-canonical sensitivity analysis gives A1 1.0474 if those three samples are dropped. The canonical verdict is unchanged. See evidence/phase6-adaptive-full-inference/final-v2/SAFARI_SENSITIVITY_NONCANONICAL.md.
3. **Safari was closed as INCOMPLETE, then resumed at the owner's request.** The INCOMPLETE record is retained. The resumption was decided before any Safari performance result had been seen. Correctness-v2 preceded all performance sessions. Static1 attempt 1 was aborted and never observed.
4. **M1 Chrome 153 correctness ran post-hoc,** after canonical performance (an ordering deviation). Performance was not rerun.
5. **Firefox attempts that produced no evidence:** correctness attempt 1 was not captured (driver bug); static2 attempt 1 was cut by a tool time limit; static2 attempt 2 was lost to a battery-forced sleep. None was observed; all are logged.
6. **Firefox static1 ran on battery** (Low Power Mode off). Retained per frozen rule 2.
7. **WebDriver operated Firefox and Safari** on the real installed browsers.
   - Firefox 155.0 was the official build.
   - On Safari, native clicks did not reach the page handlers, so the page's own element.click() was used and logged.
8. **Windows Chrome 152 Phase 5D raw runs are not on the Mac.** The Windows Phase 7 walls are unavailable; no substitute was used.
9. **Phase 7 values depend on the environment set.** v1 (3 environments, universal pairwise) found no finite break-even in 5 of 6 sessions. v2 (4 environments, universal dot) finds break-even in 1 turn in 5 of 8 sessions. Both are reported; v2 is the protocol-conformant result.
10. **The original ≥2x end-to-end gate was broadly not passed.**
    - Edge p32 was 1.9918x, not >2x.
    - The old Node ≈2.239x microbenchmark is superseded.
    - The highest Phase 6 full-inference kernel-vs-generic speedup is 1.914x (Windows, dot, p64).
    - The Safari p32 ratios above 3x are artefacts of the start anomaly and must not be cited as speedups.

## 6. Supported claims
- **Correctness.** BitNet b1.58 2B4T (I2_S) runs CPU-only, single-threaded, fully inside four desktop browser environments. G, D and P produce bit-identical final logits for the canonical input (top1 12366, cosine 1, relL2 0, max |diff| 0).
- **The winner depends on the environment.** The same WASM SIMD strategy ranks differently across environments:
  - dot is best on Windows Chrome 152;
  - pairwise is best on M1 Chrome 153 and Firefox 155;
  - on M1 Safari 17.4.1 the winner splits by workload: pairwise wins all four prefill sizes, generic wins decode.
- **Same hardware, different engines.** On the same M1 machine, microkernel D/G is 0.824 (Chrome), 0.868 (Safari) and 1.296 (Firefox). Hardware alone does not explain the effect, which implicates engine instruction selection, lowering or optimization paths.
- **Microkernel → full-inference transfer.** The microkernel D-vs-P ranking holds end-to-end in Windows, M1 Chrome and M1 Firefox. In Safari it holds for prefill and reverses for decode.
- **Measured full-inference speedups over generic:**
  - up to 1.914x on Windows Chrome 152 (dot, p64);
  - up to 1.522x on M1 Firefox 155 (pairwise);
  - up to 1.152x on M1 Chrome 153 (pairwise).
- **Throughput.** Absolute throughput is low for interactive use: best decode 1.67 / 3.58 / 2.62 / 2.81 tok/s (Windows Chrome / M1 Chrome / M1 Firefox / M1 Safari).
- **The selector is not a reliable universal choice.** It transferred to full inference in 2 of 4 environments and failed in 2. In Phase 7 v2 it beat the best fixed kernel in 5 of 8 sessions and was slower in 2.

## 7. Explicitly unsupported claims (do not make)
- A universal 2x full-inference speedup, or that the selector generally pays off.
- "V8, Safari or SpiderMonkey dot is broken", or that ARM causes the effect.
- Any specific JIT lowering cause, or any cause of the Safari anomalies, without native inspection.
- That the linked pairwise runtime is globally dot-free. Only the target I2_S object replaced its 16 dot instructions.
- CPU-only causality from same-family browsers on different OS/hardware.
- Safari p32 speedups (> 3x). They are artefacts of the session-1 start anomaly.
- Any generalization to unseen devices (Phase 8 not executed).
- Selector microbenchmark timings as canonical inference performance.
- That inference timings include model load. Model load is excluded from all inference timings.

## Generated data tables (from frozen JSON; do not edit by hand)

Sources: `evidence/phase6-adaptive-full-inference/final-v2/PHASE6_SUMMARY.json`, `evidence/phase7-break-even-v2/phase7-break-even.json`.

### Phase 6 canonical static medians (ms; median of 6 retained samples)

**Windows / Chrome 152** — oracle best: p32=dot, p64=dot, p128=dot, p256=dot, decode64=dot

| workload | generic (G) | dot (D) | pairwise (P) | D/G speedup | P/G speedup |
|---|---|---|---|---|---|
| p32 | 12,830.9 | 7,243.2 | 9,814.2 | 1.771x | 1.307x |
| p64 | 29,460.2 | 15,394.2 | 20,693.9 | 1.914x | 1.424x |
| p128 | 59,786.2 | 36,630.6 | 41,443.8 | 1.632x | 1.443x |
| p256 | 117,395.6 | 62,872.9 | 88,173.6 | 1.867x | 1.331x |
| decode64 | 49,277.9 | 38,402.8 | 52,103.4 | 1.283x | 0.946x |

Best decode throughput: 1.67 tok/s (decode64, dot). Best p128 prefill: 3.49 tok/s. Full-inference GM ratios: D/G 1.677, P/G 1.276, P/D 0.761.

**Apple M1 / Chrome 153** — oracle best: p32=pairwise, p64=pairwise, p128=pairwise, p256=pairwise, decode64=pairwise

| workload | generic (G) | dot (D) | pairwise (P) | D/G speedup | P/G speedup |
|---|---|---|---|---|---|
| p32 | 4,477.0 | 5,189.2 | 3,913.9 | 0.863x | 1.144x |
| p64 | 8,968.5 | 10,330.6 | 7,784.9 | 0.868x | 1.152x |
| p128 | 18,338.4 | 21,199.8 | 16,165.5 | 0.865x | 1.134x |
| p256 | 38,700.4 | 44,674.8 | 34,624.1 | 0.866x | 1.118x |
| decode64 | 18,861.5 | 20,464.7 | 17,863.4 | 0.922x | 1.056x |

Best decode throughput: 3.58 tok/s (decode64, pairwise). Best p128 prefill: 7.92 tok/s. Full-inference GM ratios: D/G 0.876, P/G 1.120, P/D 1.278.

**Apple M1 / Firefox 155** — oracle best: p32=pairwise, p64=pairwise, p128=pairwise, p256=pairwise, decode64=pairwise

| workload | generic (G) | dot (D) | pairwise (P) | D/G speedup | P/G speedup |
|---|---|---|---|---|---|
| p32 | 6,805.0 | 5,353.5 | 4,470.0 | 1.271x | 1.522x |
| p64 | 13,630.5 | 10,425.0 | 8,954.5 | 1.307x | 1.522x |
| p128 | 27,138.0 | 21,378.5 | 18,637.5 | 1.269x | 1.456x |
| p256 | 57,157.0 | 46,832.0 | 41,022.5 | 1.220x | 1.393x |
| decode64 | 27,478.0 | 25,487.5 | 24,402.5 | 1.078x | 1.126x |

Best decode throughput: 2.62 tok/s (decode64, pairwise). Best p128 prefill: 6.87 tok/s. Full-inference GM ratios: D/G 1.227, P/G 1.396, P/D 1.138.

**Apple M1 / Safari 17.4.1** — oracle best: p32=pairwise, p64=pairwise, p128=pairwise, p256=pairwise, decode64=generic

| workload | generic (G) | dot (D) | pairwise (P) | D/G speedup | P/G speedup |
|---|---|---|---|---|---|
| p32 | 16,267.0 | 5,036.0 | 4,374.0 | 3.230x | 3.719x |
| p64 | 9,280.0 | 10,076.0 | 8,767.5 | 0.921x | 1.058x |
| p128 | 18,979.0 | 21,033.5 | 18,147.0 | 0.902x | 1.046x |
| p256 | 43,572.5 | 45,769.5 | 39,553.0 | 0.952x | 1.102x |
| decode64 | 22,811.0 | 23,844.5 | 44,003.0 | 0.957x | 0.518x |

Best decode throughput: 2.81 tok/s (decode64, generic). Best p128 prefill: 7.05 tok/s. Full-inference GM ratios: D/G 1.196, P/G 1.186, P/D 0.992.

### Phase 6 adaptive sessions

| environment | session | selected | selector wall (ms) | GM regret | pass |
|---|---|---|---|---|---|
| windows-chrome152 | 1 | pairwise | 152.8 | 1.3143 | False |
| windows-chrome152 | 2 | dot | 157.3 | 1.0000 | True |
| m1-chrome153 | 1 | pairwise | 161.1 | 1.0000 | True |
| m1-chrome153 | 2 | pairwise | 151.2 | 1.0000 | True |
| m1-firefox155 | 1 | pairwise | 188.0 | 1.0000 | True |
| m1-firefox155 | 2 | pairwise | 161.0 | 1.0000 | True |
| m1-safari17-4-1 | 1 | generic | 141.0 | 1.3531 | False |
| m1-safari17-4-1 | 2 | pairwise | 163.0 | 1.1404 | False |

### Correctness-v2

| environment | pass | ordering | top1 ids G/D/P | result SHA256 |
|---|---|---|---|---|
| windows-chrome152 | True | before canonical performance (frozen reference result) | 12366/12366/12366 | `1f52d7ba0df6c4c6…` |
| m1-chrome153 | True | POST-HOC: run after canonical performance (protocol-ordering deviation, disclosed; performance not rerun) | 12366/12366/12366 | `8835997a8413893c…` |
| m1-firefox155 | True | before canonical performance | 12366/12366/12366 | `7db35b3bebac31f1…` |
| m1-safari17-4-1 | True | before canonical performance (performance resumed after an owner-authorized INCOMPLETE closure; disclosed) | 12366/12366/12366 | `ee6cb066a15d8301…` |

### Phase 7 break-even (universal static = dot; generic GM turn 55.2 s, dot GM turn 50.6 s, pairwise GM turn 54.0 s)

| environment | session | selected | saving/turn (ms) | selector wall used (ms) | break-even |
|---|---|---|---|---|---|
| windows-chrome152 | 1 | pairwise | -18,513.9 | unavailable | no finite break-even |
| windows-chrome152 | 2 | dot | 0.0 | unavailable | no finite break-even |
| m1-chrome153 | 1 | pairwise | 7,635.7 | 172.4 | 1 |
| m1-chrome153 | 2 | pairwise | 7,635.7 | 172.4 | 1 |
| m1-firefox155 | 1 | pairwise | 3,826.0 | 173.0 | 1 |
| m1-firefox155 | 2 | pairwise | 3,826.0 | 173.0 | 1 |
| m1-safari17-4-1 | 1 | generic | 3,088.0 | 182.0 | 1 |
| m1-safari17-4-1 | 2 | pairwise | -17,272.0 | 182.0 | no finite break-even |
