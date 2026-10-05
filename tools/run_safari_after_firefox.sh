#!/bin/bash
# Runs the frozen Phase 6 sequence on the real Safari 17.4.1, strictly AFTER
# the Firefox driver has exited (no concurrent measurements). Safari is fully
# quit between sessions so every session starts from a fresh Safari process.
# Correctness-v2 gates performance (driver exits non-zero on correctness FAIL).
set -u
cd /Users/saman/p1-ternary-kernel-phase0
ENV=m1-safari17-4-1
LOG=evidence/phase6-adaptive-full-inference/results/$ENV/DRIVER_LOG.jsonl
mkdir -p "$(dirname "$LOG")"
note() { printf '{"event": "NOTE", "t": "%s", "note": "%s"}\n' "$(date -u +%Y-%m-%dT%H:%M:%S+00:00)" "$1" >> "$LOG"; echo "$1"; }

while pgrep -f "phase6_webdriver_driver.py --env m1-firefox155" >/dev/null; do sleep 60; done
note "Firefox driver exited; starting Safari sequence (no concurrent browser measurement)."

for step in correctness static1 static2 adaptive1 adaptive2; do
  osascript -e 'tell application "Safari" to quit' >/dev/null 2>&1; sleep 5
  note "Safari quit before step $step (fresh Safari process per session)."
  python3 tools/phase6_webdriver_driver.py --env "$ENV" \
    --webdriver http://127.0.0.1:4444 --caps '{"browserName":"safari"}' \
    --model /Users/saman/Downloads/ggml-model-i2_s.gguf --only "$step"
  rc=$?
  if [ $rc -ne 0 ]; then note "STOP: step $step exited $rc; Safari sequence halted."; exit $rc; fi
done
osascript -e 'tell application "Safari" to quit' >/dev/null 2>&1
note "Safari sequence ALL_DONE."
