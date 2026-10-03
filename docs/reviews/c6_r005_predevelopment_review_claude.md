CHANGES_REQUIRED

# C6 R005 pre-development engineering review

- Reviewer family: Claude
- Actual reviewer model: Claude Opus 5.5 (`claude-opus-5-5`)
- Reviewed commit: `1f295fadabd099d406a2f43abca42ad094b2ba74` (HEAD at review start). Implementation repairs are in `52e056f` and check evidence in `1f295fa`. The only later commit is this report.
- SHA256 of `evidence/c6_r005_repair_checks/CHECKS.json`: `751849c052900ef9278761ed8f1c405b7502fd456604dd9c9b4c2d94c4c34129`
- Scope: read-only, about 20 minutes, plus a second pass at the owner's request (see "Recheck").
  - I ran no simulation, test, mutation probe, panel or rescoring.
  - I changed no code, manifest, STATUS.json, receipt or `.gate`.
  - I ran only read-only static checks: the accepted-freeze guard, a count of mutant patterns, and hashes of the withdrawn artifacts.
- No numeric quality score is given (AGENTS.md "Never").

## Verdict

The verdict is **CHANGES_REQUIRED, with a small, well-defined batch plus one owner decision.**

I found no defect in:
- the model equations, or in the native optimization's preservation of them;
- the repaired rolling-window clock;
- intact/sham source preservation;
- the completeness of the causal ablations;
- two-turn state continuity.

Changes are still required because of how the lifecycle binds files. `development_pass` (`geomind/run_c6_r4.py:21`) refuses the final panel unless the development receipt's `file_hashes` equal the current `dependencies()`. That set includes the tests, the mutants and the analysis code (`tools/c6_r4_design_gate.py:20-24`). A defect in any of these that is fixed after the single development gate makes that receipt unusable, and a third attempt would then be needed. Decision 0019 also requires the complete code/test/mutant batch before testing and development.

## Ranked findings

### 1. Medium–high: proposal-required mutant classes are missing

**Evidence.** Proposal §10 says that mutants "must exercise" a fixed list. `tools/c6_r4_mutants.py:2-30` has 27 mutants, and I statically confirmed that each pattern occurs exactly once. It has **no mutant** for these required classes:

- early emission;
- unmatched episode state (the pairing check at `geomind/c6_r4_field_analysis.py:89-90`, or per-condition candidate entropy);
- cherry-picked episode continuation (`geomind/c6_r4_field_protocol.py:121-122`);
- misclassified physical source loss (`geomind/c6_r4_field_protocol.py:98-101`);
- untransformed kicks (`geomind/c6_r4_field_protocol.py:18-22`);
- reset environment or clock (`geomind/c6_r4_field_analysis.py:75-79`);
- subset-mismatched chain contrasts;
- duplicate IDs (`geomind/c6_r4_field.py:85`);
- uncorrected CI (`ci_level` replaced by .95);
- coarse/refined input mixing;
- false witness tuples (`geomind/c6_r4_field_analysis.py:91`).

`endpoint_omission` drops `level_interface`, an Arm A ID, not a primary or diagnostic endpoint.

**Required fix.** Add one semantic mutant for each missing class, plus one that drops a primary endpoint and one that drops a turn-diagnostic endpoint. Each must hit a line that a contract test exercises; where no contract would kill a mutant, add one in the same batch. Leave `KNOWN_BACKSTOPS` and `EXPECTED_TIMEOUTS` empty unless a reason is documented.

### 2. Medium (lifecycle conflict, owner decision): a surviving mutant found after development cannot be repaired

**Evidence.**
- Proposal §10 schedules the mutation probe only in the final ordered pipeline, after readiness and final registration.
- The milestone fingerprint includes the manifest (`tools/milestones.py:55-62`). Final registration (status, `final_entropy`, `development_results_sha256`) therefore resets every stage stamp, so the mutation probe first runs after the development gate.
- The development receipt binds `tests/test_c6_r4_field.py` and `tools/c6_r4_mutants.py`.
- So if that probe finds a surviving mutant, strengthening the tests changes a bound file. `development_pass` then fails, and the design stops for a test-sensitivity reason, not an apparatus reason. Finding 1 makes survivors more likely, not less.

**Required fix: one of these, chosen by the owner before the gate and recorded in the exception decision.**
- **(a) Recommended.** Narrow the development receipt's binding to the files that determine world rows and readiness: the `geomind/c6_r4_field*.py` modules, `run_c6_r4.py`, the native source and build, the protocol, the design gate, the integrity and C4 detector modules, `tools/c6_r3_design_gate.py`, the source pin and the environment. Tests and mutants would then be bound at final registration through the milestone fingerprint, as for every other milestone. Readiness measures the apparatus, and tests do not change world outputs. The analysis module should stay bound, because `readiness` and world validation depend on it.
- **(b)** Authorize one `tools/verify.py --milestone c6 --through mutation` before the development gate, as an engineering check. This deviates from the §10 order and adds one mutation run, since final registration will repeat it.

Either way, the decision must be made before the gate. Afterwards it cannot be made without an outcome-informed exception.

### 3. Medium: chain-scope turn-1 endpoints silently drop worlds that become engineering-invalid at turn 2

**Evidence.**
- `geomind/c6_r4_field_analysis.py:111,116` uses `valid=gate and not invalid_turn[turn]` for both the unfiltered and the `chain_` prefixes.
- A world that raises at turn 2 never becomes `chain_complete`, so it is missing from `chain` (`:110`).
- Even so, the `b_chain_*_turn1` endpoints and `H-BG/H-PS_chain_turn1` stay engineering-valid.
- `tests/test_c6_r4_field.py:311-322` builds exactly this case but asserts only the unfiltered turn-1 claim.

Proposal §9 says such a world "invalidates each panel endpoint that depends on its failed assay, rather than being filtered out of that endpoint's eligible-world mask". §6 says chains need valid controls and numerics for both turns.

**Counter-check.** H-RBG is already INCONCLUSIVE in this case (`:149`), so the damage is limited to the four reported chain-turn-1 verdicts. The unfiltered turn-1 behaviour, where a late failure keeps an earlier valid result, is correct.

**Required fix.** For `chain_`, use `valid = gate and not any(invalid_turn.values())`, and assert in that test that the chain-turn-1 endpoints become INCONCLUSIVE.

### 4. Low–medium: the final-entropy guard does not exclude entropy that was already used or seen

**Evidence.** `geomind/run_c6_r4.py:46` rejects only the current development, smoke and bootstrap values. Several other values would pass:
- the reference-battery entropy `46035004`;
- the equivariance fixture seed `46034005`;
- the withdrawn R004 namespace `46034001–46034004`.

R004 development worlds 0–3 were generated from `SeedSequence([46034001, world, …])`, and their partial outcomes were seen. A final entropy of 46034001 would regenerate those same initial worlds. The R3 namespaces are not checked either.

**Required fix.** Reject every C6 namespace that was ever reserved or used (R3, R004, R005, reference and fixture seeds), listed explicitly in the protocol, and add a contract test.

### 5. Low–medium: the probe phase does not transform with the common phase origin

**Evidence.** Proposal §7 says a common phase rotation carries the probe phase. R005 adds `phase_origin` to populations (`geomind/c6_r4_field.py:129`) and to replacement phases (`geomind/c6_r4_field_protocol.py:21`). However, the descriptor impulse at `geomind/c6_r4_field_assay.py:207` uses `alpha` alone, and the covariance contract does not cover the descriptor.

**Counter-check.** Production `phase_origin` is always 0, so recorded values are unaffected. This is a gap in the declared covariance, not a bias in the results.

**Required fix.** Use `alpha + owner.phase_origin` for the impulse, record both values, and add a contract that a phase-rotated grid gives the same per-probe gains.

### 6. Low: the pending-registration guard contract becomes vacuous after registration

**Evidence.** `tests/test_c6_r4_field.py:347-351` asserts the refusal only `if manifest['status']=='PENDING_DEVELOPMENT_APPROVAL'`. Once the owner registers the run, and in every later pipeline test stage, the test asserts nothing.

**Required fix.** Monkeypatch the manifest status and the output path so the test always checks the pending refusal and the wrong-path refusal.

### 7. Low: no response descriptors for unsuccessful-source worlds

**Evidence.** Proposal §4 says "Record descriptors for every reached prefix and branch, including unsuccessful source worlds through explicit no-treatment diagnostics." However, `operation` returns before any descriptor when the source is lost (`geomind/c6_r4_field_protocol.py:105`), and an unqualified R0 gets none (`:160`). Only amplitude and coherence diagnostics are recorded (`:89-90`).

**Required fix.** Either compute the descriptor for each reached snapshot and B_after, with the cost included in the budget, or have the owner record that "descriptors" here means the state and amplitude diagnostics. This affects diagnostics only.

### 8. Low (document): empty bootstrap resamples turn results INCONCLUSIVE near the ten-world floor

**Evidence.** `bootstrap` returns `None` if any of the 100,000 all-world resamples contains no eligible world (`geomind/c6_r4_field_analysis.py:97-103`). The expected number of empty resamples is 1e5·((40−m)/40)^40. That is about 1.0 at m=10 (a 63% chance of at least one), 0.26 at m=11 and 0.06 at m=12.

This errs toward INCONCLUSIVE, and empty-resample handling is unspecified, but the effective floor is above the stated ten worlds.

**Required fix.** Document this, or define the handling, in the protocol or exception decision before the final registration. Never change it after results.

### 9. Low: binding and validation hygiene

- **Fix:** add `tools/c6_r3_design_gate.py` and `milestones/c6.json` to `dependencies()` (`tools/c6_r4_design_gate.py:20-24`). The runner and gate import `write_world`/`jsonable` from the first, and the milestone config lists it.
- **Fix:** validate the before-background episode publications (`cell['before_formation']`) with `publication_valid`. At present only the condition episodes are checked (`geomind/c6_r4_field_analysis.py:80-95`).
- `F.emissions` multiplies by `c.output` (`geomind/c6_r4_field.py:219`), so the sham's `output_max_by_dt` is zero by construction and is not a measurement. Zero sham output does hold for another reason: when every cohort is off, the actual medium evolves with no cohorts (`geomind/c6_r4_field.py:177-181`), and `test_outgoing_channel_uses_selected_mean_then_mask` kills `nonzero_sham`. **Fix:** say so in the receipt, or compare the sham's field trajectory with a source-free evolution.
- `peak_rss_bytes` uses `ru_maxrss` (`geomind/c6_r4_field_protocol.py:172`). That value is in bytes on macOS but kilobytes on Linux, and it is a lifetime-of-process peak inside the panel's process pool. **Fix:** record the platform unit and label it as a per-process peak.

### Noted, not defects

- **Cross-grid agreement is enforced on everything.**
  - It covers every structural candidate, every rolling window (including the decaying NO-R branch) and the diagnostic before-formation episodes (`geomind/c6_r4_field_assay.py:166-167`, `geomind/c6_r4_field_protocol.py:79-81,109-111`).
  - `closure_valid` also raises a G→M refinement failure even when M→G has already made the candidate physically non-qualified (`geomind/c6_r4_field_assay.py:137-147`).
  - All of this is conservative and consistent with the stop table. It is a readiness risk: any invalid world makes the gate STOP (`tools/c6_r4_design_gate.py:106`).
- **Output stays on in the intact endpoint forks.** Endpoint recovery and causal forks run with the intact output still on (`geomind/c6_r4_field_protocol.py:82` comes before `:86-87`). Emission never reaches the carrier or the source, so only the cost is affected.
- **The NO-R "ablated" G→M fork restores K and J.** Under `no_geometry_to_mode` the G→M effect is exactly zero, and NO-R's intact M→G effect is exactly zero (J=0). So the NO-R qualification cannot flip, and no false leak can be raised.

## Checks performed

1. **Model fidelity.**
   - I compared `native/c6_r4/field.cpp` and `geomind/c6_r4_field_reference.py` term by term with proposal §2: medium law, eight-tone drive at absolute substage time, saturating incoming kernel with denominator guard, selected-mean output masked after the full channel, geometry and mode laws, and J/K and origin ablations.
   - The R005 native refactor is algebraically identical to the old version. It keeps ascending-j accumulation per element, uses exact IEEE negation for the antisymmetric terms, and has `ow==w` when mode≠2.
   - The protocol diff in `52e056f` is entropy-only.
2. **Rolling clock.** The windows now use prefix frames t=70…99 followed by operation frames 100…200: 131 unique samples and 101 windows labelled 100…200 (300…400 at turn 2). Window 0 equals the qualification window. The actual-law exact-mode regression would fail on the old join, and `rolling_clock_duplicate` targets that line.
3. **Native and reference.**
   - The contracts cover every mode with output on and off, for 24 elements.
   - Because of the factorization, production native calls always have nc≤1: nc=0 for all-off actual media, and nc=1 for an active or passive cohort. The development reference battery exercises both, including `no_backreaction` through the all-off path, and the factorization is checked against the unfactored kernel.
   - The full battery on the optimized kernel was **not** verified here.
4. **Sham and ablations.**
   - The sham check compares per-step trace hashes of all cohort and carrier columns, on all three grids.
   - G→M freezes the pair and incoming weights at common pre-intervention positions; M→G sets J=0.
   - Contracts confirm exact zero effects under ablation and nonzero effects when intact.
5. **Numerical refinement.**
   - Three independent full owners are compared at every production step over every reached scope.
   - Grid-dependent or poorly resolved causal, structural, recovery and response decisions raise `NumericalFailure`, which makes the world invalid. Leaking ablations raise `ValueError`.
   - The physical non-qualification paths are the ones the proposal names: no structural candidate, a recovery failure, or every intact causal effect ≤1e-8 on every grid.
6. **Covariance.** The introduction axis, scene origin and phase origin go into `population`. Kicks rotate and replacement phases shift. Tokens follow elements, and selection is token-based. The probe-phase gap is Finding 5.
7. **Continuation and analysis.**
   - Turn 2 continues from the actual intact episode-0 object at t=300, with link and clock checks at 300 and 500 and equality of the after/introduced fields and carriers.
   - Formation uses episodes 1–4 over a fixed /4.
   - Witness tuples are recorded in all three backgrounds, and the mechanical chain mask is used.
   - The CHANGE truth table, the ordered H-BG→H-PS and H-RBG rules, and the 79-endpoint coverage check (`:190`) are present.
8. **Evidence and guards.**
   - `python3 tools/accepted_freeze.py` exits 0.
   - The five withdrawn R004 SHA256s match `INTERRUPTED.json`.
   - The manifest is `PENDING_DEVELOPMENT_APPROVAL`, and the gate refuses to create output unless the status is `REGISTERED_DEVELOPMENT_ONLY` and the path is exactly `evidence/c6_r5_design_gate` (`tools/c6_r4_design_gate.py:127-129`).
   - The panel checks the gate first, then requires a bound development PASS and clean contracts.
   - `CHECKS.json` lists all 79 endpoints as `not_run` with reasons.
   - I did not recompute the R3-bound hashes beyond the freeze guard.

## Remaining uncertainties (not verified)

- **Optimized-kernel reference battery.** Scheduled inside the development gate.
- **Runtime.** I make no projection. The withdrawn R004 partial worlds took 200–233 s, but they stopped after the first operation and came from different code. A full two-turn world (four 50-probe × 3-grid descriptors and 19 candidate episodes per turn, with their forks) is a much larger workload. A budget STOP within 1800 s with two workers cannot be ruled out without running.
- **Yield.** Source and chain yield, and the rate of cross-grid threshold disagreement, are unmeasured.
- **Mutation kill rate.** Unmeasured (see Finding 2).

## Recommendation on the single-attempt clause and an owner exception

Proposal §9 says "No second development attempt for the same design." The clause exists to stop outcome-driven retries and tuning.

R004 was withdrawn for a deterministic implementation defect: the boundary join turned an exactly stable 0.2 rad/C0 mode into a 0.0133 Δf. Its outputs cannot measure readiness under the approved design.

R005 changes no equation, coefficient, cut, margin, horizon or budget, and uses fresh namespaces. The implementer did see four worlds' partial outcomes. Fresh entropy (once Finding 4 closes reuse) and unchanged physical settings limit that exposure to the classification-rule repairs, and those move the code toward the approved §3/§7 text.

**I recommend one explicit, engineering-only owner exception: a single fresh R005 development gate, capped at 1800 s as decision 0019 already budgets.** Conditions:

1. One batch fixes Findings 1, 3, 4, 5 and 6 and resolves 7–9 (fix or documented interpretation). It changes no model, coefficient, cut, margin, horizon or budget. Focused contracts run once at the end, and everything is committed before the gate.
2. The owner chooses Finding 2 option (a) or (b) in the exception decision. That decision names this review and the post-fix commit, and records R004 as withdrawn engineering evidence. Only then does the manifest become `REGISTERED_DEVELOPMENT_ONLY`.
3. Any R005 gate outcome is final for this design, including a budget/timeout STOP and an engineering-invalid world. A further deterministic implementation defect would need a new owner decision, not an automatic retry.
4. No outcome-based tuning, pilot or rehearsal.

A READY_FOR_DEVELOPMENT verdict, if given after the fix batch, would only ever be limited engineering approval. It would not accept C6, support any hypothesis, replace the later panel review or override the owner.

## Recheck (second pass, same session)

At the owner's request I rechecked every finding for false positives and searched for gaps.

**Findings 1, 3, 5, 7 and 8 and the "noted" items survived.** I recomputed the bootstrap figures. I statically confirmed that each mutant pattern occurs exactly once, that `nonzero_sham` is killed by the outgoing-channel contract, and that production native calls are nc≤1, so the battery covers the reached operator.

**New in this pass:**
- **Finding 2:** the lifecycle conflict between the post-development mutation probe and the receipt binding of tests and mutants.
- **Finding 4:** the final-entropy guard permits seen R004 entropy.
- **Finding 6:** the vacuous pending-guard contract.
- **Finding 9:** the peak-memory units.
- The accepted-freeze guard run.

**Corrected wording:** physical non-qualification also covers structural and recovery failures, not just causal effects.

## Next action

1. **Implementer (Codex):** apply the fix batch, run the focused contracts once, commit.
2. **Owner:** decide the exception and Finding 2's option.
3. **Reviewer:** a short diff re-check, not a full re-review, before the single gate.
