NOT_READY

Revision-6.4 pre-integration stop report. Implementer: Codex:GPT-6.
This is a specification stop, not an integration delivery or a failed fixture.
No revision-6 engine, runner, evaluator or fixture harness was implemented.
No existing file was edited. The 5.1 code and its versioned template loader
remain intact; loading/runtime compatibility was not retested in this session.

The owner's current request authorizes implementation and tiny contract tests,
and expressly says: **"If any clause is ambiguous, write the question in the
report and stop."** That instruction triggers this stop. Decision 0028 items
17–19 concern the engines and the earlier 5.1 development, and do not supply
the missing revision-6 fixture selections. Precedence used in this audit:
18 > 16 > 14 > 12 > 1–11 > base 5.1. The round-6 APPROVE_WITH_NOTES is a
design review; it does not constitute review of implementation that does not
yet exist. Section 18.5 supplies its two subsequent LOW clarifications.

## Questions requiring the drafter's specification

**Q1 — Which medium does F6 assay?** Sections 12.7, 14.7 and 18.5 define the
encoded angle, Jammalamadaka–SenGupta statistic, demodulated hidden-interval
circular mean, resultant threshold 0.05 and minimum five defined pairs. They
do not choose the medium state: F5(i), F5(ii), or both; checkpoint 40, 45, 50,
or all three. Section 14.5 explicitly assigns the three-checkpoint assay to
F5, while section 18.1 assigns initial/growth/recovery consumers to F5 and F7.
Neither explicitly assigns that state-selection procedure to F6. Please name
F6's state source(s), checkpoints, recipient/donor episodes, pooling unit and
whether own/donor comparisons use fresh frozen copies with growth, adaptation
and recovery off. Selecting one checkpoint versus six changes the descriptive
measurement and copy workload. The undefined-mean rule itself is resolved.

**Q2 — What concrete run constructs F8's carried-history boundary?** Sections
12.7 and 12.10 require P_i, e_i and reward updates at entry to remember_static
after a move block, compared with within-block episodes, without resetting
histories. The base supplies 20-episode blocks and the rotation, but the
fixture does not select its initial/checkpoint state, reward versus task-blind
mode, which blocks are run, world episode ids, or medium/growth/recovery keys.
Sections 16.2 and 18.1 instantiate fixture consumers for F5/F7 only. Please
specify the F8 start, exact block sequence and episode ids, arm/policy, enabled
growth/qualification/recovery rules, and seed-consumer keys. If F8 is intended
as a synthetic carried-history contract rather than a live move→memory run,
please prescribe that state/history recipe instead. These alternatives yield
different eligibility, reward updates and runtime. No new key or reset rule
was invented here.

These questions concern constructing the requested F1–F8 harness **exactly**;
they do not propose memory PASS thresholds or change the G2 claim. Under
AGENTS.md, the drafter owns any proposal clarification and its self-audit.
Stop pending those answers; no implementation choices have been substituted.

## Clause-to-delivery map

In this table, **blocked** means no new executable implementation and no
numerical/unit verification of that design clause. Existing 5.1 code is an
inherited reference, not evidence that revision 6 is implemented. The only
new verification is the documentary receipt contract batch described below.

| Governing clause | Required code/contract | Delivered status and test |
|---|---|---|
| 1; 9; 10; 12.6; 14.8 | Supersession and narrowed input-dependent angular response; site-0 superiority label; deferred claims | Recorded here; no functional claim or endpoint result |
| 2; 3; 5; base 2–4 | Native rev6_rhs_v1 C4 + masked drive + soft wall in live, frozen and recovery modes; held RK4 lists, continuous clock, step order | Blocked; no RHS or native parity test |
| 12.3 role table | Output drive/sensor eligibility/P_i/e_i/coverage/root exclusions; C4-only output lock; separate geometric exposure | Blocked; no mask/history contracts |
| 12.3; base 7–8 | rev6_template_v1 roles and three version ids in canonical hash, round trip, role-only difference; extraction/reindex/carrier/recovery preservation; unchanged old loader | Blocked; tracked 5.1 bytes preserved, runtime round trips not run |
| 14.1; 12.3; 4 | Fresh endpoint graph and current effective roots every step and after mutations; D4 forward OR backward reach and protection | Blocked; no graph/timer contract |
| 12.4; 4 | Singleton O; B-out origin spiral, neighbor phase or persistent growth fallback; normal newborn contract | Blocked; no output birth/readout contract |
| 12.1; 14.2; 16.1; 18.3 | Fair pointer, eight pairs × thirteen directions, r*=0.556, six stable conditions, full restore, no trial randomness | Blocked; R3-2 candidate c=(0.556,0) REJECT test **not implemented or run** |
| 4; base 5; 18.5 | D1→D4→D3→B-out→B-path→B1; cap/cost and 1+2+2 accepted quotas; terminal request versus attempt accounting | Blocked; no resource/quota/outcome test |
| 6; 12.10; 14.9; base 11 | M mirrors accepted B1 counts/times only, exact matching with unmatched slots retained; U FIFO/retry/drop with revision-6 entropy | Blocked; no control test |
| 12.5; 14.6; 16.2; 18.1–18.2 | Instantiated master seeds, world ranges, donor rank permutation, persistent PCG64 consumers and exact little-endian recovery sub-hash | REV6_SEED_INVENTORY.json: 2,840 master keys and all 128 donor entries; documentary contracts only; no RNG draws |
| 12.5–12.6; 14.6; base 8–9 | Donor clock replay, every-stage output-channel lesion, held descriptive receiver lesion, reasoned not-run, default/random/site-0/oracle comparators | Blocked; donor **map** recorded, no intervention implemented/tested |
| 12.5; 7 | 128 paired normalized differences, sample SD, 127 df, constant/nonfinite rules, primary alpha=.05 and secondary alpha/3 | Blocked; no inference implementation/test |
| 7; 12.6; 12.9; 14.9; 18.3–18.5; base 11 | G0 exact-match/coverage cuts; G0' inclusive late slope and terminal placement taxonomy; G2 conjunction and seed cuts; INVALID precedence | Blocked; no aggregation test/result |
| base 4; 6–10; 12.3; 16.3 | Inherited learning, reward, qualification, full-state recovery, snapshot budgets, G1/G1c/G5 and engine readiness | Existing 5.1 retained; no rev6 adaptation/recovery integration or review |
| 12.8; 14.9; 16.3 | All owner, source/unit/endpoint, readiness, fixture INVALID, perceive usability, M matching and outcome stop rows | Applicable stop is recorded here; executable stop table blocked |
| 14.3; 16.1 | F1a/b/c exact scaffold coordinates, native C4 lists, exposure, step/deadline and 160s persistence | Blocked; no fixture constructed or integrated |
| 12.7; 14.4 | F2 empty output/default; disconnected output bitwise stream independence | Blocked; no fixture constructed or integrated |
| 12.7 | F3 every-stage mask, F4 exact relays/every-stage lesion | Blocked; no fixture constructed or integrated |
| 14.5; 16.1; 18.1 | F5 task-blind starts, normal bindings, 50 growth episodes, checkpoints 40/45/50, paired frozen assays, pooled A/B/E and missing-O zero | Blocked; known seed keys recorded, no state construction |
| 12.7; 14.7; 18.5 | F6 circular mean/resultant/defined-pair count/correlation/raw traces, descriptive | Q1 unresolved; no fixture constructed |
| 12.7; 16.1; 18.1 | F7 independently recreated F5(i) start; own growth/M streams, B1 exact matching and exposure | Blocked; exact supplied keys recorded, no fixture constructed |
| 12.7; 12.10 | F8 carried-history memory boundary P_i/e_i/reward diagnostics, descriptive | Q2 unresolved; no fixture constructed |
| 8 projection; base 10 | F1–F8 and 48-training costs derived from stored 5.1 measurements; no new measurement | Conditional arithmetic in REV6_COST_ESTIMATE.json and below |
| 11; 13; 15; 17; 18.4–18.5 audit tables | Historical finding dispositions and causes | Read as rationale; no new acceptance or claimed drafter fix |

## Frozen receipt, without outcomes

REV6_SEED_INVENTORY.json records current input hashes and rewritten HEAD,
16 training-slot mappings, 2,840 instantiated key→uint64 masters, all 128
recipient/rank/donor entries, fixture donor pairs, world ranges and consumer
lifetimes/sharing. Donor π(j) is the **rank of j**, not the sorted list of ids;
sorting uses the full 256-bit hash, not its uint64 prefix. Recovery masters
use big-endian extraction and the inherited per-check sub-hash uses decimal
master and `kick:<world-step index>` with little-endian extraction. No master
was used to create a generator, draw a sample, initialize a native handle or
evaluate an episode. F5(ii) has no random medium consumer. No F6/F8 consumer
is silently fabricated. The receipt explicitly says evaluation results do not
exist and is not an evaluation, fixture PASS or completed registration gate.

## Cost estimate from 5.1 evidence

No benchmark, pilot, development seed or panel was run. The stored measured
200-episode cost receipt development_20261006/COST.json supplies 2.799475 ms
per training step, 0.545975 s per qualification check, 0.136119 s recovery per
check at its observed candidate mix, and 19.114088 ms per evaluator episode.
These are reused 5.1 rates; revision-6 graph/trial/mask/wall cost is unmeasured.
They describe awake monotonic stage time, not an elapsed-calendar guarantee.

Known fixture components: F1a/b/c at 1,600 steps each gives a 13.44 s training
proxy; two 50-episode F5 starts plus 50-episode F7-M gives 67.19 s. F5's
2 starts × 3 checkpoints × 10 episodes × 3 modes = 180 copy episodes gives
3.44 s; inherited intact qualification/recovery bookkeeping at 12 checks per
start gives 16.37 s. Their subtotal is **100.44 s**, excluding F2–F4, F6/F8,
donor-capture/diagnostic storage and revision-6 overhead. It is not a complete
F1–F8 estimate. Q1/Q2 prevent an exact total; tiny stage-algebra tests would
also need bounded counts in the harness rather than arbitrary fixture runs.

Development training is 48 × 2,000 × 160 = 15,360,000 steps, giving **11.94
serial hours**. Retaining inherited qualification only in the 16 intact runs
gives 8,512 checks: **1.29 h** qualification and **0.32 h** recovery at the
observed mix. At the inherited 20-snapshot cap, snapshot covariance copies
cost 16 × 20 × 2 × 4 × 128 = 327,680 episodes. Final whole-medium copies for
intact/M/U cost 48 × 4 × 128 = 24,576. Three added medium interventions
(donor, output-channel lesion, descriptive receiver lesion), on all four tasks
for each intact seed, add 24,576. This conditional 376,832-medium-episode
workload gives **2.00 h**, for a priced subtotal of **15.56 serial hours**.
If secondary interventions are not all requested, their workload is smaller;
the full all-four-task case is displayed for budgeting, not prescribed here.

The subtotal excludes capture of the donor schedules, scoring default/random
and the two relays, added graph/B-path work, I/O and any workload beyond those
counts. Using the earlier density-conditional rates in
PERF_RECHECK_PROJECTION.json, the same 376,832 medium episodes alone cost
8.16 h at synthetic N=24 or 23.38 h at synthetic N=64. Training at its
supplied-drive N=50 rate would take 50.76 h for the 48 runs. These independent
component sensitivities are not one mutually consistent predicted run, and
the 24-hour reporting line remains meaningful. No parallel scaling assumption
is used. Exact full-fixture costing must follow Q1/Q2 clarification; measured
fixture costing still requires separate owner authorization.

## Verification and delivery

The documentary synthetic contract batch ran once after writing the
packet: **6 tests passed in 0.089 s**. It checked seed extraction and inventory completeness, donor rank bijection and
distinct panels, exact recovery byte-order recipe, no-result labels, and
unchanged tracked growing_shapes hashes. No project imports, native loading,
fixture construction/integration, training or evaluation are part of that
batch. All 202 pre-existing tracked growing_shapes files matched their initial
SHA256 hashes. REV6_DOCUMENT_CONTRACTS.json records the actual result; it cannot
stand in for any missing integration contract in the table above.

Workspace .git is read-only under the supplied permission profile. Delivery
uses the verified archive and its SHA256 manifest described in
REV6_DELIVERY.md. This packet contains reports and small documentary evidence,
not implementation code. All members are below 50 MB; no historical raw bulk
outputs or other-session changes are included. There is no integration commit
or scientific/milestone status change. Resume only after the drafter answers
Q1/Q2 and records the clarifications; the implementation review and separate
fixture approval remain future gates.
