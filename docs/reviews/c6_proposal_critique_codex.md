CHANGES_REQUIRED
Reviewer family: Codex
Reviewer model: gpt-6
Reviewed proposal commit: 6660692
Reviewed proposal SHA-256: be43a7e4f6c2e0968afc9a2f820c2d02d55e5098c486da643e63b194a660c6eb

Review date: 2026-10-02. Independent, pre-approval design critique under proposal §12 and stop rule 15. Both the proposal hash and the supplied locked-core hash were verified. This report makes no milestone-status change and does not authorize implementation. Claude, the drafter, owns the amendments and their self-audit; the owner decides approval.

## Findings, ranked by severity

### F1 — High: fake level-1 parts do not receive the promised natural rate

**Location:** §3, lines 94–98; §5, lines 261–265; §10, lines 461, 472. Frozen implementation: `geomind/c5_units.py:136–159`.

**Defect:** The required unchanged `resonator_state` publishes the mean intrinsic element rate as `natural_rate`, even when its `rate` argument contains a measured isolated collective rate.

**Failure scenario:** A fake level-1 part mixes elements from real parts with different assigned rates; the rotating-frame argument for homogeneous real parts no longer applies, but E1 reads the fake's intrinsic-rate mean while real composite parts receive measured isolated rates. Running the fake alone and passing its measurement as `rate` only changes `collective_rate` and the mode signature; it does not fix the field E1 actually consumes (`c5_coarse.py:37`). The promised fair publication procedure therefore cannot be implemented by the named unchanged constructor.

**Smallest fix:** Specify one new C6 owner-side publication wrapper for real and fake level-1 parts that sets `natural_rate` to the measured isolated rate, retaining the frozen constructor read-only. State the measurement window and estimator and test that the measurement reaches the consumed field. **Blocks approval: yes; stop rule 8.**

### F3 — High: the element lift requires offsets that are not published

**Location:** §3a, line 181; §5, lines 265–266; §7, lines 297–299; §10, line 471. Frozen schema: `geomind/c5_units.py:143–159,193–198`.

**Defect:** The specified lift to every scored element cannot be reconstructed from the published states, which contain position offsets only for boundary ports and sorted, identity-free internal phase offsets.

**Failure scenario:** A scored non-port element has no published position offset or identity-linked phase offset; after regrouping, two elements with exchanged phase identities have the same sorted signature but require different lifted predictions. Publishing every internal offset to the predictor would instead defeat the stated upper-level information boundary.

**Smallest fix:** Explicitly make the lift an evaluator-only decoder using fixed, identity-linked offsets recorded from each partition's initial full snapshot. Keep that decoder outside the effective model, pin whether scoring uses paired responses or absolute trajectories, and forbid later full-state updates. **Blocks approval: yes; stop rule 8.**

### F4 — High: criterion 6 can certify parts without observing them

**Location:** §3, lines 151–156; §3a, line 168; §4, lines 234–243.

**Defect:** Discarding every incomplete own-level window makes dynamic validity vacuous when the parent window is shorter than a child's window, an ordering the proposal permits.

**Failure scenario:** C₂ = 3.2 and C₃ = 1.6 satisfy the stated C₂ bound and do not violate any requirement that C₃ exceed C₂. The level-3 window lasts 48 units, the level-2 window 96; there are zero complete level-2 windows, so an `all(...)` check passes even for a broken level-2 part. Requiring slower parents to avoid this would reintroduce scale separation into H-C.

**Smallest fix:** Require at least one complete own-level observation for every part, extending observation with the same generic rule when necessary, or fail/abstain explicitly on insufficient observation. Do not constrain the timescale ordering. **Blocks approval: yes.**

### F5 — High: baseline dominance is not a predictive-error bound

**Location:** §0, line 22; §1, lines 56–60; §7, lines 294–319; §8, line 360.

**Defect:** The gate equates statistically positive improvement over three baselines with bounded predictive accuracy without registering any acceptable absolute response-error bound.

**Failure scenario:** Errors 100, 101 and 102 for the baselines and 99 for the model, with consistently positive paired gains, satisfy all six gain tests while leaving normalized position predictions unusable. The effective-state bounds measure window-summary extrapolation, not these excited coarse trajectories; descriptive frequency and recovery errors do not close the gap.

**Smallest fix:** Retain the owner-approved six-gain rule and additionally register a dimensionless maximum acceptable coarse response error, with its aggregation and verdict rule, at both transitions. Otherwise narrow the claim to baseline-relative improvement and explicitly resolve its insufficiency for R4's bounded-error H-C requirement with the owner. **Blocks approval: yes.**

### F2 — Medium: direct reuse of the rigid scale uses the wrong composite centre

**Location:** §3, line 101; §6, line 282; §10, line 463. Frozen implementation: `geomind/c5_compose.py:59–65`, `geomind/c5_units.py:171–175`.

**Defect:** The reuse instruction does not distinguish applying `scale_units` to published centroids from applying it directly to labelled elements, whose primitive-element mean differs from a composite's published X.

**Failure scenario:** Three children of sizes 6, 8 and 16 at x = 0, 1 and 2 publish X = 1, but their primitive centroid is 4/3. With two further parts centred at 4 and 7, s = 1.25 requires displacement −0.75 for the first published X; the frozen helper supplies approximately −0.694444. Merely changing labels to the level-2 labels does not repair this. At transition 3, the claimed dimensionless intervention then differs from transition 2. Primitive radius-of-gyration helpers likewise cannot silently supply a composite's published L for the push.

**Smallest fix:** Specify generic rigid translations computed from published X and L, then apply them with `shift_units`; `scale_units` itself can be reused on the array of published centroids to compute those translations. Add an unequal-child-size contract. **Blocks approval: no by itself; this is a concrete reuse hazard, not an impossibility with a suitable adapter.**

### F6 — Medium: the finest-level grid does not subsume the other sampling grids

**Location:** §3a, line 168; §4, lines 235, 242–243.

**Defect:** Calling C₁ = 1 the finest observation interval does not specify that additional exact grids are needed to supply samples at non-integral own-level intervals C_k.

**Failure scenario:** C₂ = 3.2 requires samples at 3.2, 6.4, 9.6, etc.; the C₁ grid contains none of the first three. Rounding frame indices changes the actual intervals while `window_statistics` assumes constant `frame_dt`, or interpolation introduces an unregistered error. Cumulative rounding correctly makes these times RK4-step exact, but does not make the level grids nested.

**Smallest fix:** Explicitly record on the union of exact required step indices, or on their integer-step greatest-common-divisor grid, and subsample separately for each level. **Blocks approval: no by itself; multiple recorded grids can satisfy the written own-level rule.**

### F7 — Medium: censoring and timescale aggregation do not determine valid ratios

**Location:** §3, lines 146–156; §5, line 271; §8, line 363; §9, lines 413–416. Frozen helper: `geomind/c5_experiment.py:465–468`.

**Defect:** Calling censored timescale ratios lower bounds is invalid when a child timescale in the denominator is censored, and the development aggregation defining a single C_n is unspecified.

**Failure scenario:** A finite parent τ = 3 and a child censored at 2 produce a plug-in ratio 1.5; the admissible child τ = 100 gives 0.03. That observation cannot support separation. If the parent is censored, its lower bound can support a positive separation claim with a finite denominator, but cannot support a negative claim from its upper bootstrap endpoint. Different choices between ratio-of-medians, median-of-ratios, and treatment of censored measurements also register different C_n values from the same development observations. The τ observation horizon itself is not fixed numerically by the ledger.

**Smallest fix:** Specify the τ horizon, development estimator, aggregation, rounding convention and censoring rules. Use valid interval bounds for ratios and return INCONCLUSIVE when censoring cannot establish the applicable direction. Never treat a bootstrap interval of substituted censoring limits as an interval for the uncensored ratio. **Blocks approval: yes.**

### F8 — Medium: E2 is not a complete numerical recipe

**Location:** §3a, line 179; §7, lines 303–306; §10, lines 501–504.

**Defect:** Central differences followed by eigendecomposition leave the differentiation scale and the treatment of non-diagonalizable or ill-conditioned Jacobians unspecified.

**Failure scenario:** Position differences chosen in fixed absolute units change their dimensionless size across levels. A Jacobian with a Jordan block, such as [[0,1],[0,0]], has a valid exponential I + tJ but no invertible eigenvector matrix; the usual eigenvector-inverse construction cannot implement the written prediction. E1's mixed position–phase, directed-neighbour RHS supplies no symmetry theorem guaranteeing diagonalizability. A formed state also need not be stationary in laboratory coordinates, so δ₀ and the reference trajectory need explicit definitions.

**Smallest fix:** Register size-normalized position and dimensionless phase difference steps, a convergence check, the reference/response convention, and a general matrix-exponential method or an explicit fail/stop rule for unsupported Jacobians. Describe this as a candidate linear-response reduction, not a guaranteed Hessian reduction of the first-order C4 law. **Blocks approval: yes; stop rule 8.**

### F9 — Medium: the overlap design gate permits a circular selection

**Location:** §4, lines 234–247; §9, line 421; §12, line 618.

**Defect:** Specifying calibration on "touching accepted groups at level 3" without defining an acceptance-independent population permits a gate that passes by construction, because accepted level-3 candidates already satisfy overlap ≤ 0.2.

**Failure scenario:** Under that literal population choice, every intact touching candidate with overlap 0.21 is rejected by criterion 6 and omitted from calibration; the gate reports no violation, or receives an empty population. Formation may stop for low yield, but the advertised overlap check has not diagnosed the threshold's contact-versus-merger validity. If "accepted groups" instead means the harvested input parts before the new geometric cut, that must be stated explicitly.

**Smallest fix:** Measure overlap on candidates selected without criterion 6's geometric cut and retain both accepted and rejected cases, with an independently defined intact-contact fixture or validity criterion. Specify an empty-sample action. **Blocks approval: yes.**

### F10 — Medium: the native plan requires pipeline capabilities that are absent

**Location:** §10, lines 467, 534, 538, 545–558; §12, line 621. Existing pipeline: `tools/verify.py:39–60,77–101`; configuration: `tools/milestones.py:34–43`.

**Defect:** The proposal promises native compilation in preflight and permits panels up to three hours, but current preflight has no build command and every command stage has a fixed 3,600-second timeout.

**Failure scenario:** A valid design-gate projection of 90 minutes proceeds to registration and the recorded panel, which the existing pipeline kills after one hour. Adding a `preflight` stage to `milestones/c6.json` also fails the exact configuration schema. After a code fix, stop rule 9's instruction to resume from the failed stage contradicts the new dependency fingerprint, which invalidates earlier stages.

**Smallest fix:** Name the necessary permitted changes to pinned shared tooling: an enforced native build/toolchain check before execution and a registered stage timeout consistent with the approved runtime budget. State that resumption skips only stages verified for identical code; a code change restarts all stages invalidated by its fingerprint. Keep prior receipts and freeze metadata unchanged. **Blocks approval: yes; stop rule 8.**

### F11 — Low: exact contact and fixed stepping are inconsistent

**Location:** §3, line 129; §3a, line 177.

**Defect:** Fixed 0.02 approach steps do not generally reach a position whose minimum cross-part gap is exactly 0.6.

**Failure scenario:** Even along a collinear approach, initial separation 1.003 reaches 0.603 then 0.583; stopping at the latter violates the gap, while the former does not meet the written contact condition.

**Smallest fix:** Specify bracketing followed by a final root solve and a registered element-scale tolerance, plus deterministic handling of an inadmissible approach. **Blocks approval: no by itself; resolve in the drafter's amendment before implementation.**

### F12 — Low: individual endpoint claims need an explicit multiplicity scope

**Location:** §6, line 278; §7, line 319; §8, lines 356–387; §9, lines 418–420; §13, line 654.

**Defect:** The text explains the conjunction but does not state whether separately reported endpoint and extension verdicts are simultaneous claims or nominal individual claims.

**Failure scenario:** A reader treats every PASS among many 95% intervals as family-wise evidence. Selecting the largest worst-cell development gain among four candidates also makes that readiness gain optimistic; it is not independent corroboration of prediction.

**Smallest fix:** Label individual intervals/verdicts nominal unless a correction is registered, identify the central conjunction as an intersection-union requirement, and explicitly label selected development gains as selection-biased readiness measurements. Fresh final worlds already protect the final selected-recipe test; no post-hoc correction or redesign is requested. **Blocks approval: no.**

### F13 — Low: stop-rule ownership is not explicit row by row

**Location:** §12, lines 598–627; AGENTS.md, proposal-phase stop-condition rule.

**Defect:** The stop table omits a responsible-role column and row 12 combines different phase-dependent actions and roles in one row.

**Failure scenario:** A level-mixing defect is found before registration: the blanket implementer instruction to stop and await the owner coexists with an immediate drafter-fix instruction; after registration the same row instead assigns withdrawal to the implementer. This is less explicit than the required one yes/no row, one action, one role.

**Smallest fix:** Add the responsible role to every row and split phase-dependent conditions into separate rows; list subsequent drafter and owner actions separately from the initial STOP. **Blocks approval: no by itself.**

## A–I disposition

Here FOUND means a design defect was found in that area, not that every item in it is defective.

| Area | Disposition | Evidence |
|---|---|---|
| A. Theory alignment | FOUND | F5: the bounded-prediction claim is stronger than the scored rule. Locked definitions are otherwise preserved; the optional extensions stay outside H-C. |
| B. Level discipline | FOUND | F2, F4, F6–F8; row-by-row ledger audit below. |
| C. Implementability | FOUND | F1/F3, F8, F10–F11 require amendments for exact execution; F2/F6 identify reuse/sampling hazards that correct adapters can resolve. |
| D. Fairness/non-vacuity | FOUND | F1 compromises fake-group publication; F4 is vacuous for a permitted timescale ordering. |
| E. Predetermined outcomes | FOUND | F9 permits a guaranteed gate pass when its population is accepted level-3 candidates. No intact inferential result is established by C5 or by the void pilot level-3 result. |
| F. Statistics | FOUND | F7, F12; formation thresholds, world unit and six-gain conjunction are sound. |
| G. C++ engine | FOUND | F10 concerns integration into the pipeline, not the stated numerical-equivalence tolerances. |
| H. Process | FOUND | F10, F13; owner approval, drafter ownership, registration and evidence-review family split are otherwise explicit. |
| I. Claimed tests/omissions | FOUND | F3, F5, F7–F9: lift information, an accuracy bound, censoring rules, a complete linear recipe and independent overlap calibration are missing. |

## Normalization ledger: every row checked

| §3a line | Quantity | Result |
|---|---|---|
| 164 | Detector times | Own-level scaling sound; F4/F6 affect recursive observation. |
| 165 | Frequency tolerances | Sound inverse-time scaling. |
| 166 | Dimensionless detector statistics | Sound. |
| 167 | Links and kicks | Dimensionless intent sound; composite rigid movement conflicts with F2. |
| 168 | Criterion-6 windows | F4/F6. |
| 169 | Geometric overlap | Dimensionless, own-shape area fraction sound; F9 concerns calibration selection. |
| 170 | Degeneracy | Sound area normalization by the part's L². |
| 171 | Rate spread | Sound: δ_n C_n = 0.096; the stated typical drift is 1.68768 rad, not a deterministic guarantee for every random pair. |
| 172 | τ contexts | Alone versus in-world distinction sound; estimator/horizon/censoring incomplete (F7). |
| 173 | Intervention/sample times | Own-level scaling sound; F6 for the observation grid. |
| 174 | Doses and margins | Sound dimensionless phase quantities. |
| 175 | Push | Own published L required; primitive radius is not interchangeable (F2). |
| 176 | Element law/contact scale | Sound explicit fixed microscopic physics under the proposed D7 reading. |
| 177 | Placement steps | Correct element units; F11 concerns exactness. |
| 178 | Counts | Sound fixed counts at both transitions. |
| 179 | Effective recipe | Information intent sound; F8 leaves its finite-difference normalization unspecified. |
| 180 | Alternative partitions | Own sub-part level, same size profile and contiguity are sound; F1 affects their publication. |
| 181 | Element lift | Correctly evaluator-side and common element units; unavailable decoder information (F3). |
| 182 | Effective-state bounds | Sound own-level fractions; do not bound excited coarse error (F5). |
| 183 | Formation time | Bias from the scaled horizon disclosed; descriptive only. |
| 184 | Static-control rate shift | Sound constant shift preserves internal rate differences; do not replace it with element-wise zeroing. |
| 185 | In-place recovery | Sound own-level pattern test; avoiding imposed within-parent membership failure is appropriate. |

The six declared evaluator cross-level comparisons are legitimate: upward transfer, common element lift, flat-depth comparison, rigid-element decomposition, interface census, and views from below. The missing decoder must remain evaluator-side. Recursive validity may be computed by the owner and supplied as validity; it must not introduce descendant reads into the predictor.

## Checked and found sound

No entire A–I area is free of findings. These specific checks had no finding:

- **A:** §§3–5,7–8 of the locked core are treated as structural definitions. Stability/recovery thresholds are explicitly model-specific tests. Same-law closure and scale separation never enter H-C. “Same procedure, one physics; effective dynamics may differ” fits locked §7; the proposed standard/decision amendment must still occur before registration.
- **C/G:** `c5_coarse.run` can consume level-2 states with sibling-folded distance lists without inspecting descendants. Exact pairwise convex clipping is available; a union-of-convex-pieces implementation is feasible in new files. A raster alternative still needs its resolution and error bound registered.
- **D:** Imposed candidates prevent empty decoupled controls; meaningful transfer/downward effects carry 0.01-rad margins. Complete G→M and M→G ablations remove their entire pathways. Fixed-RMS phase and rigid-scale geometry ladders are coherent dose families. A channel-matched, in-world calibrated relaxation baseline is deliberately strong and fair when its calibration is recorded and never fitted on scored excitations.
- **E:** C5's push weakness motivates a useful pre-panel readiness stop; it does not logically predetermine fresh C6 outcomes. The pilot's level-3 formation result is explicitly void. Its recovery failures remain a disclosed risk, not proof of the new design's verdict.
- **F:** For n = 40, Wilson lower bounds are 0.495059 at 26 successes and 0.520177 at 27. Binomial pass probabilities at true rates 0.75/0.65 are 0.896768/0.440766. At n = 30, 21 successes suffice and the probability at 0.75 is 0.803407. The ten-world minimum, M = 5/minimum size 3, source-isolated harvests and one group per world support world-level analysis. Requiring all six gains at both transitions is conservative for the central conjunction; four-way development selection does not create a four-way search on fresh final evidence.
- **G:** The installed compiler identification matches `Apple clang version 21.0.0 (clang-2100.3.34.2)`. Exact neighbour indices/masks, ablation-aware single-step relative tolerance, 1,000-step held-neighbour tolerance and check 4's absolute floor are appropriate proposed checks. Identical candidate sets/outcomes on all 15 prespecified development worlds is a defensible fail-stop bar, plausibly achievable but not guaranteed under switching dynamics. No failed world may be discarded to obtain equivalence. This sample does not prove equivalence of every causal/statistical verdict on all future worlds; line 560 should be read within that limit. Check 4 preceding counted formation/calibration numbers is the correct order.
- **H/I:** Registration precedes every final-seed run; disjoint purposes and upstream source paths are specified; coverage requires every endpoint to be evaluated or explicitly not run. Claude's evidence review remains cross-family from Codex implementation, and this critique supplies the independent design check. Staging, fixed depth, absent noise, passive dynamics, C7 dissolution and C8 usefulness/efficiency are candidly excluded.

## Commands and scope

Inspection used these command families, with `sed` ranges and `rg` expressions narrowed to the cited sections; no command below launched a simulation:

```text
pwd
git status --short
git status --porcelain=v1
git rev-parse HEAD
git show --format=fuller --stat 6660692
git diff --stat
git diff --check
git config core.hooksPath
shasum -a 256 experiments/c6_proposal.md /Users/new/RiderProjects/RPG_theory/research/RRG_CURRENT/00_LOCKED_CORE.md
cat AGENTS.md
cat experiments/c5_manifest.json
cat evidence/c5_r003/HANDOFF.md evidence/c5_r003_review_codex/INDEPENDENT_REVIEW.md evidence/c6_dev_pilot/README.md
cat .githooks/pre-commit .githooks/commit-msg
clang++ --version
python3 -B /private/tmp/c6-design-review/probe.py
head -5 docs/reviews/c6_proposal_critique_codex.md
wc -l docs/reviews/c6_proposal_critique_codex.md
```

Additional read-only `rg`, `rg --files`, `nl -ba`, `sed -n` and `head` calls inspected:

- the complete proposal, including all six self-audits, decisions and role/stop table;
- theory files `00_LOCKED_CORE.md`, `05_CHANGE_CONTROL.md`, `06_PROOF_MATRIX.md`; framework §§3,5,15,16; mathematical core §§11–13,18–19,28,37–39;
- R4's recursive interface, C4–C6 and ten invariants;
- the complete frozen `c4_model.py`, `c5_detect.py`, `c5_compose.py`, `c5_coarse.py`; `c4_detect.py` statistics/kicks; `c5_units.py` harvest, geometry and constructors; named `c5_experiment.py` assignment, intervention, response-error, relaxation, e-fold and verdict functions;
- `docs/PROCESS_REVIEW.md`, `tools/verify.py`, `tools/milestones.py` and relevant hook/configuration definitions.

A quick registry search for `GeoMind|ai_RPG_test|c6_proposal` in the external memory registry returned no match; no prior memory claim was used. The temporary probe reads constructor syntax with `ast` and computes synthetic centroid, sampling, contact, Wilson/binomial, rounding and censoring examples with the standard library. It imports no project module, integrates no dynamics and consumes no development/final seeds. The probe was rerun after making its centroid example use three children.

The scoped commit commands are `git add -- docs/reviews/c6_proposal_critique_codex.md`, `git diff --cached --check`, `git diff --cached --stat`, and `git commit -m "Review C6 proposal design independently" -m "Assisted-by: Codex:gpt-6"`; the final scope is checked with `git show --stat --oneline HEAD` and `git status --short`.

Only this report is changed in the repository. The required commit runs the existing pre-commit and provenance hooks; those guards inspect freezes, registration/coverage and generated status. No pytest suite, C0 experiment, C4/C5 panel, smoke stage, mutation probe, design gate or verification pipeline was run. No proposal, code, manifest, STATUS.json, committed receipt or `.gate/` file was edited. Review completed within the requested 20-minute cap.
