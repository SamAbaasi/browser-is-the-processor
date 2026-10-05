# M1 Firefox 155 — methodology notes and disclosures

## Environment
- Apple M1 MacBook Pro, macOS 14.4.1 (23E224)
- Mozilla Firefox **155.0** exact: official Mozilla build from
  `archive.mozilla.org/pub/firefox/releases/155.0/mac/en-US/Firefox 155.0.dmg`
  (dmg SHA256 `3ae135f2023cf0c6cbce3bb757e06564ff8148b1266f682b8eccff0993a1a9f5`),
  installed unmodified (Apple `codesign --verify --deep --strict` valid) at
  `_tools/firefox155/Firefox.app`. The system-installed Firefox 156.0 was NOT
  used, because the frozen protocol names Firefox 155.
- UA observed in correctness-v2: `Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15;
  rv:155.0) Gecko/20100101 Firefox/155.0`

## How the browser was operated
- W3C WebDriver via geckodriver 0.37.1 (SHA256
  `5d82307edc8549124bd4e7b6f275e1228e0a530e5abbfb294be3f310486561a4`), driven by
  `phase6_webdriver_driver.py` (copied into this freeze with its hash).
- The frozen harness pages were used byte-identical. The driver puts the
  GGUF into the page's own `<input type=file>`, clicks the page's own
  button, waits, and captures the JSON the page printed into `#output` via
  `log(JSON.stringify(finalResult, null, 2))`, with an exact round-trip
  check. That is the same string the page's "Copy JSON" button produces.
- Each session (correctness, each static session, each adaptive session)
  ran in a fresh Firefox process with a fresh temporary profile created by
  geckodriver.
- geckodriver and Firefox were launched from the agent's command shell,
  which runs under a macOS sandbox profile. Firefox therefore ran as a child
  of that sandboxed process. Kernel computation runs in Web Workers and is
  not expected to be affected, but this is a difference from the M1 Chrome
  runs, which a person launched from the Dock.
- WebDriver-controlled Firefox applies geckodriver's standard automation
  preferences (updates, telemetry and similar disabled). JIT preferences
  were not changed.

## Ordering
correctness-v2 PASS (2026-10-04 18:30:42Z) was recorded BEFORE the first
canonical performance session (static1, 18:30:45Z), as the protocol
requires.

## Correctness capture
`correctness_result_sha256` inside the static/adaptive JSONs is the
harness's frozen constant (`1f52d7ba…`, the Windows Chrome 152 reference
result). This environment's own correctness-v2 result is
`m1-firefox155-correctness-v2.json` (SHA256 `7db35b3b…`).

## Disclosed attempts that produced no evidence
1. correctness-v2 attempt 1 (18:28:51Z): the page reported CORRECTNESS PASS,
   but the driver read `null` because Firefox WebDriver scripts cannot see
   the page's top-level `let finalResult`. Driver capture was fixed to read
   the page output. Correctness re-run (attempt 2 is the recorded result).
2. static2 attempt 1 (18:55:21Z): ABORTED. The driver process was killed by
   the agent tool's background time limit and the WebDriver session could
   not be reattached. The result was never observed.
3. static2 attempt 2 (19:01:36Z): ABORTED. The Mac was on battery; macOS
   forced "Low Power Sleep" at 1% charge (19:07:20Z), about 6 minutes in,
   and hibernated until AC attach. The result was never observed.
The recorded static2 is attempt 3, which started on AC power.

## Power conditions
- static1 (18:30–18:55Z, 2026-10-04): on BATTERY, charge falling. macOS
  battery warning level 2 (10% capacity) at 18:52Z. Low Power Mode was
  OFF (`pmset lowpowermode 0` for both battery and AC; no transitions
  logged). Retained unchanged per frozen rule 2 (no reruns to improve
  results).
- static2 attempt 3, adaptive1, adaptive2: driver required AC power before
  each session. The power state is logged in each `session_start` event.
- The M1 Chrome 153 canonical runs (2026-09-15): power source not
  recorded; the macOS power log no longer covers that date.

## Unchanged
No retained sample removed. No threshold, workload, ordering, aggregation,
kernel mapping, or selector parameter changed.
