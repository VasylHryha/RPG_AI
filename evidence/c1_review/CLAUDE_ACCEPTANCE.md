# Claude independent review — GeoMind C1 R002 (with repairs R003 → R004)

**Verdict for C1 R002 (`geomind-c1-r4-002`): CHANGES_REQUIRED.**

Reviewer: Claude (Opus 5.5), 1 October 2026, against `GEOMIND_GEOMETRIC_AI_QUALITY_STANDARD_R4.md` C1, §5.2, §6 and §7.

R002's transaction mechanics are sound. Every commit I checked was reference-correct, every refusal kept byte-identical prior state, frame signs and gauges are right, and duplicates, cycles and migration behave. The blocking problems are evidential:

- The "fresh" R002 worlds are the R001 worlds relabeled, so the post-inspection redesign was never evaluated on new data (§5.2).
- The headline numbers overstate what the C1 mechanism did: 12/13 commits used no relaxation, and duplicate certificates inflated the cost tenfold.
- The ten focused checks miss defects they appear to cover.

The owner authorized direct fixes, then asked for a recheck of those fixes. My first repair, **R003**, failed my own recheck (S1–S3 below) and is superseded. The current implementation is **R004 (`geomind-c1-r4-004`): REVIEW_READY**. I wrote R003 and R004, so this document is **not** their independent acceptance. A different reviewer must decide R004 before C2 starts. C2 has not been started.

**Conflict with the existing receipt.** `ACCEPTANCE.md` (SHA256 `5b008dac…364c`, by a separate agent) accepts R002 and says it establishes the C2 prerequisite. I disagree, for findings F1–F5. I did not edit that file. The owner must resolve the conflict in the R4 status table.

No numeric quality score is assigned. A pass/fail count cannot honestly be converted into one.

## Exact reviewed identities

### R002, as reviewed (read-only, unchanged)

- Manifest: canonical `3d2385e73bc23a0e45ac3e7e65675ecb654bafd228fb4661a4b335925901dd12`, file `9d6cec1e0f226103d39779de8eaa09a8b425c5665ab5462ff1695e1c717ac705`. The file is archived byte-identically as `experiments/c1_r4_002_manifest.json`.
- `results.json` `c4e901f390cf230a7b021bc729cb719792c7d0c69a4e3960ad652734ae357c01`
- `instances.jsonl` `054b27a3f286d1a28a0a098938eabfa54c3dbc881a8535d2f3208ccba29b5c01`
- `contracts.xml` `b171bd1744e0b53dc135a8dce54842ca647323e2e0fc63c4e6f1c0f7e55a6ad5`
- `INTEGRITY.json` `206f71f9ada77ec9d4da602221c161a335a94f8abd14340f246cdc456da19989`
- `REVIEW.md` `6550c415340cf8ad1b72d3955d6ae354f4cb93d9d3abdedf2dc7785d89d3a569`
- `HANDOFF.md` `6c82592d8b578e7124948b8c61d1ff954732cf4e64623f2bd90bc706f6f11d3d`
- `README.md` `75b2c4095215a93ac0552672731901a7169a2e8f2cb2c8948985357604f4f39b`
- Accepted C0 receipt `evidence/c0_review/ACCEPTANCE.md` `ce6ecce70f35bb4af918b80a1c54136649a1f515f4788a3f34de776d87b6c453`, bound by every C1 receipt.

At review time, all 19 registered R002 inputs matched across the receipt, the live files and the archived `source/`, and all 48 saved states matched their receipt hashes. The reviewed sources were:

| File | SHA256 |
|---|---|
| `geomind/incremental.py` | `3e35ef264dde32c31d29363a839397031dde74ec533712ea03fb3c994fbef43f` |
| `geomind/c1_reference.py` | `e4d9439a69e65152cf04605f7aa7de0d878c2f27a530d5dc02ef148cac59279f` |
| `geomind/c1_cases.py` | `0cbd7efe8336847eb79bcd38bf831e2180106ae27579a0c4ef09803c684caa71` |
| `geomind/run_c1.py` | `5aa6289ed2eca78a0b997339fae317aa4daf471f773a3bbc360b5d39a3858d63` |
| `tests/test_c1.py` | `ecd57c74784feab31a19cc534ea4bad4697b645576b8bd7533e47c828ed6694a` |
| `geomind/geometry.py` (C0, accepted, unchanged) | `973740d321705d9c8633a6cd2da1696af91cec930e53bcb6b6b4831e280066f0` |

### R003 (superseded; receipts unchanged)

- Manifest file `24040c3116e953a18eb557b69f8caa6af8e0597afba1a40c1c17beceaaa794a1`, archived as `experiments/c1_r4_003_manifest.json`.
- `evidence/c1_r003/results.json` `46e5567d13f2ec1e2a21fb7d99686f42ab67dad65c3f51a357b3b4403eff36f0`, with its archived `source/`.

### R004, the current implementation (REVIEW_READY)

- Manifest: canonical `80b987dea7e6955542a9104939504468048b5ebb4e2bd597549c96cc616ee40b`, file `6959cc6886fe59ff73203c3099baaf67566480eac8ee1083011cfd2b6b860754`.
- `evidence/c1_r004/results.json` `d769208dabe696f3f7e0ef9e4d17edcf652b12a33bc42a816239254b4ea44361`
- `evidence/c1_r004/instances.jsonl` `6c2a6f983e435cc304de6f096f57f6c46068276323c158ab6435e98b4f0b5ba2`
- `evidence/c1_r004/contracts.xml` `a0b636a961be50f3f1b5e6ed1d0268b7269589e9b4ab42554ce47a9cf52a2ed2` (14 checks)
- `evidence/c1_r004/README.md` `4c64562be5ef2bd84a9193dea2db74ed83906ce165571ddf72417e94141a154e`

| R004 source | SHA256 |
|---|---|
| `geomind/incremental.py` | `093159523e7abdbd8c6a1be64039bc20241a9a447adfd6c41a2452516cb2b06b` |
| `geomind/run_c1.py` | `ce9f93dffa5490c7c66ae9761bf7633ab8f9869fd15fdfdc8dc5f6e3e8d17ddc` |
| `geomind/c1_cases.py` (generator v3, unchanged since R003) | `56f080e4e06eecdcfcc2910250003d9b5d5a745b37f32d65b564c7876348bf05` |
| `geomind/c1_reference.py` (unchanged since R002) | `e4d9439a69e65152cf04605f7aa7de0d878c2f27a530d5dc02ef148cac59279f` |
| `tests/test_c1.py` | `13a8696215923e1a212a02a6f1cec7b4c7dc759abee59c504827a9e5a65c8ad6` |

All 21 R004 inputs match the receipt, the live files and `evidence/c1_r004/source/`. All 160 gzip-compressed saved states hash, uncompressed, to their receipt hashes. All 12 accepted C0 inputs are byte-identical to the C0 receipt. Source commit: none (not a git repository). Environment: Python 3.9.6, NumPy 2.0.2, macOS arm64.

## Findings on R002, ranked by severity

### F1 — High: "fresh seeds" did not produce fresh worlds; the post-inspection redesign was evaluated on the same geometry (§5.2)

`generate_case` v2 fixed positions, edges, offsets and intervention endpoints by index; the seed only permuted node names and sampled queries. Mapped to position space, all **16/16** size/intervention cells are identical for the R001 seeds, the R002 seeds and an arbitrary seed. R002's frame initialization was designed after R001's 11 failures on these exact geometries. That invalidates "13/16" as held-out evidence, though not per-commit correctness. On seed-varied worlds, the queue resolves **0** contradictions: 0/12 in R003 and 0/20 in R004, including every 32-node world.

*Fix:* generator v3 (R003, kept in R004) draws grid widths, jitter, chord cycles, endpoints and the contradiction vector per seed. R004 uses five worlds per cell, and its manifest records the post-inspection registration.

### F2 — High: the headline commit count misattributes the work

**12 of 13** R002 commits made **zero** relaxation steps; the spanning-tree frame placement solved them exactly. The C1 queue resolved 1 of the 4 cases that needed relaxation. *Fix:* per-case relaxation steps and a receipt-level `committed_without_relaxation_step`. In R004 that count is 60/60 for the queue arm, reported plainly.

### F3 — Medium: ten identical certificate passes inflated dynamic cost tenfold

After the queue emptied, R002 recomputed the global certificate ten times on **unchanged** coordinates. That was 97.4–99.98% of the dynamic visits in no-relaxation commits; at 2,048 nodes, 39,410 of 39,417. It also saturated `touched_edges`, and the claim that "ten metered certificates" were needed is wrong. It changed no outcome. *Fix:* R003 used one global certificate. R004 uses a single **local** certificate over exactly the nodes whose force may have changed, with a soundness argument and an invariant check (below).

### F4 — Medium: no comparison with a fresh recompute (§6)

R002 recorded update and fresh-recompute times but never compared them; 13/13 commits were slower than a fresh recompute. *Fix:* R004 reports a per-case in-memory update / fresh recompute ratio, with persistence timed separately, under endpoints registered before execution.

### F5 — Medium: the focused checks missed defects they appear to cover

A mutation probe of R002's ten checks caught **7/15** defects. Survivors included uncharged certificate and warm-start visits, removal of one duplicate copy (the "duplicate removal" test removes a unique edge), and dropped evaluator energy and status gates. The custom-tolerance test never relaxed. *Fix:* R004's fourteen checks catch **18/23** R004 mutants. The five survivors are backup guards, each compensated by another tested guard (see `FOCUSED_CHECKS.md`).

### F6 — Medium-low: refused updates reported stale answers as coverage

Refused R002 cases recorded `query_coverage = 1.0` for prior-state answers; at 128 nodes, 20/60 of them were wrong for the new observation. *Fix:* coverage and accuracy are `None` for refusals, and prior-state answers are counted separately. Query semantics are unchanged: R4 requires the prior snapshot to keep answering. A stale-since-refusal marker is a C2 protocol decision.

### F7 — Low: possible livelock between local and global tolerance tests

Different summation orders could let a node be flagged globally yet skipped locally, burning the budget. *Fix:* certificate-flagged nodes take one forced step.

### F8 — Low: test-report provenance guards against staleness, not forgery

A hand-built JUnit file with the right properties passes `check_contract_report`. That is adequate for an honest workflow, but it is not proof of execution.

### Confirmed correct in R002

- Frame signs, reverse bridges, re-gauging and freed anchors.
- Isolated nodes and Counter multiplicity.
- Atomic commit and byte-identical rollback.
- Strict budget checks and nonfinite guards.
- Frozen/fork isolation and load-time step bound.
- Reference independence, and answers fixed before references.

A randomized chained differential test of 616 updates found no wrong commit and no broken rollback.

## Self-recheck of my own R003 repair (superseded)

- **S1 — High: R003's update was global by construction.** Every update took the full observation and re-ran `_prepare` (sort plus component DFS). It also rebuilt edge Counters, re-gauged every node, ran a global O(E) certificate, and serialized and hashed the whole snapshot twice. At 2,048 nodes that was about 0.26 s of preparation and 0.18 s of persistence around 1–3 ms of dynamics, so its H-L outcome was fixed by design.
- **S2 — Medium: an unfair comparison.** "0/36 faster than a fresh recompute" compared a transaction that included persistence with an in-memory recompute that did not.
- **S3 — Medium: gaps in scope.** There was no fallback arm for contradictions, although R4 permits a metered one. No endpoints were registered, so no H-L verdict was decidable. `touched_edges` was still saturated, states took 38 MB, and only three worlds were used per cell.

## R004: what changed and what it shows

**Design.**
- **State and input.** In-memory incremental state (adjacency; per-node canonical degree lists reproducing the C0 `bincount` degree bit for bit; component members; anchors; coordinates read relative to the component anchor). `apply` takes additive deltas, and every mutation is journaled and undone on refusal.
- **Operation cap.** One 100,000-operation cap per transaction covers every in-memory step.
- **Frame placement.** Frames are placed by a spanning tree of added edges, and only the smaller frames translate.
- **Dynamics and certificate.** The C0 residual law and step. A local certificate checks added-edge endpoints, new nodes, freed anchors, moved nodes and their neighbors, below tolerance × (1 − 1e-6). It is sound because a loaded state is fully C0-certified, rigid translations preserve old residuals, and alpha cannot grow.
- **Arms.** A queue-only arm, and a fallback arm that adds a separately capped (5M) warm-started CG solve on the affected components.
- **Persistence.** Export and load are global, timed separately, and validated by the accepted C0 code.
- **Pre-registration.** Endpoints and verdict rules were registered in the manifest before the panel, after R002/R003 inspection and one smoke test on non-panel seed 7. Panel seeds start at 10,000,000.

**Panel.** 80 interventions (4 sizes × 4 kinds × 5 seed-varied worlds) ran in 83.9 s, and all six gates PASS.

- **Queue arm.** 60/60 non-contradiction updates commit correctly, with maximum error `3.96e-11`. 20/20 contradictions are explicitly unresolved, with proven cap exhaustion and byte-identical rollback.
- **Fallback arm.** 80/80 commit correctly, with maximum error `6.29e-9` and energy gap ≤ `2.2e-16`.
- **Abstention, retention and determinism.** All 792/792 excluded cross-component pairs abstain in both arms. Retention, query immutability and exact reload pass everywhere, and the two arms produce byte-identical exports whenever no fallback ran.
- **Scaling, as medians over 5 worlds:**
  - Consistent-edge operations go from 27 at 32 nodes to 36 at 2,048; new-node operations from 24 to 30.
  - At 2,048 nodes, in-memory updates take 0.22–0.25 ms against a fresh recompute of 38–68 ms, ratios 0.004–0.009.
  - A bridge translates exactly the smaller component (512 nodes at 2,048) in 567 operations and 0.70 ms.
- **Contradictions.** The fallback alone needs 7.0–7.8× fewer operations than a fresh sparse-LS solve's edge visits. The fallback arm is still slower end to end (0.16 s median at 2,048 nodes against a 65 ms fresh recompute), because it first exhausts the 100k queue cap.
- **Registered H-L verdicts:**
  - consistent additive in-memory updates: **SUPPORTED_WITHIN_SCOPE**;
  - contradiction resolution by the local queue: **NOT_SUPPORTED** (rate 0.0 at ≥ 128 nodes);
  - durable persistence: global by design, not tested.
- **H-P** remains INCONCLUSIVE. Median frozen accuracy is 0.81 against 1.0 after either arm, but a store that includes the new constraints answers them by construction.

## Checks actually performed

1. Read R4 (§0–4 C0/C1, §5–7, the execution record), every R002 receipt, handoff, review and integrity file, the existing `ACCEPTANCE.md`, and all C1 sources and tests, plus `geometry.py` and `references.py`.
2. Identity checks on R002 (19 inputs, 48 states), R003 (20 inputs) and R004 (21 inputs, 160 gzipped states), plus confirmation that the accepted C0 inputs are unchanged.
3. `review_checks.py`, run once on R002 code (228.5 s):
   - seed isomorphism;
   - certificate share and cost comparison;
   - migration of 48 real R001/C0 artifacts;
   - probes;
   - a 616-update randomized differential test;
   - 20M-budget replays of the refused updates (128 nodes needs 2.16M visits; 512 and 2,048 nodes did not converge).
4. Mutation probes: R002, 7/15 caught; R003, 12/15; R004, 18/23. One earlier R004 run exposed two real gaps (an uncertified moved-node neighbor and unsorted degree lists). Both are now covered by tests; that run was discarded and the probe rerun on the final code.
5. R004 verification:
   - `tests/test_c1.py`: 14 PASS, recorded with source binding.
   - `tests/test_c0.py` and `tests/test_review_contracts.py`: 58 PASS (contract tests only; the C0 world experiment was not rerun).
   - A full scratch rehearsal of the panel, then the recorded 80-case panel.
   - Read-only re-verification of the receipt claims: state hashes, abstention totals, arm agreement and cost ratios.

Details are in `evidence/c1_claude_review/FOCUSED_CHECKS.md` and `evidence/c1_r004/HANDOFF.md`.

## Remaining practical and scientific limitations (R004)

- **Contradictions need a global solve.** The C0-step queue cannot resolve contradictions within 100k operations at any tested size, so the useful path for them is the fallback, which is global. A better local mechanism (exact coordinate minimization, or warm-started CG without first exhausting the queue) would be a new registered experiment.
- **Locality comes from frame placement and bookkeeping, not dynamics.** All 60 queue commits used zero relaxation steps. A comparably incremental *compiled* baseline would match them, so no superiority over compiled methods is claimed.
- **Persistence is global.** Export and load are O(V+E) per call. A durable per-update log would be needed for end-to-end locality with persistence.
- **Narrow panel.** One generator family, unit weights in the panel (weights, duplicates and tiny weights are covered only by focused checks), one added edge per intervention, and five worlds per cell with min/median/max spread but no confidence intervals.
- **Noisy timings.** Wall clock is single-run; one 32-node consistent update in the fallback arm measured 10× a fresh recompute through noise. The registered speed endpoint uses only 2,048 nodes, where every ratio was ≤ 0.02.
- **Refusals are visible only in the trace.** Queries keep answering from the prior snapshot, as R4 requires.
- **Tiny-weight contradictions** need the fallback arm.
- **Numerical edge case.** A committed state whose individual residual terms are finite but whose total energy overflows float64 would be refused only at export/load. That needs residuals above about 1e153 on many edges.
- **H-P** has no task-learning comparison.
- **R004 needs independent acceptance** from a reviewer other than its author.

## Precise next step (smallest meaningful verification batch for R004)

1. Run `.venv/bin/python -m pytest -q tests/test_c1.py --junitxml=<fresh dir>/contracts.xml`: 14 checks, about 5–10 s.
2. Read-only identity check of `evidence/c1_r004/` against the live sources, `source/` and the gunzipped states.
3. Review the local-certificate soundness argument in `geomind/incremental.py` against `_apply_structure` and `_relax`, since the H-L locality claim rests on it.
4. Optionally run `.venv/bin/python evidence/c1_claude_review/mutation_checks.py <scratch dir> --live`, about 8 minutes.
5. Reconcile `ACCEPTANCE.md` and this receipt in the R4 status table, then decide R004 acceptance.

Rerun the panel (about 85 s) only after a source change, and only into a fresh directory.
