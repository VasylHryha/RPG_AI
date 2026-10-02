Verdict: **ACCEPTED**.

Reviewer family: Codex
Reviewer model: gpt-6
Date: 2026-10-02 (Europe/Kiev)

Reviewed implementation and registration commit: `2b53c545096106812baf6469507f86768064906c` (`2b53c54`).
Reviewed evidence commit and initial checkout: `92814d1f1c7fccfe07590898b35720016d119931` (`92814d1`).
Reviewed `evidence/c5_r003/results.json` SHA256: `e51ec5c1f77f7df215a8b9cb285c0f20d0b9c798125089c04d15a248eda2fc85`.

The digest matches both the working file and the committed evidence blob. All 19 receipt-bound dependencies match the working checkout, registration commit and evidence commit. This is one independent review on committed experimental evidence, within the owner's approximately 20-minute cap. Production code, tests, manifest, earlier receipts, STATUS.json and .gate/ were not edited. Acceptance here concerns the bounded C5 implementation; the owner records milestone status.

Separately, **both recorded hypothesis verdicts follow registration: H-M level 2 SUPPORTED_WITHIN_SCOPE; H-C first transition INCONCLUSIVE**. H-M support requires the formation-near-threshold qualifier below. No recursion, next-level predictive accuracy, usefulness, efficiency or novelty is established.

## R002 findings F1–F4

| Finding | Status | Code, contracts and R003 receipt |
|---|---|---|
| F1, missing upper-facing composite | **fixed; new low gate gap N1** | `geomind/c5_units.py:163` composes the same state shape from children only. `geomind/c5_experiment.py:320` publishes it through the real accepted-group path at `:525`. The parent, its children, measured rates and validity are stored. Contracts at `tests/test_c5.py:587`, `:605`, `:610`, `:623` and `:631` cover composition, publication, missing count, unequal-size geometry and gate failure. The receipt contains 17 valid parents for 17 accepted candidates; direct per-world matching finds no duplicates or omissions. The endpoint/gate reject a total-count mismatch, but their global count is weaker than a per-candidate bijection (N1). |
| F2, crossing hulls admitted | **fixed** | `geomind/c5_units.py:78` clips convex polygons; `:98` computes maximum intersection-area fraction, and `geomind/c5_detect.py:77` enforces <= 0.2 through actual unit validity. `tests/test_c5.py:70` and `:81` cover contact and the crossing hexagons. Reviewer reproduction gives overlap 0.9278032303 for both hexagons and actual criterion-6 rejection; touching hexagons pass. An independent intersection construction agrees on 200 synthetic polygon pairs. R003 records each unit's worst window overlap and all candidates' criterion-6 values. The development calibration provenance has the low limitation N2. |
| F3, ties admitted more than k | **fixed** | `geomind/c5_coarse.py:51` selects exactly k candidates by stable sort, then applies the radius. Own neighbours precede cross ports; cross ties use port order. This policy is explicit and differs from C4's element-index tie ordering where those private indices are unavailable. The reviewer tie case now gives neighbour counts [8, 8] and no cross links; `tests/test_c5.py:547` also checks a free slot. The recorded coarse comparisons use this registered code. |
| F4, harvest sources shared between worlds | **fixed** | `geomind/c5_experiment.py:99` assigns each grouped source once and discards non-fitting templates. The runner restores source order at `geomind/run_c5.py:68` before assignment. Contracts at `tests/test_c5.py:563` and `:575` cover both assignment and the caller. The former split case now assigns [0,0,1,1,2] and [3,3,4,4,5]. All 30 receipt records store five source IDs; the 150 selected templates use 93 distinct harvest sources, with **zero shared across worlds**. |

### Parent semantics and the boundaries of F1's fix

I independently reconstructed all 17 parents' unweighted child-centroid means, radii of gyration, circular phases, coherence, phase patterns and hull ports. Their collective rates equal the mean of the children's measured intact-continuation rates, which also match the per-unit downward records. Child validity equals the corresponding world-window validity. Parent S retains the candidate's scalar criteria/recovery statistics and next-window prediction errors, including `parts_alive`; it is meaningful recorded validity, not an empty dictionary. The caller publishes only accepted candidates.

The hull of all child ports is a coherent convex-boundary rule: each child exposes its hull, so this reconstructs the convex hull of their union without reading descendants. Parent port positions and phase offsets are correctly re-expressed, and coupling-capacity lists are inherited from the selected child ports. Interior ports are deliberately omitted. No level-specific branch or manually authored parent geometry appears in this constructor.

The size-weighted natural rate is the **declared primitive-population mean**, whereas X, L and the mode describe the child-unit collection without size weighting. A synthetic 6/9/16-size case with rates -0.03/0/0.03 returns the declared natural rate 0.0096774194 and the unweighted centroid. That arithmetic is correct. It is not an independently measured isolated-parent drift rate: unequal child rates, internal coupling and inherited capacities can make the next-level approximation imperfect. Likewise, inherited capacities are not a newly measured parent-level neighbour census. These are predictive assumptions requiring a later full-versus-coarse comparison, not evidence that C6 already works. The synthetic level-3 construction and coarse-RHS consumption establish schema reuse only; they do not establish dynamical recursion. This does not block the bounded first-transition implementation with H-C explicitly INCONCLUSIVE.

## New findings, ranked by severity

### N1 — Low: global publication counts do not enforce a per-candidate bijection

**Locations:** `geomind/c5_experiment.py:691`, `:694`, `:697`; `geomind/c5_units.py:214`. **Blocks acceptance: no.**

The evaluator validates each supplied parent against its supplied children and compares total groups with total accepted candidates. It does not match each group to the accepted candidate in its own world. A concrete evaluator-only reproduction starts from a deep copy of the stored records:

```python
active = [w for w in copied_records if w["groups"]]
active[0]["groups"].append(copy.deepcopy(active[0]["groups"][0]))
active[1]["groups"] = []
# Leave candidates unchanged; evaluate only these copied stored records.
```

`level2_interface` still returns `{"published": 17, "accepted_candidates": 17, "problems": {}, "verdict": "PASS"}`. One world has a duplicate publication and another has none. No dynamics or receipt edit is involved.

The actual production caller constructs one group per accepted candidate, and I independently checked exact ordered unit-set matching for every committed world. The committed evidence therefore satisfies the intended contract despite this weaker guard. A durable regression should exercise duplicate/omitted/swapped publications and require matching within each world, keyed by candidate identity/unit set. Add that in an authorized future revision or separate new-file evaluator work; do not modify accepted files or rescore R003.

### N2 — Low: development overlap calibration is reported without its raw measurements

**Locations:** `experiments/c5_manifest.json:59`; `docs/decisions/0006-c5-r003-review-fixes.md:15`. **Blocks acceptance: no.**

The supplied committed materials state a development 99th percentile of 0.100 and maximum of 0.132, but provide no per-development-world hull-area records from which those numbers can be recomputed. This review verifies the overlap algorithm, its synthetic discriminatory behavior and its application to stored final criterion values; it does **not** independently verify those two development summary numbers.

The stated basis is reasonable as an operational contact-versus-interpenetration calibration: a fixed 0.2 cut exceeds the reported development contact range and rejects the concrete 0.928 crossing failure. It is not a universal physical merger boundary. The numeric cut was retained and the changed area-based meaning was registered before fresh final evidence, so this provenance limitation does not invalidate the panel. Retaining raw development calibration measurements in a future new artifact would make the rationale independently auditable without rerunning development dynamics.

No new high or medium finding was identified in this bounded review.

## Scope, registration and rescue

Decision 0004 approves this lane independently of C2; C3 remains unauthorized. The R001 withdrawal record, the R002 review and decision 0006 provide an explicit repair history. R001 and R002 receipts remain byte-identical to their introducing evidence commits; their recorded outcomes are preserved.

Comparing R002's committed manifest with R003 confirms unchanged placement radius **2.5**, rate half-width **0.03**, minimum gap **0.6**, **T = 3.2**, integration, intervention doses and primary doses, excitations, effective-state bounds, bootstrap settings, endpoint verdict rules/truth tables, numerical tolerances and **30 final worlds**. The numeric overlap threshold remains **0.2**, while its geometric definition changes as the F2 repair requires. Source isolation raises the harvest ratio from 1.3 to 1.5, and publication adds the `level2_interface` gate/endpoint. These changes are disclosed and directly respond to F1–F4; they do not create a new formation setting or weaker causal/coarse pass rule.

The R003 final entropy **6141758840824254324** differs from R002's **1348336910983156933**, R001's **7961019210925654807** and development entropy **22222**. Registration precedes evidence and all recorded stages name the registration commit. A digest/commit audit establishes these facts, not the randomness of the original entropy draw or the absence of hypothetical unrecorded private runs. The inspected history and supplied artifacts show an explained repair on fresh registered seeds, not a post-hoc verdict change or unexplained settings rescue.

Source-isolation discards follow harvest order and the remaining capacity of a world, before assembly/formation. They can change the template distribution, so R003 is not an unchanged replication of R002. They do not select templates by final formation or causal success. Each harvest source's seeded generation is separate; templates from one source may remain dependent within a world, which the registered world-level analysis accommodates.

## Detector, interventions, comparisons and receipt

- **Information boundary and C4 reuse:** the detector reads X, Theta and owner-computed validity; it never receives primitive members, intrinsic rates or fixture labels. The owner/evaluator uses original member sets to compute validity and translate interventions. Criteria 1–5 reuse frozen C4 functions. Only window, frame interval and recovery time scale by T, and frequency tolerance by 1/T; other thresholds are unchanged. All recorded audit rows pass. Criterion 5 retains original-to-control, original-to-kicked and control-to-kicked agreement, not merely agreement between two fragmented futures.
- **Causality and doses:** matched G→M branches share the phase probe; the complete ablation removes distance weighting and freezes phase topology. M→G sets J=0. All 17 group records have both complete-ablation effects **exactly 0.0**. This is expected by construction; intact effects and dose ladders supply the informative evidence. G→M uses rigid scales 1.1/1.25/1.5; M→G uses zero-mean fixed-RMS kicks 0.5/1.0/1.5, with newly sampled directions per dose. This is a controlled distribution family, not one direction scaled three times.
- **Coarse prediction:** the scored run has no reopening callback and no later full-state injection. The separate reopening protocol and invalid flags remain reported. Coarse evolution reads published constituent states and ports without descendant scans. Phase branch alignment uses only t0. Response error excludes the excited unit and combines RMS wrapped phase error with RMS position error normalized by the responding unit's L. Every stored gain equals the mean of its two excitation errors, baseline minus **open-loop** coarse error.
- **Strong comparison and limits:** all three baselines are required: no transfer, rigid transfer and relaxation using the group's tau2 measured from the intact probe control, not fitted to held-out excitations. That calibration advantage is declared. Three of 34 excitations are flagged invalid. Work and frequency/recovery errors are recorded descriptively; there is no efficiency claim. Full lower dynamics remain active and interventions impose lawful rigid boundary changes rather than deleting children.
- **Controls:** each receives 25 imposed candidates and accepts zero. Every spread-control candidate fails criterion 3; every static-control candidate fails criterion 5. The static control has no criterion-3 or criterion-4 failures. Additional failures coexist, so these controls exercise the intended reasons without isolating them as the sole failure.
- **Detail and uncertainty:** all 19 endpoints appear as evaluated with matching values and verdicts; none is silently test-only or missing. Per-unit validity is present for rejected and accepted candidates; per-group criteria, recovery scores, child/parent states, effects and excitation errors are retained. Inferential summaries use 17 formed-world observations rather than frames or constituent counts. Effective-state bounds hold for 16/17 parents. Timescale separation uses each group's tau2 divided by its own units' mean tau1: mean **3.38956**, CI **[2.60574, 4.32326]**, with zero censored tau2 groups. The C4 component view is disclosed: 17/17 accepted groups are single C4 components; it does not alone prove all C4 resonator criteria for their union. Criterion 6 and timescale separation carry the distinct-parts claim.
- **Process:** PIPELINE.json attests one ordered preflight → tests → smoke → mutation → panel sequence, all for the same fingerprint and registration commit. Every referenced artifact hash and the read-only verified stamps match. The committed focused report has 46 passing contracts; MUTATION.json has 52/52 detected, no timeouts, survivors or problems. The runner itself calls `milestones.check("c5", "panel")` before final execution. C4's ten frozen files and three historical shared-tool pins pass `tools/accepted_freeze.py`; the preserved historical C4 assertion about C5–C8 status is not treated as a current C5 finding.

## Do the hypothesis verdicts follow the registered rules?

**Yes.** This conclusion is separate from implementation acceptance and from the scientific strength of the resulting support statement. Recomputing the 17 stored-record evaluator endpoints reproduces their values, bootstrap intervals and verdicts exactly; coverage also includes the audit and numerical endpoints. An independent truth-table transcription agrees on **39,366** combinations, including upper bounds immediately below, exactly at and above 0.25. Boundary probes and a nine-formed-world evaluator case confirm that all eight inferential endpoints remain INCONCLUSIVE below ten formed worlds; formation has its own FAIL rule there.

- **H-M level 2:** formation is **17/30 = 0.566667**, which exceeds the registered point-estimate cut 0.5 and supplies at least ten formed worlds. G→M, M→G and both dose directions pass, with complete ablations exactly zero. Row 1's causal FAIL condition does not apply; **row 2 gives SUPPORTED_WITHIN_SCOPE**; row 3 is the fallback and is not reached.
- **H-C first transition:** formation's Wilson upper bound **0.726225** does not meet row 1's strict < 0.25 rejection. Downward effect, emergent transfer, effective state and timescale separation pass. The coarse gain over relaxation is **0.00790824**, CI **[-0.00403674, 0.01878750]**: INCONCLUSIVE, while gains over the other two baselines pass. No composition endpoint FAIL triggers row 2; row 3 requires all five PASS and therefore does not apply; **row 4 gives INCONCLUSIVE**. An interval spanning zero does not demonstrate equivalence, dominance or added predictive value over relaxation.

### Required formation-near-threshold qualifier

The handoff adequately discloses formation of **15/30, 13/30 and 17/30** across R001–R003 and explains why their changed designs cannot be pooled. R003's Wilson interval is **[0.391973, 0.726225]**; it includes 0.5. The registered rule tests the observed fraction, not whether the interval's lower bound exceeds 0.5. Requiring the latter now would retroactively replace registration and would be improper.

Nevertheless, threshold crossing is fragile evidence of reproducible formation at or above one half, particularly after a sequence of corrective revisions. Any support summary should explicitly say: **“H-M is supported within the registered R003 scope for the formed groups; formation is near the pass threshold, and this panel does not establish a population formation rate above 50%.”** This qualifies the strength and scope of support without changing the recorded verdict. No robust formation guarantee or H-C support should be inferred, and acceptance does not itself authorize a subsequent milestone.

## Verification performed

Exactly these executable checks were run during this review:

1. `.venv/bin/python -m pytest -q -x` — **237 passed in 54.10s**, once, with no production/test edits.
2. `shasum -a 256 evidence/c5_r003/results.json` — matches the required digest quoted above.
3. `.venv/bin/python /private/tmp/c5_r003_review_checks.py` — **PASS**: committed receipt and 19 dependency identities; registration order; preserved R001/R002 receipts; unchanged R002 settings and fresh entropy; ordered stage hashes/read-only stamps; 46 recorded contracts and 52 recorded mutants; 17 stored-endpoint recomputations including CIs; 19-endpoint coverage; 25 independent summary means/counts and Wilson arithmetic; per-world publication matching and source isolation; per-unit/group validity, rates, exact zero ablations, gain arithmetic and control reasons; 39,366 truth-table cases; 57 endpoint boundary cases; all eight inferential endpoints INCONCLUSIVE with nine formed worlds; crossing/touching hexagons through real validity, 200 independent clipping checks, exact-k ties and source-assignment callers. Its deliberate duplicate/omission negative control reproduced N1. It asserts that no world dynamics are called for evaluator checks.
4. `.venv/bin/python /private/tmp/c5_r003_parent_probe.py` — **PASS**: independent reconstruction of all 17 parent geometries, modes and ports; synthetic unequal-size/nonzero-rate composition; level-3 schema construction and coarse selector/RHS consumption without integration or descendants. These additional probes address the new constructor's semantics, not another experimental panel.
5. `python3 tools/accepted_freeze.py` and `python3 tools/status.py --check` — both exit **0**. `git config core.hooksPath` reports `.githooks`.
6. Read-only `git status/rev-parse/log/show/diff/merge-base`, `cat`, `nl`, `sed`, `rg`, `jq` and file/hash/XML inspection of AGENTS.md, the specified R4 sections, proposal, approval/repair decisions, R002 review, R003 manifest/configuration/code/tests/mutants/evidence, and generic gate/pipeline/freeze/hooks.

The two reviewer scripts are temporary and are not part of the commit. The N1 regression and N2 calibration records deserve durable future coverage as described above. No recorded panel, smoke stage, mutation probe, verify pipeline, C0 experiment or final-seed world simulation was run. The report is the only task-owned repository change.
