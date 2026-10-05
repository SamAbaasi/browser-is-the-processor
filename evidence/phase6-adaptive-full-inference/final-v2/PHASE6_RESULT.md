# Phase 6 — final result (4 environments)

Gate (frozen): correctness-v2 PASS and EVERY adaptive session GM regret <= 1.05.

| Environment | Correctness-v2 | Oracle (all workloads) | Adaptive 1 | Adaptive 2 | Phase 6 |
|---|---|---|---|---|---|
| Windows / Chrome 152 | PASS | dot | pairwise, 152.8 ms, GM 1.3143 | dot, 157.3 ms, GM 1.0000 | FAIL |
| Apple M1 / Chrome 153 | PASS (post-hoc) | pairwise | pairwise, 161.1 ms, GM 1.0000 | pairwise, 151.2 ms, GM 1.0000 | PASS |
| Apple M1 / Firefox 155 | PASS | pairwise | pairwise, 188.0 ms, GM 1.0000 | pairwise, 161.0 ms, GM 1.0000 | PASS |
| Apple M1 / Safari 17.4.1 | PASS | generic/pairwise | generic, 141.0 ms, GM 1.3531 | pairwise, 163.0 ms, GM 1.1404 | FAIL |

Phase 6 gate verdict: FAIL: the frozen gate requires every tested environment to pass; windows-chrome152, m1-safari17-4-1 failed
Evaluated: windows-chrome152, m1-chrome153, m1-firefox155, m1-safari17-4-1. Incomplete: none.

Notes:
- Windows Chrome 152 FAIL is preserved: adaptive session 1 selected pairwise (GM regret 1.3143) while the canonical static oracle was dot for every workload. Later passes do not erase it.
- M1 Chrome 153 correctness-v2 was run AFTER its canonical performance data (post-hoc validation). This protocol-ordering deviation is disclosed; performance was not rerun.
- Firefox and Safari were operated by W3C WebDriver on the real installed browsers; see each freeze's METHODOLOGY_NOTES.md.
- Safari 17.4.1 performance was resumed after an owner-authorized INCOMPLETE closure (the INCOMPLETE record is retained as history; static1 attempt 1 was aborted and never observed). Correctness-v2 preceded all performance sessions.
- Phase 5D selector success against its microkernel oracle and Phase 6 full-inference transfer are separate questions.
