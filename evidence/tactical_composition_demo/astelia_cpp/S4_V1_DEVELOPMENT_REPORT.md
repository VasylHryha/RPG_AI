STOP

# S4 v1 development report

Implementer family: Codex (GPT-6). Exploratory development under decision 0028 items 15-16 and the owner’s explicit two-part request. Independent Claude review remains required; no self-acceptance is claimed.

**Stage B STOP:** resonator novice mean S = −0.110, so Stage C was not run. Resonator regular mean S = −9.555; mean enemy artillery alive = 8.010 of 10, with 147/200 regular fights timing out. All four arms completed the same held-out comparisons before stopping. There is no fresh P2/P3 spread, δ or n proposal.

Section 12 uses legal-target status recorded at the start of the tick producing the damage. The native v1 skeleton splits own incoming damage and favors engaged enemy targets for resonator and morale; push-pull and nearest remain unchanged. v0 is explicitly selectable. The prior STOP report remains in git at efc3f3a; the drafter answered its timing question at 90d6f29.

Part 1 implementation commit: `dca84c76bdc10e5c36ba13e9a9dc92d305cc1554`. [Part 1 byte parity, admission and v1 engineering checks](s4_v1_checks/PART1_PARITY.json): all 152 S3 fixtures (38 per arm) and twelve amended replay summaries match v0 byte-for-byte; each v1 stateful arm also played 38 engineering fixtures without failure and passed captured-snapshot refinement below 0.02. [Affected tests](s4_v1_checks/tests.stdout.txt).

[Amended protocol](S4_AMENDED_PROTOCOL.md), unchanged optimizer/budget: pycma 4.5.0 ask/tell; population 16; sigma 0.25; sixteen generations; 19 fixed common tuning clusters per candidate; 9,766 fight evaluations per tuned arm/stage including cache hits. A starts at midpoints, B/C at the preceding tuning-selected best. All objective values enter covariance adaptation; highest mean retains the earlier tie. Validation never selects knobs. Dimensions remain 10/10/2, nearest untuned. B tuning uses ten novice/nine regular clusters; validation uses 100 per level.

[Fresh development seed declaration](S4_V1_SEEDS.json) and [all candidate/generation/orientation/cache uses](s4_v1_development/s4_seeds.json). Independent development bases 510000000/511000000/512000000, validation +100000, final C heads +101000; these were declared before fights and do not derive from the judging root. No judging-root contents were read by the harness. Source/build/cache/pycma inputs are pinned in [run identity](s4_v1_development/run_identity.json).

Expected duration was logged before the first evaluation: 90–120 minutes with ten workers if all stages run; measured 64.80 minutes. The amended combined-time accounting retains 34.48 prior minutes and the 180-minute cap (145.52-minute allowance). Every generation checks the conservative remaining-work projection; every evaluation checks the deadline.

[Reconstruction audit](s4_v1_development/AUDIT.json): 60,996 accounted fights, 60,996 fresh and 0 cache hits, plus 8 captures; 1536 evaluated CMA candidates. Zero controller failures; all executed A/B metrics have zero forks, search calls and artillery rollouts. Stage C and its planning-work check are not_run after the B novice stop. Both orientations, raw scores, budgets, retention and CMA ask/tell were reconstructed.

| Stage | Resonator novice mean S | Novice stop gate |
|---|---:|---|
| A | 5.0450 | pass |
| B | -0.1100 | STOP |

Stopped after all four arms’ Stage B validation because tuned resonator novice mean S ≤ 0. Later stages were not run; no registration is eligible.

Validation is cluster-averaged across both orientations. Intervals below are descriptive normal 95% intervals, with no registered scientific verdict. Stage C’s pooled doctrine comparison is not_run; its predeclared reporting method would use shared-seed blocks for SE/interval to retain cross-doctrine covariance. A removes projectile observation asymmetry; B/C restore full armies. Army composition also changes, so A/B differences cannot be attributed solely to projectile visibility.

## Stage A validation

| Arm | Endpoint | Mean S | SD | SE | Descriptive 95% interval | Timeouts / fights | Mean enemy artillery alive |
|---|---|---:|---:|---:|---|---|---:|
| resonator | s4_melee10 / novice | 5.0450 | 1.4738 | 0.1474 | [4.7561, 5.3339] | 0 / 200 | 0.0000 |
| morale | s4_melee10 / novice | 4.8150 | 0.8577 | 0.0858 | [4.6469, 4.9831] | 0 / 200 | 0.0000 |
| pushpull | s4_melee10 / novice | 1.6300 | 2.2670 | 0.2267 | [1.1857, 2.0743] | 0 / 200 | 0.0000 |
| nearest | s4_melee10 / novice | 0.6000 | 2.5256 | 0.2526 | [0.1050, 1.0950] | 0 / 200 | 0.0000 |

Regular head-to-head is not_run in A: the declared stage is novice melee-only. All artillery counts are zero by army construction.

| Arm | Selected tuning mean S | Cluster SD | Stage evaluations |
|---|---:|---:|---:|
| resonator | 5.3684 | 0.7609 | 9,766 |
| morale | 4.8158 | 0.6914 | 9,766 |
| pushpull | 2.2632 | 2.3651 | 9,766 |

## Stage B validation

| Arm | Endpoint | Mean S | SD | SE | Descriptive 95% interval | Timeouts / fights | Mean enemy artillery alive |
|---|---|---:|---:|---:|---|---|---:|
| resonator | s4_full_head / novice | -0.1100 | 8.0775 | 0.8077 | [-1.6932, 1.4732] | 0 / 200 | 2.7650 |
| resonator | s4_full_head / regular | -9.5550 | 7.8109 | 0.7811 | [-11.0859, -8.0241] | 147 / 200 | 8.0100 |
| morale | s4_full_head / novice | 1.1000 | 3.0740 | 0.3074 | [0.4975, 1.7025] | 0 / 200 | 1.2600 |
| morale | s4_full_head / regular | -2.1650 | 1.7782 | 0.1778 | [-2.5135, -1.8165] | 195 / 200 | 9.7850 |
| pushpull | s4_full_head / novice | -2.2000 | 2.8436 | 0.2844 | [-2.7573, -1.6427] | 0 / 200 | 2.8050 |
| pushpull | s4_full_head / regular | -1.1450 | 1.9966 | 0.1997 | [-1.5363, -0.7537] | 200 / 200 | 9.9800 |
| nearest | s4_full_head / novice | -17.5250 | 4.1227 | 0.4123 | [-18.3331, -16.7169] | 0 / 200 | 9.7750 |
| nearest | s4_full_head / regular | -24.0350 | 6.0131 | 0.6013 | [-25.2136, -22.8564] | 0 / 200 | 10.0000 |

| Arm | Selected tuning mean S | Cluster SD | Stage evaluations |
|---|---:|---:|---:|
| resonator | -0.3684 | 8.8299 | 9,766 |
| morale | 0.1579 | 2.7941 | 9,766 |
| pushpull | -1.3947 | 2.8017 | 9,766 |

## Stage C validation

| Arm | Validation | Regular head | Timeouts | Mean enemy guns alive |
|---|---|---|---|---|
| resonator | not_run: Stage B novice stop gate | not_run: Stage B novice stop gate | not_run: Stage B novice stop gate | not_run: Stage B novice stop gate |
| morale | not_run: Stage B novice stop gate | not_run: Stage B novice stop gate | not_run: Stage B novice stop gate | not_run: Stage B novice stop gate |
| pushpull | not_run: Stage B novice stop gate | not_run: Stage B novice stop gate | not_run: Stage B novice stop gate | not_run: Stage B novice stop gate |
| nearest | not_run: Stage B novice stop gate | not_run: Stage B novice stop gate | not_run: Stage B novice stop gate | not_run: Stage B novice stop gate |

## Margin and sample-size planning

not_run: stopped before C. No fresh P2/P3 paired spread, δ or bounded n planning is available. Historical amended v0 measurements remain separate.

## End-state diagnostics and remaining gate

Enemy artillery is counted directly from living occupied enemy artillery at fight end. Means and total counts per arm/setting are retained in VALIDATION_END_STATES.json. Timeout means reaching the 150-second duration; it remains an ordinary scored fight. Every endpoint above has 100 clusters / 200 fights; the doctrine pool has 1,900 configuration clusters with 100 independent shared-seed blocks. Counts are descriptive and do not change the survivor-first objective.

Selected knobs per stage are in A_best.json, B_best.json and C_best.json where executed. [Raw fight log](s4_v1_development/fights.jsonl.gz), candidate logs, all validation scores and matching replay captures are retained. HTML replays are generated artifacts; no browser qualification is claimed for this run.

No outcome-informed equation changes, tuning restarts, budget extensions, judging-seed use, S5 registration, recorded run, SPEC_0G.json edits, frozen GeoMind edits, committed receipt edits or milestone status changes occurred. The authorized v1 equation change preceded tuning. No tactical superiority, equivalence, RRG recursion or C4/C5 qualification is inferred from development readiness. Claude’s independent development review is next; δ and a fresh S5 specification remain owner decisions.

Delivery: the original workspace’s .git is read-only in this session (git add was denied creating index.lock). Part 1 was committed before development in the isolated checkout `/private/tmp/ai_RPG_test_s4_v1_20261005`, branch `codex/s4-v1-development`, based on 90d6f29. Part 2 evidence and this report are committed there with repository hooks enabled. Files are mirrored to the requested workspace paths; `s4_v1_checks/commits.bundle` delivers both scoped commits without changing the original checkout’s Git metadata. The original untracked `viz_0g/replays_0g.json` is excluded.
