# M1 Safari 17.4.1 — methodology notes and disclosures

## Environment
- Apple M1 MacBook Pro, macOS 14.4.1 (23E224)
- Safari **17.4.1** (19618.1.15.11.14), the system-installed Safari. This
  matches the version named in the frozen protocol.
- UA observed in correctness-v2: `Mozilla/5.0 (Macintosh; Intel Mac OS X
  10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1
  Safari/605.1.15`

## How the browser was operated
- W3C WebDriver via the system `safaridriver` (shipped with Safari 17.4.1),
  driven by `phase6_webdriver_driver.py` (copied into this freeze with its
  hash). The person who owns the machine enabled Safari "Allow Remote
  Automation" with `safaridriver --enable` and their admin password.
- The frozen harness pages were used byte-identical. The driver puts the
  GGUF into the page's own `<input type=file>`, triggers the page's own
  button, waits, and captures the JSON the page printed into `#output` via
  `log(JSON.stringify(finalResult, null, 2))`, with an exact round-trip
  check.
- Safari was fully quit (AppleScript `quit`) before every session, so each
  session (correctness, each static session, each adaptive session) began
  in a fresh Safari process. WebDriver sessions run in Safari's isolated
  automation window with ephemeral website data.
- Safari runs measured only after the Firefox 155 driver had exited (no
  concurrent browser measurement). Every session start was gated on AC
  power, and the power state is logged in DRIVER_LOG.jsonl.

## Click handling (disclosed)
Under safaridriver, the WebDriver "Element Click" command returned success
but did not reach the page's `onclick` handler: the output stayed empty,
the button never disabled, and WebContent stayed idle.
- correctness-v2: the native click at 04:56:34Z did not start the run. After
  diagnosing it, the page's own button was triggered with `element.click()`
  at ~05:00:55Z (same handler), and the run then executed and passed.
- From static1 onward the driver verifies that the clicked button became
  disabled (the page disables it while running). If it did not, the driver
  calls the page's own `element.click()` on the same button and logs a
  `click_fallback_element_click` event. No harness logic is replaced. The
  few seconds before the fallback precede the run and are not part of any
  measured interval.

## Ordering
correctness-v2 PASS (05:01:49Z) was recorded before the first canonical
performance session (static1, 05:02:02Z).

## Correctness reference inside result JSONs
`correctness_result_sha256` in static/adaptive JSONs is the harness's frozen
constant (`1f52d7ba…`, the Windows Chrome 152 reference result). This
environment's own result is `m1-safari17-4-1-correctness-v2.json` (SHA256
`ee6cb066…`).

## Unchanged
No retained sample removed. No threshold, workload, ordering, aggregation,
kernel mapping, or selector parameter changed.

## Status at closure: INCOMPLETE (2026-10-05)
- static1 attempt 1 started 05:02:02Z (via the logged element.click fallback)
  and was ABORTED at 05:14:37Z at the machine owner's explicit request to stop
  all runs. Its result was never captured or observed.
- The owner then decided to close Phase 6 with Safari recorded as INCOMPLETE
  rather than resume. No Safari canonical performance data exists. No static or
  adaptive Safari JSON was produced.
- Consequence: no Phase 6 performance claim of any kind is made for Safari
  17.4.1. Only correctness-v2 (PASS, run before any performance session) is
  evidence for this environment.
