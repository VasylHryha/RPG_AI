CHANGES_REQUIRED

# C6 R005 pre-development engineering review

- Reviewer family: Claude
- Actual reviewer model: Claude Opus 5.5 (`claude-opus-5-5`)
- Reviewed commit: `1f295fadabd099d406a2f43abca42ad094b2ba74` (HEAD at review start; implementation repairs in `52e056f`, check evidence in `1f295fa`; no later commits)
- SHA256 of `evidence/c6_r005_repair_checks/CHECKS.json`: `751849c052900ef9278761ed8f1c405b7502fd456604dd9c9b4c2d94c4c34129`
- Scope: read-only, about 20 minutes. I ran no simulations, tests, mutation probe, panel or rescoring. I made no changes to code, the manifest, STATUS.json, receipts or `.gate`.
- Date: 2026-10-03

## Verdict

The verdict is **CHANGES_REQUIRED, but the required changes are small.** The physics, the clock repair, the native/reference agreement and the source-preservation design look correct to me. I found no defect in the model equations, the rolling-window timestamps or the causal ablations.

The changes are still required because of how the lifecycle binds files. `run_c6_r4.development_pass` (`geomind/run_c6_r4.py:21`) refuses the final panel unless the development receipt's `file_hashes` equal the current `dependencies()`. Those dependencies include `tools/c6_r4_mutants.py` and `geomind/c6_r4_field_analysis.py` (`tools/c6_r4_design_gate.py:20-24`). So any defect in the mutant set or the analysis that is fixed after the development gate would make that development receipt unusable. That would need a third development attempt, which the proposal forbids. Decision 0019 also requires the complete "code/test/mutant batch" before testing and development. Findings 1 and 2 must therefore be fixed before the one R005 development gate, not after it.

## Ranked findings

### 1. Medium–high: the mutant inventory leaves out proposal-required mutant classes

**Evidence.** `experiments/c6_proposal_r4.md` §10 says mutants "must exercise" a fixed list. `tools/c6_r4_mutants.py:2-30` covers many of them: sham mask and denominator, NO-R J/K leaks, G→M incoming-weight leak, carrier contamination, episode-zero leakage, enabled-subset cherry-picking, false enablement flag, restaged source, sham check, numerics, causal ablation and spread, rolling clock, publication link and S, native cache identity, complex hash, storage-order selection, and one endpoint omission. It has **no mutant** for these required classes:

- early emission (current output switched on before qualification or during the prefix);
- unmatched episode state (removing the `inputs`/`perturbations` pairing check at `geomind/c6_r4_field_analysis.py:89-90`, or drawing per-condition candidate entropy);
- cherry-picked episode continuation (protocol continuing from a qualifying episode 1–4 when episode 0 fails, `geomind/c6_r4_field_protocol.py:121-122`);
- misclassified physical source loss (for example, SOURCE_LOST turned into invalid or eligible, `geomind/c6_r4_field_protocol.py:98-101`);
- untransformed kicks (removing the rotation or phase offset in `physical_perturbations`, `geomind/c6_r4_field_protocol.py:18-22`);
- reset environment or clock (the check at `geomind/c6_r4_field_analysis.py:75-79` is never mutated);
- subset-mismatched chain contrasts (different world masks at turn 1 and turn 2);
- duplicate IDs (the validation at `geomind/c6_r4_field.py:85`);
- uncorrected CI (`ci_level` replaced by .95 in the primary verdict);
- coarse/refined input mixing (for example, a fine-grid owner seeded from the grid-0 state or carrier);
- false witness tuples (the tuple consistency check at `geomind/c6_r4_field_analysis.py:91`).

The existing `endpoint_omission` mutant drops `level_interface`, an Arm A ID. It does not drop a primary or diagnostic endpoint.

**Why it blocks.** The mutant file is bound into the development receipt, and decision 0019 requires the batch to be complete. If it is completed after development, the R005 receipt becomes unusable for the panel.

**Required fix.** Add one semantic mutant for each missing class, and one that drops a primary ID and one that drops a turn-diagnostic ID. Each mutant must target a line that a contract test actually exercises. Where no contract would kill a mutant, add the contract in the same batch. Leave `KNOWN_BACKSTOPS` and `EXPECTED_TIMEOUTS` empty unless a reason is documented.

### 2. Medium: chain-scope turn-1 endpoints silently drop worlds that become engineering-invalid at turn 2

**Evidence.** `geomind/c6_r4_field_analysis.py:111,116` sets `valid=gate and not invalid_turn[turn]` for both the unfiltered and the `chain_` prefixes. A world whose turn-2 assay raises (`row['invalid']['turn']==2`) never becomes `chain_complete`. It is therefore absent from `chain` (line 110), and the `b_chain_*_turn1` endpoints and `H-BG_chain_turn1`/`H-PS_chain_turn1` stay engineering-valid with that world filtered out. `test_physical_loss_is_valid_eligibility_and_late_error_preserves_first_turn` (`tests/test_c6_r4_field.py:311-322`) builds exactly this case and only asserts the unfiltered turn-1 claim.

The proposal §9 says "An engineering-invalid reached world invalidates each panel endpoint that depends on its failed assay, rather than being filtered out of that endpoint's eligible-world mask." Membership in the chain mask depends on turn-2 validity, and §6 says complete chains need "valid controls/numerics for both turns".

**Counter-check.** H-RBG is already INCONCLUSIVE in this case, because `recursive` receives `not any(invalid_turn.values())`. The defect is therefore limited to the four reported chain-turn-1 verdicts. It is still a selection-by-engineering-outcome path in a registered primary endpoint. The unfiltered turn-1 behaviour, which keeps an earlier valid result after a late failure, is correct and should not change.

**Required fix.** For the `chain_` prefix, use `valid = gate and not any(invalid_turn.values())` at both turns. Extend the cited test to assert that the `b_chain_*_turn1` endpoints are INCONCLUSIVE when any world is invalid at turn 2.

### 3. Low–medium: the probe phase does not transform with the common phase origin

**Evidence.** Proposal §7 says "Common phase rotation carries material phases, medium values, drive phases, probe phase and replacement-phase intervention arrays together." R005 adds `phase_origin` to populations (`geomind/c6_r4_field.py:129`) and to replacement phases (`geomind/c6_r4_field_protocol.py:21`). However, `A.descriptor` builds the impulse as `.05*exp(1j*(alpha+quadrature*pi/2))` (`geomind/c6_r4_field_assay.py:207`) with no `phase_origin`. `run_world` draws `alpha` independently (`geomind/c6_r4_field_protocol.py:135`), and `test_covariance_carries_future_introduction_axis_and_realized_kicks` does not cover the descriptor.

**Counter-check.** Production owners always have `phase_origin=0`, so recorded values would not change. This is a gap in the declared covariance, not a bias in the results. It is cheap to fix now and impossible to fix after development, because of the file binding.

**Required fix.** Use `alpha + owner.phase_origin` for the impulse (recording both values), and add a contract that a phase-rotated grid gives the same per-probe gains.

### 4. Low: no response descriptors for unsuccessful-source worlds

**Evidence.** Proposal §4 says "Record descriptors for every reached prefix and branch, including unsuccessful source worlds through explicit no-treatment diagnostics." `operation` returns before any `A.descriptor` call when the source is lost (`geomind/c6_r4_field_protocol.py:105`). `run_world` records no descriptor for an unqualified R0 (`:160`). Mean-amplitude and coherence diagnostics are recorded (`:89-90`), but the background response descriptor is not.

**Required fix.** Either compute `A.descriptor` for the reached snapshot and each reached B_after in these worlds, with the cost included in the budget, or have the owner record in the exception decision that "descriptors" here means the state and amplitude diagnostics only. This affects diagnostics only, not primary endpoints.

### 5. Low: the sham "output-zero" measurement only restates metadata

**Evidence.** `F.emissions` multiplies by `c.output` (`geomind/c6_r4_field.py:219`), so `output_max_by_dt` for the sham is zero by construction (`geomind/c6_r4_field_assay.py:38-40`). It does not measure what the kernel applied. In practice the guarantee does hold, by a different route. When every cohort is off, `F.advance` evolves the actual medium with `active.cohorts=[]` (`geomind/c6_r4_field.py:177-181`). The native kernel never sees a sham emitter, and `test_outgoing_channel_uses_selected_mean_then_mask` kills the `nonzero_sham` mutant.

**Required fix.** None is strictly needed. Either state this in the receipt, or replace the check with a real measurement: compare the sham's actual-field trajectory with a source-free medium evolution, which the all-off factorization already computes.

### 6. Low (document): empty bootstrap resamples turn a valid result into INCONCLUSIVE near the ten-world floor

**Evidence.** `bootstrap` returns `None` if any of the 100,000 all-world resamples contains no eligible world (`geomind/c6_r4_field_analysis.py:97-103`). With 40 worlds and m eligible worlds, the expected number of empty resamples is about 1e5·((40−m)/40)^40. That is about 1.0 at m=10 (a 63% chance of at least one), about 0.26 at m=11 and about 0.06 at m=12.

This errs toward INCONCLUSIVE, and the proposal leaves empty-resample handling unspecified. It does mean that n=10–12 is not really the stated "≥10" floor.

**Required fix.** Owner/drafter choice before the final registration: either document this behaviour in the protocol or exception decision, or define how empty resamples are handled. Do not change it after results.

### 7. Low: binding and fixture hygiene

- `dependencies()` (`tools/c6_r4_design_gate.py:20-24`) leaves out `tools/c6_r3_design_gate.py`. The runner and the gate import `write_world`/`jsonable` from that file, and `milestones/c6.json` lists it. It also leaves out `milestones/c6.json` itself. **Fix:** add both, so the development receipt binds everything that writes or validates its artifacts.
- `equivariance()` hard-codes fixture seed `46034005` (`tools/c6_r4_design_gate.py:89`), from the R004 namespace. This is a deterministic engineering fixture, not experimental entropy, so it is acceptable. Moving it to a named protocol field would make the namespace audit clean.
- Before-background episode publications (`cell['before_formation']`) are never passed to `publication_valid` (`geomind/c6_r4_field_analysis.py:80-95`). **Fix:** validate them the same way as the condition episodes.

### Noted, not a defect

- Cross-grid agreement is enforced on every structural candidate and every rolling window, including the decaying NO-R branch (`geomind/c6_r4_field_assay.py:166-167`, `geomind/c6_r4_field_protocol.py:79-81`). A threshold flip in any diagnostic window invalidates the whole world. This is stricter than "selections, binary qualification decisions and continuation IDs". It is conservative and consistent with the stop table, and with step-tolerance errors far below the threshold spacing it should be rare. It is a readiness risk for the gate, not a fidelity defect.
- During endpoint recovery and causal forks, the intact source's output stays on (`geomind/c6_r4_field_protocol.py:82` runs before outputs are zeroed at `:86-87`). Emission only enters the actual medium, never the carrier or source, so the source measurements are unaffected. Only the cost is affected.
- In the NO-R endpoint causal "ablated" fork, `mode='no_geometry_to_mode'` restores K and J for that fork. Under that mode the G→M effect is exactly zero, and NO-R's intact M→G effect is exactly zero (J=0). So the NO-R qualification cannot flip, and no false leak can be raised.

## Checks performed

1. **Model fidelity.**
   - I compared `native/c6_r4/field.cpp` and `geomind/c6_r4_field_reference.py` term by term with proposal §2: medium law, eight-tone drive from absolute substage time, saturating incoming kernel with denominator guard, selected-mean output with mask applied after the full channel, geometry and mode laws, J/K and origin ablations.
   - The R005 native refactor is algebraically identical to the old version. The pair loop keeps ascending-j accumulation per element. Antisymmetric terms use exact IEEE negation of `dx` and of the odd/even trig functions. `ow==w` when mode≠2.
   - The protocol diff in `52e056f` changes only the entropy namespaces (46034xxx → 46035xxx). Model, detector, causal, numerics, margins, CI level and budget are unchanged.
2. **Rolling clock.**
   - `rolling_persistence` (`geomind/c6_r4_field_protocol.py:50-63`) now uses prefix frames t=70…99 followed by operation frames t=100…200. That is 131 unique samples and 101 windows labelled 100…200. Window 0 equals the qualification window, because operation frame 0 is `pack()` of the qualification state.
   - Turn 2 uses the reserved episode's own prefix and the same layout, so its windows run 300…400.
   - The new regression (`tests/test_c6_r4_field.py:183-196`) uses the actual law, an exact stable mode and both 100-C0 horizons. It would fail on the old join (false Δf = .2/15). The `rolling_clock_duplicate` mutant targets the exact line.
3. **Native and reference.**
   - The contracts compare every mode with output on and off, for 24 elements (RHS <1e-12, 0.1-C0 trajectory <1e-11).
   - Production native calls always have nc≤1, because previous sources are always off and the factorization splits them out. The development reference battery (nc=1, 100-C0 exposures and probe/recovery fixtures) therefore covers the reached operator. The factorization itself is checked against the unfactored native kernel.
   - The full battery on the optimized kernel was **not** verified here; it runs inside the development gate.
4. **Sham and ablations.**
   - The sham check compares per-step SHA256 traces of all cohort and carrier columns, on all three grids. Factorization makes the source columns independent of actual-medium content.
   - G→M freezes both the pair-coupling weights and the incoming sampling weights at common pre-intervention positions. M→G sets J=0 for the population.
   - Contracts confirm exact zero effects under each ablation and nonzero effects when intact.
5. **Numerical refinement.**
   - Three independent full owners run from the same inputs. They are compared at every production step over every reached scope, normalized by the scope's initial radius of gyration.
   - Grid-dependent causal decisions, spread failures, structural or recovery disagreement and response-gain or paired-contrast deviation above .001 now raise `NumericalFailure`, which makes the world invalid. Leaking ablations raise `ValueError`.
   - Only "all intact ≤ 1e-8 on every grid" stays a physical non-qualification. This matches §3 and §7.
6. **Covariance.** The future introduction axis, scene origin and phase origin go into `population`. Position kicks rotate and replacement phases shift. Tokens and IDs follow elements under permutation, and selection is token-based. The probe-phase gap is Finding 3.
7. **Two-turn continuity and analysis.**
   - Turn 2 continues from the actual intact episode-0 grid object at t=300. The links check the clock at 300 and 500, the after/introduced field and carrier equality, and the restaging.
   - Formation uses exactly episodes 1–4 over a fixed /4, and an invalid episode raises.
   - Witness tuples are recorded in all three backgrounds. Chain masks are mechanical-completion masks, not witness masks.
   - The CHANGE truth table, the ordered H-BG→H-PS and H-RBG rules, and the 79-endpoint coverage check (`:190`) match §9.
8. **Evidence and guards.**
   - The withdrawn R004 artifacts match `INTERRUPTED.json` (all five SHA256s reproduced).
   - The manifest status is `PENDING_DEVELOPMENT_APPROVAL`, and `tools/c6_r4_design_gate.py:127-129` refuses to create output unless the status is `REGISTERED_DEVELOPMENT_ONLY` and the output path is exactly `evidence/c6_r5_design_gate`.
   - The panel runner checks the gate first and requires a bound development PASS, a fresh integer final entropy that differs from the development, smoke and bootstrap values, and clean contracts.
   - `CHECKS.json` lists all 79 endpoints as `not_run` with reasons, and records accepted-freeze PASS and R3 preservation. I did not recompute the accepted-freeze or R3 hashes.

## Remaining uncertainties (not verified here)

- **Optimized-kernel reference battery.** Not run or verified; it is scheduled inside the development gate.
- **Runtime.** I make no projection. The only measured data are the withdrawn R004 partial worlds (200–233 s each). Those stopped after the first operation and come from different code, so they do not bound the cost of a full two-turn chain (four response descriptors of 50 probes × 3 grids per turn, 19 candidate episodes per turn, and their recovery and causal forks). A budget STOP within 1800 s with two workers is a real possibility that cannot be ruled out without running.
- **Readiness yield.** Source and chain yield, and how often cross-grid threshold disagreement makes a world invalid, are unmeasured. Any invalid world makes the gate STOP (`readiness`, `tools/c6_r4_design_gate.py:106`).
- **Mutation kill rate.** Not measured; it runs in the final pipeline only.

## Recommendation on the single-attempt clause and an owner exception

Proposal §9 says "No second development attempt for the same design." The clause exists to prevent outcome-driven retries and tuning. The R004 attempt was withdrawn for a deterministic implementation defect: the boundary join misread a stable 0.2 rad/C0 mode as a 0.0133 Δf. Its outputs cannot measure apparatus readiness under the approved design. R005 changes no equation, coefficient, cut, margin, horizon or budget (the protocol diff is entropy-only). It uses fresh development, smoke, bootstrap and reference namespaces, and it preserves the R004 bytes. The implementer did see four worlds' partial outcomes, but fresh entropy and the unchanged physical settings limit that exposure to the classification-rule repairs. Those repairs move the code toward the approved §3/§7 text: engineering failures are no longer counted as nonformation.

**I recommend that the owner grant one explicit, engineering-only exception: a single fresh R005 development gate, capped at 1800 s, as decision 0019 already budgets.** Conditions:

1. Fix Findings 1–3 and resolve 4, 6 and 7 (fix them, or document the interpretation in the decision), in one batch. Run the focused contracts once at the end of the batch, and commit before the gate. Fixes must not touch the model, coefficients, cuts, margins, horizons or budget.
2. Record the exception in a new decision that names this review, the post-fix commit, and the fact that R004 is withdrawn engineering evidence, not a development attempt on the design. Only after that, set the manifest to `REGISTERED_DEVELOPMENT_ONLY`.
3. Agree in advance that any outcome of the R005 gate is final for this design, including a budget/timeout STOP or an engineering-invalid world, unless a further defect is shown to be a deterministic implementation error. Even then, a third attempt needs a fresh owner decision, not an automatic right.
4. No outcome-based tuning, no pilot runs and no rehearsal before the gate.

READY_FOR_DEVELOPMENT would only ever be limited engineering approval. It does not accept C6, support any hypothesis, replace the later panel review, or override the owner's decision on the exception.

## Next action

The implementer (Codex) applies the fix batch above, runs the focused contracts once, and commits. The owner then decides on the single-attempt exception. A short re-check of the diff, without a full re-review, is enough before the gate.
