# P1 — The Browser Is the Processor

A ternary (BitNet b1.58 / I2_S) matrix kernel designed around WebAssembly
SIMD128, measured end-to-end inside real desktop browsers: CPU-only,
single-threaded, no WebGPU.

**Start here: [EVIDENCE_INDEX.md](EVIDENCE_INDEX.md).** It lists every
frozen artifact, phase gate, negative result, protocol deviation, supported
claim and explicitly unsupported claim, with data tables generated from the
frozen JSON.

## Headline results (see the index for every caveat)
- BitNet b1.58 2B4T runs fully in-browser on Windows Chrome 152 and Apple M1
  Chrome 153 / Firefox 155 / Safari 17.4.1. The three kernel variants produce
  **bit-identical logits** in all four environments.
- **The same WASM SIMD instruction strategy wins in one engine and loses in
  another.**
  - The handwritten `i32x4.dot_i16x8_s` kernel is best on Windows Chrome 152.
  - The `i16x8.mul + i32x4.extadd_pairwise_i16x8_s` substitution is best on M1
    Chrome 153 and Firefox 155.
  - On M1 Safari 17.4.1 the winner splits by workload: pairwise for prefill,
    the compiler-autovectorized kernel for decode.
- Full-inference speedups over the compiler-autovectorized SIMD baseline reach
  1.91x. The original ≥2x gate was **not** passed.
- Absolute throughput is low: about 1.7–3.6 decode tok/s.
- The frozen adaptive kernel selector **failed** its gate on Windows Chrome 152
  and on M1 Safari 17.4.1. Against the best fixed kernel it paid off in 5 of 8
  sessions and was slower in 2.

## Method
- Protocols, thresholds and evaluators were frozen and hashed **before**
  measurement.
- Every retained sample is kept, with no outlier removal and no reruns to
  improve results.
- Failures and aborted attempts are disclosed in each freeze's
  METHODOLOGY_NOTES.md and DRIVER_LOG.jsonl.

## Layout
| Path | Contents |
|---|---|
| `browser/` | frozen harness pages and WASM runtimes (G/D/P, selector, correctness-v2) |
| `experiments/` | frozen protocols (Phase 6, correctness-v2, Phase 8) |
| `evidence/` | frozen results, freezes with SHA256SUMS, Phase 6 summary, Phase 7 |
| `tools/` | evaluator, freeze, consolidation, break-even and WebDriver driver |
| `claude-code-p1-handoff-2026-09-15/` | handoff bundle with the Windows Chrome 152 raw results and earlier-phase reference bundles |
| `figures/` | article figures generated from frozen JSON (`python3 tools/make_figures.py`) |
| `docs/PUBLIC_SOURCE_INDEX.md` | public papers, model revision, checkpoint-integrity and WASM SIMD spec references (provenance) |
| `PACKAGE_SHA256SUMS`, `README_RECOVERY.md` | manifest of the verbatim correctness-v2 recovery package |

## Model
The GGUF is not redistributed here. Use microsoft/bitnet-b1.58-2B-4T-gguf at
revision `6e8c386a5609ebd6ef546dc3cb89d684be5c08d4` (1,844,472,032 bytes,
SHA256 `13939ce5…714c5`).

## AI assistance
Parts of the tooling, automation and documentation were produced with AI
assistance (Claude Code) and reviewed by the author. Research design,
decisions and accountability rest with the author.
