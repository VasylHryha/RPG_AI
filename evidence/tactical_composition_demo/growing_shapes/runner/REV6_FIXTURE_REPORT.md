FIXTURES_FAIL

F1b failed the frozen response criterion. F1a passed; F1c is descriptive. F2, F3 and F4 passed. Section 12.8 blocks F5 and development; F6–F9 were not reached in the required sequence. Each executed fixture ran once. No implementation code changed and no fixture was rerun. This is implementer evidence for the plan's A6 review, not acceptance or authorization for development.

Execution grant: `docs/decisions/0030-0h-rev6-fixture-run.md`, committed approval SHA256 `36579b122c0a6ff545b4bcd4f7e8401e1d825b72a66f0fad97c2ebcb25ac6cce`. Integration identity: `855d9310fbae5c71fa9d507d288372b17858a88c`. Start HEAD `d82114b3d346d343294d5f6f355bf37c116e1041` is a descendant containing approval/review and unrelated work. All pinned scientific bytes match, and all tracked inputs match the integration commit. Ignored native images/build manifests match its committed identity pin. `fixture_run_20261006/COMMIT_IDENTITY.json` and `START_IDENTITY.json` preserve the exact checks. The grant referenced the committed decision and checked scientific inputs once before F1. The instantiated seed inventory and donor mapping were copied to `PRE_EXECUTION_SEED_INVENTORY.json` before results. `caffeinate -i -s` covered the serial process.

No training, development, evaluation panel 512–767, judging entropy or registration was executed. F4 uses fixture validation recipient 768 and donor 778 only. Calibration 0–255 was reused from the pinned 5.1 receipt without rerunning it. F5's proposed fixture growth sequence was never started.

## Declared criteria and measurements

F1a/F1b require error ≤ 0.3 rad at every 0.1 s world step from first entry through t = 16 s inclusive, and a directed S→O path in ≥ 80% of 1600 endpoint samples over 160 s. Native C4 topology and motion remain intact; growth, adaptation and deaths are off. F1c has the same recorded diagnostics and no gate.

| Configuration | Outcome | Absolute wrapped error at 16 s (rad) | First entry by deadline | Path persistence |
|---|---|---:|---|---|
| F1a, direct | PASS | 0.069708868 | 12.6 s; delay 4.6 s | 1600/1600 (100%) |
| F1b, dense | FAIL | 0.737819443 | None by 16 s | 1600/1600 (100%) |
| F1c, long | DESCRIPTIVE | 1.545666007 | None by 16 s | 1600/1600 (100%) |

F1a's maximum error from first entry through the deadline is 0.298176417 rad, with continuous compliance. F1b never enters tolerance during (8,16] s; its minimum error in that window is 0.737819443 rad. Its first entry in the **already saved full trace** is 23.4 s (15.4 s after the step), outside the frozen deadline; this does not change FAIL. F1c never reaches tolerance by 160 s; its final error is 0.758974776 rad. F1a/F1b final errors are approximately 5.17e-13 and 1.45e-8 rad. All three have zero output direct-drive exposure and zero direct-drive exposure for the g=0 intermediates. Every world step's neighbours and link weights remain in `F1.json.gz`.

| Fixture | Declared criterion | Measured values | Outcome |
|---|---|---|---|
| F2 | Empty O emits the exact default; disconnected singleton gives bitwise identical phases under constant/step streams, with zero path exposure | Empty default check true (angle=0, magnitude=0); 160 phases/stream, byte-identical; maximum phase difference 0; 0/320 path samples | PASS |
| F3 | Output at the sensor has bitwise +0 direct drive at every RK4 stage | 5 native steps × 4 stages = 20; all output drive terms `0x0.0p+0` | PASS |
| F4 | Site-0/oracle relays emit exactly their declared wrapped outputs; lesion zeroes incoming coupling at every stage; native/reference assay parity | Site-0 = 0.3999999999999999, oracle = 1.0999999999999996, exactly the wrapped targets; 20/20 lesion coupling terms +0. Five modes × 160 decisions/backend: angle difference 0, exact magnitudes/choices/paths/output presence; tolerance 1e-12 | PASS |
| F5(i), F5(ii) | B-out accepted in (i); B-path accepted in (ii); both starts A≥0.3 rad, B≥0.3 rad and max(E)≥0.5, pooled over 3 checkpoints × 10 assays | A, B, E and B-out/B-path event counts **not measured**; neither start executed | NOT_RUN: F1 block |
| F6 | Descriptive own/donor JS correlation on six F5 checkpoints; hidden resultant R≥0.05, ≥5 defined pairs; singleton/hold baselines use unique recipients | Correlations, defined-pair counts and encoding/retention values not measured | NOT_RUN: no F5 checkpoints |
| F7 | Match every accepted F5(i) B1 birth; zero unmatched | Requested, matched and unmatched counts **not measured** (not zero) | NOT_RUN: no paired F5(i) run |
| F8 | Descriptive first memory episode versus within-block P_i, eligibility and reward Δg; B1 demand/acceptance | No live F5(i) state; no values measured | NOT_RUN |
| F9 | Descriptive zero-demand, approach, retreat-inside-range and stop decoded actions | No cases executed; decoder limit not newly measured | NOT_RUN: sequence stopped |

F4 parity covers intact, donor, output_channel, site0 and oracle on recipient 768 (donor 778 for donor mode), with ten total fresh assay copies. Scores also match exactly. F5's A would measure own-versus-donor mean absolute wrapped output difference; B would measure own-versus-channel-lesion difference; E would pool per-site path exposure. None exists for this execution.

Section 19.9's input-only phasor, K=0 and fixed-structure comparisons apply to the later final evaluation panel, not the declared F5 fixture assay. They are **NOT_RUN**; no panel or extra comparator assay was added to this grant.

## Drift and readout occupancy

Maximum radii below cover measured endpoint states; the declared initial maximum radius is 3.2 m.u. in each scaffold. The wall starts at radius 6. Initial source radius is 3.2; initial output radii are 2.644, 1.532 and 1.804 m.u. for a/b/c.

| Configuration | Maximum endpoint radius (m.u.) | Final source radius | Final output radius | Wall exposure (element·s) | No sensor access (element·s) |
|---|---:|---:|---:|---:|---:|
| F1a | 3.225108103 | 3.199777778 | 2.644222222 | 0 | 0 |
| F1b | 3.134319623 | 2.869110430 | 1.862889570 | 0 | 0 |
| F1c | 3.103557677 | 1.518114357 | 0.033709437 | 0 | 1117.0 |

Readout occupancy is **1/1 output present at all 1600 steps in each configuration**; each of eight successive 20 s bins has 200/200 output-present samples and 200/200 path-present samples. Singleton coherence is C=1 by the declared readout, and no abstention due to absence occurs. `MEASURED_SUMMARY.json` records every bin's occupancy, path fraction, maximum radius and source-drive presence. Full per-step exposure stays in the hashed trace.

F1b retains its path and output while missing the response deadline. F1c moves strongly toward the origin: source radius 3.2→1.518114357 and output radius 1.804→0.033709437, with endpoint maximum radius about 1.49 in the 20–40 s bin. Source drive-presence bins remain 100%, but proximity and therefore drive strength change under motion; path presence alone cannot establish response. These observations support reporting compaction/drift as a risk. F5 growth/collapse behavior remains unmeasured, and these measurements do not isolate motion as the causal explanation of F1b's delay.

## Stop rows

| Yes/no row | Answer | Action | Responsible role |
|---|---|---|---|
| Required owner approval missing? | No | No refusal triggered | implementer |
| Scientific identity missing/mismatched? | No | Execution-start check passed | implementer |
| F1–F4 fail any criterion? | **Yes: F1b** | **Block F5 and development; report** | implementer |
| Measurement failure / INVALID readout? | No | No INVALID row triggered | implementer |
| F5 fails? | Not evaluated | No F5 verdict; prior block remains | drafter |
| F7 has unmatched births? | Not evaluated | No G0 feasibility inference | implementer |
| Code defect requiring a patch? | None observed | No patch or rerun | implementer |

F1, F2, F3 and F4 each executed once, in order. The first-four gate was then applied before F5. F6/F7/F8 depend on F5 states and F9 was later in the specified sequence, so all remained unexecuted. Changing a criterion requires the drafter's new revision and fresh entropy rather than changing this recorded verdict.

## Measured stage costs (UTC date 2026-10-06)

Awake time uses macOS `mach_absolute_time` (excludes sleep). Elapsed time is the difference of recorded UTC timestamps; `mach_continuous_time` independently records elapsed time including sleep. Their differences show no sleep interval. Exact timestamps and all three clocks are retained in the receipt and per-fixture timing files.

| Fixture stage | Start UTC | End UTC | Awake seconds | Elapsed UTC seconds |
|---|---|---|---:|---:|
| F1 | 09:56:26.077965 | 09:56:29.151340 | 3.073385 | 3.073375 |
| F2 | 09:56:30.160810 | 09:56:30.274449 | 0.113651 | 0.113639 |
| F3 | 09:56:30.275462 | 09:56:30.276044 | 0.000582 | 0.000582 |
| F4 | 09:56:30.276523 | 09:56:30.761359 | 0.484850 | 0.484836 |
| F5 growth/qualification/recovery/assay, both starts | NOT_RUN | NOT_RUN | not measured | not measured |
| F6, F7, F8, F9 | NOT_RUN | NOT_RUN | not measured | not measured |

F1 integrated 4800 world steps including endpoint neighbour/weight/exposure collection; F2 integrated 320. F3 measured one 0.1 s equivalent (five RK4 substeps); F4 included the same native lesion check and ten native/reference assay episodes with donor capture. The executed sequence, including trace serialization between stages, took **4.796945 s awake / 4.796981 s UTC elapsed**, from 09:56:26.077877 to 09:56:30.874858 UTC; approximately 1.1245 s is serialization/receipt overhead outside fixture timers. Startup/identity checking is outside this total. Times are host observations, with no quiet-machine or throughput guarantee.

## A7: development cost projection

**A complete projection from measured revision-6 fixture stages cannot be qualified:** the stop prevented every live growth, qualification, recovery and grown-checkpoint assay timing. F1/F2 yield frozen diagnostic-step rates of 0.000640289 and 0.000355158 s/step; these small frozen scaffolds do not estimate live 64-member training. F4 costs 0.484850 s for ten mixed native/reference small-copy episodes plus setup/capture; it does not isolate large native assay throughput. No extra benchmark was run to fill the gaps.

`DEVELOPMENT_COST_PROJECTION.json` records the full static workload and identifies every historical rate. For all four tasks usable and up to 20 snapshots per intact training, the planned 48 trainings contain 15,360,000 live steps, 76,800 growth checks, 8,512 qualification checks and at most 432,128 assay episodes: 327,680 snapshot assays, 88,064 intact final-panel assays and 16,384 control assays. The three 19.9 comparators add 18,432 episodes to the earlier workload. Donor capture adds 8,192 world episodes. Counts describe a full completion; protocol stops can shorten it.

Using the **reused 5.1 rates** in the immutable `REV6_COST_ESTIMATE.json`, pricing every comparator at its historical medium-assay rate, gives an **unqualified proxy subtotal of 15.855 serial hours**: training 11.944, qualification 1.291, recovery 0.322, evaluation 2.294, donor capture 0.0038. Adding the already recorded static synthetic B-path sensitivity gives:

| Population assumption | One exhausted site/check | Eight exhausted sites/check |
|---|---:|---:|
| 26 | 16.962 h | 24.711 h |
| 48 | 18.214 h | 34.722 h |
| 64 | 19.453 h | 44.639 h |

These are arithmetic scenarios, **not measured revision-6 development estimates, bounds or approval-ready durations**. Actual population, task mix, B-path demand, recovery/candidate mix, Python singleton/hold dispatch, growth/diagnostic cost, report I/O and host contention remain unpriced or unqualified. Some scenarios exceed 24 h. A7 is partial; development remains blocked by F1 independently of cost and has no owner grant.

Evidence: `fixture_run_20261006/RUN_RECEIPT.json`, `MEASURED_SUMMARY.json`, `DEVELOPMENT_COST_PROJECTION.json`, exact per-fixture timing records, execution log, start identity and small hashed traces. Delivery manifest and verification bind every shipped file. No integration readiness report, historical 5.1 verdict, milestone status or plan file was edited.

Assisted-by: Codex:GPT-6
