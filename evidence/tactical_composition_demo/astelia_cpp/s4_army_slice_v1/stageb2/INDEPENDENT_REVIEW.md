CHANGES_REQUIRED
Reviewer family: Codex
Reviewer: independent reviewer agent, distinct from implementer; same model family because no other family was callable in this session.
Scope: read-only inspection of the prospective Stage B2 implementation, native seams, mathematics, training/resume, coverage, baseline bridge, DAgger, readout and learned-dodge gates. No tests, compilation, training, fights or heavy jobs were run by the reviewer. The implementer reports 11 focused tests passing in 8.51 seconds; that result is not independently reproduced here. Production-host arbitration, safety and performance remain unqualified.

Owner request received verbatim:
> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

## Ranked actionable findings

### F1 — High: learned-dodge eligibility does not bind the successful parent fights to the checkpoint being inherited

`enable_dodge.py:21-29` reads `complete`, `harm_stop` and aggregated wins, then captures the hashes of whatever parent parity/export/checkpoint files exist now. It does not verify the look's `ledger_sha256` against the outcome ledger, run the parent parity gate, verify completion coverage, or bind the current `.pt` to the calibrated export/outcome used in those fights. The subsequent `check()` proves that files have not changed since enablement; it cannot prove that these were the files which earned eligibility. A stale successful look and a replaced parent checkpoint can therefore initialize react-OFF work without the declared behavioural prerequisite being established for that checkpoint.

Required disposition: validate the complete parent identity chain before writing `DODGE_READY.json`, and retain the relevant ledger/outcome/checkpoint/export bindings. Add a light fixture which changes a parent checkpoint or disconnects the look from its outcome ledger and must be rejected. Do not run fights for this repair.

### F2 — Medium: invalid padding can win a categorical candidate head

`models.py:70-75` uses `-1e6` for invalid entries and takes an argmax over the entire padded bank. `native_patch.py` generates the same pattern in `toolScores`/`infer`. The allowed finite parameter schema provides no lower bound on valid logits. When all valid scores are below `-1e6`, padding wins; Python selects a zero point, while native movement can throw on `banks.move.at(mi)`. At exactly the sentinel, enumeration order can also select an invalid entry. Matching the sentinel across twins does not establish that selection is among valid candidates.

Required disposition: make validity an unconditional selection invariant, keeping finite parity output if required, and add an adversarial light case with very negative finite valid scores. Canonical max-valid shifting is one possible implementation; actual selection must never consult padding.

### F3 — Medium: empty required aim banks are silently accepted despite the declared stop condition

`candidates.py:69-71` and `candidates.h` reject missing movement only. An empty annulus/arena intersection can leave every aim option invalid. `models.py` then chooses padding index zero; `native_patch.py` explicitly substitutes `Point{}` for an empty aim bank. Native command projection may produce no aim, while the supervised aim objective masks this row instead of rejecting it. This disagrees with the protocol's yes/no stop row, "Empty candidate bank for required aim / overflow / nonfinite value? Reject affected revision."

Required disposition: distinguish a genuinely unused aim head from required artillery aim with no legal option, and enforce the declared handling consistently in coverage, training and native inference. Preserve honest no-candidate audit rows rather than silently converting them into an apparent valid coordinate. Add a light empty-intersection native/Python contract check.

### F4 — Medium: learned-dodge receipts misstate the inherited N2 law

`training.py:make` loads the nonzero react-ON parent state for learned-dodge. `worker.py:45` still reports `law_initial=[0]*6` and `K_initial=1.`. Those values describe a fresh model, not the warm start. This creates incorrect mechanism provenance precisely in the ON/OFF comparison. The actual initialized law, coupling value and checkpoint identity should survive resume so that a restart cannot redefine the initial baseline. The forcing delta already captures the fresh initialized model, but its initial reference should likewise be explicit in the receipt.

Required disposition: persist and report actual initialization values and warm-start provenance; use the persisted initialization after epoch resume. Verify with a synthetic nonzero-law parent, without optimization or fights.

### F5 — Medium: the best-splash tie contract is stronger than the implemented mathematics

`tools.py:best_splash`, `tools.h:best_splash` and the protocol specify a maximum count with nearest-origin tie breaking. The finite arrangement candidates can attain the maximum count, but they do not contain every closest point in a maximum-count region. For one enemy at `(100,0)`, splash radius `10`, origin `(0,0)`, legal band `[0,200]` and a sufficiently large rectangle, the only relevant emitted candidate is `(100,0)`; `(90,0)` attains the same count and is nearer the origin. Python/native parity agrees on the wrong stronger tie claim.

Required disposition: either implement the global tie contract by adding the relevant closest points, or state explicitly that nearest-origin tie breaking applies only among the enumerated count-maximizing witnesses. The geometric maximum-count claim and the narrower deterministic tie contract should be separate. Add this one-enemy mathematical case to the focused checks.

### F6 — Medium: direct candidate and primitive twins have inconsistent validation envelopes

`data.py:pack` validates entity/public-bank limits, but coverage calls `mapped_labels` → `bank` directly. Python `bank` does not enforce the C++ `candidates.h` own-state/entity/bank envelope. A frame with more than 63 friends can still fit the padded movement capacity and pass Python coverage while native candidate generation rejects it. Primitive sign checks also admit nonfinite coordinates and several nonfinite scalar parameters: for example, `flight_time` accepts a NaN lob speed because `lob_speed<=0` is false, and `range_project` does not reject a nonfinite query point. The protocol's reject-nonfinite condition is not enforced by these public tool entrypoints.

Required disposition: share explicit finite-input/schema/envelope validation at Python/native tool and bank boundaries, including the path used by coverage. Check outputs as well. Add small malformed/nonfinite parity fixtures; no heavy jobs are needed.

## Nonblocking observations and limits

- The candidate-only and bounded residual coverage reports describe raw goals. In learned-dodge, the inherited `participate` function still projects goals into an enemy engagement band before body execution. O's react movement overrides participation; the react-OFF learner's copied dodge does not. Consequently a raw dodge candidate can be covered while the executed learner endpoint cannot match it. The existing documentation correctly reserves arbitration qualification for later host work; the first host check should explicitly measure participation overrides on dodge-labelled rows before claiming learned-dodge expressiveness. This is a deployment limitation, not authorization for new fights now.
- Source manifests inspected here enumerate code and the ML lock, not living Markdown documents. Stage A/B/rev2 were read only. The tooling provides separate variant roots, per-invocation files, own-occupancy DAgger, calibrated network-only baselines and paired fights. The RRG note limits claims appropriately and does not treat tool reuse as source recursion.
- Synthetic no-combat inference tests are useful bounded evidence, but do not validate full native compilation or shared safety/body arbitration. The host commands and unmeasured estimates make that limitation visible.

Disposition: collect the required repairs into one batch, record the implementer's response separately without rewriting these original findings, and rerun only the focused checks justified by those changes. This review does not authorize training, fights, reward training, growth or milestone acceptance.

## Repair disposition check

Disposition: ALL F1–F6 RESOLVED FOR THE PREPARED DEVELOPMENT BUILD.

This was a short read-only check of the six repair paths and their focused fixtures, not another broad review. The original verdict and findings above remain the historical initial review. The implementer reports 17 focused tests passing in 6.91 seconds after the single repair batch; the reviewer did not run or independently reproduce them.

| Finding | Checked disposition |
|---|---|
| F1 | Resolved. Enablement now calls parent parity/outcome gates, ties the successful look to its ledger, validates calibrated fit/checkpoint/export identities and every registered completion/raw hash, and recomputes actual wins and the harm boundary. Schema-2 readiness freezes those inputs. |
| F2 | Resolved. Python chooses from validity-masked scores; native argmax stops at the actual candidate count. Max-valid shifting preserves finite padded output under the ordinary admitted numeric envelope. The extreme-negative-logit fixture exercises the original counterexample. |
| F3 | Resolved. Required artillery aim-bank emptiness rejects training/native inference. Audit-only Python mapping explicitly preserves no-candidate counts without admitting those observations for fitting. |
| F4 | Resolved. Actual initialization law/K, force identity and warm-start checkpoint/readiness provenance are captured before resume, persisted in epoch state and checked against current initialization; final receipts use those values. |
| F5 | Resolved by the permitted contract correction. The protocol and Python API now scope the deterministic tie to enumerated count-maximizing witnesses. The one-enemy fixture records the distinction from a global nearest-point optimization. |
| F6 | Resolved for the reported gaps. Direct Python/native banks now validate matching unit/own/public-bank schemas, IDs, physical values, finite inputs and capacity envelopes; primitive boundary/output checks cover the nonfinite examples, including coverage's direct-bank path. |

No concrete remaining blocker was found in these six repairs. `OWNER_RECHECK_STAGEB2.md` still says "focused repair validation pending" at the time of this check; update that administrative status to the already reported result.

Boundaries remain unchanged: production native compilation, complete host parity, speed, shared participation/body arbitration, shadow isolation and behavioural comparisons have not been established by this delivery. The protocol now explicitly requires later host measurement of raw/post-participation/executed dodge errors; raw candidate coverage is not executed-action coverage. Training, fights and learned-dodge execution remain prospective and subject to the documented parent-result/cap gates. No tests, compilation, training, fights or protected edits were performed during this disposition check.
