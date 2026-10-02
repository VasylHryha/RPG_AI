# C6 revision-2 development result

Owner-approved proposal: `experiments/c6_proposal_r2.md` (0011).
Code: `b9e30f7`. Eight workers; elapsed 55.0 minutes. Development only; no panel verdict.
**STOP 1:** pass-2 formation fell below the approved 0.75 target (23/30 at each level).

| Pass | Level 2 formed | Level 3 formed | Factors used C2 / C3 |
|---|---|---|---|
| 1 | 17/30 | 8/30 | 3.2 / 9.6 |
| 2 | 14/30 | 10/30 | 3.4 / 16.4 |

Pass-1 factors were available: 200 base, 48 level-2 and 8 level-3 isolated measurements; none censored.
Pass-2 factor estimates, reported only: 4.6 / 11.0; settings were not iterated.
All 10 level-2 and 5 level-3 native/NumPy detection comparisons matched exactly; numerical checks passed at both levels.
All source hashes remained unchanged. Before this run, 346 tests passed in 78.37 seconds; pinned native build succeeded.
The compiler, flags and binary/source hashes are preserved in `NATIVE_BUILD.json`.

Criterion 6 checks direct parts only. In pass 2, level-3 direct parts had 3/150 overlap failures and 3/150 dynamic failures.
Level-3 rejection counts include 17 recovery failures and 4 direct-part failures; deeper failures did not veto parents.
Readiness, runtime qualification, final registration, panel and independent review were not reached.
This does not establish causal closure, bounded prediction, or a verdict on the owner's principle.
No rerun or redesign is authorized by this STOP. Decision: `docs/decisions/0013-c6-r2-design-gate-stop.md`.

Receipt SHA256 (uncompressed): `737016d89525baf8a6d6ea7c73a4ea23f87b9a139ac62c616b3aec9a40944a99`.
Receipt SHA256 (gzip): `ace2cd2ae402b1c217dece8268b2def3b7372fe7b9c37d895327f7900d7df375`.
