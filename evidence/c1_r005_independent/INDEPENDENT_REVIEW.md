Verdict: **CHANGES_REQUIRED**.

# Independent review: GeoMind C1 R005 (`geomind-c1-r4-005`, commit 5f1047a)

Reviewer: a Claude agent that did not write R003, R004 or R005 and shares no conversation context with their author. Date: 2026-10-01. Everything this review wrote is under `evidence/c1_r005_independent/`. No source, test, manifest, standard, README or existing evidence file was modified. C0 was not run, C2 was not started, and nothing was committed.

Some working-tree changes predate this review and are not mine: the modified `.gitignore` and the untracked `.codex/`, `.githooks/`, `AGENTS.md`, `CLAUDE.md` and `tools/`.

The review was cut short by a coordinator time cap. The items not finished are listed under "Checks performed".

## Reviewed identities

| Item | SHA256 |
|---|---|
| `experiments/c1_manifest.json` (file bytes) | `e154c968df94c49d2a3ab00ba8165fbb29fc53ad3a344d5fa301e8c47c561e72` |
| R005 manifest canonical digest (receipt `manifest_hash`, equal to the live digest) | `2f0f1d59de649eb349884d28fc68ecf4f4e41a82f38cdc9a3c372b7f8713bcf4` |
| `evidence/c1_r005/results.json` | `fb13bed3dfc9b7a7a2ae205c1f16fe6f656ed4e0aeb6b00ad9f4a845be90635a` |
| `geomind/incremental.py` | `84ad79a62ec6b0b9831615bc7f5ad6eefd2ef00fd1313d8073f9172cca36a23a` |
| `geomind/run_c1.py` | `1065d44969e0228de627397a55d1b2d97f120fdb0c07ed40a29784f8f5f7f17e` |
| `geomind/c1_reference.py` | `1f853a205d18a26b7c9e544d8c3dd04980096ac56ced259672e40486a3c14df4` |
| `geomind/c1_cases.py` | `56f080e4e06eecdcfcc2910250003d9b5d5a745b37f32d65b564c7876348bf05` |
| `tests/test_c1.py` | `2ee715bcfa6af5da2647df43bf50a4838fee867c60717c56314a947668f0cb16` |
| `geomind/geometry.py` (accepted C0, unchanged) | `973740d321705d9c8633a6cd2da1696af91cec930e53bcb6b6b4831e280066f0` |
| `geomind/references.py` (accepted C0, unchanged) | `771f9b355083240fa2bf1a5e713bb1f964f9fd493d7e485aa2d4ba1f5e5255f9` |
| `evidence/c1_r005/contracts.xml` (equal to the receipt) | `9bc987eb780e5497a92d5618594a188817e1acddd19c674e6ce9f7c22c0ef453` |
| This review's `contracts.xml` | `26304359514e51fa5787e1be83a41aae99e3d570a429911be6c816b4a1ee33ec` |

## Summary

R005 genuinely repairs the R004 findings. Under directed and randomized probing:
- The export-gauge invariant held.
- The local certificate held.
- Rollback held.
- I found no hidden O(V), O(E) or O(R) work.

The panel reruns byte-identically, and the evidence identity is intact.

One new defect blocks acceptance, though it is small:
- **N1:** `apply` commits **PASS** on numeric inputs that pass `finite_number` but are not JSON-serializable (numpy `float32`/`int64` offsets or weights). `export()` then raises `TypeError` forever after. That is a committed state that cannot be persisted.
- The accepted C0 learner refuses the same observation with INVALID_STATE, because it serializes its proposal before committing (`geometry.py:230`).
- It is the same class of defect as R004's F3, which the previous review treated as blocking.

The fix is a few lines. Everything else I found is non-blocking.

## R004 findings: are they fixed?

| R004 finding | Status in R005 | Evidence |
|---|---|---|
| F1 (High): uncharged Θ(R) relation-map copy | **Fixed** | `_validate_delta` (`incremental.py:413-447`) now reads only the delta and looks stored relations up by key. Rerun of `probe_hidden_work.py`: apply takes 134 / 119 / 155 / 161 / 175 µs at 32 / 512 / 2,048 / 8,192 / 32,768 nodes. The no-copy variant gives 122 to 140 µs. My deterministic probe W1 counts Python line events inside `apply` (all frames in `incremental.py`): **540, 540, 580, 639, 580** at 32 to 32,768 nodes, tracking charged operations (30, 30, 36, 45, 36). Builtin C calls are 171 to 186, with no state-sized container constructor. A code audit of `apply`, `_apply_structure`, `_relax` and `_certify` found no uncharged step proportional to V, E or R. Every container built is delta-, frame- or certificate-sized, and each of those is charged. The wall-clock endpoint was registered and passes (time ratio 1.73 in the receipt, 1.84 in my rerun; ≤ 4 required) |
| F2 (High): certificate unsound in the export gauge | **Fixed** | Coordinates are stored with anchors at exactly 0.0, and `export` writes them unchanged (`:345-365`). The residual expression has the same operations and order as C0 `_gradient`, so the residual bits are identical. I checked the soundness argument in the docstring (`:20-34`) against the code and found it complete. A node's C0 force, its normalized force or its alpha check can change only through (i) an added incident edge (endpoints are in `dirty`), (ii) a written endpoint coordinate (translated or re-gauged members are certified at `:663`, relaxed nodes and *all* their neighbours at `:703-709`, and fallback components in full at `:822`), or (iii) losing anchor status (freed anchors are in `dirty`). Alpha only shrinks. The bound `4(n+2)·eps·Σ|w·r| + 8·eps·|f|` exceeds the two-sided sequential-summation error (about `(n+½)·eps·Σ`) plus the norm rounding. The anchor choice (`:584-590`) equals the C0 rule, because only endpoint degrees change. Probes (P1–P5 rerun, all reloaded through `IncrementalGeometry.load`, with in-memory answers equal to reloaded answers exactly): P2 and P4 (8 cases) all reload. P5 at scale 1e3–1e6 gives 1,338 PASS and **0 reload rejections**, and 0–1e2 gives 1,416 PASS and 0 rejections, both with 0 query/export mismatches and 0 errors above 1e-5. P1 commits and reloads up to a 1e8 shift and refuses explicitly at 1e9 and 1e10 |
| F3 (Medium): degree overflow committed | **Fixed** | `:547-548`. P3 returns INVALID_STATE, matching C0 `learn` |
| F4 (wording): verdict scope | **Fixed**, with one new disclosure gap (N2) | The verdicts are split, bridges are NOT_TESTED for size independence, and `hypothesis_limits` states that locality comes from frame placement, not dynamics. The incremental compiled baseline is measured |
| F5 (wording): mixed-unit fallback ratio | **Fixed** | The ratio was removed. The README states that the units differ (`run_c1.py:463`) |
| F6 (Low): refused rows in accuracy medians | **Fixed for the medians** | `frozen_vs_adaptive` now uses committed rows only (`run_c1.py:439-441`). The per-row field `post_transaction_total_accuracy` still mixes prior-state answers on refusals, but it no longer feeds an aggregate |
| F7 (Low): oversized invalid delta returned NOT_CONVERGED | **Fixed** | Validation runs before charging (`:464-465`). Focused test at `test_c1.py:465-467` |

## New findings, ranked by severity

### N1 — Medium (blocking, small): non-JSON numeric inputs commit PASS and leave an unexportable state

**Evidence.** `probe_numeric_types.py` (output `probe_numeric_types.out.jsonl`) starts from a C0-valid 3-node saved state:

| Delta | `apply` | `export()` | C0 `learn` on the same observation |
|---|---|---|---|
| offset `(np.float32(1), np.float32(1))` | **PASS** | `TypeError: Object of type float32 is not JSON serializable` | INVALID_STATE |
| weight `np.int64(2)` | **PASS** | `TypeError` (int64) | INVALID_STATE |
| new node, offset `np.int64` | **PASS** | `TypeError` (int64) | INVALID_STATE |
| `np.float64` (a `float` subclass; control) | PASS | OK, reload OK | PASS |

The compatibility path `update()` also returns PASS.

**Cause.**
- `finite_number` accepts any `numbers.Real`.
- `_validate_delta` (`incremental.py:436-439`, and the relation vectors at `:424`) never checks that the records serialize.
- The committed `Constraint` objects keep the numpy scalars, and `export` calls `canonical(asdict(e))`.

C0's accepted contract avoids this by calling `canonical(proposal)` before committing (`geometry.py:230`). This violates §3 ("committed only after … checks"; failed updates must not leave an unusable snapshot). It also breaks the manifest's claim that export and load produce the canonical C0 snapshot for every committed state.

The panel itself is unaffected. The generator yields Python or `np.float64` values, and all 143 panel commits exported and reloaded.

**Fix.** In `_validate_delta`, add a delta-sized serialization check that mirrors C0. Either:
- call `canonical([asdict(e) for e in added_edges] + [[n, list(v)] for n, v in added_relations])`, which makes `TypeError` lead to INVALID_STATE before any mutation; or
- require `type(v) in (int, float)` for offsets, weights and relation vectors.

Charge it as part of the existing `input_records`.

**Smallest verification batch.**
1. Add the four rows above as a focused test. Expect INVALID_STATE, a byte-identical export, and the `np.float64` control still PASS.
2. Rerun `pytest tests/test_c1.py`.
3. Because the source hash changes, rerun the panel into a fresh directory under a new experiment ID. Its outcomes should be byte-identical, since panel inputs are never numpy non-float scalars.

### N2 — Low (non-blocking, wording): the O(component) re-anchoring tail of "local" updates is not disclosed where the verdict is stated

**Evidence.** The export-gauge design re-stores a whole component whenever the C0 max-degree anchor moves (`incremental.py:599-612`). This work is charged correctly. Probe W2 (`logs/probe_work_and_reanchor.log`) uses fresh seeds disjoint from every panel:

| Kind | Nodes | Re-gauged fraction | Median / mean / max operations |
|---|---:|---:|---|
| Consistent edge | 32 | 0.325 | 30 / 46.5 / 91 |
| Consistent edge | 128 | 0.19 | 33 / 88.2 / 327 |
| Consistent edge | 512 | 0.065 | 36 / 117.6 / 1,304 |
| Consistent edge | 2,048 | 0.025 | 36 / 166.9 / 5,255 |
| Consistent edge | 8,192 | 0.0 (of 40) | 36 / 37.4 / 45 |
| New node | 32 | 0.225 | 27 / 39.2 / 90 |
| New node | 128 | 0.115 | 30 / 62.4 / 326 |
| New node | 512 | 0.03 | 30 / 67.6 / 1,300 |

The registered rule uses medians and is applied correctly. The verdict text in the README, the receipt and the standard's execution record does not say that:
- any update that moves the anchor costs O(component);
- the mean cost at 2,048 nodes is about 3.6× the 32-node mean in this sample;
- an adversarial stream (two hubs alternately overtaking each other) makes every update O(component).

The HANDOFF counts re-anchored worlds but does not state this consequence.

**Fix.** Add one sentence to `hypothesis_limits`, the HANDOFF and the standard's R005 record: "consistent-edge/new-node locality is a median property; an update that moves the C0 anchor re-stores its component (charged, O(component)); worst case is O(component) per update."

### N3 — Low (non-blocking): the baseline speed claim is single-shot and the duties are unmatched

The "7–13×" figure is computed correctly from the receipt medians at 2,048 nodes: 13.1× for consistent edges, 10.2× for new nodes and 7.6× for bridges. My rerun gives **17.9×, 12.2× and 15.2×**, and per-world ratios range from 7.5× to 46×.

The baseline's timed `apply` does no input validation, degree upkeep, C0-gauge maintenance or certificate. Those are duties the candidate needs for persistence compatibility. The direction is therefore robust (the baseline is an order of magnitude faster), but the exact range is not.

The "matched-baseline stop signal" statement is fair and conservative in substance. It is scoped to additive kinds, and the HANDOFF correctly says the baseline cannot represent contradictions. However, the baseline comparison is "reported, not a gate" (`run_c1.py:310`), so "on the registered quality/cost criteria" (HANDOFF) overstates its status. Say "on the reported cost measures".

### N4 — Trivial (non-blocking)

- `results.json` `next_action` still says "Independent C1 review of R004 before C2" (`run_c1.py:444`).
- `probe_rollback.py`'s field list omits `_energy_bound`. By reading, that field is assigned only on PASS (`:484`), so rollback cannot change it.

## Confirmed correct

- **Evaluator independence and ordering.** `c1_reference.py` imports only `Answer` and `finite_number` from C0. Both arms and the baseline answer before `SparseLeastSquares` and `CompiledCoordinates` are built (`run_c1.py:229-241`).
- **Gates.** A commit needs status equality, every error ≤ 1e-5 and an energy gap ≤ 1e-8. A refusal needs a byte-identical export and a proven cap exhaustion. Reload equality is exact. The negative controls in `test_evaluator_negative_controls_two_arms_and_stale_coverage` pass.
- **Baseline correctness.** The baseline is gated on its own correctness (`run_c1.py:254-258`). It is fed the same delta and queries, and its untimed construction mirrors the candidate's untimed `from_saved`.
- **Endpoints.** `evaluate_endpoints` implements `endpoint_rules` as written: commits in every world at 32 and 2,048 nodes, an operations ratio ≤ 2, a time ratio ≤ 4, every 2,048-node speed ratio < 1, and the contradiction rate thresholds.
- **Rollback.** `probe_rollback.py` deep-compared 22 internal structures after 1,250 refusals at caps 0 to 99,999, including 5-frame merges, contradictions, duplicates and anchor lifts. It found **0 differences**, and every replay matched a fresh fork. Reading the journal confirms these are undone in order: partial edge inserts (the journal entry precedes the fallible steps), merges, anchor reassignment, new-node pops after unmerge, and fallback writes through `tx.move`.
- **Degrees and anchors.** 1,000/1,000 bit-exact degree checks and 0 anchor mismatches (`probe_degree_and_units`).
- **Evidence identity** (`identity_check.py` → `identity_check.out.json`):
  - all 22 `file_hashes` equal the live files and `source/`;
  - `instances.jsonl` equals the receipt;
  - all 223 state hashes match across 160 gzip files, with identical fallback exports written once;
  - the 12 accepted C0 inputs are unchanged, and the C0 receipt hash matches `ACCEPTANCE.md`;
  - `contracts.xml` is bound to the exact `file_hashes`, with 19/19 passing, and its hash equals the receipt's.
- **Panel reproducibility.** My rerun into `panel/` passes all six gates in 57.8 s. All 160 arm artifact hashes, every operation count, every status and every baseline count are identical to the receipt (`compare_panel.out.json`). The verdicts are identical too.
- **Claims checked against the receipt.**
  - Accurate as stated: 63/17 queue, 80/80 fallback (17 via CG), 60 without relaxation, 3/5 at 32 nodes (68,584–98,106 operations), 0/15 at ≥ 128, maximum error 6.06e-8, re-gauge counts 3/3/4/1, 2,048-node speed ratios ≤ 0.006, and bridges 0.034–0.27.
  - Approximately right: "apply flat to 32,768" (134 to 175 µs in my rerun).

## Checks performed

| Check | Result | Time |
|---|---|---|
| `pytest -q tests/test_c1.py --junitxml=evidence/c1_r005_independent/contracts.xml` | 19 passed | 7.2 s |
| `identity_check.py` | all match | < 2 s |
| Panel rerun → `panel/` (`logs/panel_rerun.log`), then `compare_panel.py` | 6/6 gates PASS; byte-identical | 58 s |
| `probe_certificate.py` (P1–P3) | all reload or refuse explicitly; P3 gives INVALID_STATE | 1.4 s |
| `probe_regauge_and_random.py 300 3,6` and `300 0,2` (P4, P5) | 0 reload rejections in 2,754 PASS commits | 36 s and 37 s |
| `probe_rollback.py` | 0 differences in 1,250 refusals | 15 s |
| `probe_degree_and_units.py` | 0 degree or anchor mismatches | 4 s |
| `probe_hidden_work.py` | flat to 32,768 nodes | 122 s |
| `probe_numeric_types.py` (N1) | 3 PASS commits that cannot be exported | 1 s |
| `probe_work_and_reanchor.py` W1 and W2 | W1: flat line counts. W2: see N2 | stopped at about 11 min |

**Problems and incomplete items:**
- **Large-scale P5 (1e6–1e8): NOT_RUN.** `probe_regauge_and_random.py 300 6,8` spent more than 8 minutes in 5M-operation CG fallbacks on tiny graphs, and I stopped it. Note in `logs/probe_regauge_6-8.log`.
- **W2 for new nodes at 2,048 and 8,192: NOT_RUN.** Stopped at the time cap.
- **My own wider adversarial chain probe: NOT_RUN.** It would have covered re-anchoring without a merge, 3+-frame merges with the anchor in a non-largest frame, tiny and huge weights, and the exact check that every changed force was certified. These cases are covered only by the rerun probes above, the author's focused tests (`test_c1.py:312-442`, which pass) and my reading of the code.
- **Mutation probe: NOT_RUN.**
- **Timing overlap.** `probe_numeric_types.py` ran during the tail of the panel rerun, so the rerun's 2,048-node bridge timings may be slightly inflated. Its deterministic outputs are unaffected.

## Hypothesis verdicts

- **H-L, consistent-edge and new-node in-memory updates: SUPPORTED_WITHIN_SCOPE is justified by the registered (median) rule.**
  - The operation and wall-clock meters are now honest (F1 fixed, W1 flat).
  - The scope must also state the O(component) re-anchoring tail (N2).
  - The locality comes from compiled frame bookkeeping, not from the residual dynamics, as `hypothesis_limits` says.
- **Bridges: NOT_TESTED for size independence is honest.** The faster-than-recompute endpoint is met.
- **Contradiction resolution by the local queue: NOT_SUPPORTED is justified** (0/15 at ≥ 128 nodes).
- **Durable persistence: NOT_TESTED is honest.** N1 shows one input class where persistence fails after a PASS.
- **H-P: INCONCLUSIVE is acceptable.** NOT_TESTED would be more precise, since no task learning was run.
- **Stop signal.** It is a fair, author-unfavourable reading for additive kinds. See N3 for its wording.

## Remaining limitations

- One generator family with unit weights in the panel.
- Single-shot timings that vary between runs by up to 2×.
- My probes are searches, not proofs; coordinates of 1e6–1e8 were probed only by P1.
- The fallback is not shown to beat a fresh recompute.

## Independence statement

This reviewer is the same model family as R005's author and may share blind spots. It had no access to the author's conversation context. It read `CLAUDE_ACCEPTANCE.md` and `FOCUSED_CHECKS.md` for context only. Every number above comes from commands run in this review, and the scripts, outputs and logs are in this directory. Implementation acceptance is decided separately from the hypothesis verdicts. No numeric score is given.
