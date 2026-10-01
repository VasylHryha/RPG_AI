Verdict: **CHANGES_REQUIRED**.

Reviewer family: Codex
Reviewer model: gpt-6
Date: 2026-10-02 (Europe/Kiev; review began 2026-10-01)
Owner-requested self-audit: 2026-10-02; amendment of this same review, not another experimental review.

Reviewed evidence commit: `6e8421434df1af4b4aae0243a4bb81e7025b687d`.
Reviewed implementation and registration commit: `b5dbc6810fdf2965728a2270228d36842775ef8d`.
Reviewed `evidence/c5_r002/results.json` SHA256: `a2c4f52fdd2c86696b81659beeea84729cb7084cbe243a11bb3d47322d840407`.

The receipt digest is verified against both the working file and the committed evidence blob. All 19 receipt-bound C5 dependencies match registration, evidence and the inspected checkout (`744ea556ad1d041ae967abd7b7f69e8692ebf417`). Commits `abb1447` and `744ea55` are the separate freeze-pinning review, not C5 dependencies. This is one independent review of R002, using committed experimental evidence and temporary reviewer probes. No experimental stage was rerun.

Implementation acceptance requires changes for F1 and F2 below. Separately, **both recorded hypothesis verdicts follow the registered rules: H-M level 2 INCONCLUSIVE and H-C first transition INCONCLUSIVE**. The implementation findings do not authorize replacing the recorded verdicts or editing this receipt.

## Findings, ranked by severity

### F1 — High: the accepted composite never becomes the promised upper-facing unit

**Locations:** `geomind/c5_experiment.py:312`, `geomind/c5_experiment.py:300`, `geomind/c5_experiment.py:503`, `geomind/c5_experiment.py:624`; `geomind/c5_units.py:105`. **Blocks acceptance: yes.**

The approved proposal explicitly promises a level-2 `ResonatorState`: centroid of unit centroids, their radius of gyration, their collective phase/rate, boundary units' ports, and criteria 1–6 plus prediction errors in S (`experiments/c5_proposal.md:79`). The R4 recursive interface and C5 composition contract require the new resonator to expose the same object shape upward (`GEOMIND_GEOMETRIC_AI_QUALITY_STANDARD_R4.md:297`, `:315`). None of the 21 registered changes withdraws this requirement.

An AST inspection of every `geomind/c5_*.py` file finds exactly one production call to `resonator_state`: `states_at()` at line 312. It creates **level-1** states using the default `level=1`, with `rate=0.0` and empty validity. The coarse model evolves this list of constituents. Detection returns candidate statistics; `group_runs()` returns effects and comparison metrics; `run_worlds()` records these dictionaries. No path constructs or publishes the composite's state. Recursively inspecting all 30 receipt records finds no `level`, `effective_position`, `characteristic_size`, `mode_signature`, `boundary_ports`, or `member_digest` field. The 13 groups contain only constituent IDs and experimental statistics.

`effective_state_l2` passes by checking three scalar errors already in candidate statistics. That calculation follows the registered numerical rule, but it does not establish that the parent interface exists. Merely setting the existing helper's `level` argument to 2 would also use primitive-member geometry rather than the approved unit-centroid geometry. This omission concerns completing the **first** composition step, not demanding a C6 experiment.

For the next revision, implement and exercise publication of the accepted parent's effective state through the declared contract, with meaningful rate and validity fields, while keeping constituent ownership private. A durable contract should check this actual promotion/output path, including rejection of unaccepted candidates; the present interface test checks only a constituent (`tests/test_c5.py:45`). No such test or implementation was added during review.

### F2 — Medium: the distinctness proxy misses strongly interpenetrating units

**Locations:** `geomind/c5_units.py:67`, `geomind/c5_units.py:74`, `geomind/c5_detect.py:81`; `experiments/c5_manifest.json:195`. **Blocks acceptance: yes.**

The implementation correctly computes its registered proxy: the fraction of hull vertices strictly inside another hull. However, this proxy is insufficient for its stated purpose of excluding interpenetration/merger. Hull edges can cross without either hull containing a vertex of the other. Criteria 2–4 on original member sets do not independently detect this geometric failure.

A synthetic probe, with no dynamics or panel data, uses two **six-member** regular hexagons:

```python
import numpy as np
from geomind.c5_units import port_overlap

a = np.arange(6) * np.pi / 3
h1 = np.c_[np.cos(a), np.sin(a)]
h2 = np.c_[np.cos(a + np.pi/6), np.sin(a + np.pi/6)] + [.01, .01]
port_overlap(np.vstack([h1, h2]), np.repeat([0, 1], 6), [0, 1])
# [0.0, 0.0]
```

Independent convex-polygon clipping gives intersection area **2.4105035014**, or **92.7803% of either hull's area**. These have different centroids and no coincident members. A simpler crossed-rectangle probe also returns zero overlap. The owner-requested self-audit repeats this configuration for 31 frames with constant phases, computes the actual `unit_validity()` values, and passes those results to `parts_alive()`: both units have shape CV, lock deviation, frequency change, pattern change and port overlap **all zero**, and criterion 6 returns `True`. This strengthens the original isolated-proxy probe without assuming or hand-writing passing internal statistics. This is not the intentionally permitted case of ports merely touching. It remains a synthetic criterion-6 counterexample, not a claim that the complete dynamical formation protocol accepts these static frames.

The change from own-neighbour fraction to a geometric proxy is defensible in principle: contact area need not mean merger. This particular proxy has a concrete blind spot. The recorded scalar overlaps cannot determine whether it affected any of the 13 final groups, and I did not regenerate those worlds. Thus this finding does **not** assert that any particular recorded group is merged; it establishes that the stated merger exclusion is not adequately enforced.

The timescale endpoint supplies useful dynamical evidence of slower between-unit relaxation, but a ratio above 1 does not repair a geometric test that admits almost coincident hulls. Strengthen the distinctness test or provide a justified restriction that excludes this configuration. The hexagon crossing case deserves a durable regression in the next revision, alongside the existing containment test (`tests/test_c5.py:66`). A change to this registered design requires the repository's new-revision process, not rescoring R002.

### F3 — Low: exact distance ties change the coarse neighbour rule

**Locations:** `geomind/c5_coarse.py:58`, `geomind/c5_coarse.py:60`, `geomind/c5_coarse.py:62`; frozen reference `geomind/c4_model.py:77`. **Blocks acceptance on its own: no; correct in the next implementation revision.**

The coarse selector includes **every** candidate with distance <= the kth distance. C4 takes exactly the first k candidates with a stable argsort. A synthetic `CoarseState` with eight own-neighbour distances of 0.5 and one cross-port distance of 0.5 gives `n_p=9` and selects the cross port at k=8. The frozen selector admits only eight neighbours. The earlier report's unqualified statement that the selectors use the same rule missed this boundary case. No recorded final-world impact is established. Use an exact-k selection with a declared tie policy and a durable tie control; do not modify frozen C4 code.

### F4 — Low: shared harvest provenance limits the independence claim

**Locations:** `geomind/c5_units.py:41`, `geomind/run_c5.py:68`, `geomind/c5_experiment.py:98`, `geomind/c5_experiment.py:503`. **Blocks acceptance on its own: no; uncertainty/provenance limitation.**

Each assembled world has its own RNG and each template is used once, but multiple templates may come from the same C4 harvest world. The receipt's 205 eligible templates from 195 harvest worlds establish that some harvest sources contribute multiple eligible templates. Slicing the global ordered pool in groups of five can split one harvest source across two assembled worlds. A synthetic assignment with source IDs `[0,0,1,1,2,2,3,3,4,4]`, using the actual `build_worlds()` selection with assembly mocked, gives `[0,0,1,1,2]` and `[2,3,3,4,4]`. The shared upstream randomness means full independence over both harvest and assembly is not guaranteed by disjoint assembly seeds. Source IDs are present in templates but omitted from the receipt records, so whether and how much sources were actually shared across final-world boundaries cannot be audited from stored records without regenerating worlds, which was not done.

My original wording “13 independent worlds” was too strong. There are 13 separately seeded assembled-world observations. The registered world-level bootstrap is reproduced correctly; inference conditional on the harvested templates must be distinguished from uncertainty over independent fresh harvests. Preserve template-to-source assignments in future receipts and justify the uncertainty scope, or isolate harvest sources per assembled world under a new registration. This does not change R002's registered verdict arithmetic.

## Withdrawal legitimacy and the registered design

The R001 withdrawal is legitimate under AGENTS.md's pre-review design-defect procedure. Decision 0005 records the withdrawal; no R001 review is present in history, and R001's evidence remains byte-identical to its evidence commit. Its recorded INCONCLUSIVE verdicts were preserved. The R002 registration precedes its evidence commit, and the final entropy changes from `7961019210925654807` to `1348336910983156933`.

Comparing the committed R001 and R002 manifests confirms unchanged level-1 selection, placement radius **2.5**, rate half-width **0.03**, minimum gap **0.6**, **T=3.2**, maximum port overlap **0.2**, detector and effective-state thresholds, sample size **30**, and the other non-revised settings. The identified protocol changes are explicit: the M→G family/primary dose, open-loop scoring, a stronger relaxation baseline, timescale separation with censoring, and disclosure of the C4 component view.

The dose-defect explanation is independently reproducible using **random numbers only**. With 200,000 three-unit draws from reviewer seed 90317, RMS wrapped pairwise size is **1.72486 ± 0.56166** for independent uniform offsets, versus **1.73205** with effectively zero variation for zero-mean RMS-1 kicks. “Same mean” is an approximation, but the important claim is correct: uniform offsets are not a controlled higher dose. RMS-1.5 kicks have mean effective size **2.27807** in the same probe. No final-world outcomes were used in this check.

The replacement ladder improves the validity of the dose test; it is not accurate to characterize that repair itself as necessarily making every pass harder. Open-loop scoring, the additional baseline and the additional H-C endpoint do make the comparison stricter. The disclosed defect-based rationale, preserved earlier evidence, unchanged settings and fresh registration support a design repair, not a relabelling or post-hoc rescue of R001.

## Detector, interventions, coarse comparison and controls

- **Information boundary and frozen criteria:** `c5_detect` receives unit X, Theta and owner-computed validity, never primitive member lists, intrinsic rates or fixture labels. The full-model owner/evaluator translates rigid interventions and supplies resulting unit states. Components, locking, statistics, kicks and criteria 1–5 use the frozen C4 functions. Only window, frame interval and recovery time scale by T, and frequency tolerance by 1/T. Recovery at `c5_detect.py:61` retains the original unit set in both futures and the agreement between matched futures, exactly the C4 R003 rule.
- **Hierarchy evidence:** original constituent sets are checked with their own C4 criteria 2–4, and per-unit values are recorded for accepted and rejected candidates. The separation statistic uses each group's tau2 divided by the mean tau1 of its own units, then averages by world. Its recorded mean is **3.20999**, CI **[2.74694, 3.66114]**, with **0/13** tau2 values censored. This is a meaningful operational dynamical test under the registration, not proof that every stable partition is a hierarchy. The receipt and handoff correctly disclose that the frozen C4 **component** rule sees **13/13** groups as one component; they do not thereby establish that the union passed all C4 resonator criteria. F2 remains material.
- **Matched pathways and dose families:** the G→M pair uses the same unit-phase probe and s0 phase topology; its complete ablation sets w=1 and freezes that topology. M→G sets J=0. All 13 group records have both complete-ablation effects **exactly 0.0**, as expected by construction. Intact effects and dose response are the informative evidence. G→M uses rigid scales 1.1/1.25/1.5; M→G uses the same zero-mean fixed-RMS construction at 0.5/1.0/1.5. The latter samples a new direction for each dose, so it is a controlled distribution family, not the same realized direction scaled three times.
- **Coarse information and scoring:** `CoarseState` reads only published constituent states, their ports, capacities, natural rates and sizes; it does not scan descendants. Links grow/break using nearest-within-radius port selection, with the exact-tie discrepancy in F3. The scored calls at `c5_experiment.py:342` have no reopening callback. Phase alignment uses only the initial branch. Full trajectories enter scoring and the separately reported reopened protocol, not later open-loop updates. The primary error is RMS wrapped phase error plus RMS position error normalized by each responding unit's L, excluding the excited unit. Every stored group gain equals the mean of its two excitation errors, baseline minus **open-loop** coarse error.
- **Relaxation baseline:** it uses the same group's tau2 from the intact G→M control, not a fit to the scored excitations. This calibration advantage is registered and disclosed; it is a reasonable, stronger comparison. No-transfer and rigid-transfer are weaker comparators, and acceptance of the primary coarse endpoint requires beating all three.
- **Controls:** each has **24 imposed candidates**, zero accepted. Every spread-control candidate fails criterion 3; every static-control candidate fails criterion 5. Other failures coexist, so these are not isolated single-cause rejections, but the intended rejecting reasons are genuinely exercised. The static control has no criterion-3 or criterion-4 failures.

## Do the hypothesis verdicts follow registration?

**Yes, separately from implementation acceptance.** The endpoint rules and ordered truth tables match the manifest. Reviewer checks covered **39,366** truth-table combinations, including the strict Wilson-upper-bound boundary at 0.25, and **42** endpoint rule/boundary checks. The everyday suite also checks the minimum sample size for all eight inferential endpoints. Formation has its separately registered FAIL rule below ten formed worlds; small samples do not produce causal/composition support.

All **18** manifest endpoints appear as evaluated, with matching value and verdict; none is silently test-only. All stored inferential summaries have **13 separately seeded assembled-world observations**, rather than treating frames or constituents as trials; the upstream-independence limitation is F4. Recomputing the evaluator from stored records reproduces all **16** evaluator endpoints exactly, including bootstrap intervals. The remaining two endpoints are the same-rule audit and numerical checks. Independent arithmetic also reproduces the Wilson interval, 25 summary means/sample counts, per-group gains and downward-effect aggregation.

- **H-M level 2:** formation is **13/30 = 0.433333**, below 0.5, so `formation_l2=FAIL`. G→M, M→G and dose response are PASS. Row 1 does not apply; row 2 requires formation PASS; **row 3 gives INCONCLUSIVE**.
- **H-C first transition:** formation Wilson interval is **[0.2737748558, 0.6080269300]**, so row 1's upper bound <0.25 does not apply. Downward effect, emergent transfer, effective-state numerical bounds and timescale separation are PASS. The coarse gain over relaxation is **−0.0039887522**, CI **[−0.0206073761, 0.0107173758]**, hence `coarse_vs_full=INCONCLUSIVE`; its other two gains have positive CIs. There is no FAIL composition endpoint for row 2. Row 3 also requires H-M support and all five composition endpoints PASS. **Row 4 gives INCONCLUSIVE**. Formation failure would already prevent support even if the coarse endpoint passed.

“Ties relaxation” is an informal description of an interval spanning zero, not a demonstrated equivalence or a registered NOT_SUPPORTED result. Neither hypothesis should be called supported. These findings do not promote C6 or claim recursion, utility, efficiency or novelty.

## Verification performed

The following are the review's executed checks, distinct from inspection of the implementer's earlier run:

1. `.venv/bin/python -m pytest -q -x` — **228 passed in 96.73s**. Run once; no production/test edits.
2. `shasum -a 256 evidence/c5_r002/results.json` — exact required SHA256 above.
3. `.venv/bin/python /private/tmp/c5_r002_review_checks.py` — **PASS**: committed receipt/manifest/dependency identities; 19 C5 dependencies; all 24 C1 and 43 C2 receipt-bound files; ten C4 frozen files and three historical pins; stage artifact hashes and verified stamps; 37 passing recorded contracts; 41/41 recorded mutants detected with no timeouts; unchanged R001 evidence/settings and fresh entropy; 16 stored-endpoint recomputations; 18-endpoint coverage; raw group arithmetic, zero ablations and controls; 39,366 truth-table cases; random-only dose comparison; crossed rectangles; AST and receipt inspection establishing F1. An initial invocation's output was lost in a server restart; only this read-only/probe script was repeated to recover the result. It executes no world dynamics.
4. `.venv/bin/python /private/tmp/c5_r002_geometry_probe.py` — **PASS**, reproduced F2 with two six-member hexagons and independently clipped their hulls. NumPy emitted deprecation warnings for two-dimensional `cross`; the numerical results and assertions passed.
5. `.venv/bin/python /private/tmp/c5_r002_rule_probe.py` — **PASS**, 42 endpoint boundary checks, independent Wilson arithmetic and 25 summary means/sample sizes. No simulations.
6. `python3 tools/accepted_freeze.py` and `python3 tools/status.py --check` — both exit **0**. `core.hooksPath` is `.githooks`.
7. Read-only `git log/show/diff`, `cat`, `nl`, `sed`, `rg` and `jq` inspection of AGENTS.md, the specified standard/proposal/decision/manifest/code/tests/mutants/configuration, committed evidence, generic gate/pipeline/hook code and the separate freeze-pinning report. Git comparison confirms registration before evidence, no C5 dependency change between those commits, and no changes to R001 evidence. No earlier independent C5 review is present in the inspected history.
8. Owner-requested self-audit: `.venv/bin/python /private/tmp/c5_r002_review_self_audit.py` — **PASS**. Reverified the receipt and all 19 dependencies against the original hashes and the current freeze guard; explicitly checked all six missing state fields and the constructor path for F1; exercised actual unit-validity calculation for F2; reproduced the exact-tie discrepancy for F3; and demonstrated the possible cross-world harvest-source split for F4 with assembly mocked. No world dynamics ran. Production code stayed unchanged, so the previously passing everyday suite was not repeated. Only this existing report was amended.

The available artifacts attest one ordered pipeline: preflight **0.10s**, contracts **9.35s**, development-only smoke **60.35s**, parallel mutation **36.09s**, recorded panel **247.85s**, all at `b5dbc68`. Artifact bytes reverify, including the smoke's development designation. The runner itself calls `milestones.check("c5", "panel")`. This validates the recorded process; local artifacts cannot prove the absence of unrecorded executions.

No recorded panel, smoke stage, mutation probe, `tools/verify.py`, or final-seed simulation was executed during review. No production code, manifest, committed experimental evidence, STATUS.json or gate stamp was changed. The historical C4 helper's NOT_STARTED assertion was not treated as a C5 finding. Temporary probes were kept outside the repository; only this report is committed. The owner retains status authority. Under AGENTS.md, acceptance fixes belong in a newly registered revision on fresh seeds, with R002 evidence preserved.
