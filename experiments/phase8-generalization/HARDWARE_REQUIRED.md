# Phase 8 — hardware/environments required (hardware stop, 2026-10-05)

None of the following was available when P1 closed. Any ONE qualifying
environment allows Phase 8 to run under the frozen PHASE8_PROTOCOL.md.

Known prior environments:
- Windows Chrome 152: x86-64, 8 logical cores, 32 GB. The CPU model was NOT
  recorded (browsers do not expose it). Get it from the original machine
  before claiming an x86 environment is "different".
- Apple M1 (8 GB): Chrome 153, Firefox 155, Safari 17.4.1.

Required candidates, in order of evidential strength:
1. **Windows-on-ARM laptop (Qualcomm Snapdragon X series)**, Edge or Chrome
   stable. Different CPU vendor and microarchitecture from both prior
   machines.
2. **AMD Zen 4/5 x86-64 machine** (Windows or Linux), Chrome and/or Firefox
   stable. Qualifies only if the original Windows machine is shown to be
   non-AMD.
3. **Android phone with ≥ 8 GB RAM** (recent ARM Cortex big.LITTLE SoC),
   Chrome for Android. Different device class and OS. The 1.84 GB model must
   fit within the browser's per-tab memory limits; record failures to load
   as results.
4. **Intel x86-64 machine** (recent Core Ultra or similar). Qualifies only if
   the original Windows machine is shown to be non-Intel or a different
   microarchitecture generation.
5. **Newer Apple Silicon (M3/M4)** with any browser. This is the WEAK form
   (same vendor family) and must be labeled "weak".

Per environment, the operator must provide:
- exclusive use for about 3 hours on AC power
- the exact browser version installed
- the historical GGUF (SHA256 13939ce5…) available locally
- permission to run the frozen harness (manually or via disclosed WebDriver)
