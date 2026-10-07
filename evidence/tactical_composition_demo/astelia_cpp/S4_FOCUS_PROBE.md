DONE

All 160/160 fights completed: 10 fresh development seed clusters × 2 orientations × P0/P4/P5/P6 × regular/novice, controlled team 0. Single declared setting; descriptive scripted probe of DESIGN_0G §19.2, not an RRG controller or a scientific/readiness verdict. No tuning, registration, judging entropy or status change.

Parameters and full head request templates were declared before any engineering/development fight in [POLICY.md](s4_focus_probe_v1/POLICY.md), [DECLARATION.json](s4_focus_probe_v1/DECLARATION.json) and the new [development ledger](s4_focus_probe_v1/DEVELOPMENT_SEED_LEDGER.json). Every arm uses the exact v6 attempt-2 stage-B knobs. P4 guns select lowest-HP reachable enemy gun, ties by id, and keep the full v6 target otherwise. No target suppression or fire-holding occurs. P5 also replaces gun movement with radial commitment at own reach minus 12px (bounded below by own minRange). P6 direct/ranged units also target the shared focus within native direct reach; their movement and all melee commands remain v6. All enemy guns gone restores complete v6 actions.

Shared focus is the weakest gun reachable by any own gun; if none is reachable, weakest living gun overall. P4/P5 still select individually within each gun's reach. Different reach sets can split the battery across targets. P5 replaces the entire gun movement command, including neighbour forces, so it tests a scripted commitment policy rather than isolating one term in the v6 equations. P6 uses edge-to-edge direct reach; line-of-fire blockers remain native and may prevent a shot. Enemy motion, collisions, clipping and reflexes can obstruct commitment. Base v6 internal target memory remains the baseline computation, while actual action targets change observed combat. These are declared limitations, not post-outcome changes.

| Arm | Head | Elimination wins | Timeouts | Mean S | Enemy guns destroyed /10 | Own gun losses /10 | Own losses /50 | Shell hits / fired at enemy guns | First gun kill mean s (fights with a kill) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| P0 | regular | 0/20 | 19/20 | +5.60 | 0.65 | 2.60 | 35.05 | 317 / 331 | 75.29 (9/20) |
| P0 | novice | 14/20 | 0/20 | +2.95 | 8.70 | 7.30 | 45.75 | 542 / 552 | 33.91 (20/20) |
| P4 | regular | 0/20 | 20/20 | +8.05 | 0.45 | 2.25 | 32.40 | 391 / 404 | 70.94 (9/20) |
| P4 | novice | 17/20 | 0/20 | +11.05 | 9.75 | 5.30 | 38.70 | 631 / 646 | 31.78 (20/20) |
| P5 | regular | 0/20 | 19/20 | -14.80 | 3.40 | 10.00 | 37.10 | 966 / 1131 | 14.27 (20/20) |
| P5 | novice | 20/20 | 0/20 | +38.85 | 10.00 | 1.10 | 11.15 | 754 / 979 | 11.53 (20/20) |
| P6 | regular | 0/20 | 19/20 | -15.95 | 3.45 | 10.00 | 38.45 | 966 / 1131 | 14.27 (20/20) |
| P6 | novice | 20/20 | 0/20 | +38.85 | 10.00 | 1.10 | 11.15 | 754 / 979 | 11.53 (20/20) |

Who kills our guns (total deaths across20 fights per cell; source team 0 is friendly, team 1 enemy):

| Arm | Head | Own gun killers by team / role |
|---|---|---|
| P0 | regular | team 1 artillery: 50, team 1 ranged: 2 |
| P0 | novice | team 1 artillery: 145, team 1 ranged: 1 |
| P4 | regular | team 1 artillery: 42, team 1 ranged: 3 |
| P4 | novice | team 1 artillery: 104, team 1 ranged: 2 |
| P5 | regular | team 0 ranged: 2, team 1 artillery: 133, team 1 melee: 7, team 1 ranged: 58 |
| P5 | novice | team 1 artillery: 5, team 1 melee: 1, team 1 ranged: 16 |
| P6 | regular | team 0 ranged: 2, team 1 artillery: 133, team 1 melee: 6, team 1 ranged: 59 |
| P6 | novice | team 1 artillery: 5, team 1 melee: 1, team 1 ranged: 16 |

Elimination requires enemy0, own>=1 and t<150s. Timeout never counts as a win. S is own survivors minus enemy survivors. Gun/own casualties are means per fight; launch/hit totals sum 20 fights. Hit numerator counts distinct damaging own shell launches aimed at enemy guns that damage at least one enemy gun; multiple splash victims count once. Soft-target launches incidentally hitting guns are excluded from both targeted counts. Denominator includes misses and shells still airborne at termination. First kill times are conditional on at least one enemy gun dying; no-kill fights are not assigned150s or zero. Medians, per-fight times, killer unit ids/roles/teams, elimination times and losses per enemy kill are in JSON. Orientations are paired within clusters; no confidence/acceptance claim or general mechanism rejection follows from this one setting. Auto barrage/slow remain inactive on both sides because sandboxAbilities=false; regular formation and shell dodge remain active.

P6 realization audit: 1574 direct-unit focus ticks in 15/20 regular fights; zero eligible direct-unit ticks in all 20 novice fights. All 20 P5/P6 novice observer streams, actions and terminal metrics are byte-identical after decompression. Thus P6 adds no realized intervention against novice in this set; its 20/20 does not establish an incremental direct-unit benefit. [P6_REALIZATION.json](s4_focus_probe_v1/P6_REALIZATION.json) preserves counts and stream SHA256 values. This stored-only audit did not change policy or outcomes.

Regular elimination wins: P0 0/20, P4 0/20, P5 0/20, P6 0/20. Novice: P0 14/20, P4 17/20, P5 20/20, P6 20/20. These are observed outcomes for the declared policies; no setting was changed after outcomes.

Build elapsed/awake 2.967/2.967s; final focused checks 7.435/7.435s; combat 158.558/158.557s; stored-only all-tick recount 200.352/200.351s. P6 stored-only realization audit 28.642/28.642s. Total measured probe-stage awake time 401.618s, below 3600s. Each compute stage used caffeinate; combat/recount caps 1200s and a remaining1h projection guard. No code edits occurred during fights or recount.

Independent stored-data review reads: 22.231s captured; an initial repeat read lacked a retained terminal session/timing and has a conservative 60 s budget reservation. No fights or tests were repeated by the reviewer. Probe stages plus this conservative review accounting total 483.848s, below 3600s.

Historical attribution/v6 contract stdout and stderr remain byte-identical across historical v6, observer, volley and new focus binaries. P0 also matches observer states, actions, telemetry and metrics byte-for-byte in both two-second engineering comparisons. All 8734 protected tracked inputs retain SHA256 identity. The initial test stopped on unrelated roadmap commit74c8b77 by another session; the original declaration and failed check are retained, and CONCURRENT_WORK.json records its exclusion from the overbroad protection snapshot. No policy, engine input, parameter or seed changed. All 160 raw hashes, requests, casualties, first kill times, killer totals and targeted shell identities reconcile. No controller failures, forks, search, rollouts or branch steps occurred.

Owner rechecks and dispositions: [OWNER_RECHECK.md](s4_focus_probe_v1/OWNER_RECHECK.md). The verbatim request was sent to separate reviewers. Claude CLI is not logged in; separate Codex review is the disclosed same-family fallback. The owner explicitly forbids PLAN_CURRENT edits, so tracking stays adjacent. No numeric scores or cross-family acceptance claim.

Evidence: [compact aggregate JSON](s4_focus_probe_v1/COMPACT.json), [full per-fight summary](s4_focus_probe_v1/SUMMARY.json), [native outcomes](s4_focus_probe_v1/FIGHTS.json), [all-tick verification](s4_focus_probe_v1/ANALYSIS_VERIFICATION.json), [historical fixtures](s4_focus_probe_v1/HISTORICAL_FIXTURES.json), [P0 parity](s4_focus_probe_v1/P0_PARITY.json). Raw 30 Hz traces, requests, stderr and ledger claim stay local, identified by SHA256 and byte count in [RAW_FILES_LOCAL.json](s4_focus_probe_v1/RAW_FILES_LOCAL.json). Files over 45MB are never delivered. Reproducible final scripts are run.py, analyze.py, report.py, check.py, build.py and deliver.py plus the new native sources; create_focus_probe_v1.py and make_analysis.py are historical bootstrap helpers, not final script generators. Delivery commit/bundle identity and fetched-blob verification are recorded in adjacent DELIVERY_TRANSPORT.json.
