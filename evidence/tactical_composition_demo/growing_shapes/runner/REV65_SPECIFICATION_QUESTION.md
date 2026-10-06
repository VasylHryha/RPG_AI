NOT_READY

2026-10-06. Read-only inspection of HEAD 915dc32, AGENTS.md, DESIGN_0H_REV6.md revision 6.5 (including section 19.7), and Claude's CHANGES_REQUIRED implementation review of 437e36a. No code edits, builds, tests, timings, fixtures, training, development or evaluation were performed in this repair session.

Section 19.3 requires clarification before implementation:

The base design section 3 maps the memory cue to physical site pi_e(0), permuted per episode. Does the single-oscillator baseline stay at one globally fixed physical site, or sit at the cue's assigned physical site and stay fixed there throughout each episode? These alternatives give different access to the visible cue and therefore different encoding performance. Neither section 19.3 nor the cited external recheck section 4.3 specifies this choice or the oscillator's initial phase and gain.

Revision-6 output members are drive-masked. A single driven oscillator therefore also needs an explicit baseline readout convention: decoding its ordinary-element phase directly bypasses the designated-output role rule, whereas giving it the output role prevents encoding.

Proposed concrete contract for owner/drafter confirmation: one ordinary oscillator at the cue's assigned physical site pi_e(0), position fixed for the entire episode, omega = pi, gain = 1, initial carrier-relative phase = 0, no adaptation or growth, the unchanged lawful site drive during the visible 4 s, free evolution during the hidden 12 s, and the same memory decoder supplied directly with this oscillator's phase and C = 1. This direct singleton readout is explicitly a baseline-only convention. If a globally fixed site or different initialization is intended, specify it before implementation.

Question: Is that concrete baseline contract approved?

Stopped under the user's instruction: "If anything in section 19 is ambiguous, write the question and stop." The drafter owns any design amendment; the governing design was not edited or re-pinned. Findings 1-10 remain pending. The only changes in this session are this question and the current-status prefix in REV6_INTEGRATION_REPORT.md. The historical implementation report is retained below that prefix and is not current verification evidence.

Assisted-by: Codex:GPT-6
