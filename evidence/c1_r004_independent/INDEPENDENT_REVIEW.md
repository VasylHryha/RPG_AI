Verdict: **CHANGES_REQUIRED**.

# Independent review: GeoMind C1 R004 (`geomind-c1-r4-004`)

Reviewer: a Claude agent that did not write R002, R003 or R004 and shares no conversation context with their author. Date: 2026-10-01. Everything this review wrote is under `evidence/c1_r004_independent/`. No source, test, manifest, standard, README or existing evidence file was modified. C0 was not run, C2 was not started, and nothing was committed. (The untracked files `evidence/c1_review/RECONCILIATION.md` and `.idea/*` predate this review and are not mine.)

## Reviewed identities

| Item | SHA256 |
|---|---|
| `experiments/c1_manifest.json` (file bytes) | `6959cc6886fe59ff73203c3099baaf67566480eac8ee1083011cfd2b6b860754` |
| R004 manifest canonical digest (`manifest_hash` in the receipt, equal to the live digest) | `80b987dea7e6955542a9104939504468048b5ebb4e2bd597549c96cc616ee40b` |
| `evidence/c1_r004/results.json` | `d769208dabe696f3f7e0ef9e4d17edcf652b12a33bc42a816239254b4ea44361` |
| `geomind/incremental.py` | `093159523e7abdbd8c6a1be64039bc20241a9a447adfd6c41a2452516cb2b06b` |
| `geomind/run_c1.py` | `ce9f93dffa5490c7c66ae9761bf7633ab8f9869fd15fdfdc8dc5f6e3e8d17ddc` |
| `geomind/c1_cases.py` | `56f080e4e06eecdcfcc2910250003d9b5d5a745b37f32d65b564c7876348bf05` |
| `geomind/c1_reference.py` | `e4d9439a69e65152cf04605f7aa7de0d878c2f27a530d5dc02ef148cac59279f` |
| `tests/test_c1.py` | `13a8696215923e1a212a02a6f1cec7b4c7dc759abee59c504827a9e5a65c8ad6` |
| `geomind/geometry.py` (accepted C0) | `973740d321705d9c8633a6cd2da1696af91cec930e53bcb6b6b4831e280066f0` |
| `geomind/references.py` (accepted C0) | `771f9b355083240fa2bf1a5e713bb1f964f9fd493d7e485aa2d4ba1f5e5255f9` |
| `evidence/c1_r004/contracts.xml` | `a0b636a961be50f3f1b5e6ed1d0268b7269589e9b4ab42554ce47a9cf52a2ed2` |

## Summary

The R004 evidence is genuine and reproducible:
- Identities, states and the contract binding all check out.
- The panel reruns byte-identically.
- Rollback, bit-exact degree upkeep, query/export consistency and evaluator independence held under adversarial probing.

Two defects violate the C1 contract the receipt claims to meet, so I cannot accept it:
- **F1:** an uncharged O(R) step runs inside every "local" in-memory update. It is the dominant cost at the panel's largest size, and the locality endpoint is measured on a meter that omits it.
- **F2:** the local certificate is not sound for the snapshot it commits. I produced PASS commits, from candidate-generated states alone, that the accepted C0 validator rejects on reload. The code comments, docstring and HANDOFF say this cannot happen.

**F3** (weighted-degree overflow commits a state that C0 calls INVALID_STATE) is a smaller instance of the same "commit that cannot be persisted" problem.

Several claim-wording issues (F4, F5) also need correcting. None of the 80 committed panel answers is wrong: every panel export reloaded and matched the reference.

## Findings, ranked by severity

### F1 — High (blocking): uncharged Θ(R) work in every `apply`; the locality meter omits the dominant step

**Evidence.**
- `geomind/incremental.py:372` runs `catalog = dict(self._relation_map)` on every transaction. The generator gives almost every edge its own relation, because jittered offsets are all distinct. R therefore tracks E: 47 relations for 47 edges at 32 nodes, 4,177 for 4,177 at 2,048.
- The copy is not charged to any `TRACE_COUNTERS` category. That contradicts the manifest's `budget_scope` ("every in-memory step") and the HANDOFF's "One 100,000-operation cap covers every in-memory step".
- The panel receipt shows the growth. Median queue-arm `validation_seconds` for consistent edges is 34 / 65 / 87 / 141 µs at 32 / 128 / 512 / 2,048 nodes, while charged operations are 27 / 36 / 36 / 36.

`probe_hidden_work.py` (output `probe_hidden_work.out.jsonl`, 113 s) measured the shipped code against a variant that overlays the delta's relations instead of copying the map. The variant is monkeypatched in the probe only.

| Nodes | Relations | Charged ops | Apply as shipped (validation) | Apply, no-copy variant (validation) |
|---:|---:|---:|---:|---:|
| 32 | 46 | 30 | 66 µs (20) | 57 µs (12) |
| 2,048 | 4,182 | 39 | 275 µs (192) | 119 µs (35) |
| 8,192 | 17,052 | 36 | 691 µs (606) | 133 µs (40) |
| 32,768 | 68,925 | 36 | 2,644 µs (2,542) | 133 µs (41) |

As shipped, a consistent-edge update is linear in the number of stored relations, which here is linear in E, while its meter reports a constant. At the panel's 2,048 nodes the copy is about 70% of apply time.

The registered locality endpoint compares charged operations (ratios 1.33 and 1.25), so it passed on a meter that misses this step. This is the "hidden global work" the standard tells reviewers to look for. It is a missing cost charge, and it leaves the H-L SUPPORTED_WITHIN_SCOPE verdict unestablished by the current evidence.

**Fix.** In `_validate_delta`, check new relation names against `self._relation_map` plus a small dict of the delta's own relations, as the probe variant does. Do not copy the stored map. Then audit `apply` for any other step proportional to state size, and either charge it or remove it.

**Smallest verification.**
1. Add a focused test that fails if validation reads stored relations in proportion to R. For example, wrap `_relation_map` in a counting mapping, or assert that `validation_seconds` and charged operations stay flat between a 32-relation and a 30,000-relation state.
2. Rerun `pytest tests/test_c1.py` and the registered panel into a fresh directory under a new experiment ID.
3. Recompute the H-L endpoints.

The no-copy variant suggests the verdict will probably survive, but it has to be measured on the fixed code.

### F2 — High (blocking): the local certificate is not sound for the committed snapshot; PASS commits can fail the accepted C0 validator

Three claims are at issue:
- `incremental.py:13-19`: "Rigid frame translations preserve every old residual … The certificate therefore checks exactly … moved nodes and neighbors of moved nodes."
- `incremental.py:34-35`: "Certified forces stay below tolerance by this factor, so summation-order differences from the C0 validator cannot make a commit fail on reload."
- HANDOFF line 14: "It checks every node whose force may have changed: … moved nodes and their neighbors."

The HANDOFF also says the H-L locality claim rests on this argument. Three distinct holes, each reproduced:

- **(a) Translated nodes are never certified** (`probe_certificate.py`, P2).
  - `tx.dirty` (`:563`) holds endpoints, new nodes and freed anchors. Translated members are moved by `tx.move` at `:536` and counted in `moved_nodes`, but they are never added to `certify`.
  - Floating-point translation does not preserve residuals exactly.
  - Reproduction: a C0-valid saved state has a free node `r` with force 0.9999e-8. A bridge then translates `r`'s frame by about 1e5.
  - Result: `apply` returns PASS. `r`'s in-memory force is **1.0000076e-8 ≥ 1e-8**, and `r` is not in `_last_certified`. `IncrementalGeometry.load(export())` raises "Persisted coordinates are not an equilibrium". The accepted C0 learner returns PASS on the same full observation.
- **(b) Anchor reassignment re-gauges the whole component at export** (`probe_regauge_and_random.py`, P4).
  - Internal coordinates are absolute (`:256`), but `export` writes `x − x_anchor` (`:313`).
  - When the anchor moves to a node with large |x|, every residual in the component is re-rounded, including those of uncertified nodes.
  - Nothing in the old frame translates. Three new leaves on `p` (|x_p| = 1e5) make `p` the anchor.
  - Result: PASS, with the uncertified near-tolerance node `r` rejected on reload, for gaps of 1e-12 and 1e-13 below the tolerance.
- **(c) The 1e-6 relative margin (1e-14 absolute) does not cover re-gauge rounding, even for certified nodes** (P5).
  - Method: randomized chains using only candidate-produced states (no hand-edited artifacts), mixing queue relaxation, fallback, merges, duplicates and new nodes. Each chain continues in memory, and every PASS export is reloaded.
  - **Coordinate scale 10^3–10^6:** 1,324 PASS commits, of which **11 were rejected by the C0 validator on reload**. In all 11, the failing nodes were *certified* and *under* tolerance in memory, and failed only in the export gauge. Six of the 11 had an anchor change and five did not; seven involved a translation, including one rejection with neither.
  - **Scale 10^2–10^3:** 0 of 1,416 rejected.
  - **Scale 1–10^4:** 0 of 715 rejected.
  - The author's mutation probe records that the margin mutant survives because it is "compensated by another tested guard". The probe above shows the margin is itself insufficient, not redundant.

**Impact.** In-memory answers stay within 1e-5, so no panel answer is wrong. The panel's coordinates (about 450 or less) are below the observed failure scale, and all 80 panel exports reloaded.

Nevertheless, `apply` reports PASS (converged and committed) for a state that the accepted rules call non-equilibrium, and that cannot be exported and reloaded. That breaks §3 ("committed only after … convergence checks"), the in-memory = after-reload contract, and the stated soundness argument. Map coordinates around 1e3–1e5 are not exotic.

**Fix.** All three parts are needed:
1. Add every translated member to the certificate. This is local: O(Σ degree) over the smaller frame, the same order as the `translation_writes` already charged. Charge it.
2. Compute certificate residuals in the export gauge, mirroring `export` and `_gradient` exactly: `c_i = x_i − x_anchor(i)` and `r = (c_t − c_s) − d`. Use a margin that bounds only summation-order differences.
3. When the anchor of a component changes and `x_new_anchor ≠ x_old_anchor`, do one of two things:
   - re-certify that component in the new gauge, charged and reported as O(component) work that is non-local for that update; or
   - re-store the component's coordinates relative to the new anchor (also O(component), charged) and certify the rounding-affected nodes.

   Correct the docstring, the comment at `:34-35`, the manifest's `certificate` text and HANDOFF line 14 to state the exact argument, including floating-point effects.

**Smallest verification.**
1. Add focused tests reproducing P2, P4 and one seeded large-scale chain from P5. Each must end in either a reloadable commit or an explicit refusal.
2. Rerun `pytest tests/test_c1.py`.
3. Rerun `probe_certificate.py` and `probe_regauge_and_random.py 300 3,6`; the expected `RELOAD_REJECTED` count is 0.
4. Rerun the panel into a fresh directory together with F1, and report how many consistent-edge updates now trigger an O(component) re-gauge.

### F3 — Medium (blocking, small): weighted-degree overflow commits a state C0 rejects as INVALID_STATE

**Evidence.** `incremental.py:489` updates degrees without checking that they are finite. Probe P3: a saved state has edge `a→b` with weight 1e308. Adding a consistent duplicate makes the degree of `a` infinite, but the residuals are zero, so the certificate passes, since `magnitude/inf = 0` and `alpha = 0`.
- Result: `apply` returns **PASS**.
- Reload fails with "Weighted degree overflow".
- The accepted C0 `learn` returns INVALID_STATE on the same observation.

The existing overflow test covers only offset overflow (`test_custom_update_tolerance_and_overflow_are_transactional`).

**Fix.** After the degree update, raise `ValueError("Weighted degree overflow")` if either degree is non-finite, which leads to INVALID_STATE and rollback. Add P3 as a focused test.

### F4 — Medium (claim wording; must be corrected): the H-L "SUPPORTED_WITHIN_SCOPE" statement is broader than its evidence

1. **Bridges.** The verdict label "consistent additive in-memory updates" includes bridges. Bridges are not in the locality endpoint (`locality_kinds` is consistent_edge and new_node only), and their cost scales with the smaller component: median operations 48 → 567 and apply time 0.11 → 0.70 ms from 32 to 2,048 nodes. That is the correct behaviour (§4 C1 says a bridge may need global change), but the label implies bridges were shown to be local. Rename the verdict to "consistent-edge and new-node in-memory updates", and report bridges separately as O(smaller component).
2. **Where the locality comes from.** All 60 queue commits made zero relaxation steps. The locality comes from rigid frame placement with union-by-size translation, which is the incremental form of the compiled-coordinate baseline, not from the residual-law dynamics. `results.json` (`hypothesis_limits`, `checks_not_run`) discloses that there is no incremental compiled baseline and no superiority claim. The HANDOFF and the standard's execution record (line 507) state the verdict without either caveat. Add both sentences there.
3. **Timing variance.** Speed ratios are single-shot `perf_counter` timings. In my rerun one 2,048-node bridge world reached 0.062, against the HANDOFF's "every 2,048-node speed ratio < 0.02". The registered rule (< 1) is met by a wide margin, but the "< 0.02" sentence describes one run and should say so or give a range across runs.

### F5 — Medium (claim wording): "fallback uses 7.0–7.8× fewer operations than a fresh sparse-LS solve" mixes units, scope and tolerance

**Evidence.**
- `c1_reference.py:48,55` counts edges once per matrix product, and runs two separate scalar CGs (one per axis) over all three components. At 512 nodes: 128 iterations per axis, 260,478 visits, equal to 261 × E (`probe_degree_and_units.out.json`).
- The fallback counts each edge once per product for both axes together. It works only on the affected component (roughly half the edges), to a tolerance of about 2.5e-9 instead of 1e-11.
- Like for like, that is about 70 warm-started iterations against 128 cold ones, roughly 2× and not 7×.

The HANDOFF (line 37) and the standard (line 505) correctly add that the arm is slower end to end. **Fix:** restate the comparison in matched units, scope and tolerance, or drop the ratio.

### F6 — Low (non-blocking): `post_transaction_total_accuracy` includes prior-state answers on refused rows

On refused rows it counts prior-state answers that happen to be within tolerance; the values are 0.54–0.59 on queue refusals. The field is not labelled coverage (`update_coverage` is correctly `None`), and it feeds only the `frozen_vs_adaptive` medians, which are dominated by commits. Consider setting it to `None` on refusal or renaming it.

### F7 — Low (non-blocking): invalid oversized deltas refuse as NOT_CONVERGED

`apply` charges `input_records` before `_validate_delta` (`:411-412`). An invalid delta larger than the cap therefore refuses as NOT_CONVERGED instead of INVALID_STATE. Rollback is still correct. This finding comes from reading the code; I did not run a probe for it.

## Confirmed correct (with evidence)

- **Spec conformance (§4 C1).** The four additive interventions run at 32 / 128 / 512 / 2,048 nodes from saved C0 states, five seed-varied worlds per cell (seeds from 10,000,000). The residual law and step (`0.25/max(1, max weighted degree)`) match C0. Queue rounds run in stable ID order. The cap is 100,000. Cap exhaustion returns NOT_CONVERGED with byte-identical rollback. The fallback is a distinct arm with its own 5M cap, and fallback commits are never counted as queue successes. Answers are compared with fresh sparse LS (qualified against dense LS) and with compiled coordinates. Retention uses the untouched third component, with exact equality. "Potentially affected" pairs are graded against the reference.
- **Frame placement.** Signs and shifts are correct: `shift_b − shift_a = d − (x_t − x_s)` (`:501-504`, `:527`). 3+-frame merges, duplicates and new isolated nodes passed 3,455 randomized PASS commits against `LeastSquares`, with maximum error 2.25e-7 (all within 1e-5) and 0 status mismatches.
- **Anchor and gauge.** The candidate set (previous anchors, endpoints, new nodes) is sufficient because only endpoint degrees change. The tie-break matches C0 `_prepare`. Live anchors equalled `_prepare` anchors in 1,000/1,000 checks.
- **Bit-exact degree upkeep.** 1,000/1,000 live checks, without reload, using non-associative weights (0.1, 0.2, 0.3, 1/3, …), duplicates and isolated nodes: 0 mismatches.
- **Rollback.** `probe_rollback.py` (22 s) swept the queue cap from 0 to 3,000 plus 99,999, with fallback caps {0, 1, 50, 500}, over a 5-frame merge + contradiction + duplicate delta and a consistent merge-only delta. It deep-compared all 24 internal structures after 1,247 refusals: **0 differences**. Replaying the delta on a rolled-back state always matched a fresh fork.
- **Query/export consistency.** In-memory answers equalled export→load answers exactly in every P5 commit (0 mismatches). The arithmetic is identical by construction (`:284-285` against `:313`).
- **Fallback CG.** The Laplacian sign matches the C0 gradient, the anchor row is pinned, and it restarts on the true gradient. All operations are charged to the fallback meter.
- **Evaluator.** `c1_reference.py` imports only `Answer`/`finite_number` from accepted C0 code. Both arms answer before the references are built (`run_c1.py:229-232`). `correct_commit` requires status equality, all errors ≤ 1e-5 and an energy gap ≤ 1e-8 over all updated edges. Rejection requires byte-identical export and a proven cap exhaustion. Refused rows have `update_coverage = None`. The negative controls in `test_evaluator_negative_controls_two_arms_and_stale_coverage` pass. 792/792 excluded cross pairs abstain in both arms.
- **Evidence identity** (`identity_check.py`):
  - all 21 `file_hashes` equal the live files and `source/`;
  - `instances.jsonl` equals `results.json` `instances`;
  - all 220 state hashes match (160 gzip files; identical fallback exports are written once);
  - the 12 accepted C0 inputs are unchanged, and the C0 `results.json` hash matches `ACCEPTANCE.md`;
  - `contracts.xml` is bound to the exact `file_hashes`, with 14/14 passing and its hash equal to the receipt's.
- **Panel reproducibility.** My rerun passed all 6 gates in 117.5 s, with 160/160 arm artifact hashes and operation counts identical to the receipt.

## Checks actually performed

| Check | Result | Time |
|---|---|---|
| `pytest -q tests/test_c1.py --junitxml=evidence/c1_r004_independent/contracts.xml` | 14 passed | 8.11 s |
| `identity_check.py` (→ `identity_check.out.json`) | all match | < 2 s |
| `probe_certificate.py` (P1 large shifts, P2 near-tolerance translation, P3 degree overflow) | P2 and P3 reproduce F2(a) and F3; P1 is safe (large shifts either reload or refuse) | 2.2 s |
| `probe_regauge_and_random.py` (P4 re-anchor; P5 candidate-only chains at three scale ranges) | P4 reproduces F2(b); P5 found 11 reload rejections at 10^3–10^6 and 0 at smaller scales | 28 s, 51 s, 48 s |
| `probe_hidden_work.py` | F1 confirmed up to 32,768 nodes | 113 s |
| `probe_rollback.py` | 0 rollback differences in 1,247 refusals | 22 s |
| `probe_degree_and_units.py` | degrees and anchors exact; reference visit units confirmed (F5) | 9 s |
| Panel rerun → `panel/` (log in `panel_logs/panel_rerun.log`) | all gates PASS, byte-identical artifacts | 117.5 s |

**Problems I hit and how I resolved them:**
- My first identity script listed fallback "after" states as missing. The runner writes identical fallback exports only once, so I changed the script to verify them against the queue file and its hash.
- The first P4 perturbation overshot the tolerance, because the compiled saved state already carried a 2.9e-12 residual from the BFS root. I set the coordinate directly instead.
- A P4 case with far = 1e7 was rejected by the evaluator's compiled initializer (residual above 1e-10). I replaced it with 1e6.
- Seven large-scale P5 initial states hit the same initializer limit and were skipped and counted (`init_skipped`).
- A foreground `sleep` was blocked by the harness. I waited on the panel log with an until-loop instead.

I did not rerun the author's 8-minute mutation probe.

## Hypothesis verdicts

- **H-L, consistent additive in-memory updates: SUPPORTED_WITHIN_SCOPE is not established by the current receipt.**
  - The locality endpoint passed on an operation meter that omits a Θ(R) step (F1), and the "local certificate" behind convergence is unsound outside the panel's coordinate range (F2).
  - The speed endpoint against a fresh full recompute does hold. Even with the copy, apply time is far below recompute time.
  - After the F1/F2 fixes it is likely to hold again for consistent edges and new nodes, but only scoped as F4 describes: the locality comes from rigid frame placement, which is equivalent to an incremental compiled update, not from relaxation; there is no incremental compiled baseline; and bridges are O(smaller component).
- **H-L, contradiction resolution by the local queue: NOT_SUPPORTED is justified.** The rate is 0/15 at 128 nodes and above (0/20 overall) under the registered rule. Note that the exact least-squares correction to a contradiction is spread across the component, so failure within a 100,000 cap was the expected outcome and does not show anything surprising about locality.
- **H-L, durable persistence: NOT_TESTED** is honest. F2 shows that persistence can also *fail* after an in-memory PASS, which must be stated.
- **H-P: INCONCLUSIVE is acceptable.** NOT_TESTED would be more precise. The frozen accuracy of 0.81 against 1.0 is true by construction (the updated store contains the new constraints). No task learning, transfer or adaptive-versus-frozen comparison on a downstream task was run, as `hypothesis_limits` itself says.

## Remaining limitations

- One generator family with unit weights in the panel. Weighted, duplicate and tiny-weight cases are covered only by focused checks and my probes.
- Single-shot wall-clock timing in one Python process; ratios vary between runs (F4.3).
- No incremental compiled baseline, so nothing supports a claim of superiority over compiled methods.
- The fallback is slower end to end than a fresh recompute for every contradiction.
- My probes are directed and randomized searches, not proofs. Other floating-point boundary cases may exist. The fixed certificate should be argued in terms of the export gauge and tested at large coordinate scales.

## Independence statement

This reviewer is the same model family as R004's author, so it may share blind spots. It had no access to the author's conversation context and did not rely on the author's review (`evidence/c1_review/CLAUDE_ACCEPTANCE.md`, `evidence/c1_claude_review/FOCUSED_CHECKS.md`) beyond reading it for context. Every number above comes from commands run in this review, and the scripts and outputs are in this directory. Implementation acceptance here is separate from the hypothesis verdicts. No numeric score is given.
