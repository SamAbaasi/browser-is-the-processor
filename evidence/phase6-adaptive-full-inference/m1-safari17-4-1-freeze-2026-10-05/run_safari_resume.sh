#!/bin/bash
# Resume M1 Safari 17.4.1 Phase 6 performance (correctness already PASS and not rerun).
# Same frozen harness; Safari fully quit between sessions; AC-gated by the driver.
set -u
cd /Users/saman/p1-ternary-kernel-phase0
ENV=m1-safari17-4-1
LOG=evidence/phase6-adaptive-full-inference/results/$ENV/DRIVER_LOG.jsonl
note() { printf '{"event": "NOTE", "t": "%s", "note": "%s"}\n' "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)" "$1" >> "$LOG"; echo "$1"; }
for step in static1 static2 adaptive1 adaptive2; do
  osascript -e 'tell application "Safari" to quit' >/dev/null 2>&1; sleep 5
  note "Safari quit before step $step (fresh Safari process per session)."
  python3 tools/phase6_webdriver_driver.py --env "$ENV" \
    --webdriver http://127.0.0.1:4444 --caps '{"browserName":"safari"}' \
    --model /Users/saman/Downloads/ggml-model-i2_s.gguf --only "$step"
  rc=$?
  if [ $rc -ne 0 ]; then note "STOP: step $step exited $rc; Safari resume halted."; exit $rc; fi
done
osascript -e 'tell application "Safari" to quit' >/dev/null 2>&1
note "Safari resume ALL_DONE."
