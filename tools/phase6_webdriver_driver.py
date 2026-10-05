#!/usr/bin/env python3
"""
Phase 6 browser driver (W3C WebDriver, stdlib only).

Operates the FROZEN, byte-identical harness pages exactly as a person
would: select the historical GGUF in the page's own <input type=file>,
press the page's own run button, wait, and capture the page's own
`finalResult` serialized exactly as the page's "Copy JSON" button does:
JSON.stringify(finalResult, null, 2).

It does not modify, inject into, or re-implement any harness logic.
Every session uses a FRESH browser process with a clean temporary
profile (independent sessions).

Sequence (frozen Phase 6 order; correctness gates performance):
  correctness-v2 -> static1 -> static2 -> adaptive1 -> adaptive2

Driver metadata is written to DRIVER_LOG.jsonl next to the results,
never into the harness result JSON.
"""

import argparse
import json
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = "http://127.0.0.1:8123"
POLL_S = 15
MAX_RUN_S = 4 * 3600

# Capture = the exact JSON text the harness itself printed into #output
# via log(JSON.stringify(finalResult, null, 2)) -- identical to the page's
# "Copy JSON" string. (Firefox WebDriver scripts run in a sandbox that
# cannot see the page's top-level `let finalResult`, so we read the DOM.)
# A round-trip check proves the extracted text is exactly that string.
SERIALIZE = r"""
const t = document.querySelector('#output').textContent;
let s = null;
let i = t.lastIndexOf('\n\nCORRECTNESS ');
if (i >= 0) {
  const st = t.lastIndexOf('\n\n{\n', i);
  if (st >= 0) s = t.slice(st + 2, i);
} else {
  for (const m of ['=== STATIC SESSION COMPLETE ===\n', '=== ADAPTIVE SESSION COMPLETE ===\n']) {
    const k = t.lastIndexOf(m);
    if (k >= 0) { s = t.slice(k + m.length).replace(/\n$/, ''); break; }
  }
}
if (s === null) return null;
const exact = JSON.stringify(JSON.parse(s), null, 2) === s;
return exact ? s : 'ROUNDTRIP_MISMATCH';
"""


def now():
    return datetime.now(timezone.utc).isoformat()


class WD:
    def __init__(self, url):
        self.url = url.rstrip("/")
        self.sid = None

    def _req(self, method, path, body=None, timeout=120):
        data = None if body is None else json.dumps(body).encode()
        r = urllib.request.Request(self.url + path, data=data, method=method,
                                   headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            out = json.loads(resp.read() or b"{}")
        v = out.get("value")
        if isinstance(v, dict) and v.get("error"):
            raise RuntimeError(f"{v['error']}: {v.get('message')}")
        return v

    def new_session(self, caps):
        v = self._req("POST", "/session", {"capabilities": {"alwaysMatch": caps}}, timeout=180)
        self.sid = v["sessionId"]
        return v["capabilities"]

    def s(self, method, path, body=None, timeout=120):
        return self._req(method, f"/session/{self.sid}{path}", body, timeout)

    def get(self, url):
        self.s("POST", "/url", {"url": url}, timeout=180)

    def find(self, css):
        v = self.s("POST", "/element", {"using": "css selector", "value": css})
        return next(iter(v.values()))

    def send_keys(self, el, text):
        self.s("POST", f"/element/{el}/value", {"text": text})

    def click(self, el):
        self.s("POST", f"/element/{el}/click", {})

    def js(self, script):
        return self.s("POST", "/execute/sync", {"script": script, "args": []}, timeout=120)

    def quit(self):
        if self.sid:
            try:
                self._req("DELETE", f"/session/{self.sid}", timeout=60)
            finally:
                self.sid = None


def log_event(logf, **kw):
    kw["t"] = now()
    with open(logf, "a") as f:
        f.write(json.dumps(kw) + "\n")
    print(json.dumps(kw), flush=True)


def power_state():
    out = subprocess.run(["pmset", "-g", "batt"], capture_output=True, text=True).stdout
    return " | ".join(l.strip() for l in out.strip().splitlines())


def wait_for_ac(logf, label):
    """Measurements only on AC power: battery exhaustion forces sleep mid-session."""
    warned = False
    while "AC Power" not in power_state():
        if not warned:
            log_event(logf, event="waiting_for_ac_power", run=label, power=power_state())
            warned = True
        time.sleep(60)


def run_page(wd, caps, page, button, model, done_js, logf, label):
    wait_for_ac(logf, label)
    got_caps = wd.new_session(caps)
    log_event(logf, event="session_start", run=label, session_id=wd.sid,
              power=power_state(),
              browserName=got_caps.get("browserName"),
              browserVersion=got_caps.get("browserVersion"),
              platformName=got_caps.get("platformName"))
    try:
        wd.get(f"{BASE}/{page}")
        wd.send_keys(wd.find("#model"), model)
        wd.click(wd.find(button))
        log_event(logf, event="run_clicked", run=label, button=button)
        # Verify the page's handler actually started the run (the clicked button
        # is disabled while running). Under safaridriver a native WebDriver click
        # can fail to reach the onclick handler; fall back to the page's own
        # element.click() (same handler, no harness change) and log it.
        time.sleep(3)
        started_js = f"return document.querySelector('{button}').disabled;"
        if not wd.js(started_js):
            wd.js(f"document.querySelector('{button}').click();")
            time.sleep(3)
            log_event(logf, event="click_fallback_element_click", run=label,
                      button=button, started=wd.js(started_js))
        t0 = time.time()
        while True:
            time.sleep(POLL_S)
            state = wd.js(done_js)
            if state.get("done"):
                break
            if time.time() - t0 > MAX_RUN_S:
                raise TimeoutError(f"{label} exceeded {MAX_RUN_S}s")
        text = wd.js(SERIALIZE)
        log_event(logf, event="run_finished", run=label,
                  status=state.get("status"), elapsed_s=round(time.time() - t0, 1),
                  captured=text is not None)
        return text, state
    finally:
        wd.quit()
        log_event(logf, event="session_end", run=label)


CORRECTNESS_DONE = """
const o = document.querySelector('#output').textContent;
const done = o.includes('CORRECTNESS PASS') || o.includes('CORRECTNESS FAIL') || o.includes('ERROR:');
return {done, status: done ? o.slice(-300) : null};
"""

CANONICAL_DONE = """
const s = document.querySelector('#status').textContent;
const done = /complete$/i.test(s.trim()) || s.trim() === 'FAILED';
return {done, status: s};
"""


def validate_correctness(d):
    ok = (d["schema"] == "p1-phase6-correctness-v2"
          and d["canonical_input"] == [128000, 791, 6864, 315, 9822, 374]
          and d["same_vocab"] is True and d["finite_pass"] is True
          and all(d["variants"][v]["n_vocab"] == 128256 for v in ("generic", "dot", "pairwise"))
          and all(c["cosine"] >= 0.99 and c["relative_l2"] <= 0.05 for c in d["comparisons"].values())
          and d["overall_pass"] is True)
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--env", required=True, help="environment label, e.g. m1-firefox155")
    ap.add_argument("--webdriver", required=True, help="e.g. http://127.0.0.1:4445")
    ap.add_argument("--caps", required=True, help="JSON capabilities (alwaysMatch)")
    ap.add_argument("--model", required=True)
    ap.add_argument("--repo", default=".")
    ap.add_argument("--only", default="correctness,static1,static2,adaptive1,adaptive2")
    args = ap.parse_args()

    repo = Path(args.repo)
    caps = json.loads(args.caps)
    res_dir = repo / "evidence/phase6-adaptive-full-inference/results" / args.env
    cor_dir = repo / "evidence/phase6-adaptive-full-inference/correctness/v2"
    res_dir.mkdir(parents=True, exist_ok=True)
    logf = res_dir / "DRIVER_LOG.jsonl"
    wd = WD(args.webdriver)
    steps = args.only.split(",")

    if "correctness" in steps:
        out = cor_dir / f"{args.env}-correctness-v2.json"
        if out.exists():
            sys.exit(f"refusing to overwrite existing {out}")
        text, _ = run_page(wd, caps, "phase6-correctness-v2.html", "#run",
                           args.model, CORRECTNESS_DONE, logf, "correctness-v2")
        if text is None or text == "ROUNDTRIP_MISMATCH":
            log_event(logf, event="STOP", reason=f"correctness capture failed: {text}")
            sys.exit(2)
        out.write_text(text)
        passed = validate_correctness(json.loads(text))
        log_event(logf, event="correctness_validated", file=str(out), pass_=passed)
        if not passed:
            log_event(logf, event="STOP", reason="correctness FAIL gates Phase 6 performance")
            sys.exit(3)

    runs = [("static1", "#static1", "static-session1.json"),
            ("static2", "#static2", "static-session2.json"),
            ("adaptive1", "#adaptive1", "adaptive-session1.json"),
            ("adaptive2", "#adaptive2", "adaptive-session2.json")]
    for key, button, fname in runs:
        if key not in steps:
            continue
        out = res_dir / fname
        if out.exists():
            sys.exit(f"refusing to overwrite existing {out}")
        text, state = run_page(wd, caps, "phase6-canonical.html", button,
                               args.model, CANONICAL_DONE, logf, key)
        if text is None or text == "ROUNDTRIP_MISMATCH" or state.get("status", "").strip() == "FAILED":
            log_event(logf, event="STOP", reason=f"{key} failed", status=state.get("status"))
            sys.exit(4)
        out.write_text(text)
        log_event(logf, event="saved", file=str(out))

    log_event(logf, event="ALL_DONE", env=args.env)


if __name__ == "__main__":
    main()
