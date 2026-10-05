# Phase 7 v2: break-even analysis on the complete 4-environment matrix

Date: 2026-10-05. Analysis only, no new benchmark. The definition is unchanged
from the frozen Phase 7 section of PHASE6_PROTOCOL.md (SHA256 5431b9c7…):
- representative turn = prefill128 + decode64, canonical static medians;
- selector cost = MAX canonical Phase 5D selector wall per environment;
- each adaptive session is evaluated independently.

**Status.** v2 is the protocol-conformant Phase 7 result. It uses all four
Phase 6 environments now that M1 Safari 17.4.1 is complete. Phase 7 v1
(`evidence/phase7-break-even/`, 3 environments, computed while Safari was
INCOMPLETE) is retained unchanged as superseded history.

## Universal static kernel (lowest cross-environment GM turn, 4 environments)
| Kernel | GM turn (ms) |
|---|---|
| **dot** | **50,638.2** |
| pairwise | 54,019.2 |
| generic | 55,163.8 |

In v1 (3 environments) the universal kernel was pairwise (51,552.6 ms). Adding
Safari, where pairwise decode is about 1.9× slower than generic, changes the
universal choice to dot. **The "best fixed kernel" is itself sensitive to which
environments are included.**

## Per environment and adaptive session (baseline: universal = dot)
| Environment | Session | Selected | Turn selected (ms) | Turn universal (ms) | Saving/turn (ms) | Selector wall (ms) | Break-even |
|---|---|---|---|---|---|---|---|
| Windows Chrome 152 | A1 | pairwise | 93,547.2 | 75,033.4 | −18,513.9 | unavailable | **no finite break-even** (selection is slower) |
| Windows Chrome 152 | A2 | dot | 75,033.4 | 75,033.4 | 0.0 | unavailable | **no finite break-even** |
| M1 Chrome 153 | A1 | pairwise | 34,028.9 | 41,664.6 | 7,635.7 (18.3%) | 172.4 | **1 turn** |
| M1 Chrome 153 | A2 | pairwise | 34,028.9 | 41,664.6 | 7,635.7 (18.3%) | 172.4 | **1 turn** |
| M1 Firefox 155 | A1 | pairwise | 43,040.0 | 46,866.0 | 3,826.0 (8.2%) | 173.0 | **1 turn** |
| M1 Firefox 155 | A2 | pairwise | 43,040.0 | 46,866.0 | 3,826.0 (8.2%) | 173.0 | **1 turn** |
| M1 Safari 17.4.1 | A1 | generic | 41,790.0 | 44,878.0 | 3,088.0 (6.9%) | 182.0 | **1 turn** |
| M1 Safari 17.4.1 | A2 | pairwise | 62,150.0 | 44,878.0 | −17,272.0 | 182.0 | **no finite break-even** (selection is slower) |

First-use cost = selector wall + canonical steady-state turn (model load and
cold-start JIT excluded):

| Environment | First-use cost (ms) |
|---|---|
| M1 Chrome | 34,201.3 |
| M1 Firefox | 43,213.0 |
| M1 Safari A1 | 41,972.0 |
| M1 Safari A2 | 62,332.0 |

The Safari generic p32 start anomaly (see
`final-v2/SAFARI_SENSITIVITY_NONCANONICAL.md`) does not enter Phase 7, which
uses p128 + decode64 only.

## Findings
1. Against the 4-environment universal kernel (dot), the selector:
   - **paid for itself in 5 of 8 sessions**, within one turn (M1 Chrome ×2,
     M1 Firefox ×2, Safari A1), saving 6.9–18.3% per turn;
   - **tied in 1** (Windows A2);
   - **was slower in 2** (Windows A1, −18.5 s/turn; Safari A2, −17.3 s/turn).
2. Phase 7 v1, with 3 environments and universal = pairwise, found no finite
   break-even in 5 of 6 sessions. **The value attributed to runtime selection
   depends on the environment set that defines the "universal" baseline.**
3. Supported reading: when engines disagree on the best kernel, a measured
   runtime choice can beat any single fixed choice. But in this matrix it
   picked a slower kernel in 2 of 8 sessions, so it is not reliable insurance.

## Not supported
- A general claim that adaptive selection pays off.
- A Windows break-even value. The raw Windows Phase 5D walls are unavailable;
  no substitute was used.
