APPROVE_WITH_NOTES

Reviewer family: Codex
Reviewed commit: c6ec559110162ece21f6a35489bcfa2f81f3b4fc
Review date: 2026-10-07
Scope: DESIGN_0H_REV7.md section 19, revision 7.12; C2/C3 pilot evidence and inherited 7.x contracts.

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

C2 is a coherent, bounded design change with genuine supporting pilot measurements. Its operational rule matches the pilot, and neither different realized pins nor the instrumentation fix requires redesign. The notes below correct the geometric justification and claim language and strengthen implementation checks. This is design approval with notes, not owner approval of the pin change, fixture readiness, a fixture verdict, scientific acceptance or development authorization. The recorded 7.11 FAIL remains unchanged.

## Scope and evidence

Read AGENTS.md first, CURRENT.md, the current plan, section 19 and governing earlier amendments, the revision-3 diagnosis including section 8, both earlier diagnosis rechecks, the four named pilot scripts, all eight named baseline/C2/C3 summary logs, and relevant medium, native, fixture, Run, control, template and evaluator code. Used standard-library stored-data reads, hashing and static geometric arithmetic only. No project imports, tests, builds or simulations ran. Only this review file was written; existing untracked work was preserved.

The reviewed design is unchanged from c6ec559 in the working tree. Key SHA256 identities:

| Input | SHA256 |
|---|---|
| DESIGN_0H_REV7.md | `108e4f45e8a1ac7a97c5bf0fcb7e8949978a549c4c7673f13ca8cc5f44738fc6` |
| REV711_F5I_DIAGNOSIS.md | `4cde12dcf66953d5412148e03191c00a7aaaf60eda78927ab3d1c166c446635d` |
| pilot_common.py | `451ff72b5095c8a8e53b37a2f506294203bca890c9b54228de107dd72312bce0` |
| pilot_c2_opin.py | `8b43dba0aa0b550d1b08c1a6dc5ee7587cb6214474ba5e70da0e218a84c74315` |
| rev7_design.py | `d4bb361086ef76a9ab80fc9ac4ba5145d5536d8b45af2197cc78a6982f4465ef` |
| rev7_fixtures.py | `9cfeb10501860e283a92c0a487953ffefd44278022ddaf1428539a0566c1700e` |

All eight new local raw files listed at the end of RAW_FILES_OUTSIDE_GIT.json match their declared byte counts and SHA256: two baseline assays, two C2 assays, two C2 training-only pilots and two C3 pilots. Each has exactly 8,000 recorded live integrations ending at 800 s, and none exercises a nonempty recovery candidate. Raw files remain local evidence outside Git; hashes do not establish historical process-to-image binding or replace a launch receipt for monkeypatched pilot behavior.

## Findings and concrete fixes

### N1 — Medium: correct the receiver-degree proof of the initially missing route

Section 19.2, line 899 uses the degree-8 strong radius 1.442 to justify the six-seed construction. That degree is unavailable: an inserted O initially has at most six held phase neighbors. A distance merely above 1.5 does not exclude a strong edge at every possible receiver degree.

The claimed conclusion at the literal construction is nevertheless correct. The exact minimum seed-to-unit-circle distance is **3.1 − 0.556 − 1 = 1.544 m.u.** With all six seeds held, the strong radius is `sqrt(log(64/6)) = 1.5385459415`, slightly below 1.544. If a seed is excluded at distance at least 3, the hexagon diameter 1.112 makes the nearest seed at least 1.888 away. If that nearest distance is below 2.444, its two adjacent vertices are also within 3, giving at least three neighbors and a strong radius at most `sqrt(log(64/3)) ≈ 1.749`, still insufficient. At distances at least 2.444, even the degree-1 radius `sqrt(log(64)) ≈ 2.039` is insufficient. Thus no seed→O strong edge exists anywhere on the unit circle for the frozen literal hexagon. Independently evaluating the finite angular intervals defined by the radius-3 crossings gives a maximum incoming coefficient **0.4916640768 /s**, at O = (1, 0), below 0.5 /s.

This argument concerns the construction, not the moved seed after 20 s. The stored C2(ii) pilot also supplies useful separate evidence: at its first B-path check, immediately after B-out at 20 s, `output_first=true` and every active site (2, 6, 7) has `missing_path_before=true`. Two accepted B-path births at site 6 then connect sites 6 and 7. This pilot did not receive an already-connected active route merely by adding O.

**Fix, drafter:** replace the degree-8 argument with the actual-degree justification and exact 1.544 clearance; distinguish construction from the first live insertion. **Fix, implementer:** record the graph, held O degree and incoming coefficients immediately after first B-out and before B-path in the seeded fixture. The initial t=0 graph has no O and is trivially disconnected; do not present that alone as proof about the first live insertion. Keep the inherited F5 gates.

### N2 — Low: state the information prior and total-policy estimand precisely

Section 19.3, line 917 is accurate about the absence of direct task-label, score or assay access, but does not establish task-independent position selection. Effective roots depend on active drives and gains; B1 placement, phase and the subsequent geometry depend on task observations. Reward-arm gains can also depend on earlier scores. The pin is consequently selected from **task-conditioned medium state**. Its implementation can remain universal across tasks without supplying a task-specific equation.

This is a disclosed adaptive infrastructure prior, compatible with the bounded claim of starting with no ordinary elements. The output is supplied permanently and placed near the medium's driven state; this does not demonstrate an autonomous choice of a useful output site or an absence of task information in initialization. The chosen distance is fixed within this revision, but the rule was selected using the engineering outcomes; calling it wholly outcome-independent would be wrong.

Different intact/M/U pins are downstream outcomes under the same causal rule. They are **mediators, not automatically a confound** of the complete policy comparison. Exact M B1 count/timing matching does not match O coordinates, birth times, phase initialization, or downstream path geometry. G0 can compare need-driven versus random B1 policies under this common adaptive provisioning rule, including those downstream effects; it cannot identify an effect holding output geometry fixed or attribute all improvement exclusively to later growth. U remains descriptive.

**Fix, drafter:** say “the same state-dependent rule for all tasks, with no direct task-label, score or assay lookup,” disclose the indirect observation/reward channels, and specify that G0 estimates the total policy effect including induced output initialization. Make the last stop row forbid direct access and undeclared inputs, rather than implying that task-conditioned medium state is forbidden. Retain per-run reporting of the selected root, pin, output timing and phase/RNG branch. A common realized pin is needed only for a separately designed fixed-geometry question, not as an automatic repair to this protocol.

### N3 — Low: distinguish exact metric reproduction from complete Harness.F5 equivalence

The pilot uses the same 50 perceive episodes, world IDs, growth/recovery keys, checkpoints 40/45/50, ten recipient/donor pairs, fresh own/donor/output-channel evaluations, wrapped-angle A/B formulas, absent-output treatment and E averaging as Harness.F5. Its stored baseline reproduces the compact fixture **exactly at the stored float/list level**, not just rounded headline values:

| Start | A | B | E |
|---|---:|---:|---|
| Baseline (i) | 0.19031953755626294 | 0.2090518472328278 | [0, 0, 0, 0, 0, 0, 0, 0] |
| Baseline (ii) | 1.4505015648748454 | 1.3031787239861423 | [0.5, 0.7, 0.8, 0, 0, 0, 0, 0] |
| C2 (i) | 1.0418222610259926 | 1.2708760083009119 | [0, 0.7, 0.8, 0.6, 0, 0, 0, 0] |
| C2 (ii) | 1.518784250132054 | 1.2524449455656252 | [0.5, 0.7, 0, 0, 0, 0, 0, 0.7] |

However, pilot_common.py:83–89 omits Harness.F5's assertion that **each assay stream has exactly 160 decisions**. Its `zip` can silently truncate a malformed pair. It also deliberately omits the start-specific birth requirement, formal verdict, fixture prerequisite/stop sequencing and descriptive qualification outputs. The present data establishes metric reproduction, not full harness equivalence or equality of every trajectory/decision. Training-step assertions do not validate assay lengths.

**Fix, drafter:** describe this as “the same A/B/E estimator, with exact baseline metric reproduction.” **Fix for future pilot instrumentation:** copy the three-stream 160-decision check before averaging and retain per-pair/checkpoint summaries. Do not overwrite the historical scripts or invalidate the reproduced measurements merely for this defensive-check omission. Formal fixtures still use Harness.F5 and its full gates.

### N4 — Low: strengthen the evidence checks and correct the scheduling shorthand

The class-level wrapper calls `_ORIG(self, drives)` on the actual receiver. Its external `LIVE` identity guard records only the live object; no instance closure capturing the live bound method is copied by `Rev7Medium.clone`. This fixes the earlier failure mechanism. Static native/Python cloning and the exact live-step counts support isolation. The synthetic check itself compares only clock, index and sink length, not native bytes, RNG, histories or timers, and is executed only at the initial state. It should not be described as a comprehensive live-state isolation test.

The two C2 trajectories exercise no B-out placement refusal, so retry/reselection is supported by source inspection, not by those trajectories. Pin coordinates in the step traces are rounded to four decimals; exact unit length comes from the source formula, not from those rounded numbers. The pilot omits the inherited `birth_attempt` record, and its B-out birth event records the rule name but not the selected root identity or unrounded root coordinates.

Section 19.2's development shorthand “in the first training episode where a root exists” is not the operational schedule. In empty C2, B1 creates root 0 at 20 s, after that check's B-out; O is born at the next check, 40 s, in a later episode. Placement refusal can delay it further.

**Fix, implementer:** strengthen the bounded clone check with live native-state and Python/RNG fingerprints on a populated state; retain the training-only sink. Implement section 19.4's adversarial cases for lowest-id versus nearest root, inactive/silent/zero-gain/O exclusions, a rejected candidate followed by changed root selection, root death after placement, pin-copy mismatch, and cap/cost exemption. Record the selected root and unrounded pin at the successful insertion and the rejected candidate on a refusal. **Fix, drafter:** replace the episode shorthand with “the first admissible growth check with an effective root.” These checks belong in the complete implementation batch; this review ran none of them.

### N5 — Low: describe prior review dispositions without implying an approval that did not occur

Section 19.1 says the diagnosis “passed two Codex owner rechecks.” Both named reviews start **CHANGES_REQUIRED**. Revision 3 records corrections to their findings; that is distinct from either earlier review approving that later revision. The C3 pilots have no F5 assay: their zero late connectivity in (i) supports that observation, not a formal F5 failure or exclusion of every possible group policy.

**Fix, drafter:** say “two rechecks returned CHANGES_REQUIRED; revision 3 records the corresponding fixes,” and keep C3 conclusions specific to its measured training connectivity. The section-8 C2 metrics and recommendation can stand without asserting an unrecorded diagnosis acceptance.

## Operational and interaction checks

- **Pilot fidelity:** `self.influence().roots` and the strong graph use the identical effective-root predicate: ordinary, unsilenced, positive gain, active positive-strength strict reach. Sorted union selects the lowest persistent ID, not the nearest root or lowest site. With reach 3 and sites at radius 4, an effective root has radius greater than 1, so the origin fallback is unreachable under this contract. The 0.3 birth clearance is not what proves that fact.
- **Once, frozen, and retried:** the output-existence guard prevents subsequent births; output role pins the native coordinates and exempts O from D1/D3/D4. Each refused call recomputes the root and candidate. The C2 raw traces each contain one B-out, at 40 s / 20 s, and a single rounded O coordinate thereafter. The empty run records `no_root` at 20 s. The seeded factory retains precisely the six declared seed elements and removes the literal O.
- **Phase, placement and resources:** the pilot retains the inherited circular mean within strict distance 3 and RNG fallback for resultant below 0.1. It uses the common element/sensor clearances and ignores ordinary cap/cost for O. Different phase/RNG branches are allowed state-dependent outcomes and must be reported with their own declared streams.
- **Output first and controls:** deaths precede B-out, B-path precedes B1, and the root predicate is live. No root permits bootstrap B1; a root without an output/path defers B1. Persistent placement failure is a possible unresolved failure, not a reason to waive F5 or add an unregistered relocation. M still attempts exactly the intact run's accepted B1 births at each check, after its own common B-out/B-path processing; unmatched attempts remain failures/inconclusive under the existing fixture/development rules. O never enters the matched B1 set. M/U have not been piloted here; a genuine F7 matching check is still necessary.
- **Strong edges and protection:** no thresholds or D-rules change. All graph decisions must retain actual held receiver-degree normalization. O has zero direct site drive and is not a root. Its inherited phase initialization and its participation in coupling and neighbors remain supplied infrastructure; the new pin does not prove exclusive mediation by a particular grown bridge.
- **F6–F9 and development:** no new target substitution is needed. F6 uses both starts' stored checkpoints and the empty-start baseline; F7 uses the intact empty-start B1 schedule; F8 continues the live empty-start state with its stored pin; F9 keeps its literal synthetic scaffold. Their measurements remain absent. F1–F4/N1 scaffold coordinates and case definitions stay unchanged, although renewed design/configuration/source identity is required for any new revision execution. The reused fixture inventory is outcome-informed engineering evidence, not fresh or independent. Untouched development entropy, qualification, positive-task gates, full-run M matching and a qualified cost projection remain separate requirements.

## Recheck disposition and delivery

A separate Codex reviewer received the owner's request verbatim and independently challenged the actual-degree proof, task-conditioned prior, control estimand, assay guard and clone semantics. Its recommendations are incorporated above, including an analytic geometry proof. This support is same-family; this report is the requested Codex review of the Claude design. No numeric quality score was assigned.

The drafter should record this recheck and each disposition in docs/PLAN_CURRENT.md during their authorized follow-up; the owner's instruction forbids editing that existing file in this task. The owner-pin approval stop remains in force. Existing files and evidence were not edited. `.git` is read-only in this session, so no staging or commit was attempted; only this requested review file is delivered.

Assisted-by: Codex:GPT-6
