# What is intentionally not included

- The 1.844 GB historical GGUF model is not included. Keep it locally on the Mac and verify SHA256 externally.
- The complete Windows/WSL source repository is not included. The user already has it at `~/p1-ternary-kernel-phase0` in WSL.
- The exact frozen correctness-v2 harness/source is not available in the current chat files. Claude Code must locate/copy the original from the user's Windows/WSL repo; it must not recreate a supposedly frozen file from this summary.
- M1 Chrome freeze archive created locally by the user is not included here because it is not mounted in this chat. The raw four canonical JSONs and exact evaluator output are included.
