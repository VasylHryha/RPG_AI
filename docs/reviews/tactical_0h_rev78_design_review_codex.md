CHANGES_REQUIRED

Reviewer family: Codex
Reviewer model: GPT-6
Design SHA256: 13312aac5b3e115c9ec90abb391d38efcc301c87dae40062f801b1cb6cfe59a2

Reviewed `evidence/tactical_composition_demo/DESIGN_0H_REV7.md`, revision 7.8, section 15, against the stored revision-7.7 F1 records, the fixture report, and the inherited pin, graph and clock contracts. The requested threshold/last-link questions concern section 15; section 12 is the historical N1d amendment, which this change leaves intact. This verdict blocks job 2 under the owner's explicit conditional instruction. No design or implementation file was edited, and no configuration/source identity was regenerated.

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

## Blocking findings

**R78-1 — The chain degree used in the re-derivation is contradicted by the stored records and the RHS.** Section 15 says chain elements have at most two neighbours on each side within the coupling radius, giving n=3–4. The phase graph selects up to eight elements within r<3; it does not truncate to two on each side. F1b has three phase neighbours throughout, but F1c has six for virtually its entire trajectory: across its 11,200 element/endpoints, six have degree five and 11,194 have degree six. Every element has degree six at t=160. The compact chain creates more full-radius neighbours, even when their individual weights are small.

`medium/rev7_medium.cpp::Medium::rhs` divides phase coupling by the full held phase-neighbour count. It does not divide by the strong degree or by a chain reference of four. The saved F1 `weights` equal exp(-r²)/len(neighbors) exactly for every stored edge, with zero discrepancy in a standalone check. Consequently, w=0.25 gives an aligned single-edge inverse rate of 0.75 s at n=6 and 1 s at n=8, rather than the stated 0.5 s. Using the actual F1c degree in the stated ledger would give w_min=6/(32·1·0.5)=0.375. A chosen reference degree of four could define a provisional engineering screen, but cannot honestly be called the actual degree of these scaffolds or a degree-bound timing re-derivation. Section 14.3's single-edge/whole-network limitation still applies.

Required disposition: the drafter must correct the degree and timing claims before implementation. Do not silently change the RHS denominator, neighbour selection or unchanged response gates to make the derivation hold.

**R78-2 — The pinned-last-link diagnosis is right for F1b, but incomplete for the mandatory live-layout F1c; the proposed threshold does not repair that failure.** F1b's final positions are S=3.129788044836463, i1=2.7659999999998868, i2=2.402211955163314, O=1.532, all on the x-axis. The two ordinary gaps are approximately 0.363788; the closing gap is 0.870211955163314, with raw weight 0.468945441414558. This supports the reported local pinned-end bottleneck. F1b's O is its disclosed literal pin (1.532,0), not the live origin.

F1c has O=(0,0). At t=160 its closest member is (1.4126041642985532,0), giving a closing gap of 1.4126041642985532 and raw weight 0.135952390417636. Its source-to-site distance is also about 1.412605; source eligibility still uses the unchanged strict site reach, not the strong element cutoff. F1c's final normalized nearest-output edge weight is 0.0226587317362726, with n=6. Its aligned single-edge inverse rate is approximately 1.37916 s. The 0.87/w≈0.47 F1b example does not describe F1c.

I filtered the already-stored directed phase edges by inclusive computed r≤sqrt(ln4), retaining the stored driven ordinary roots. No integration, project import, harness call or new experiment was performed. The same reconstruction at sqrt(ln2) exactly reproduces the recorded path counts, validating the diagnostic:

| Scaffold | Recorded 7.7 strong paths | Full stored graph paths | Proposed cutoff on stored endpoints |
|---|---:|---:|---:|
| F1a | 1600/1600 | 1600/1600 | 1600/1600 |
| F1b | 28/1600 | 1600/1600 | 1600/1600 |
| F1c | 6/1600 | 1600/1600 | 16/1600 (1%) |

F1c's last eligible endpoint under the proposed cutoff is t=1.6 s; its closest output link exceeds the new radius from t=1.7 s onward. Its strong-path fraction therefore remains far below the unchanged 80% gate. F1 scaffolds have frozen growth, and their motion/phase RHS uses the full graph; changing the strong-path predicate alone does not change their trajectory. This is a prospective design diagnostic on immutable historical records, not a replacement verdict or a revision-7.8 fixture result. The original 7.7 FAIL remains unchanged.

Required disposition: the drafter must explicitly address F1c and reconcile the intended strong-path criterion with the already-passing response, or disclose that this candidate knowingly leaves the mandatory gate unsatisfied and explain its purpose. Do not simply lower the cutoff again to fit the saved endpoints. Decide which claim the graph screen should test, preserve an honest clock ledger and the inherited scientific claim limits, and obtain review of the corrected proposal before implementation.

## Non-blocking checks and limits

**R78-3 — Radius arithmetic and weak-link exclusion are correct.** For w=exp(-r²), w≥0.25 corresponds to inclusive r≤sqrt(ln4)=1.1774100225154747. At r=2.2 and 2.6, raw weights are 0.00790705405159344 and 0.00115922917390459, respectively; 0.25 exceeds them by factors 31.6173 and 215.661. Those historical weak links stay excluded. This numerical separation does not validate the false degree premise or establish task-clock transmission through an arbitrary graph.

**R78-4 — Outcome-informed status is honestly disclosed.** Section 15 explicitly names the observed 7.7 F1 outcome, preserves the FAIL, identifies deterministic F1 scaffolds and discloses the inherited F5/F7 fixture-key reuse exception and untouched development inventory. The threshold is outcome-informed engineering, not an independent replication or evidence that the original rule passed. No new claim of fresh fixture entropy should be made.

**R78-5 — No trivial response pass, but E becomes easier.** At the proposed cutoff G_s remains a subset of G, and isolated permanent O still has no root/path privilege. Relative to 7.7, the relaxed cutoff enlarges G_s and can increase path exposure and suppress B-path sooner; it cannot improve frozen-scaffold response by itself. A/B response cuts are unchanged and F1c's structural cut still fails. Multiple incoming links, weak site drive, detuning and conflicting phases mean that neither a single-edge threshold nor structural E proves exclusive mediation or end-to-end clock adequacy. The separation of full-graph RHS/D4/qualification/budget from strong transmission screening remains internally consistent.

## Evidence identity and recheck disposition

Stored inputs read directly:

- `growing_shapes/runner/REV77_FIXTURE_REPORT.md`.
- `growing_shapes/runner/rev77_fixture_run_20261006/F1.json.gz`, SHA256 `e5049842d6b9e0e8b0006d67a717c83b109a686ef5b38a75affbdf8585dccb63`.
- `growing_shapes/runner/rev77_fixture_run_20261006/HARNESS_RECEIPT.json.gz`, SHA256 `b57bed928571b553e4eb5481596cbdff910514480f95bb22f7bf2810ea2e5d9b`; its F1 result exactly matches the standalone F1 file. Its F5–F9 entries remain NOT_RUN.

The owner's request was sent verbatim to read-only reviewer `/root/design_recheck`, as required by AGENTS.md. The available reviewer family was Codex; this bounded recheck is separate from the Codex cross-family review of the Claude-authored design. It independently confirmed both blocking findings, the actual degrees, both final output gaps and all reconstructed path counts. Disposition: incorporated before delivery; no numeric quality score assigned. Findings are recorded here because the owner explicitly prohibits edits to `docs/PLAN_CURRENT.md`.

Implementation, identity regeneration, synthetic implementation tests and integration-report changes were not performed because the design verdict is CHANGES_REQUIRED. No N1/F1–F9 execution, training, panels or project code ran. The drafter owns the design correction.

Assisted-by: Codex:GPT-6
