APPROVE_WITH_NOTES
Reviewer family: Codex
Reviewed run commit: d5044e8 (Claude execution of Codex-sealed v3 implementation at c27f5b9)
Reviewed design context: 69e13a2bbd1475a3a40e2ec43010ebdb3104c55f, DESIGN_0G §§19.8–19.12

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

No defect was found that invalidates P16. The observed result passes the sealed descriptive rules; it remains one development panel and needs §19.12 replication before serving as the v7 witness. This is Codex's cross-family review of Claude's executed run/report, with a separate Codex supporting reviewer; it does not make the original Codex controller implementation independently cross-family accepted.

Verification: all 620 entries in RAW_FILES_LOCAL.json matched size/SHA256 BEFORE parsing; the inventory exactly covers the raw directory. All 120 planned requests/claims/completions/gate receipts, per-fight entropy and admitted binaries matched. Declaration/SEAL, all implementation/policy/ledger/template pins and protected sources matched. Only the evolving plan/design files differ now: their exact sealed bytes were verified from a9dfc6f without restoring/editing them. The current design additions do not retroactively alter the run. P12's 40 controls finished and its sanity receipt was reported before either intervention started. Development entropy is disjoint from the declared prior development ledgers; judging entropy was not opened. Engineering parity receipts compare original P12 against v3 P12 on the same engineering request.

Full stored-only recomputation exactly matches COMPACT.json, SUMMARY.json and ANALYSIS_VERIFICATION.json, including every rendered measurement, all raw/clipped geometry/arrival fields and denominators, gun/role shell statistics, HP conservation, V, last hits, killers/losses, gun-survival curves, paired orientation/cluster outcomes and both declared readings. Terminal observer unit/gun counts and times independently reconcile for every fight. Reproducible helper, exact verification and recount log are in evidence/tactical_composition_demo/astelia_cpp/s4_escort_probe_v3_recheck_codex/. No combat or process listing was performed.

P12 regular: 3/20 eliminations, S −17.55, enemy guns destroyed 8.15, own guns lost 9.05, own losses 49.05; novice 20/20, S +20.05. P16 regular: 19/20, S +4.9, 10 enemy guns destroyed, 4.95 own guns lost, 44.95 own losses; novice 20/20, S +22.65. P17 regular: 0/20, S −36.05; novice 20/20, S +9.2. No cell times out or has a controller/numerical failure.

All 19 P16 regular wins are genuine (enemy=0, own≥1, t<150):

| Cluster | Orientation | Time (s) | Own survivors | Enemy survivors |
|---|---|---|---|---|
| c00 | 0 | 60.766666667 | 6 | 0 |
| c00 | 1 | 29.966666667 | 9 | 0 |
| c01 | 0 | 72.000000000 | 2 | 0 |
| c01 | 1 | 48.300000000 | 5 | 0 |
| c02 | 0 | 46.066666667 | 8 | 0 |
| c02 | 1 | 66.566666667 | 3 | 0 |
| c03 | 0 | 43.666666667 | 6 | 0 |
| c03 | 1 | 44.400000000 | 3 | 0 |
| c04 | 0 | 42.866666667 | 8 | 0 |
| c04 | 1 | 41.866666667 | 7 | 0 |
| c05 | 0 | 51.433333333 | 3 | 0 |
| c05 | 1 | 65.866666667 | 1 | 0 |
| c06 | 0 | 32.800000000 | 9 | 0 |
| c06 | 1 | 55.500000000 | 5 | 0 |
| c07 | 0 | 44.233333333 | 8 | 0 |
| c07 | 1 | 53.366666667 | 6 | 0 |
| c08 | 0 | 50.433333333 | 5 | 0 |
| c08 | 1 | 51.600000000 | 3 | 0 |
| c09 | 0 | 46.866666667 | 4 | 0 |

Only c09/o1 is a P16 regular nonwin. Paired P16-minus-P12 regular wins by cluster: [2,2,2,2,0,2,1,2,2,1]; nine positive and one tie. Every novice cluster ties at two wins. P16 regular chosen-target V is 3.321 versus P12 2.630; actual all-role gun-targeted-shell multiplicity 2.779 versus 2.216; early artillery screen kills (<20 s) 384 versus 238; own guns at 30 s 6.05 versus 2.85. These support the intended mechanism descriptively, without separating targeting from the changed movement focus or claiming mediation/causality from outcome-conditioned trajectories.

Attribution: the controller prepares the exact original P12 object every tick and never mutates its state or RNG. The ordering is the only gun-policy change; the original reach set, anchor fallback, radial focus rule, clipping, id-ordered repulsion and pre-spacing multiplier remain intact. The recount checks the HP-ranked P12 gun oracle and V-ranked P16 oracle on each stored prepare snapshot. Separately, all 40 P16 streams have 46,165 audit rows, 672,961 non-gun commands equal to the cached P12 command on the SAME observation, and 386,942 gun failure flags equal to baseline. There are 32,651 differing gun target choices and 130,487 differing movement tuples, all within the allowed focus-derived change. Paired initial P12/P16 observer snapshots match. Direct comparison of later action streams from different combat trajectories would confound policy with observation differences. Native decide is a pure prepared lookup (src/native/s3_controller.cpp:257), so the host's extra audit calls cannot advance state/RNG. Supporting reviewer independently confirmed the source and raw parity checks.

Engine/measurement challenge: V uses the public prepare observation, inclusive splash+victim body radius, and living opposing units; it cannot observe future releases/impacts. Actual impact splash and friendly damage use the engine's declared capped-HP rules. Dead target/no-impact and airborne shells have distinct counters; gun-only and all-role success denominators are separate, zero denominators remain unavailable. No hidden branch/search/rollout work or novel non-gun action was found. All 19 wins have zero unlanded enemy artillery shells at termination. The shared engine ends immediately on elimination; full hostile direct-projectile state is not stored, so no claim about hypothetical continued combat after termination is supported. This is a common measurement boundary, not evidence of a P16-specific exploit. The result proves performance in this declared native world; neither general tactical reliability nor source recursion.

Findings and dispositions (presentation only):

- C1 FIXED: first table's shell labels now explicitly identify gun victims per successful gun-targeted shell; they are not the all-role values used for the new mechanism endpoint.
- C2 FIXED: added the existing stored orientation win/S, cluster mean S and paired mean-S differences that the original rendered table omitted. No data or arithmetic was changed.
- C3 FIXED: report identifies this completed run review separately from OWNER_RECHECK.md, which reviewed precombat preparation.
- N1 RETAINED: P12 varies across earlier panels and this unusually large result comes from ten paired clusters. §19.12's fresh twenty-cluster replication remains required. No population, v7 design acceptance, registration, judging or resonator claim follows from v3.

The stricter sealed observed-owner reading also requires positive novice S; it passes, so it does not change this verdict. The exact results and declared readings are preserved. Existing receipts, code, ledgers, PLAN_CURRENT and DESIGN_0G were not edited. Owner's explicit plan exclusion overrides the usual AGENTS plan-tracking location; this review and v4 OWNER_RECHECK.md track disposition instead.

Original report SHA256: 021c8def8a19bd94b0482a423e2071a4215cc79469814b3445c1f41fdf030863
Corrected report SHA256: 6ef486fb7a87254517b3e6966763e1e81d0c38084772bf33a5007e65fcf51d1f
Native executable SHA256: 83a6c10f24901760bc028c328895024dbc3a14cc9da4799928b6ad1f8699c871
Full stored recount: PASS, 495.530 s.
