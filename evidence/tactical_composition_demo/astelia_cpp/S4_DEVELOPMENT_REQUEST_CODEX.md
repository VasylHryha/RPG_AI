# Request to Codex: session S4, development (tuning, noise, watching), with no registration and no judging seeds

Repository `/Users/new/RiderProjects/ai_RPG_test`. Read `AGENTS.md`.
- **Approval:** the owner approved this session and assigned it to Codex (2026-10-05). Exploratory, under decision 0028. Commit with `Assisted-by: Codex:<model>`.
- **The contract:** `../DESIGN_0G.md` revision 3, sections 5 (knobs and protocol), 6 (panels and inference) and 10 (stop rows).
- **Notes to apply:** Claude's S3 review `../astelia_cpp_review_claude/S3_REVIEW.md`, notes 1-3.
- **If the contract is unclear,** report the question; do not choose silently.
- **Before any run longer than a few minutes,** state the expected time in the log and in a commit message.

## 0. Before tuning

1. **Runner settings**, added to `s3_runner.py` as fixed, named development settings and recorded in every result line:
   - the P2/P3 opponent skills, elite skills without `artyRollout`, applied to the 19 doctrine opponents;
   - a small-army setting for the owner's first stage: 10 melee against 10 melee, with no ranged or artillery units.
2. **The morale-against-regular anomaly** (S3 review, note 2):
   - find out why morale scores −5.75 against regular but −17.15 against novice, while the other arms do worse against regular;
   - compare the configurations of the two levels and watch a few fights;
   - report whether it is a real matchup effect or a configuration difference, and fix only a genuine defect.
3. **Watching fights** (owner decision):
   - add trace export for chosen fights;
   - add a small self-contained HTML replay viewer (one file, no external dependencies) that plays a trace: unit positions, team colours, HP, targets, and the resonator phase or morale as a colour per unit;
   - commit a few recorded fights per stage, so the owner can open them.

## 1. Tuning protocol (design section 5)

- **One optimizer for every tuned arm** (resonator, morale, push-pull):
  - each round samples candidates within the knob bounds around the current best;
  - candidates are raced in stages (for example 8, 16, 32 clusters, dropping one that is clearly behind);
  - a candidate is accepted only by the compose acceptance rule (gain > max(min_gain, 2 se)).
  - State the exact sampler, stages and rule **before** the first tuning fight. They are the same for every arm.
- **Equal fight budget per tuned arm,** declared before tuning. Cache hits count. Nearest is untuned.
- **Every evaluated candidate is logged:** knobs, fights, scores, accepted or rejected, failures.
- **Seeds:** a development (tuning) split and a separate validation split, both recorded in a seed ledger. **Judging seeds are not drawn or used.**
- **Stages** (owner):
  - **A:** 10v10 melee, against novice head-to-head;
  - **B:** full armies, against novice and regular head-to-head;
  - **C:** full armies, the P2/P3 panel (19 doctrines, elite-no-rollout skills).

  Each stage starts from the previous stage's best knobs. Record fights to watch at the end of each stage.

## 2. Measurements for S5

On the **validation split** only, after tuning:
- each tuned arm and nearest: head-to-head clusters against novice and against regular, and the paired P2/P3 panel (resonator against morale, resonator against push-pull);
- report the means, the paired cluster spread and its uncertainty;
- propose δ (in survivors) with the reasoning, and n per endpoint by a stated bounded power rule.

δ is the owner's decision. Never shrink it to obtain a pass.

## 3. Stop rows (design section 10)

- **If the tuned resonator does not beat novice head-to-head** on the validation split (mean cluster S ≤ 0) after its full budget: stop, set the report's first line to `STOP`, and describe what was seen.
- **Any controller failure in a development fight:** fix it first, and restart that arm's budget.
- **An outcome-informed equation change:** log it, and restart that arm's budget.

## Not in scope

- registration, judging seeds, a recorded run;
- any new arm or knob beyond design section 5;
- changes to frozen GeoMind files or committed receipts.

## Report

`S4_DEVELOPMENT_REPORT.md`:
- the first line: `READY_FOR_S5`, `STOP` or `NOT_READY`;
- the anomaly finding;
- the declared optimizer and budget;
- per stage, the best knobs and validation results per arm;
- the measured spreads and the proposed δ and n;
- the recorded fights and how to open the viewer;
- every deviation.

Claude reviews it afterwards.
