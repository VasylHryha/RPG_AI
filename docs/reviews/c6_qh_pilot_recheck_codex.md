CHANGES_REQUIRED_FOR_HARNESS_REUSE; STORED_PILOT_OBSERVATIONS_RECHECKED; C6_BLOCKED

Reviewer family: Codex
Reviewer model: GPT-6
Review type: implementer self-audit, not independent acceptance
Reviewed commit: e2a31cc (preparation: 9d72c5a)
Reviewed SUMMARY.json SHA256: 4b0d82536d2e3b977baf82a9ca07c50088d9a25dc0dbb4b6d87e20bb0965db18
Date: 2026-10-03

## Outcome

The stored 16-pair exploratory observations remain supported: Q qualifies
15/16 and structurally retains 15/16; H qualifies 6/16 and structurally retains
0/16. Quiet/patch conditions hold at the saved frames on all grids. The harness
has material enforcement and failure-receipt gaps and should not be reused.
The earlier successful tests did not establish its behavior on these paths.

This review does not reopen the one-run authorization. Original specification,
entropy, harness and receipts remain byte-identical. New audit files are
REVIEW_READY; this is not cross-family acceptance, C6 evidence, a new hypothesis
verdict or permission for development/retry. C6 remains BLOCKED / R006 STOP.

## Ranked findings and disposition

| ID | Severity | Finding and concrete evidence | Observed pilot impact | Required disposition before reuse |
|---|---|---|---|---|
| F1 | High | `pilot.py:398` dispatches `--worker` before checking the exclusive run directory. A stub worker is reached even with a consumed latch. Its real worker would write a named result with atomic replacement and has no parent resource supervisor. | No extra arm/file was found in the committed run. | Private authenticated worker channel tied to the owning supervisor; reject standalone workers and existing result targets. |
| F2 | High | `pilot.py:61` checks identities, then invokes a loader with an implicit build path. A synthetic artifact change between those calls reaches the original `build.build()` fallback; the probe substitutes a rejecting compiler stub, so no real build runs. | Before/after native identities still match; no artifact drift was found. | A future no-build loader must make rebuilding impossible rather than infer it from a prior check; do not modify this recorded loader/harness retrospectively. |
| F3 | High | Finalization at `pilot.py:368–387` has unguarded cleanup, bulk JSON loading and interpretation. Synthetic malformed partial JSON and a cleanup exception each escape without a SUMMARY. | All 32 observed records parse and the actual final summary exists. | Isolate cleanup/parse/interpret errors per arm and record them in a best-effort INCOMPLETE summary; preserve raw corrupt/partial files. |
| F4 | High | `pilot.py:316` checks CPU before harvest, then the last worker can push completion CPU over the cap with no further loop. A stub records 20 CPU seconds against a 10-second cap with no STOP. Final hashing/writing follows the captured wall/CPU totals at lines 383–387; delayed synthetic receipt writing exceeds a scaled wall cap without detection. `wait4(pid,0)` and filesystem calls can block outside a deadline check. | Recorded wall 245.859 s and CPU 508.386 s are far below caps, but the exact full setup/shutdown/receipt totals are not measured. | Recheck resource limits after every harvest, include finalization in an outer clock, and use an independent supervisor/watchdog for a strict whole-lifecycle wall bound. Do not claim a sampled monitor gives an absolute instantaneous RSS bound. |
| F5 | Medium | `pilot.py:347` drops a process group when its leader exits. A successful synthetic leader leaves a live descendant outside subsequent monitoring and final cancellation. Its group's final CPU is not fully accounted. | The scientific worker path has no intended child process with the matching native artifact; the probe is a prospective lifecycle failure, not evidence of a leaked pilot worker. | Track group lifetime through descendant shutdown, not only leader reaping; account descendants or prospectively prohibit them. |
| F6 | Medium | `pilot.py:261` builds a dict by arm identity without duplicate rejection. All 32 rows plus a duplicate are accepted as COMPLETE. Required trajectory/schema validation is also absent from this interpretation path. | Exact 32-file inventory, unique identities, complete trajectories and counts pass the stronger audit. | Use strict per-arm identity/schema validation and explicit required/not-run fields before interpretation. The new read-only auditor rejects duplicate/missing/invalid identities and bad measurements. |
| F7 | Low | The stored `last_serialization_seconds` is assigned after the write and therefore describes an earlier save; worker seconds/RSS are sampled before its last serialization. Repeated replacement checkpoints do not retain a chronological history of every overwritten state. | Parent wait4 accounting includes worker completion and lifetime peak RSS; no scientific conclusion relies on serialization timing. | Label the per-record samples correctly, separately account cumulative serialization, and use an append-only journal if checkpoint history is required. |

The high findings are confirmed by bounded negative probes, not hypothetical
warnings. Their severity refers to harness enforcement/reuse. It does not
convert this complete saved pilot into a failed scientific outcome. A native
race requires concurrent artifact drift; no such drift was found here. The
original scope explicitly prohibited concurrent dependency/build edits.

## Stronger check of the actual saved observations

`evidence/c6_dev_pilot/r4_sensitivity_recheck/audit.py` is read-only. It never
calls integration, native loading, recovery/causal simulation, operation or
world generation. It checks the original summary hash, specification hash,
all 85 dependency identities and exact artifact inventory/hashes. It restores
and verifies snapshot identities, checks material/probe/background pairing,
trajectory shapes/endpoints and actual-versus-carrier amplitudes.

It independently derives detector statistics from the saved prefixes for
**96 minimum-size candidate rows across all three grids**, then derives all
**6,363 rolling windows** from the saved prefixes/continuations. Selection,
returned recovery decisions, causal thresholds/refinement and first-loss rows
agree with the original record. All reported counts and qualification
forward/reverse discordances agree. This checks the existing verdict rules;
it does not introduce new rules or change an old verdict.

The seven frequency-only qualification associations (pairs 1, 2, 3, 8, 9, 10,
13) also hold on the finer grids. Five of the six initially qualified H units
first fail through frequency alone on all grids; the sixth fails phase-pattern
stability. Mixed failures and the both-failing pair remain excluded from that
association. No unique causal mechanism is established.

Limitations remain explicit: the helper did not store recovery/causal control
trajectories, so effects cannot be independently reconstructed. The audit
checks returned effects and their decisions. Per-production-step integration
errors remain original recorded diagnostics; integration was not rerun. Site
retention is verified at saved frames, not proven between those frames. These
are limits of this exploratory record, not newly claimed C6 qualification.

Receipts: `STORED_RECHECK.json` and `CHECKS.json` in the new recheck directory.
Twelve targeted negative/control tests passed in **2.61 seconds** after the
complete planned audit/test batch. No full project suite was repeated because
no project implementation or original pilot file changed. Synthetic processes
were bounded and their owned groups cleaned up. The original one-shot pilot
was not repeated. Legacy fault probes pass when the existing failure is
reproduced; their pass count must not be misread as repaired-harness acceptance.

## Model, architecture and C++ — owner questions

The heavy numerical law already runs in C++: `native/c6_r4/field.cpp:54`
implements the field/material derivative and `:115` implements integration.
Python orchestrates qualification, statistics, records and supervision.
Changing language can change runtime cost; it does not by itself change these
registered model outcomes. The pilot finished well inside its resource budget.
This does not qualify full-world C6 runtime, whose registered STOP remains.

The medium sites retain heterogeneous frequencies. Each candidate receives
its own incoming carrier initialized from its arm's background; the native
law sums its saturated, spatially weighted site signal into the candidate's
phase dynamics (`field.cpp:79–104`). That path offers a plausible explanation
for changing collective frequency under a retained strong background. It is
an inference from the equation and failure pattern, not isolated causation:
Q/H also changes amplitude and phase initialization.

This does not disprove RRG or establish that R4 can never enable formation.
There are only 16 paired populations under one supplied construction. No
H-success/Q-failure pair was observed; the pilot is exploratory, and H is not
source-produced B_after. It tests suppression/stability here, not two-link
recursive background generation or universal possibility change.

A change of modeling approach is a reasonable **separate prospective proposal**.
Its question should be whether the apparatus can distinguish both suppression
and enablement while retaining the RRG definitions, not how to loosen detector
thresholds until this panel looks favorable. Separate amplitude, phase
organization and frequency heterogeneity as causal factors before attributing
a mechanism. Predeclare comparisons, normalization and stop rules before new
inputs; retain current evidence as history. A coherent-medium arm, K/J search,
new development entropy and further execution are outside the existing pilot
authorization. No such study is implemented or run by this review.

## Self-challenge and remaining gate

- Duplicate/standalone-worker faults might otherwise be dismissed as deliberate
  forgery. The exposed CLI can also be used accidentally for debugging and can
  overwrite an existing arm file; caller guards are therefore relevant.
- The descendant fault is not a demonstrated leak in this run. It is explicitly
  bounded to supervisor lifecycle/reuse; the normal scientific worker has no
  intended descendants.
- Broad hard-deadline claims were stronger than the monitor actually enforces.
  The current observed cost margin is substantial; this is not evidence that
  the completed run exceeded a cap.
- A result matching stored hashes alone could preserve an implementation error.
  The new trajectory-derived candidate/rolling checks specifically challenge
  that risk without resampling or revising scientific outcomes.
- A suppression pattern cannot pick the next model or prove an enabling model
  impossible. That inference is kept out of the result.

The remaining engineering gate is a separately recorded future harness repair
and its adverse lifecycle tests before reuse. The remaining scientific gate
is the owner's separately approved next-study proposal. No independent
acceptance or new execution is supplied by this same-family self-audit.
