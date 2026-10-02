# C6 principle audit and reuse plan

2026-10-02, Codex (gpt-6), source HEAD `e803af7`. Owner-requested audit/drafting, **not independent evidence review or approval**.
Read locked core first, then RRG 01–08; checked R4, AGENTS, the three proposals, decisions, all eight C6 reviews,
native/Python sources, test contracts and stored development records. The owner's current specification governs.
KEEP/FIX/DROP below describe future use; all committed evidence, decisions and reviews stay unchanged.

## Verified record

`STATUS.json` records C0, C1 R006, C2 R002, C4 R003 and C5 R003 accepted; C6 blocked. C6 manifest/config do not exist.
Accepted C4/C5 frozen hashes and receipt hashes, plus the C1/C2 receipt-bound files, match current bytes.
Stored gate gzip SHA256: `a6b6069bd4ebf3b6280ca0060f54a5ad2df4ef399194215996dd4f9f366cacdb`;
uncompressed SHA256: `02ea2b3e0b4d610131babe2d6f1d8205e54a1143bb5411bb82183b79baf0992b`; both match SUMMARY.
Reading the raw receipt confirms pass 1: 18/30 at level 2, 0/30 at level 3 (29 MERGED), STOP 2, no pass 2/readiness.
Direct parts: 7/150 overlap failures, 4/150 dynamic failures; deeper parts: 167/606 overlap failures.
Alone record: 1/606 overlap, no dynamic failures, 87 groups failing overlap only in the world.
These are development measurements under the old rule. They establish neither a revised formation rate nor H-C/H-M.
The stored check-4 comparisons report exact agreement on the tested worlds; speed claims remain prior measurements, not re-benchmarked here.

## Item-by-item disposition

| Item | Disposition and reason |
|---|---|
| RRG `00_LOCKED_CORE.md` | KEEP — §§3–8 define closure, active parts and recursion; physical extensions are explicitly separate. |
| RRG `01_world_explanation.md` | KEEP as explanation — the AI loop is relevant; physical examples impose no model constraints. |
| RRG `02_scientific_framework.md` | KEEP as research context — slower scales, energy accounting and force derivations are downstream hypotheses, not C6 prerequisites. |
| RRG `03_mathematical_core.md` | KEEP as candidate methods — equations and implementation thresholds do not redefine the loop. |
| RRG `04_status_and_blockers.md` | KEEP as theory context — its physics blockers are not GeoMind milestone gates. |
| RRG `05_CHANGE_CONTROL.md` | KEEP — examples and equations cannot silently narrow definitions. |
| RRG `06_PROOF_MATRIX.md` | KEEP — distinguishes recursive organization from optional same-equation/force claims. |
| RRG `07_EMERGENT_INTERACTION_EVIDENCE.md` | KEEP as extension evidence — no requirement to introduce weaker binding or a new interaction channel in this AI. |
| RRG `08_ADDITIONAL_PRIMARY_EVIDENCE.md` | KEEP as context — domain-specific realizations add no universal thresholds or identical-mechanism requirement. |
| R4 C6/interface/recursive invariants | KEEP — both transitions, no parent labels, one procedure, active parts, up/down transmission and held-out bounded prediction. |
| `experiments/c6_proposal.md` | FIX by supersession — retain history and D2–D8; replace expanded gates and contradictory recursive wording with revision 2. |
| Amendment A1 | KEEP — undefined timescales must stop before pass 2 requires them. |
| Amendment A2 sampler | DROP from required path — specificity itself is unnecessary; retain the historical bounded-sampler repair. |
| Amendment A2 fidelity reference | FIX by supersession — repeated deterministic runs from the same snapshot are not an independent accuracy reference. |
| Amendment A2 check-4 inputs | KEEP — equivalence harvests are inputs, not formation/readiness evidence. |
| Amendment A3 | KEEP and implement — criterion 6 protects direct parts; deeper transformations are diagnostic. |
| `experiments/c6_redesign_proposal.md` | DROP as current plan — force/binding analogies do not justify mandatory new channels, repulsion or an extra diagnostic fork. |
| Previous `experiments/c6_proposal_r2.md` draft | FIX — retain direct-part correction; restore effective-state validity, exact prediction/censor rules, ledger and stop ownership; remove unsupported time promise. |
| `docs/decisions/0007-rrg-reading-of-same-rule.md` | KEEP — same procedure at both scales; “physics” means chosen computational dynamics, not physical-force constraints. |
| `docs/decisions/0008-approve-c6.md` | KEEP — historical approval and D2–D8, including D3's development target; it does not approve revision 2. |
| `docs/decisions/0009-c6-stops-at-design-gate.md` | FIX by new record 0010 — keep STOP/data; supersede the claim that deeper overlap violates locked §5 or proves recursion stalls. |
| AGENTS proposal: drafter owns fixes | KEEP — Codex now owns the requested rewrite; no requirement to send its defects back to the previous author. |
| AGENTS proposal: no pre-approval project runs/pilot custody | KEEP — owner-requested pilots have separate entropy and committed scratch records; no automatic diagnostic permission. |
| AGENTS proposal: normalization ledger | FIX here — measured scales/no per-level hand-tuning do not imply a blanket ban on scale ratios or composition from child summaries. |
| AGENTS proposal: yes/no stop/action/role | KEEP — makes the authorized boundary explicit; no extra scientific gate follows from its table format. |
| `native/c6/element_law.cpp` | KEEP unchanged — same element-law/RK4/neighbour semantics as reference; stored comparisons support reuse, not universal bit identity. |
| `geomind/c6_native.py` | KEEP unchanged — explicit native backend, no hidden NumPy fallback, reference types read-only. |
| `tools/build_c6.py` | KEEP unchanged — D6 compiler/flag refusal and source/binary build hashes; pin them in registration. |
| `geomind/c6_compose.py` | KEEP unchanged — common contact placement, rigid operations and constant rate shift preserve the approved fixtures. |
| `geomind/c6_units.py` | KEEP core unchanged — isolated-rate estimator/wrapper, `compose_state` sibling capacities, interface validator and source-isolated harvest implement D2/R4. |
| `geomind/c6_levels.py` | FIX — parent `ok` still contains `all(r['ok'] for r in nested)`; remove deeper veto and deeper timing requirements, retain own-window checks and direct union geometry. |
| `geomind/c6_effective.py` | FIX partially — reuse E1/E2, normalized Jacobian, general exponential, linear input and certified scoring; add missing validity/reopening behavior for E2 to satisfy R4 invariant 8. |
| `geomind/c6_experiment.py` | FIX — reuse assembly/harvest/publication/timescale/readiness helpers; replace revision-1 ledger/function dependencies and finish the common recorded endpoint/verdict protocol. |
| `tools/c6_design_gate.py` | FIX — new output and RNG purposes, direct-part rule, lean checks and revised projection; remove old extra vetoes and specificity workload. |
| `tests/test_c6.py` | FIX — retain applicable engine/geometry/composition/scoring contracts; replace tests requiring deeper failures to veto intact direct parts and retire specificity/blanket no-level-branch tests. |
| `evidence/c6_design_gate/results.json.gz`, `README.md` | KEEP unchanged — correctly preserve the actual STOP and unevaluated later steps. |
| `evidence/c6_design_gate/SUMMARY.md` | FIX interpretation via 0010, preserve bytes — measurements remain; overlap is not proof that active lower state was eliminated. |
| `alone_diagnostic/alone_check.py`, `alone_check.json.gz` | KEEP unchanged — owner-requested paired development diagnostic, not milestone evidence; its identity check compares source paths, not snapshot hashes. |
| `evidence/c6_dev_pilot/README.md` | KEEP unchanged — marks old defective formation result void and distinguishes unfinished/unrun scripts. |
| `c6_dev_pilot/c6_pilot.py`, `run_pilot.sh` | KEEP as history only — old level-mixing criterion and placement study are not the revised detector. |
| `c6_dev_pilot/pilot_contact.json/.log`, `pilot_disk1.json/.log` | KEEP unchanged — development provenance/cost/contact observations; no new formation verdict. |
| `c6_dev_pilot/smoke.json`, `smoke2.json`, `smoke3.json` | KEEP unchanged — early path/placement records cannot qualify final settings. |
| `c6_dev_pilot/diag.py`, `c6_coarse_pilot.py` | KEEP as history only — interrupted/unrun work cannot count as readiness. |
| `docs/reviews/c6_proposal_critique_codex.md` | KEEP history, DROP specificity mandate — field routing, non-vacuity, bounded error and restart findings remain useful; no requirement to beat arbitrary regroupings follows from the principle. |
| `docs/reviews/c6_proposal_recheck_codex.md` | KEEP history — preserve floor, dimensionless convergence and censor handling; specificity/primitive-push requirements leave the required path. |
| `docs/reviews/c6_proposal_followup_audit_codex.md` | KEEP history — certified censor-bound argument supports retained scoring; partition-bias repairs are no longer C6 gates. |
| `docs/reviews/c6_proposal_recheck3_codex.md` | KEEP history — correctly refuses subtraction of geometry-supported signal; diffusion/partition diagnostics are unnecessary here. |
| `docs/reviews/c6_proposal_recheck4_codex.md` | KEEP history — identifies undefined diagnostic ratios; these optional outputs and their approval blockers are dropped. |
| `docs/reviews/c6_proposal_recheck5_codex.md` | KEEP history — narrow approval of its amendment, not proof that revision 1 followed the owner's principle or approval of revision 2. |
| `docs/reviews/c6_step1_engine_review_claude.md` | KEEP history — bounded engine review with measured parity/speed; realistic-size contract is now present in tests. |
| `docs/reviews/c6_step2a_review_claude.md` | KEEP history, FIX carry-forward — A1/sampler repairs are present, but nested survival was judged against the wrong requirement and repeated-run fidelity remains vacuous. |
| Pre-approval benchmark / extracted-project-function probes disclosed in proposal/reviews | DROP as future practice — code execution is not permitted merely because no final seeds/integrator are used; require explicit owner authorization. |
| `STATUS.json` C6 outcome / generated README | FIX on the next authorized status update — retain BLOCKED pending approval, replace obsolete “violating lower levels stay alive” rationale and point to revision 2; use `tools/status.py --write`. |
| `.gitignore` build entry | KEEP — generated native build stays outside committed source/evidence. |

## Exact code reuse and changes after approval

1. **Unchanged new engine/assembly code:** `native/c6/element_law.cpp`, `geomind/c6_native.py`, `tools/build_c6.py`, `geomind/c6_compose.py`.
2. **Frozen code, read-only:** C4 model/detector/initial-world/statistical helpers; C5 threshold/candidate/recovery/rigid-operation helpers, unit schema/hull/clipping/assignment helpers and `c5_coarse.run/CoarseState/links/rhs/invalid`. No frozen file is edited.
3. **Reuse C6 publication:** `c6_units.rate_estimate`, `isolated_rate`, `level1_state`, `compose_state`, `validate_interface`, assignment/isolation/filter helpers; preserve D2 rate/capacity corrections and V1/V2.
4. **Change criterion 6:** in `c6_levels.recursive_validity`, distinguish direct `ok` from nested diagnostic values. Parent acceptance consults only direct dynamic/geometry results. `horizon`, `formation`, `alone`, `detect_snapshot` use required direct-part windows; unavailable deeper diagnostics, including those requested by `publication`/`own_stability`, are recorded without rejecting the parent. Keep `published_series`, `child_series`, thresholds, union/overlap and detector criteria 1–5.
5. **Reuse prediction/scoring:** E1 alias, E2/Jacobian/exponential, `linear_input`, published-input validation, `score_excitation`, censor certificates and separation bounds. Implement declared validity flags and the separate reopen/recompute service for the selected recipe; later full state never enters scored predictions.
6. **Finish common experiment:** causal/dose/up/down/control endpoints, effective-state errors, publication coverage, ordered H-M/H-C truth tables and receipt costs are not a recorded C6 protocol yet. `c6_experiment.py` is development-only; tests of helpers do not supply panel coverage. Reuse existing formation, harvest, publication, tau and readiness helpers; remove `specificity_world` from the required path and make `same_rule_audit` consume revision-2 settings instead of parsing revision 1 and listing specificity.
7. **Lean design gate:** keep check-4 comparison, input-only banks, two passes/A1, D3 target, D4/D8 readiness and budget report. Drop C₂ range, C5-superiority fidelity, overlap-calibration veto and specificity timing. Existing `interface_fidelity` calls identical deterministic `isolated_rate` runs twice from the same snapshot; its monkeypatched test invents different outputs. D2 fidelity is tested by the retained held-out full/coarse and effective-state checks instead.
8. **Fresh records:** add explicit gate output path such as `evidence/c6_r2_design_gate/` and disjoint development purposes under development entropy; do not overwrite `evidence/c6_design_gate/`. Replace the old 3.6× workload proxy with accounting for the actual remaining protocol and flag unmeasured costs. Preserve the three-hour owner budget and announce time before running.
9. **Tests and registration:** replace nested-veto tests (including early overlap/missing deeper frames) with live-direct/deeper-transform and direct-failure controls. Keep meaningful engine, own-window, geometry, D2, interface, isolation, information-boundary, recipe/censor/floor contracts. Add required endpoint/truth-table/coverage contracts and new `tools/c6_mutants.py`/`geomind/run_c6.py`; runner self-checks the gate. No runner, mutants or C6 registration currently exist.
10. **Pipeline:** after the development gate, register revision 2 (`evidence/c6_r002` for panel), fresh final entropy and 40 worlds/level before any final run. Pinned shared `tools/verify.py`/`tools/milestones.py` may add native-build preflight and registered timeout if needed; frozen legacy tooling cannot change. One ordered pipeline, one Claude evidence review; every STOP returns to owner.

## Scope of this audit

No benchmarks, simulations, pilots, pytest, mutation, design gate or panel were run. Standard-library file/hash/gzip
inspection checked existing artifacts only; no project module was imported and no seeds were drawn.
Only documents change now. Required git commit guards run normally; no hook or gate bypass is authorized.
Current STATUS/README bytes remain unchanged to avoid running their project generator before proposal approval;
0010 supersedes the erroneous interpretation without asserting a new milestone status. Revision 2 remains unapproved.
