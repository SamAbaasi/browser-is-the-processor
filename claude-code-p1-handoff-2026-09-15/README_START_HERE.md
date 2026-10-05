# P1 Ternary WASM Kernel — Claude Code handoff

Date: 2026-09-15

This bundle is NOT a replacement for the project repository and does NOT contain the 1.844 GB GGUF model.

Use it alongside the project folder:

- Windows/WSL source repo: `~/p1-ternary-kernel-phase0`
- Mac continuation folder used for Phase 6: `~/p1-ternary-kernel-phase0`

For the remaining Phase 6 browser matrix, run Claude Code on the **Mac**, inside the project folder, because Firefox 155 and Safari 17.4.1 measurements must run on the M1 Mac. Do not open Claude Code at `/`, the Ubuntu root, or the home directory. Open the actual project folder.

Read in order:

1. `MASTER_PROMPT_FOR_CLAUDE_CODE.md`
2. `CURRENT_RESEARCH_STATE.md`
3. `FROZEN_RULES_AND_GUARDRAILS.md`
4. `phase6-run-kit/experiments/phase6-adaptive-full-inference/PHASE6_PROTOCOL.md`
5. `phase6-run-kit/experiments/phase6-adaptive-full-inference/EVALUATION_IMPLEMENTATION.md`

The four raw Phase 6 JSONs for Windows Chrome 152 and M1 Chrome 153 are included under `current-results/` with exact evaluator outputs.
