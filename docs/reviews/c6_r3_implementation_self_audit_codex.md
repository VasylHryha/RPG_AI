Verdict: **CHANGES_REQUIRED**.

Reviewer family: Codex
Reviewer model: gpt-6
Review type: implementer self-audit; not independent acceptance
Reviewed HEAD: `71473a435f29cf97cdbd303c22bc68b6af9f15ca`
Implementation commit: `560ecdbe8ebea85a1a4b27f86b018be1a609d506`
Reviewed development results SHA256: `25e69d80ef36d12271badd2359bc1bed0e71f1e9acc02bd77a3202b194603b54`

The owner requested a critical recheck and authorized substantial rework. The R3 implementation is not ready for final registration. Its recorded development STOP remains valid and unchanged. Engineering repairs below are prospective support components in new files, not an implemented or approved replacement experimental model.

The read-only [artifact audit](../../evidence/c6_r3_recheck/AUDIT.json) verified all ten compressed/raw world artifacts, eighteen receipt-bound implementation files, all twenty-five imported release files, the twelve owner identities, twenty-three manifest entries and twenty-four checksums. No development gate, mutation probe or recorded panel was rerun. Accepted C0–C5 and R3 receipt-bound files were preserved.

| Finding | Evidence and consequence | Disposition |
|---|---|---|
| F1: treatment begins before source qualification | `geomind/c6_r3_protocol.py:make_flows`, `run_world` and `assess_turn` start the coupled branches at t=0 and qualify the source at t=100. A subsequent bath difference can include preformation drift. It does not isolate backreaction of an already qualified unit. | **Open experimental blocker.** A replacement needs a common qualification prefix and paired interventions from the same qualified snapshot. New analysis checks reject timelines that precede qualification; no corrected collector/model has been executed. |
| F2: formation scope excludes mixed candidates | The stored worlds contain six pure-source candidates, none accepted, and nine mixed/prior candidates across seven worlds without recovery assays. The pure-cohort restriction is declared, so 0/10 is valid within that scope; it does not establish absence of resonators throughout the world. | **Open model/scope blocker.** Record mixed-group diagnostics without retroactive promotion, or prospectively redesign source attribution and causal isolation. Do not lower thresholds or relabel recorded mixed candidates as qualified. |
| F3: numerical accuracy and coverage | World 4 has dt=.02 versus .005 error .07428287802458922, above .05; even its half-step error exceeds .05. `numerics` checks two-second intact windows initially and after formation, rather than full formation, operation, descriptor, causality and candidate/recovery horizons in all reached branches. Finer integration samples a coarse replay. | **Open experimental blocker; validation contracts repaired.** New checks require full reached scopes, separately normalized position/phase errors, independently refined replay, and grid-stable causal effects with vanishing ablations. These checks do not supply missing real measurements or prove convergence. |
| F4: chain metadata checks copies rather than actual inputs | R3 compares equalities inside `chain_link`. A deterministic witness changes the actual inherited bath while leaving those copies equal; R3 still passes provenance. | **Repaired prospectively.** Link fields bind actual bath/source inputs; episode-zero reference, prior, qualification flow and ending bath must match the reused prefix. Episode zero must qualify and its selected unit must be the next source. |
| F5: recursive contrasts can use different populations | R3 combines per-turn contrasts with a separate complete-chain count. A fixture has twenty first-turn worlds but ten complete chains; only the excluded worlds carry the first-turn effect. R3 reports support although complete chains have no first-turn effect. | **Repaired prospectively.** Eight additional contrasts restrict both turns to exactly the same complete chains. Sixteen primary contrasts receive the corresponding family correction. No recorded verdict is changed. |
| F6: evidence flags and identities insufficiently validated | Duplicate world IDs, unpaired candidate initial states, or qualification flags inconsistent with actual causal evidence can survive the old evaluator. | **Repaired prospectively.** Exact expected world inventory, paired episode inventory, persistence/causality checks, linked finite publication fields and timeline checks are required. Missing or inconsistent evidence is rejected. |
| F7: partial source inventory can pass | A fixture with an empty imported hash inventory receives the old source-pin PASS with zero verified files. | **Repaired.** The new read-only checker verifies the complete release against the separate owner handoff/expected record, manifest and checksums; it successfully verified the real import. |
| F8: state identity and finiteness gaps | Replay digest hashes bytes without shape/time-grid identity: equal bytes reshaped to different frame/population counts have different durations but identical old hashes. Old recursive finiteness ignores NumPy arrays. | **Repaired prospectively.** New digests bind schema, kind, metadata, shapes and array boundaries; recursive finiteness includes numeric arrays. Existing recorded digests remain unchanged. |
| F9: a late engineering failure suppresses an earlier valid claim | R3 uses accumulated/global gates when assigning per-turn claims. A second-turn numerical failure can erase a valid first-turn result. | **Repaired prospectively.** Each turn retains its own valid claim scope; whole-chain engineering failure still blocks recursive qualification. |
| F10: stage timeout disagrees with approved panel budget | The shared pipeline default is 3600 seconds; the R3 prospective runtime budget is three hours. | **Repaired in shared tooling.** `tools/verify.py` honors a positive integer `timeout_seconds` from the fingerprinted stage specification. Existing configurations retain the default. A future registration must declare 10800 seconds explicitly; no final configuration/panel exists now. |

Prospective analysis semantics also make CHANGE two-sided: either a predeclared positive or negative effect outside the practical margin can pass; an interval strictly inside the margin fails, and a touching interval or insufficient quorum is inconclusive. R3 explicitly tested an increase. The replacement semantics and sixteen-contrast family must be approved and registered in a new proposal before experimental execution. This is not permission to reinterpret R3 negative results.

Additional gaps retained for the redesign:

- Background descriptors are recorded only after source qualification. All ten failed worlds therefore lack measured background before/after descriptors, limiting diagnostic value. A future collector should record independent bath diagnostics whenever physically defined.
- The sham outgoing mask is a literal receipt value. Native fixtures exercise zero-output isolation and source preservation, but future full-scope checks must measure the actual control path rather than rely on that label alone.
- Recorded costs cover native work and returned array bytes rather than all peak memory, reference work, serialization and I/O. H-EFF remains NOT_TESTED.
- A process-local cached native kernel can outlive a same-process rebuild while disk metadata changes. This was not observed in the fresh R3 run. Future loader work should bind the loaded binary identity or require a fresh process after rebuild.
- Arm A remains stopped under decision 0013. Second-turn runtime was never reached. The nineteen prospective mutants were not probed, and no cross-family acceptance review exists for a final C6 revision.

Self-challenge and counterexamples checked:

- Conditional replay is an explicitly declared model boundary. No hidden upper-level prediction API descendant read was demonstrated merely by the existence of replay.
- Mixed candidates were deliberately excluded prospectively. That is a scope limitation and design concern, not evidence that the recorded STOP was forged or that these unassayed groups qualify.
- Native/reference agreement is strong: maximum error 3.552713678800501e-15; equivariance maximum 3.930189507173054e-14. The demonstrated numerical defect concerns accuracy/coverage, not a proved mismatch between the C++ and reference laws.
- Engineering tests and synthetic support fixtures establish rejection behavior. They are not fresh-world formation measurements, population proof, milestone acceptance or a replacement for independent review.
- No replacement physical background model was selected. For example, a fixed linear operator with additive forcing retains an unchanged additive-state impulse operator; a proposed alternative must specify and test the actual response observable rather than assume response change follows from forcing alone.

Repair ownership and validation:

- `geomind/c6_r4_integrity.py`: read-only file identities, exact world inventory, shape-aware digests, complete source-pin verification.
- `geomind/c6_r4_analysis.py`: prospective evidence/causal/numerical contracts, actual chain binding, complete-chain contrasts and per-turn claim scope. It has no experimental runner or registered final seeds.
- `tools/c6_r3_recheck.py`: inspect the existing stopped development receipt without changing or rescoring it.
- `tests/test_c6_r4.py`: deterministic old-behavior witnesses, repaired rejection cases and positive/negative control fixtures; no new physics pilot or panel.
- `tools/verify.py`: registered stage timeout support, with default and invalid-value tests.
- `AGENTS.md`: owner rule requires tests once after all planned changes, with an early run only for a concrete progress blocker.

The final completed-batch test result and repair-source hashes are recorded in [CHECKS.json](../../evidence/c6_r3_recheck/CHECKS.json). No component here self-accepts C6. The next scientific step is a prospective redesign resolving F1–F3, followed by the existing owner approval, registration, verification and other-family review process.
