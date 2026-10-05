#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

GEN="$ROOT/runtimes/bitnet-2025-04-23/build-browser-generic"
SIMD="$ROOT/runtimes/bitnet-2025-04-23/build-browser-simd128"

SRC="$ROOT/experiments/phase6-adaptive-full-inference/logit_probe_browser.cpp"

PAIR_ARCHIVE="$ROOT/experiments/phase6-adaptive-full-inference/build-pairwise/libggml.a"

WORK="$ROOT/experiments/phase6-adaptive-full-inference/build-correctness-v2"
OUT="$ROOT/browser/dist/correctness-v2"

EMXX="$HOME/emsdk/upstream/emscripten/em++"

rm -rf "$WORK" "$OUT"

mkdir -p \
  "$WORK" \
  "$OUT/generic" \
  "$OUT/dot" \
  "$OUT/pairwise"

GEN_INCLUDES="$GEN/tools/CMakeFiles/p1-logit-probe.dir/includes_CXX.rsp"
SIMD_INCLUDES="$SIMD/tools/CMakeFiles/p1-logit-probe.dir/includes_CXX.rsp"

echo "=== Compile generic probe object ==="

"$EMXX" \
  -DP1_BROWSER_BENCH=1 \
  "@$GEN_INCLUDES" \
  -O3 \
  -DNDEBUG \
  -std=gnu++11 \
  -msimd128 \
  -c "$SRC" \
  -o "$WORK/probe-generic.o"

echo "=== Compile SIMD probe object ==="

"$EMXX" \
  -DP1_BROWSER_BENCH=1 \
  -DP1_HANDWRITTEN_WASM_SIMD=1 \
  "@$SIMD_INCLUDES" \
  -O3 \
  -DNDEBUG \
  -std=gnu++11 \
  -msimd128 \
  -c "$SRC" \
  -o "$WORK/probe-simd.o"

COMMON_LINK=(
  -O3
  -DNDEBUG
  -sALLOW_MEMORY_GROWTH=1
  -sMAXIMUM_MEMORY=4294967296
  -sENVIRONMENT=worker
  -sFORCE_FILESYSTEM=1
  -sEXPORTED_RUNTIME_METHODS=FS,WORKERFS,callMain
  -lworkerfs.js
)

echo "=== Link G ==="

"$EMXX" \
  -DP1_BROWSER_BENCH=1 \
  "${COMMON_LINK[@]}" \
  "$WORK/probe-generic.o" \
  -o "$OUT/generic/p1-logit-probe.js" \
  "$GEN/3rdparty/llama.cpp/src/libllama.a" \
  "$GEN/3rdparty/llama.cpp/ggml/src/libggml.a"

echo "=== Link D ==="

"$EMXX" \
  -DP1_BROWSER_BENCH=1 \
  -DP1_HANDWRITTEN_WASM_SIMD=1 \
  "${COMMON_LINK[@]}" \
  "$WORK/probe-simd.o" \
  -o "$OUT/dot/p1-logit-probe.js" \
  "$SIMD/3rdparty/llama.cpp/src/libllama.a" \
  "$SIMD/3rdparty/llama.cpp/ggml/src/libggml.a"

echo "=== Link P ==="

"$EMXX" \
  -DP1_BROWSER_BENCH=1 \
  -DP1_HANDWRITTEN_WASM_SIMD=1 \
  "${COMMON_LINK[@]}" \
  "$WORK/probe-simd.o" \
  -o "$OUT/pairwise/p1-logit-probe.js" \
  "$SIMD/3rdparty/llama.cpp/src/libllama.a" \
  "$PAIR_ARCHIVE"

echo
echo "=== Correctness v2 artifacts ==="

sha256sum \
  "$SRC" \
  "$OUT/generic/p1-logit-probe.js" \
  "$OUT/generic/p1-logit-probe.wasm" \
  "$OUT/dot/p1-logit-probe.js" \
  "$OUT/dot/p1-logit-probe.wasm" \
  "$OUT/pairwise/p1-logit-probe.js" \
  "$OUT/pairwise/p1-logit-probe.wasm"
