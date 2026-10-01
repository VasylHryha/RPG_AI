Verdict: **CHANGES_REQUIRED**.

Reviewer family: Codex

Reviewed experiment: `geomind-c4-r4-002` (C4 R002).
Reviewed evidence commit: `0706077242ecbd5cc58cd69741c8147985a18303`.
Registered source commit: `e8efb1d8f184deff8551ff1e086b6921915099ab`.
Reviewed `evidence/c4_r002/results.json` SHA256: `24a583ecc83a7efbfec3ea90966d99fa95c67937ae75c65e87d12559c1fb66d7`.

Date: 2026-10-01. Independent review of committed code and evidence, within the approximately 20-minute cap. Started with `evidence/c4_r002/HANDOFF.md` and `docs/decisions/0002-c4-r002-supersedes-r001.md`. Authority: AGENTS.md, the registered manifest, and the R4 standard. No recorded panel, pipeline smoke, mutation probe, or final-world simulation was rerun. No implementation, manifest, committed receipt, or gate stamp was changed. At the owner's subsequent request, I audited this same review, clarified R2's conflicting design records, preserved runnable checks, ran the everyday test suite on its existing development/synthetic fixtures, and reconciled the authoritative milestone status. This is an amendment to the existing review, not a second independent review.

Two findings block implementation acceptance. The reported primary-arm arithmetic is reproducible, but the recovery detector does not enforce preservation of the original group, and the registered failure rule conflicts with both the hypothesis evaluator and the supersession decision.

**R1 — High: recovery can accept fragmentation of the original resonator.**

Location: `geomind/c4_detect.py:173–180`, consumed by `criteria_checks` at lines 188–195. The approved proposal's criterion 5 requires return to the same membership with Jaccard at least 0.9; R4 C4 requires return to the same or explicitly equivalent basin. No registration change declares that a surviving fragment is equivalent to the original group.

The detector chooses whichever component of the future **control** overlaps the original members most, but never checks how much of the original group that component retains. It then measures the kicked component against that possibly much smaller control component. If both futures split identically, `recovery_jaccard` is 1.0 even though neither recovers the original membership. The preceding persistence check covers the observation window, not this future recovery window.

I reproduced this through `detect` with a synthetic stationary, phase-locked six-member history and a mocked future integration result. Both futures split into the same two three-member components and have equal phase patterns. Every detector criterion passes; original-to-final best Jaccard is only 0.5, below the registered 0.9. This isolates an evaluator defect; it does **not** establish that a particular recorded panel world fragmented.

Reproduction from the repository root with `.venv/bin/python`, using no world simulation:

```python
import json
from pathlib import Path
from unittest.mock import patch
import numpy as np
from geomind.c4_detect import components, detect, jaccard
from geomind.c4_model import INTACT

m = json.loads(Path("experiments/c4_manifest.json").read_text())
x = np.array([[0., 0.], [1., 0.], [2., 0.],
              [0., 1.], [1., 1.], [2., 1.]])
xs = np.repeat(x[None, None], 31, axis=0)
ths = np.zeros((31, 1, 6))
end = np.array([[0., 0.], [.5, 0.], [0., .5],
                [10., 0.], [10.5, 0.], [10., .5]])

def split_future(bx, bt, bw, params, dt, steps, **kw):
    return np.repeat(end[None], len(bx), axis=0), np.zeros_like(bt), None

with patch("geomind.c4_detect.simulate", split_future):
    c = detect(xs, ths, np.zeros((1, 6)), INTACT, .02, 1.,
               m["detector"], [np.random.default_rng(1)])[0][0]
labels = components(end, m["detector"]["link_factor"], np.ones((6, 6), bool))
retained = max(jaccard(range(6), np.flatnonzero(labels == k))
               for k in np.unique(labels))
assert retained == .5
assert c["accepted"] and c["stats"]["recovery_jaccard"] == 1.
```

Required correction in a new revision: enforce recovery of the original candidate membership in both control and kicked futures, while retaining the paired phase comparison. A control that itself loses the candidate cannot serve as proof of its recovery. Add a negative contract for common fragmentation, and retain original-to-control and original-to-kicked membership scores in the future receipt. Original identities may remain evaluator-private. The current receipt stores neither those scores nor the future component memberships, so this finding cannot be resolved by checking its existing `recovery_jaccard` values. Formation counts, effective-unit eligibility, and the population used for causal endpoints depend on this detector.

**R2 — Medium: formation-failure rules conflict across registration, implementation, and decision record.**

Location: `geomind/c4_experiment.py:354–362`; the incorrect expectation is also encoded in `tests/test_c4.py:247`.

The R002 manifest's `verdict_rules.H-M` says `NOT_SUPPORTED if any of these FAILs`, referring to formation, both causal endpoints, and dose response. Its `primary_arm` rule applies the same rules separately to the heterogeneous arm. The code checks only causal/dose failures. A formation failure therefore falls through to `INCONCLUSIVE`.

This affects the committed result: heterogeneous formation is 4/20 = 0.2, marked FAIL against 0.8, but `hypothesis_status_by_arm.heterogeneous.H-M` is INCONCLUSIVE. Under the manifest's explicit H-M failure rule it would be NOT_SUPPORTED. Fewer than ten formed worlds correctly makes the causal and dose endpoints inconclusive; the explicit H-M rule supplies no exception for a separately evaluated formation failure across all twenty worlds. A synthetic formation fraction of 0.5 with all three causal/dose verdicts PASS likewise returns INCONCLUSIVE, contrary to that rule.

The self-audit found a design-record conflict that my initial wording did not state: `docs/decisions/0002-c4-r002-supersedes-r001.md` says formation rules were unchanged from R001. The R001 H-M rule, like the approved proposal, makes failed formation inconclusive unless a causal endpoint fails. The R002 manifest changes that wording to "any of these FAILs," while the code/test retain the earlier formation behavior. The broad "Verdicts require at least 10 worlds with resonators" registration note also leaves its relationship to formation verdicts unclear. Thus this is a protocol/implementation inconsistency, not evidence that the underlying heterogeneous dynamics changed or proof of which outcome the owner intended.

Required correction in a new revision: register an explicit hypothesis truth table, including formation failure, insufficient formed worlds, and mixed FAIL/INCONCLUSIVE endpoints; reconcile the decision record with that rule, and make code/contracts follow it. If the explicit R002 H-M rule is retained, formation failure must propagate before the inconclusive fallback and the synthetic contract must change. Preserve R002's receipt and its recorded verdict unchanged as history; do not relabel it in place or select a new rule by which verdict looks preferable. This finding does not by itself change the identical-arm arithmetic, whose formation endpoint passes.

**Evidence and implementation checks that passed.**

- The initial working tree was clean. The review gate (`tools/milestones.py check c4 review`) passed. The manifest/source registration precedes the evidence commit, and every pipeline stage names the registered source commit. The runner calls `milestones.check("c4", "panel")` before the panel.
- The receipt SHA256 above matches the handoff and pipeline. All 13 receipt dependency hashes match both the current files and their registered committed versions. The dependency fingerprint and every artifact hash in `PIPELINE.json` also match. Accepted C1 R006 and C2 R002 receipt-bound files are unchanged.
- The attested stage order is preflight → tests → smoke → mutation → panel, totaling 95.67 seconds. The committed contract report contains 24 passing cases; the mutation receipt reports 27/27 detected, no unexpected survivors and no timeouts. These existing checks miss R1, and one existing expectation explicitly preserves R2.
- All sixteen registered endpoints are evaluated, with no silent omission. Receipt-only evaluation reproduces both arm summaries and endpoint coverage exactly. Separately, I recomputed each world mean from `resonator_effects`, formation counts and Wilson intervals, candidate decisions from their stored statistics, and effective-state counts. Independent bootstrap arithmetic reproduces all 28 stored effect/dose/difference summaries to absolute tolerance `1e-14`, using the recorded resampling seed and ordering. This verifies stored-record arithmetic, not the unretained trajectories or R1's missing membership check.
- An independent scalar evaluation of the registered motion and phase equations, including both frozen-topology ablations, agrees with the vectorized RHS on thirty synthetic configurations: maximum absolute error `8.88e-16`. No trajectories were integrated for this check.
- Inspection of `intervene` confirms that each condition uses its own paired control, the G→M probe is shared between control and treatment, and frozen phase topology comes from the unperturbed formed state rather than the scaled treatment. The primary doses alias the registered dose entries correctly. Per-world aggregation avoids counting resonators or frames as independent worlds.

**What the committed records show, conditional on the detector.**

The identical arm has 17/20 formed worlds and 33/33 effective units within the registered bounds. G→M mean is 0.01347675 rad with 95% CI [0.01224421, 0.01488400]; M→G mean is 0.95782377 in relative-radius units with CI [0.81688214, 1.12397819]. Both complete-ablation effects are zero. Dose means increase in both directions, with positive highest-minus-lowest CIs. These values follow the stored records and registered endpoint rules. They cannot establish valid recovery until R1 is addressed.

The heterogeneous arm has four formed worlds and three of four effective units within bounds. Its causal/dose endpoints correctly remain inconclusive for insufficient formed worlds. The inconsistency in its aggregate H-M label is described in R2. Its clump-control PASS is vacuous because no candidates were generated; the identical arm supplies the meaningful recovery rejection control.

The recorded numerical checks pass: held-neighbor RK4 error ratios about 17.2–17.3, switching-model error at most 0.002038, and equivariance error at most `1.07e-14`. These are the registered limited numerical checks, not a guarantee for every transient.

**Assessment of the R001 supersession and scientific scope.**

Removing both distance weighting and geometric neighbor selection is a legitimate complete G→M ablation. R002 preserves R001's evidence, reports its old single-channel ablation as a decomposition, registers a new falsifiable dose-response condition, and uses fresh final entropy. The model, integration, detector thresholds, and effective-state bounds are unchanged between the receipts. This is a transparently revised experiment informed by R001, rather than an untouched confirmation of R001's design. Commit order and code establish the registered protocol; the assertion that all design selection used only development worlds remains a provenance assertion, not something receipt hashes alone prove.

Complete-ablation vanishing is structural and supplies a control on the statistic, rather than independent hypothesis support. The intact effects and registered dose-response carry the bounded empirical result. Formation passes by the registered point estimate, while the Wilson lower bound is about 0.64. The identical-omega mode is a synchronizing fixture with collective frequency zero; G→M measures response to a shared phase probe. Effective-state validation concerns centroid/size/frequency prediction in this setting, not held-out boundary excitation or recursive composition. No novelty, generic heterogeneous closure, hierarchy, task-usefulness, or efficiency claim follows.

**Disposition.**

C4 R002 is not accepted for promotion or freezing. Preserve its committed evidence and R001's withdrawn evidence. The implementer should address R1 and R2 in a newly registered revision on fresh final seeds, finish its code/tests before the gated verification run, and obtain one new cross-family review. No C5 work is justified by this review.

The owner-requested audit retains this verdict. `STATUS.json` now records C4 R002 as CHANGES_REQUIRED and points to this review; README's table is regenerated through `tools/status.py`. No other milestone advances. Reproducible evidence and finding checks are in `REVIEW_CHECKS.py` beside this report. Run `.venv/bin/python -B evidence/c4_r002_review_codex/REVIEW_CHECKS.py` from the repository root. The script checks hashes, stored-record arithmetic, the two finding reproductions and a recovery positive control; it never runs a panel or trajectory. Its successful exit means that the audit assertions hold, including the demonstrated defects, not that C4 passed.

Audit validation: `REVIEW_CHECKS.py` passed; `.venv/bin/python -m pytest -q -x` passed all 133 tests in 35.04 seconds; `python3 tools/status.py --check`, `git diff --check`, and the existing `milestone_precommit.review_problems` format/family/digest validation passed. These tests do not resolve the demonstrated recovery defect or contradictory verdict specification. The changes are local and uncommitted.
