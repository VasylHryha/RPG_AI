CHANGES_REQUIRED
Reviewer family: Codex
Reviewer model: gpt-6
Rechecked proposal commit: 6a99b18
Proposal SHA-256: de1d81ee40a2e5b311539a893fb22de24efba5268609b8a4ebb866c123bc48ff
Follow-up audit SHA-256: c126591375e2a6a0b4fd402538db8dec987c7cddb2709cd6c0bfe7dbb9ed2eef

Date: 2026-10-02. Scope: the follow-up audit and its ninth-self-audit amendment only. Locations refer to `experiments/c6_proposal.md` at the commit above. The original counterexamples are fixed; the newly mandatory geometric subtraction needs a narrower claim and a complete rule. This does not authorize implementation or decide D8's numerical value.

## Status

| Item | Status | Proposal lines | Evidence |
|---|---|---|---|
| F14, unequal-size push: all 1,890 alternatives | RESOLVED | 304–308, 319 | All ten sites and 101 times in [0,32] gave 1,908,900 pairwise comparisons with maximum absolute contrast 9.59e-19; cancellation is algebraically exact. |
| F14, nine-element heterogeneous fixture | RESOLVED | 305–308, 318 | All 36 alternatives, nine sites, two amplitudes and 101 times gave 65,448 comparisons with maximum absolute contrast approximately 5.73e-17, consistent with exact cancellation. |
| F14, geometric null well defined, binary and unfitted | PARTIALLY_RESOLVED | 311–315, 167–172 | For a specified Laplacian and finite positive tau_n its rate is fixed without scored-data fitting, but the operator convention and censored/undefined-rate cases are not fully registered. |
| F14, residual bias and preservation of modular signal | NOT_RESOLVED | 309–324, 435 | A weakly coupled weighted-triple fixture remains positive, but differing channel rates leave positive local-diffusion contrast and a modular graph identical to the null loses its positive contrast exactly. |
| N5, full-metric certified bounds | RESOLVED | 157–164, 384 | The unchanged channel contributes a constant; the excited-channel error is Lipschitz with the stated K, including wrapped phase distance and vector position normalized by each responding L. |
| N5, both witnesses | RESOLVED | 159–162, 602 | The new certified intervals contain the lower witness's error 0 and the upper witness's error 1, also after adding another channel and heterogeneous position normalizations. |
| E2/E1 linear input constructor | RESOLVED | 300, 362–370, 597, 625 | Both recipes now receive the same arithmetic paired-response input, E1's two synthetic states are explicit, and the obsolete decoder offsets are removed. |
| Linear against circular wording | PARTIALLY_RESOLVED | 302, 942, 953 | Rigid whole-part initial kicks and approximate near-synchronization are correctly described, but identical initial phases alone do not ensure exact equality for a finite nonuniform kick. |

The pairwise cancellation proof uses oracle summaries, as the registered contracts do: outside both probe-containing parts every summarized member has the same response, so both residuals vanish. The explicit six-primitives-per-sub-part lift also passed. This establishes the decoder correction, not correctness of an unrun E1/E2 predictor.

## New findings, ranked

### R3-1 — High: the geometric subtraction does not establish the claimed specificity meaning

**Location:** lines 310–324 and 435. **Blocks: yes.**

A positive modular example survives: two triples on a complete graph, within-triple conductance 1 and between-triple conductance 0.02, real partition `(012)(345)` against `(013)(245)`. With amplitude 0.5, pairwise-excluded oracle scoring at 101 samples over [0,10] gives uniform-site mean contrast **0.04251807501187536**. The uniform complete-graph null has zero contrast for any rate, so correction preserves this example.

However, subtraction removes whatever modular signal is already represented by the graph. A concrete algebraic witness is two six-element cliques joined by a perfect matching, all element edges weight 1. Its Laplacian eigenvalues are 0, 2, 6 (five times), and 8 (five times). A rigid opposite-phase kick of the two modules decays as exp(-2t), giving tau_n = 0.5 and null rate 1. The modules equilibrate internally faster than their collective difference.

Use real parts `{0,...,5}`, `{6,...,11}`, and contiguous mixed alternatives `{0,1,2,3,6,7}`, `{4,5,8,9,10,11}`. Single-element probes, pairwise exclusion, arithmetic oracle summaries and 101 samples over [0,10] give positive contrast at **every site**, with pulse mean **0.002896534126136998**. Truth identical to this null nevertheless has corrected contrast **0 identically**, by line 314. Thus geometry-supported predictive units are excluded by construction.

Conversely, take phase diffusion at that rate and position diffusion at 0.2 times that rate on exactly the same graph. The phase-calibrated null is still rate 1 for both channels. For amplitude-0.2 pushes the corrected mean is **+0.0014300508050326865**, positive at every site; pulses contribute zero, giving a pulse/push mean **+0.0007150254025163433**. Ordinary local diffusion with a different position timescale retains a positive statistic. One phase timescale cannot certify two-channel geometric neutrality.

These are closed-form graph diagnostics under the contracts' oracle scoring, not claims that a particular C4 geometry or an unrun panel realizes them. They show that null identity is narrower than the stated flat-local-medium claim, and that the subtraction changes the endpoint from predictive grouping advantage to advantage beyond a particular geometric operator.

**Smallest fix:** retain pairwise exclusion, report geometric subtraction as a diagnostic, and qualify the primary comparison as predictive grouping advantage, potentially including geometry. If geometry-independent advantage is intended instead, the drafter must state that narrower target and register channel-specific controls and positive fixtures consistent with it; do not claim preservation of all modular signal.

### R3-2 — Medium: the new null has no total calibration rule

**Location:** lines 311–312, 167–172, 496 and 435. **Blocks: yes.**

For an undirected combinatorial Laplacian, the intended generator is `-L/(tau_n * lambda_min_positive)`. C4's k-nearest selection can be asymmetric (`geomind/c4_model.py:71`); preserving its direction or symmetrizing it changes diffusion. The proposal must identify the operator. More decisively, individual isolated tau_n values may remain censored even when the development median is valid. The new null requires their exact value, while the N5 bounds apply only to relaxation baselines. There is no null-specific abstention, bounded contrast or NOT_TESTED rule for this allowed case.

**Smallest fix:** specify the Laplacian, direction/normalization convention and mode definition, then register a yes/no rule with implementer ownership for censored/nonpositive/nonfinite tau_n and missing decay modes, including endpoint counts and verdict consequences. Do not impute a censored time.

### R3-3 — Low: contracts still use the old scoring scope

**Location:** lines 595 and 599. **Blocks separately: no.**

Different alternatives now generally have different scored sets, although both sides of each pair share one set. Line 595 still requires one set for every grouping; line 599 calls the flat-consensus contract a zero *statistic*, whereas lines 318–319 correctly require zero *uncorrected contrast*.

**Smallest fix:** say “same set within each pair” and label the consensus contracts uncorrected; keep corrected-null identity separate.

### R3-4 — Low: identical phases give first-order, not general finite-kick equivalence

**Location:** lines 302, 942 and 953. **Blocks separately: no.**

Starting from phases `(0,0,0)`, a 0.5 pulse on one member gives circular response `atan2(sin(0.5), 2+cos(0.5)) = 0.1650906703787418`, versus arithmetic response `0.5/3 = 0.16666666666666666`. My prior suggested wording was insufficiently qualified for finite kicks; this recheck corrects it. The registered rigid whole-part initial kicks are unaffected.

**Smallest fix:** retain exact equality for rigid whole-part kicks and restrict the identical-phase statement to first order for nonuniform kicks.

## N5 proof and witness receipts

For position, the baseline derivative's norm at responding part j is at most `|amount|/M * t/L_j`; using the largest inverse L bounds the RMS over all parts and samples. Reverse triangle inequality bounds the change in positional error. Wrapped phase distance has the same 1-Lipschitz bound. Adding the fixed other-channel RMS changes neither K nor the proof. The argument would need revision if both baseline channels varied with u; the amendment explicitly excludes that case.

For the audit's T=10, c=0.5/3, 101 samples, the 65-point grid has `Kh = 0.0007536352150254054`:

| Witness | Certified interval | Off-grid error |
|---|---|---|
| Lower | [0, 0.05152873137125523] | 0 |
| Upper | [0.9959714280312943, 1.000795904420604] | 0.9999999999999998 |
| Lower, position L=(0.5,1,2), fixed phase error 0.037 | [0.035901448409663146, 0.10567640904243866] | 0.037 |
| Upper, same full metric | [1.3540360509973928, 1.3614388428653845] | 1.359875655532295 |

D8 remains an executable ordered rule with the response floor; this review does not choose its ceiling.

## Commands and scope

Read-only commands, including narrowed searches/ranges:

```text
pwd
cat AGENTS.md
rg -n 'GeoMind|ai_RPG_test|c6_proposal' /Users/new/.codex/memories/MEMORY.md
rg --files ...
find docs experiments -name AGENTS.md
git status --short
git rev-parse HEAD
git diff 5ac60a0 6a99b18 -- experiments/c6_proposal.md
git show 6a99b18:experiments/c6_proposal.md | shasum -a 256
git ls-files docs/reviews/c6_proposal_recheck3_codex.md
nl -ba experiments/c6_proposal.md
nl -ba docs/reviews/c6_proposal_followup_audit_codex.md
nl -ba GEOMIND_GEOMETRIC_AI_QUALITY_STANDARD_R4.md
nl -ba docs/PROCESS_REVIEW.md
rg -n ... experiments/c6_proposal.md geomind/c4_model.py geomind/c5_coarse.py geomind/c5_experiment.py
sed -n ... geomind/c4_model.py geomind/c5_coarse.py geomind/c5_experiment.py
sed -n ... /private/tmp/c6-followup-5ac60a0/probe.py
python3 -B /private/tmp/c6-recheck3-6a99b18/probe.py
python3 -B /private/tmp/c6-recheck3-6a99b18/modular12.py
shasum -a 256 experiments/c6_proposal.md docs/reviews/c6_proposal_followup_audit_codex.md
shasum -a 256 /private/tmp/c6-recheck3-6a99b18/probe.py /private/tmp/c6-recheck3-6a99b18/modular12.py
```

Scratch scripts were written outside the repository using shell heredocs; `probe.py` was run before and after adding whole-window checks. Their final SHA-256 values are respectively `0f71440482e81cfd007ca9cf58716bf717426b3a4f9c5a29aa65c4dc5345711c` and `01fcac9e1b0105d434fac92c5d930a4ddc93fba16b1ae53acbcb0cbd397c8c80`. They use only the standard library and exact response formulas/static algebra. The memory search returned no relevant match; no memory-derived fact was used.

Finished within the 15-minute cap. No simulations, seeds, project imports, tests, dynamics integration, panels, mutation probes or verification pipelines ran. This review is the only new repository file. No proposal, earlier review, code, status, evidence, gate or accepted artifact was changed; no staging or commit was performed.
