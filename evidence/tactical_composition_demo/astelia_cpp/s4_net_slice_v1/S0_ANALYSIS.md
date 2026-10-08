# S0 collection-v2 analysis

Read-only: 200 fights; 221.74 s; zero fights executed.
Design commit: `cac370a4ab08af98d59cccd63ecaa7c3f66a81ac`. Inventory SHA256: `d2ef9c466453f348918da8bbea3fb43bc2f602df1d1c86b84434e6c697e6b725`.

| Cell/guns/split | decisions | ready multi % | assigned multi % | reaction correction % |
|---|---:|---:|---:|---:|
| D1-static/10/report | 415 | 18.55 | 1.69 | 0.00 |
| D1-static/10/test | 191 | 19.37 | 2.09 | 0.00 |
| D1-static/10/train | 2464 | 20.90 | 1.01 | 0.00 |
| D1-static/10/validation | 413 | 21.31 | 2.18 | 0.00 |
| D1-static/1/report | 3004 | 0.00 | 0.00 | 0.00 |
| D1-static/1/test | 1080 | 0.00 | 0.00 | 0.00 |
| D1-static/1/train | 15077 | 0.00 | 0.00 | 0.00 |
| D1-static/1/validation | 2162 | 0.00 | 0.00 | 0.00 |
| D1-static/2/report | 1416 | 2.68 | 0.64 | 0.00 |
| D1-static/2/test | 370 | 3.78 | 1.89 | 0.00 |
| D1-static/2/train | 5021 | 4.14 | 1.83 | 0.00 |
| D1-static/2/validation | 669 | 4.19 | 1.20 | 0.00 |
| D2-shellfire/10/report | 260 | 12.31 | 2.69 | 0.27 |
| D2-shellfire/10/test | 240 | 11.25 | 2.50 | 0.08 |
| D2-shellfire/10/train | 2846 | 12.58 | 2.53 | 0.18 |
| D2-shellfire/10/validation | 449 | 12.25 | 3.79 | 0.24 |
| D2-shellfire/1/report | 312 | 0.00 | 0.00 | 0.00 |
| D2-shellfire/1/test | 157 | 0.00 | 0.00 | 0.00 |
| D2-shellfire/1/train | 1881 | 0.00 | 0.00 | 0.00 |
| D2-shellfire/1/validation | 314 | 0.00 | 0.00 | 0.00 |
| D2-shellfire/2/report | 202 | 6.93 | 0.99 | 0.00 |
| D2-shellfire/2/test | 200 | 7.00 | 1.00 | 0.00 |
| D2-shellfire/2/train | 2422 | 7.80 | 1.11 | 0.00 |
| D2-shellfire/2/validation | 311 | 9.00 | 1.29 | 0.00 |

Joint-plan denominator and corrected group conflicts are unresolved: v2 omits plan/focus provenance. Assigned-row and per-decision family distributions, distances and conflict occupancy are in JSON. Old unit conflicts diagnose historical dependencies; new autonomous checks do not qualify command-conditioned S2 labels. Threat overflow is not group reaction; shift stays dropped.

- Any required field absent? **YES** → Mark that count unresolved (implementer).
- Multi-gun assigned coverage <5% in any multi-gun stratum? **YES** → Revise S1 cells/readiness diversity (drafter).
- Corrected oracle has exact active-label conflicts? **NO** → No action triggered; revise only if conflicts appear (drafter).

Observed exact conflicts: zero for old and prospective autonomous heads. Sparse/no collision occupancy remains unresolved; this is not a proof of decidability. Ready-only group-command coverage is a lower bound for the new startable-projected wrapper, which S1 must measure.
