# Owner recheck and disposition — offline controls

Request sent verbatim to separate reviewer `/root/controls_recheck` for source review before final tests/replay, and again for the completed results:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Reviewer: separate Codex agent, same model family. Claude CLI availability was checked; it reported `loggedIn: false` and `authMethod: none`. Cross-family review could not be obtained in this session. This independent recheck is exploratory reporting review, not registered milestone acceptance. No numeric quality scores were assigned.

Source review findings and disposition:

- Inherited forcing metadata described the old no-geometry-to-mode cut rather than the new forcing-only control. Fixed before tests and inference: the raw forcing feature remains in every head, and effective phase forcing is zero only in forcing-only-cut.
- Strong causal wording needed to consider intact-no-bonus as well as indicator recovery. Fixed before inference: report wording incorporates both, uses descriptive recovery bands rather than acceptance thresholds, and keeps partial/mixed recovery separate from resonance qualification.
- Shuffle test initially checked reproducible draws from the same input state. Strengthened before tests: carry the perturbed phase state forward between invocations, while comparing the same-role multiset to an unshuffled update of that same incoming state.

The complete source/test batch passed 16 light synthetic checks in 0.91 seconds (1.13 seconds harness wall time), at inherited nice 15. No inference source or test changed after those checks. Offline replay then completed in 749.6 seconds wall / 715.0 seconds CPU, with one Torch thread, one interop thread and BLAS thread limits of one. Every dynamic arm had independent full-prefix state; output-only removals used exact pre-addition logits and intact state, with those identities tested independently.

Timing clarification: the closing sentence of the pinned protocol says “After replay: light switch tests and a separate owner's recheck”. Actual order was complete source review/change batch → light switch tests → replay → final results recheck, following AGENTS.md's requirement to finish all code/test changes before a long run. No code changes justified a duplicate test run after replay. The pinned protocol bytes and completed evidence are preserved.

Final recheck: **PASS for bounded exploratory reporting — no unresolved findings.** See CONTROLS_RECHECK_CODEX.md for the independent review. The reviewer verified all 89 input/source hashes, original metrics JSON identity, per-fight row/target/fire reproduction, weighted head metrics, diagnostic numerators/denominators, intervention comparisons and causal limits. No inference or tests were run by the reviewer.

Plain-language disposition: in this fixed checkpoint, removing the engineered neighbour-target readout leaves only 1.52% of the original ranged margin and 0.75% of the artillery margin. Its synchronised K=0 replacement recovers 60.69% and 49.22%, respectively. Almost all of the gain therefore depends on the hand-wired feature; a simple synchrony gate does not reproduce all of it. The remaining phase-conditioned difference does not uniquely identify information carried by phase dynamics or establish resonance.

Original metrics JSON SHA256 remains `64c1c652fcca0c48d72eb05733abe4b8fc1eee1f8f63458c858d7540d781bc93`. Controls JSON SHA256 is `5a83a5451a3fba12ec9c40dfa2843c4cad362b424ed98a3836e28d3693e501d9`. The original Markdown has only the requested report correction. Work stayed within rrg_ablation; upstream Stage A/B/B2/rev2 files and docs/PLAN_CURRENT.md were not edited by this task. No training, simulated fights or commits were performed.
