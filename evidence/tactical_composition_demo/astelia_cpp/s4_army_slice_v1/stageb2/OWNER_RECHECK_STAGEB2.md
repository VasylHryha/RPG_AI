# B2 owner recheck and disposition

Status: initial 11 focused tests passed in 8.51 s; independent review completed with CHANGES_REQUIRED. All six findings repaired in one batch; 17 focused repair checks passed in 6.91 s. Separate reviewer disposition check completed: F1–F6 resolved for the prepared development build. Host build, full validation parity, safety arbitration, throughput and paired outcomes remain not run.

The task explicitly prohibits docs/PLAN_CURRENT.md writes; this file tracks the recheck instead.

Owner request to send verbatim after the focused checks:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Self-audit corrections before testing:

- Own flight law was checked against native react_rules.cpp: distance / effective lob speed, not a generic minimum-flight heuristic. Snapshot speed already includes launch multiplier.
- Added public shell/shot/field/cast candidates, because enemy motion alone cannot cover O executed dodges.
- Learned-dodge fire calibration excludes the absent react veto; otherwise its threshold would promise suppressed fire that the deployed OFF arm cannot enforce.
- Preserved a separately tested Stage B ARMYA1 native branch and bound completed network-only exports to paired readouts.
- Added full residual and no-candidate accounting; labels beyond offset capacity cannot silently count as expressible.
- Added separate learned-dodge roots and frozen-parent warm starts; automatic body dash is OFF and is documented as unavailable action capacity, not copied teleport behaviour.
- Empty-unit remapping and position shape now support no-owned-unit synthetic terminal observations in B2 copies.

No numeric quality score is assigned. This is a development build; host safety/throughput and behavioural comparisons remain not run.


Independent review: INDEPENDENT_REVIEW.md, separate Codex reviewer (other family not callable). The original findings are preserved unchanged.

| Finding | Disposition |
|---|---|
| F1 parent behavioural identity | Enable calls the live parent parity and outcome gates, validates the look-ledger connection, every complete paired receipt/raw hash, actual wins/harm, and calibrated fit/checkpoint/export identity. Frozen readiness binds all inputs. Synthetic disconnected-look and replaced-checkpoint fixtures reject both cases. |
| F2 padding argmax | Python argmax excludes invalid entries; native argmax is limited to actual candidate counts. Canonical max-valid shifts retain finite padded outputs and make a valid maximum zero. An extreme finite negative-logit native/Python fixture covers the original counterexample. |
| F3 missing required aim | Artillery with an empty legal aim bank fails training/native inference. Audit mapping explicitly allows missing banks solely to retain no-candidate counts. Unused non-artillery aim stays masked. Empty-intersection fixture checks both behaviours. |
| F4 warm-start initialization | Actual law, K, force hash and frozen readiness/checkpoint identity are persisted in epoch transactions and final receipts. Resume requires the same initialization. Synthetic nonzero-law parent and changed-identity checks cover this. |
| F5 splash tie contract | Maximum count remains exact under the stated equal-radius centre metric. Tie is explicitly nearest-origin/x/y among enumerated count-maximizing witnesses, not all feasible points. The single-enemy counterexample is a documented parity fixture. |
| F6 validation twins | Python/native primitive boundaries reject nonfinite inputs/overflow; direct bank calls validate exact unit/own/threat widths, IDs, finite values, physical values and capacity limits, including coverage's direct path. Candidate outputs are checked. Malformed/nonfinite/65-own-unit fixtures cover the gap. |

The nonblocking participation issue is added to the explicit host arbitration boundary: raw dodge coverage must not be called executed dodge coverage. No host fight or training is authorized or performed by this review disposition.
