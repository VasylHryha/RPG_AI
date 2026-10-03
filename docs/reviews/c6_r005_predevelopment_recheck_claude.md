CHANGES_REQUIRED

# C6 R005 pre-development diff recheck

- **Reviewer family:** Claude
- **Actual reviewer model:** Claude Opus 5.5 (`claude-opus-5-5`)
- **Reviewed HEAD:** `d7f268d1f649f342231f5e197d968a94bd2f4f6b`. The code repairs are in `f966675` and `0f3ac29`; the evidence is in `d7f268d`.
- **SHA256 of `evidence/c6_r005_review_repairs/CHECKS.json`:** `98108ce062b6c6bb49f8b865acf21e4f080ce83a5097418b57d743fa403f3fa7` (supplied by the host and quoted here, not recomputed by me).
- **Scope.** This is a short diff recheck against my earlier report (`docs/reviews/c6_r005_predevelopment_review_claude.md`). It is not a full re-review or panel acceptance.
  - I used only Read, Glob and Grep.
  - I ran no code, tests, mutations, simulations, panel or rescoring.
  - I wrote nothing and changed no status.
- No numeric quality score is given.

## Verdict

**CHANGES_REQUIRED, with one small blocker.**

- All nine original findings are closed or acceptably resolved on static reading.
- The Finding 7 repair added one new defect (B1 below). It costs nothing scientifically, but it must be fixed before development. The owner's choice of option A binds the analysis module and protocol into the development receipt, so after the development gate this defect can no longer be fixed without making that receipt unusable.

Everything else I checked is ready for the single R005 development gate, subject to the owner's separate fresh-development exception.

## Findings 1–9: closure

| # | Original finding | Repair seen | Status |
|---|---|---|---|
| 1 | Required mutant classes missing | `tools/c6_r4_mutants.py:30-47` adds 18 mutants (45 in total). Every class from proposal §10 is now covered, including early emission, unmatched episode state, cherry-picked continuation, misclassified physical loss, untransformed kicks, environment reset, clock reset, chain-subset mismatch, duplicate IDs, uncorrected CI, coarse/refined input mixing, false witness tuple, and primary and diagnostic endpoint omission. `KNOWN_BACKSTOPS` and `EXPECTED_TIMEOUTS` stay empty. For each new mutant I found a contract that should kill it. Examples: the prefix-emission fixture (`tests/test_c6_r4_field.py:412-420`); the direct `operation` caller fixtures (`:423-469`); the kick-covariance test (`:127-139`); the clock/field/before-publication tamper rows (`:293-307`); `engineering_valid` on chain endpoints (`:343-346`); the common chain mask (`:524-538`); the entropy registry (`:495-503`). | **Closed statically.** The kill rate is unmeasured until the ordered final pipeline. A static mutant count is not a kill rate. |
| 2 | Development binding vs. a post-development mutation probe | The owner chose option A (decision 0021). `dependencies()` (`tools/c6_r4_design_gate.py:25-29`) now excludes the tests and mutants and adds `tools/c6_r3_design_gate.py` and `milestones/c6.json`. The analysis module, readiness code, protocol, native code and pins stay bound. The tests and mutants stay in the final fingerprint (`milestones/c6.json:15,26`). A contract checks this (`tests/test_c6_r4_field.py:506-511`). | **Closed.** See residual note N3. |
| 3 | Late turn-2 failure silently dropped from chain-turn-1 endpoints | `geomind/c6_r4_field_analysis.py:122`: chain scope now uses `any(invalid_turn.values())`; the unfiltered scope keeps the per-turn rule. The test asserts every `b_chain_*` endpoint is INCONCLUSIVE and `engineering_valid` is false (`tests/:343-348`). Under the mutant, 39 complete synthetic chains with PASS would come out valid, so that assertion kills it. | **Closed.** |
| 4 | Final-entropy guard permits seen entropy | `validate_final_entropy` (`geomind/run_c6_r4.py:19-22`) rejects booleans, non-integers and negatives, and every value in `reserved_entropy` (`experiments/c6_r4_protocol.json:111-152`). The registry covers R1/R2 33333, all R3, R004 46034001–46034005 and R005 46035001–46035004, plus the test fixtures. I grepped the C6 `geomind`/`tools` sources and found no unlisted C6 RNG namespace. | **Closed.** Note N2 covers a labelled duplicate value. |
| 5 | Probe phase not carried by the common phase origin | The impulse now uses `alpha+o.phase_origin` per owner (`geomind/c6_r4_field_assay.py`, `descriptor`). It records `alpha`, `phase_origin_by_dt` and each probe's `probe_phase_by_dt`. The contract checks that per-probe gains are equal and that the raw complex responses rotate by e^{iφ}. The raw-response check kills `probe_phase_untransformed`, even if the gains alone would not. | **Closed.** |
| 6 | Pending-guard contract vacuous after registration | The rewritten test (`tests/:377-386`) uses a fixture root. Pending status with the exact path is refused, and registered status with a wrong path is refused, whatever the real status is. | **Closed.** |
| 7 | No response descriptors for unsuccessful-source worlds | Descriptors are now computed for B_before and for all three B_after branches before the eligibility return (`geomind/c6_r4_field_protocol.py:106-110`). An unqualified R0 gets an explicit no-treatment descriptor (`:163-165`). Real-caller contracts check this (`tests/:464-483`). | **Closed in substance.** I accept the declared scope (below). The repair introduced B1. |
| 8 | Empty bootstrap resamples near the ten-world floor | The conservative `INCONCLUSIVE_IF_ANY_EMPTY` rule is kept and registered in the protocol, with the 1.006 / 63.4% figures. `evaluate` rejects any other policy (`analysis.py:111`). The empty-draw count is now reported (`:148`), and there is a truth-table contract. | **Closed** (documented, not changed). |
| 9 | Hygiene | Before-background publications are validated, with an inventory check (`analysis.py:84-87`) and a tamper contract. The sham-output basis is stated in the receipt (`assay.py`, `output_check_method`). RSS is converted to bytes, with the raw unit and worker-lifetime scope recorded (`protocol.py:181-186`) and a contract for each platform. `tools/c6_r3_design_gate.py` and `milestones/c6.json` are now bound. | **Closed.** |

**Finding 7 scope (checked against the proposal).** Proposal §4 attaches "every reached prefix and branch" to the B_before/B_after sentence. §5 and the §9 diagnostics list name "B_before/every B_after". The implementer reads this as:
- the operation-source prefix (B_before);
- every B_after branch;
- an explicit no-treatment descriptor for an unqualified R0.

That is the most natural reading and matches the registered response workload. Assaying every one of the 19 candidate snapshots per turn would add workload that is not registered. My original wording ("each reached snapshot") was looser than the proposal, and I withdraw any implication that it required the broader workload.

## Blocker

### B1. The no-treatment descriptor's raw arrays are duplicated into the aggregate panel receipt

**Evidence.**
- `run_world` stores the full descriptor inside the initial-source record: `initial['no_treatment_response']=A.descriptor(...)` (`geomind/c6_r4_field_protocol.py:163-165`).
- That descriptor includes `raw`: 50 probes, each with `response_real_imag` of shape 100 samples × 25 sites × 2. That is about 250,000 numbers per descriptor (`geomind/c6_r4_field_assay.py:200-225`).
- `evaluate` copies the whole `initial_source` into `b_source_population_inputs` (`geomind/c6_r4_field_analysis.py:189`).
- The panel writes `results.json` with `indent=2` (`geomind/run_c6_r4.py:68`). At that nesting depth, my rough estimate is on the order of 10 MB per unqualified world.
- The analysis module states the intended design right next to this: raw diagnostics "stay in the hash-bound world artifact instead of being duplicated into a multi-gigabyte aggregate receipt" (`analysis.py:176-182`). It uses pointers for `response_raw` for that reason.

**Impact.**
- If even about a quarter of the 40 final worlds have no qualified source, the receipt reaches roughly 100 MB or more. That makes committing the evidence awkward, and it fails outright on any git host with a per-file size limit.
- There is no scientific or verdict effect.
- It is a blocker only because of timing. `geomind/c6_r4_field_analysis.py`, `run_c6_r4.py` and the protocol are all development-bound under option A. After the gate, the only remedies would be an oversized receipt or an invalidated development receipt.

**Required fix (small, prospective).**
1. In `b_source_population_inputs`, replace `no_treatment_response.raw` with an artifact pointer, as `response_raw` already does. For example: `{'artifact': world_NNN.json.gz, 'json_pointer': '/initial_source/no_treatment_response/raw'}`. Keep `gain_by_dt`, `per_probe_by_dt`, `alpha`, `phase_origin_by_dt` and the snapshot IDs inline.
2. Add one contract: the aggregate value carries the pointer, not raw arrays, and the world artifact still holds the raw arrays.
3. Run the focused tests once and commit. No development has run, so the development hashes changing now is harmless.

Alternatively, the owner may record in the exception decision that they accept the receipt size. I recommend the fix.

## Non-blocking notes (disclose; no change required)

- **N1. New way for a world to become invalid.**
  - `NumericalFailure` subclasses `ValueError` (`assay.py:55`). A failed refinement check on a diagnostic descriptor (more than .001 apart between grids) in a source-lost or unqualified-R0 world is therefore caught (`protocol.py:166`). It makes the whole world invalid at turn 1.
  - In development, any invalid world gives STOP (`tools/c6_r4_design_gate.py:111,115`). In the panel, it makes every turn-1 and chain endpoint INCONCLUSIVE.
  - This follows proposal §7 ("every background response gain"), and the panel-wide invalidation was already the existing conservative policy. But it enlarges the surface for a one-shot STOP: up to four extra descriptors per source-lost world and one per unqualified world.
  - Decision 0021 mentions only the runtime cost. The owner should know about this risk before granting the exception. I recommend one sentence in the exception decision; no code change.
- **N2. Labelled seed overlap.** The smoke medium seed (`smoke_entropy+1`, `run_c6_r4.py:35`) equals `bootstrap_entropy` 46035003. The registry lists both names honestly (`protocol.json:122-123`). The smoke is a 0.2-C0 engineering fixture outside inference, so this has no consequence. R004 had the same pattern.
- **N3. Option A has a boundary.** `milestones/c6.json` is development-bound and names the single test file and the mutants module. Strengthening tests after a surviving mutant is safe only inside `tests/test_c6_r4_field.py` and `tools/c6_r4_mutants.py`. Adding a new test file or changing a stage command would invalidate the development receipt.
- **N4. Registry vs. later test seeds.** Seeds added to tests after development cannot be added to the bound registry. Generating the final entropy as a high-entropy integer (as `2**127+813` in the contract implies) makes any collision with a small fixture seed negligible.

## Remaining uncertainties (not verified here)

- **Measured kill rate of the 45 mutants.** It belongs to the ordered final pipeline. I traced a plausible killing contract for each new mutant, but survivors are still possible.
- **The optimized-kernel reference battery, readiness yield and runtime.**
  - Development budget: 1800 s with two workers.
  - Finding 7 adds up to four 50-probe × 3-grid descriptors per source-lost turn and one per unqualified world.
  - These run inside the existing budget. No projection is possible without the gate.
- **Earlier test runs.** `CHECKS.json` records 58/58 passing contracts and a smoke PASS at `0f3ac29`, plus one failed attempt at `f966675` caused by a fixture with production code unchanged. I did not re-run anything or recompute any hash.
- **Descriptor coordinate covariance.** Covariance under site permutation and rotation is covered by labels (`port` is recorded by site ID), but it has no dedicated descriptor contract. Finding 5 asked only for phase.

## Bounded recommendation

1. **Implementer:** fix B1 as above (two or three lines plus one contract). Optionally add the N1 sentence to the exception record. Run the focused contracts once and commit.
2. **Reviewer:** recheck only the B1 diff; no further full recheck is needed.
3. **Owner:** grant or decline the single fresh R005 development exception. The conditions in my earlier report still apply: any gate outcome, including STOP, a timeout or an engineering-invalid world, is final for this design; no tuning, pilot or rehearsal.

A later READY_FOR_DEVELOPMENT would be engineering approval only. Scientific readiness needs the measured development gate, and acceptance needs the final ordered pipeline plus the independent panel review. This report changes no status and grants no owner authority.
