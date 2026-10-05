# Public source / provenance index

These are the public technical sources that anchor the P1 Ternary WASM Kernel research. Claude should use them for provenance, related work, citations, semantics, and implementation context — not to change frozen experimental results.

## Papers

1. **The Era of 1-bit LLMs: All Large Language Models are in 1.58 Bits**
   - Microsoft Research / arXiv 2402.17764
   - https://arxiv.org/abs/2402.17764
   - https://www.microsoft.com/en-us/research/publication/the-era-of-1-bit-llms-all-large-language-models-are-in-1-58-bits/

2. **Bitnet.cpp: Efficient Edge Inference for Ternary LLMs**
   - arXiv 2502.11880
   - https://arxiv.org/abs/2502.11880
   - Project source: https://github.com/microsoft/BitNet

3. **BitNet b1.58 2B4T Technical Report**
   - arXiv 2504.12285
   - https://arxiv.org/abs/2504.12285

## Model / checkpoint provenance

4. **Historical GGUF revision used by the canonical project**
   - Repository: microsoft/bitnet-b1.58-2B-4T-gguf
   - Revision: `6e8c386a5609ebd6ef546dc3cb89d684be5c08d4`
   - https://huggingface.co/microsoft/bitnet-b1.58-2B-4T-gguf/tree/6e8c386a5609ebd6ef546dc3cb89d684be5c08d4
   - GGUF bytes: `1844472032`
   - GGUF SHA256: `13939ce5030319a35db346e5dba7a3a3bd599dfc18b113a2a97446ff964714c5`

5. **Checkpoint-integrity issue documenting later broken model uploads**
   - microsoft/BitNet issue #608
   - https://github.com/microsoft/BitNet/issues/608
   - Use only as provenance for why the project pins a historical known-good GGUF; do not substitute issue claims for the project's own hashes/correctness evidence.

## Runtime / source provenance

6. **Microsoft BitNet source**
   - https://github.com/microsoft/BitNet
   - Historical project commit: `c17d1c5d77c48af7d6fb29c9f28a3da0277fc394`
   - Local historical source in the research repo should be treated as authoritative for the experiment, including `runtimes/bitnet-2025-04-23/src/ggml-bitnet-mad.cpp`.

7. **llama.cpp submodule/source**
   - https://github.com/ggml-org/llama.cpp
   - Use the exact submodule commit recorded by the frozen repo/manifest rather than current main.
   - Relevant I2_S implementation/source files in the local project include the historical `ggml-cpu-i2s.c` / related ggml paths.

## WebAssembly SIMD semantics

8. **WebAssembly SIMD proposal/spec**
   - https://github.com/WebAssembly/spec/blob/main/proposals/simd/SIMD.md
   - Relevant operations:
     - `i32x4.dot_i16x8_s`
     - `i16x8.mul`
     - `i32x4.extadd_pairwise_i16x8_s`

9. **MDN — WebAssembly SIMD-specific arithmetic instructions**
   - https://developer.mozilla.org/en-US/docs/WebAssembly/Reference/SIMD/arithmetic

## Provenance rule for Claude

Do not infer that a source proves the project's measured performance result. Papers/specs establish background or operation semantics. Performance claims must come from frozen project evidence.
