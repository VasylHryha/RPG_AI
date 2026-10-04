# Why we are doing this, and what each step is for

Plain-language record, written 2026-10-03 at the owner's request ("document why we did it and what the motivation"). It is a map of the
reasoning, not a result. The results are in the `REPORT*.md` files and each step's `SPECIFICATION*.md`.

**Corrected 2026-10-03** after a recheck: the trail and the "still ahead" list below were rewritten where the data did not support the earlier wording.
The list of corrections, with their basis, is in `CORRECTIONS.md`. The earlier text is in git history (`e88354c`). Authority and scope of this whole line
of work: `docs/decisions/0028-owner-directed-exploratory-composable-shapes.md`.

## The goal

Show that an AI can be built from **small pieces ("shapes"), each responsible for one job**, that combine into bigger pieces which act as one piece,
and so on upward. Today's AI is usually one very large learned block. The owner's idea is a different way to build it: pieces that are quick to make,
easy to check, easy to change, and reusable across situations.

In concrete terms: a game unit that moves, aims and chooses abilities could be three small pieces; a unit is those pieces combined; a squad is units
plus a tactics piece. Each level reuses the level below it.

## Why this might be better (the hypotheses)

1. **Quick to build.** A small piece with one job needs little data and trains in seconds.
2. **Quick to change.** When one rule changes, retrain one piece; the rest is reused. A single big block usually relearns everything.
3. **Reusable.** The same piece serves different unit types and different levels.
4. **Checkable.** A piece with one job can be tested on its own before it is combined.
5. **It is an analogy to the theory, not a test of it.** In the owner's RRG idea, a stable shape and its vibration (frequency, rhythm, signature) decide what it
   connects to, and stable combinations become the next level (the same rule repeated). These demos use ordinary networks wired into units; none of the RRG
   hypotheses (H-M, H-COMP, H-BG, H-PS, H-RBG) is tested here, and calling the pieces "shapes" does not make the AI geometric. A positive result would show a
   bounded engineering fact about imitation and adaptation in one sandbox.

## How we got here (the trail, honestly)

| Step | What it was for | What it found |
|---|---|---|
| Physics route (C4 to C6) | Do oscillating units form stable groups, and groups of groups, by one rule? | Two levels worked for the groups that formed (formation is near its threshold, so this is not a population claim); the third stalled. The route was slow and complicated, and I (Claude) misread the idea along the way |
| Two-body pilot | Why does level three fail? Do groups fuse? | In pairs of level-2 groups, they do not fuse. The stored recovery data point to phase-pattern misses of about twice the threshold on one test (a hypothesis, not tested). A post-hoc table of the stored units shows no link from a unit's size or radius to its rate (`a_twobody/ADDENDUM.md`): the model has no shape-to-frequency link. Pairs only; five-group worlds untested |
| Research and rethink (theory, outside projects, process guides) | Find a simpler, more direct test of the owner's real goal | Pieces that fit and compose are the core; the physics substrate is a later question |
| Arithmetic demo | Do small taught pieces (add, multiply, divide, square root) compose and promote? | Wiring works at one level, but one big map matched it, errors build up over a chain, and an ordinary network was far more accurate: arithmetic is the wrong test |
| Tactics, Stage 0 (AIM + MOVE) | The same question on a task where positions and ranges are natural | Two small separately taught pieces play almost as well as the scripted expert; one big controller of the same size is much weaker. A block with 16 times the rows and 7.3 times the parameters (5,765 against 787) comes within 0.05 on seen mixes and is ahead on the never-seen type. The wired design copies the teacher's own computation graph and the block is a plain network over fixed enemy slots, so structure, shared scoring and separate teaching are not separated (a structured end-to-end baseline was not run) |
| Tactics, change-cost test (Stage 0c) | The "quick to change" hypothesis | First revision inconclusive (fine-tuning stalled; my explanation was wrong, corrected). Second revision: SUPPORTED within this sandbox, on a margin of 0.001 for its first gate. Retraining only the affected piece reached the 0.80 level at the 100-row floor of the grid, where a single block of the same size first reached it at 1,000 rows (a ratio of registered first-success grid values, not a bound on the need); the block reached 0.90 in only 2 of 20 seeds within 12,000. The reused piece kept its step correct (2 degrees against 11 for the block at 12,000 rows). Part of the result restates the design (`REPORT_CHANGE2.md`, `CORRECTIONS.md`) |
| Structure versus composition (0d Part A, 2026-10-03; rechecked 2026-10-04) | Is the wired unit's advantage the structure or the separate teaching? | 30 seeds, pre-registered: a jointly trained structured network is about 0.02 below the separately taught pieces (C ahead in 30 of 30 seeds, inside the ±0.03 margin) and both are 0.40 to 0.47 above small tuned flat models at 3,000 states, so the advantage is consistent with coming from the graph that both were given, not from separate teaching (which element of the graph matters is untested). The flat baseline is weak (it plays worse than rush); a probe shows flat models climbing with data (0.74 at 60,000 states), so this is a small-data statement. Same sandbox, imitation, one level (`REPORT_0D.md`) |
| Replacement and connection (0e, 2026-10-04; rechecked) | Do pieces swap with scripted and conventional parts; is the connection useful and stable; are pieces stronger than a normal AI? | 30 seeds, pre-registered; the registration (not the result) was Codex-reviewed. Pieces replace the scripted ones within the 0.05 margin (at most 0.035 worse) and swap with a conventional policy; the connection is worth about +0.12 against a coherent alternative; registered small faults cost almost nothing, large ones collapse the unit; spread not measurable at this size; pieces are not stronger than a conventional per-slot policy, and under imitation could not be. In the original sandbox the connection could not matter, so the task was revised (V3). (`REPORT_0E.md`) |
| Recheck and shared library (2026-10-03) | Is this the best we can do? | Four same-family audits found no verdict that fails to re-derive, but several overclaims, fragile gates and code defects. Corrections are in `CORRECTIONS.md`; repaired shared tooling is in `tcd_common/`; experiment 0d was then designed and run (`PROPOSAL_0D.md`, `SPECIFICATION_0D.md`, `REPORT_0D.md`) |

## Why the change-cost test (and not the "structure versus teaching" test)

The natural next question after Stage 0 was whether the advantage comes from the wired *structure* (one scorer shared by all enemies, a step
that depends on the chosen target) or from teaching the pieces *separately*. I judged then that training mode could not separate the two. That was
too strong: training the same wired structure jointly, end to end, is a different computation and is exactly the missing baseline (the Stage 0
report names it as the natural follow-up). It was run as experiment 0d Part A (`REPORT_0D.md`): a jointly trained network of the same graph does about as well. What a rule change does *is* a separate
and practical question (hypothesis 2 above): after a change, how much data does each design need? The change-cost test measured that, but only for a
change that touches the piece the wired unit was told to retrain, so its advantage there partly holds by construction.

## What counts as success or failure of the idea

- **Supported (within this sandbox):** the wired pieces play near the expert, beat a same-size single block, adapt to a changed rule with far
  fewer examples, and the same holds as more pieces and levels are added.
- **Not supported:** a single block of the same size does as well, or the change costs the same. Either outcome is a real answer.
- **Never claimed here:** that this works on real tactics or the real simulator, that geometry beats matrix math, or anything about oscillators.
  Those are later steps.

## What is still ahead (in order of how much each would teach)

1. (Done, rechecked 2026-10-04: `REPORT_0D.md`.) Experiment 0d Part A (after a Codex review of its proposal): separate structure from composition with concurrent baselines under one tuning budget and a
   specified own-selection structured network; fixed effect-size margins with paired intervals. A MOVE-only or both-piece change and an extrapolated unit type are
   deferred until their requirements (PROPOSAL_0D.md Appendix A) are met.
1b. (Done as 0e, which became the replacement-and-connection study; its flat comparator did not qualify.) **Next (owner's idea, 2026-10-04): bottom-up structure by measured connections**: connect every pair of pieces from a pool with decoys (and each piece with itself), measure each against coherent alternatives, grow while performance clearly rises, stop when it does not, then treat the result as one piece and repeat one level up.
2. Learning from outcomes (evolution strategies or policy gradient on win rate) instead of imitating scripted teachers.
3. The squad level: a focus piece plus three units, the second level of composition (so far only pieces into a unit have been tested), against a
   structured end-to-end baseline.
4. Stage 0b: the mage's burst as a piece (needs a data design for a rare decision).
5. Stage 1: goal memory (commitment); Stage 2: enemy memory (limited vision); Stage 3: a map (walls and cover). Each added only with a situation that
   fails without it.
6. An outside benchmark for external validity (for example SMACv2 for tactics, CompoSuite or gSCAN for recombining pieces). Not set up or checked here.
7. The real Astelia simulator, after its own repairs (the GeoTactics plan, GT0).
8. The RRG-specific claim (separate, with its own source-aligned causal hypothesis; it would also need the causal background transformation and later organization in the transformed background, which the pieces here lack): the shapes and their links come from signature, rate and timing rules (compatible pieces connect; stable combinations
   become the next level). This is where the oscillator work returns.
