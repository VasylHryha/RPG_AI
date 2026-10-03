# Why we are doing this, and what each step is for

Plain-language record, written 2026-10-03 at the owner's request ("document why we did it and what the motivation"). It is a map of the
reasoning, not a result. The results are in the `REPORT*.md` files and each step's `SPECIFICATION*.md`.

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
5. **It matches the theory.** In the owner's RRG idea, a stable shape and its vibration (frequency, rhythm, signature) decide what it connects
   to, and stable combinations become the next level (the same rule repeated). These demos test the *engineering* half of that idea. They
   do not test the physics or any "vibration" claim.

## How we got here (the trail, honestly)

| Step | What it was for | What it found |
|---|---|---|
| Physics route (C4 to C6) | Do oscillating units form stable groups, and groups of groups, by one rule? | Two levels worked; the third stalled. The route was slow and complicated, and I (Claude) misread the idea along the way |
| Two-body pilot | Why does level three fail? Do groups fuse? | They do not fuse; level-3 failures were near-misses on one recovery test; the model has no way for a unit's shape to set its frequency |
| Research and rethink (theory, outside projects, process guides) | Find a simpler, more direct test of the owner's real goal | Pieces that fit and compose are the core; the physics substrate is a later question |
| Arithmetic demo | Do small taught pieces (add, multiply, divide, square root) compose and promote? | Wiring works at one level, but one big map matched it, errors build up over a chain, and an ordinary network was far more accurate: arithmetic is the wrong test |
| Tactics, Stage 0 (AIM + MOVE) | The same question on a task where positions and ranges are natural | Two small separately taught pieces play almost as well as the scripted expert; one big controller of the same size is much weaker and needs 16 times the data to approach; the advantage comes from the wired structure |
| Tactics, change-cost test (Stage 0c) | The "quick to change" hypothesis | First revision inconclusive (fine-tuning stalled; my explanation was wrong, corrected). Second revision: SUPPORTED within this sandbox. Retraining only the affected piece needed about 10 times fewer new rows than retraining a single block of the same size (100 against 1,000 rows for a common quality level; the block never reached 0.90 within 12,000), and the reused piece kept its step correct (2 degrees against 11 to 29). Marginal on how big the change was; part of the result restates the design (`REPORT_CHANGE2.md`) |

## Why the change-cost test (and not the "structure versus teaching" test)

The natural next question after Stage 0 was whether the advantage comes from the wired *structure* (one scorer shared by all enemies, a step
that depends on the chosen target) or from teaching the pieces *separately*. Looking closely, that question cannot be separated by training
mode: the two pieces have separate parameters and each has its own practice answers, so training them together gives exactly the same
computation as training them separately. What *can* differ is what happens when something changes. That is hypothesis 2 above, and it is
the practical reason to want pieces at all. So the next test changes a rule and measures how much data each design needs to follow it.

## What counts as success or failure of the idea

- **Supported (within this sandbox):** the wired pieces play near the expert, beat a same-size single block, adapt to a changed rule with far
  fewer examples, and the same holds as more pieces and levels are added.
- **Not supported:** a single block of the same size does as well, or the change costs the same. Either outcome is a real answer.
- **Never claimed here:** that this works on real tactics or the real simulator, that geometry beats matrix math, or anything about oscillators.
  Those are later steps.

## What is still ahead (in order of how much each would teach)

1. A change that touches only MOVE, or both pieces (to check the change-cost result is not specific to AIM).
2. The squad level: a focus piece plus three units, the second level of composition (so far only pieces into a unit have been tested). Recommended next.
3. Stage 0b: the mage's burst as a piece (needs a data design for a rare decision).
4. Stage 1: goal memory (commitment); Stage 2: enemy memory (limited vision); Stage 3: a map (walls and cover). Each added only with a situation that
   fails without it.
6. The real Astelia simulator, after its own repairs (the GeoTactics plan, GT0).
7. The RRG-specific claim: the shapes and their links come from signature, rate and timing rules (compatible pieces connect; stable combinations
   become the next level). This is where the oscillator work returns.
