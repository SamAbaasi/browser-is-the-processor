# Engine reproduction: `i32x4.dot_i16x8_s` vs `i16x8.mul + i32x4.extadd_pairwise_i16x8_s`

This is a minimal, self-contained reproduction of the cross-engine WebAssembly
SIMD performance difference reported in this repository. It runs the exact
frozen microkernel module `p1-triple-v6.wasm` (SHA-256
`944fc9f7818d34383a012328525243b069bf77fd147aa4ce22a08f657b720561`), which
contains three implementations of the same ternary (BitNet I2_S) dot-product
kernel:

| Kernel | Implementation |
|---|---|
| G | portable C++ compiled with Emscripten `-O3 -msimd128` (compiler-autovectorized SIMD128) |
| D | handwritten SIMD128 using `i32x4.dot_i16x8_s` (16 instances in the kernel) |
| P | identical to D, except that each `i32x4.dot_i16x8_s` is replaced by `i16x8.mul` + `i32x4.extadd_pairwise_i16x8_s` (0 dot, 16 mul) |

`p1_verify(n)` returns a bitmask. 7 means all three kernels match the scalar
reference for that `n`. No model download is needed.

## Run
```sh
cd engine-repro
python3 -m http.server 8000
# open http://localhost:8000 in the browser under test, click "Run", keep the tab in front (~90 s)
```
The page prints per-size medians and geometric-mean speedup ratios. The full
result object is also available as `window.reproResult`.

## Reference results (frozen microkernel protocol v6.2; ratio > 1 = first kernel faster)
| Environment | D/G | P/G | P/D |
|---|---|---|---|
| Windows, Chrome 152 (x86-64) | 1.933 | 1.632 | 0.844 |
| Apple M1, Chrome 153 | 0.824 | 1.125 | 1.366 |
| Apple M1, Firefox 155 | 1.296 | 1.513 | 1.167 |
| Apple M1, Safari 17.4.1 | 0.868 | 1.013 | 1.166 |

A check run of this page on 2026-10-05, in an embedded Chromium 152.0.7977.130
on the same M1, gave D/G 0.820, P/G 1.118, P/D 1.364 and verify = 7 for every
`n`, which matches the frozen M1 Chrome result. That run was a functional check,
not a canonical measurement.

No cause is claimed. The data show that the same instruction sequence ranks
differently across engines on identical hardware. Explaining why requires native
code inspection by people who know each engine.
