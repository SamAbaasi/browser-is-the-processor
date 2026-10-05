# Phase 7 — break-even analysis (analysis only, no new benchmark)

Date: 2026-10-05
Definition: frozen Phase 7 section of PHASE6_PROTOCOL.md (SHA256 5431b9c7…).
Representative turn = prefill128 + decode64, canonical static medians.
Selector cost = MAX canonical Phase 5D selector wall for that environment.
Selection rule: each Phase 6 adaptive session is evaluated independently
(frozen rule 16).

## Scope
- Computed on the 3 environments that COMPLETED Phase 6: Windows Chrome 152,
  M1 Chrome 153, M1 Firefox 155.
- M1 Safari 17.4.1 is EXCLUDED: Phase 6 performance is INCOMPLETE there
  (correctness-v2 only).
- The Windows Chrome 152 Phase 5D selector walls (raw JSON) are not available
  on this machine. Windows rows that need the wall are marked pending. No
  substitute wall was used.

## Universal static kernel (lowest cross-environment geometric-mean turn)
| Kernel | GM turn latency (ms) |
|---|---|
| **pairwise** | **51,552.6** |
| dot | 52,718.1 |
| generic | 60,512.9 |

pairwise and dot are within 2.3%. This choice uses 3 environments. Adding
Safari could change it. That is an open question, because Phase 5D picked
generic in Safari.

## Per environment and adaptive session
| Environment | Session | Selected | Turn selected (ms) | Turn universal (ms) | Saving/turn (ms) | Selector wall (ms) | Break-even |
|---|---|---|---|---|---|---|---|
| Windows Chrome 152 | A1 | pairwise | 93,547.2 | 93,547.2 | 0.0 | unavailable | **no finite break-even** |
| Windows Chrome 152 | A2 | dot | 75,033.4 | 93,547.2 | 18,513.9 (19.8%) | unavailable | pending (= 1 turn for any wall ≤ 18,513.9 ms) |
| M1 Chrome 153 | A1 | pairwise | 34,028.9 | 34,028.9 | 0.0 | 172.4 | **no finite break-even** |
| M1 Chrome 153 | A2 | pairwise | 34,028.9 | 34,028.9 | 0.0 | 172.4 | **no finite break-even** |
| M1 Firefox 155 | A1 | pairwise | 43,040.0 | 43,040.0 | 0.0 | 173.0 | **no finite break-even** |
| M1 Firefox 155 | A2 | pairwise | 43,040.0 | 43,040.0 | 0.0 | 173.0 | **no finite break-even** |

First-use cost (selector wall + canonical steady-state turn; model load and
cold-start JIT excluded because they are not canonically measured):
- M1 Chrome 153: 34,201.3 ms
- M1 Firefox 155: 43,213.0 ms
- Windows: pending

## Findings
1. In 5 of 6 adaptive sessions, the frozen selector picked the same kernel as
   the universal static baseline (pairwise). Its selector cost therefore buys
   no steady-state benefit, and there is no finite break-even.
2. Only Windows Chrome 152 session A2 (selected dot) beat the universal
   baseline: 18,513.9 ms saved per turn (19.8%). On Windows the universal
   kernel is 1.247x slower than the best static kernel (dot).
3. Supported interpretation: across the measured matrix, one fixed kernel
   matched the adaptive selector's steady-state turn latency everywhere except
   one Windows session. In this matrix, the selector's value depends on the
   environment and acts as insurance for environments like Windows. It is not
   a general speedup.

## Not supported
- Any general claim that adaptive kernel selection pays off.
- Any Safari conclusion.
- A Windows break-even number. The handoff summary states all original Phase 5D
  walls were < 200 ms, but the raw Windows Phase 5D files were not available
  here, so the row stays pending.

## Disclosures
Before this freeze, the calculator had a logic error. It marked a zero-saving
row "pending" when the wall was missing. Zero saving means no finite
break-even regardless of the wall, so this was fixed. The fix was made before
any number was frozen.
