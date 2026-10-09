# Owner recheck

Request sent verbatim to separate reviewer `/root/rrg_recheck`:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Reviewer: separate Codex agent, same model family (available collaboration reviewer). Read-only review; no numeric scores. This is an exploratory diagnostic recheck, not a registered milestone acceptance.

Code findings and disposition:

- Source provenance gap: checking hashes before/after inference did not prove the imported forward code matched the training pins. Fixed: runner now compares common.py, models.py, data.py, training.py, recording.py and training_control.py to the round-0 TRAIN_BUDGET source hashes. Reviewer independently confirmed those pins match.
- Reporting limit: reset-disabled is an exact no-op because no attack reset exists. Drift removal cannot change target prediction on fixed positions. Frozen-phase still retains deterministic ID phase features and phase readouts. Reflected explicitly in JSON definitions and Markdown.
- Remaining code review: selected windows/full prefixes, geometry units and masks, frozen graph and death handling match the pinned implementation. No blocking findings.
- Follow-up caching review: per-row N1h/other input reuse is read-only and matches pinned packing; graph cache invalidates on persistent IDs and resets per fight. Exact multi-tick/death tests added. No new blocking findings.

Execution adjustment: first partial inference was stopped after three completed sequences to reduce redundant packing/graph computation. RUN_ATTEMPT1_STOPPED.log preserves that partial attempt. No scientific metrics or complete receipt were produced by it. After the first optimization, nine light tests passed in 2.48 seconds. Inherited nice 15 already satisfies the requested low CPU priority; one Torch thread and one interop thread are used.

Additional reviewer findings and disposition before final inference:

- No geometry→mode initially also removed the forcing scalar supplied directly to the head. Fixed: only the phase RHS forcing and K are zeroed; raw forcing remains in state/head. The strengthened test verifies this retention and omega-only evolution. Separate reviewer checked the change and found no blocking issues.
- Remaining-margin wording could overstate preservation of the full original gain. Fixed: report separately quantifies margin loss and remaining margin, states that phase features/readouts remain, and avoids phase-free architecture or resonance-proof claims.
- Low R can also indicate opposing clusters. Fixed in plain-language explanation. Coupling statistics are instantaneous post-step RHS terms, hypothetical when phase is frozen; this is now explicit.

Second partial inference was stopped before completion to fix the forcing confound; preserved in RUN_ATTEMPT2_STOPPED.log. The final planned code/test/report batch passed nine light tests in 0.92 seconds, then the final replay started. No finished inference receipt was replaced.

Isolation correction: concurrent Stage B2 source edits appeared after the replay began. The original unchanged-input guard included unused Stage B2/rev2 source files, which would incorrectly reject unrelated development. Stopped the third partial attempt (18 complete sequences) and preserved RUN_ATTEMPT3_STOPPED.log. The guard now covers actual pinned forward dependencies and data/checkpoint inputs only. No unrelated changes were reverted or edited.

Performance correction in the same batch: exact reset-disabled and drift-only state/head identities reuse intact computation; all requested metrics are still scored on every selected row. The report explains this reuse. Final light tests passed nine checks in 0.90 seconds before restarting inference.

Final result/report recheck: **PASS — no unresolved findings.**

Separate reviewer independently checked the 50-sequence aggregate row/correct counts and weighted movement/aim errors against JSON, all original outcome count differences (exactly zero), zero-label aim nulls, identity-arm heads/diagnostics, and retained raw forcing with zero effective phase forcing. K=0, frozen phase and geometry→phase removal lower both ranged and artillery target accuracy in every test fight. The report bounds its claim to this trained checkpoint on fixed observations.

Presentation correction after inference: completed JSON and source rehashes were written before Markdown failed formatting absent aim as a number. Saved CHECK_RUN_SOURCE.py byte-for-byte at the exact executed hash, then changed only report() to display N/A and lead with the measured answer and K=0 phase-order summary. Regenerated Markdown from the completed JSON, without rerunning inference or altering its bytes. RUN_SOURCE_PROVENANCE.json records the source mapping, report-only diff and hashes; REPORT_CHECK.txt records the presentation checks. Reviewer verified the source snapshot and all recorded input hashes, and confirmed AST identity outside report().

Final inference: float32, 50 test fights, 63,897 full-prefix ticks, 592,992 scored unit rows; 697.15 seconds wall / 678.61 seconds CPU, inherited nice 15, one Torch thread and one interop thread. Nine ablation/cache tests passed before the final run. All work products are in rrg_ablation; docs/PLAN_CURRENT.md was not touched. Concurrent Stage B2 edits were preserved.
