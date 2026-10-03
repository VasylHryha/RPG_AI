# Geometric composition demo — NOT a milestone, NOT C6 evidence

Status: SPECIFICATION (before any run). Requested by the owner on 2026-10-03: "lets do it and document", after the
owner restated the goal: show that AI can be built from **geometry instead of matrix computation**, as small pieces that
each do one thing, combine into bigger pieces that act as one, and so on.

This folder is an exploratory demo under the AGENTS.md pilot rule: its own entropy, scratch code outside `geomind/`,
everything committed here. It changes no milestone status, accepted file, threshold or historical receipt. It does not
use the C4 oscillator law; it tests the **composition** claim only (see "What this does and does not show").

## The idea in plain terms

- A **piece** is a small map: a few points placed in the space of its inputs, plus a smooth way to read an answer off
  them. Where the points sit *is* what the piece knows. Teaching a piece means moving its points and fitting the readout.
- Four small pieces are taught separately, each one job: **add**, **multiply**, **divide**, **square root**.
- **Wiring** pieces together makes a bigger piece. Example: `distance(a, b) = sqrt(a*a + b*b)` is multiply, multiply,
  add, square root. No new training: the pieces are just connected.
- **Acting as one:** the wired distance can be *promoted*: sampled and turned into a single new small map with the same
  inputs and outputs. From outside it is one piece, and it can be wired again.
- **Next level:** the length of a diagonal of a four-sided box, `sqrt(a*a + b*b + c*c + d*d)`, is distance of
  (distance of a, b) and (distance of c, d). One taught piece is reused three times.
- **The comparison:** the mixed task `sqrt(a*b + c/d)` uses all four taught pieces once. One big map taught directly on that
  task, with the same number of points and the same amount of data, is the comparison, plus a straight line (the floor) and a
  small ordinary neural network (the matrix-math reference).

The question: does a few small, separately taught geometric pieces, combined, beat one big map of the same size, and
does promotion keep the combined piece usable as a single unit?

## What this does and does not show

It shows (or fails to show) that composition of small taught geometric pieces works and that a combined piece can act as
one. It does **not** show that oscillators or the C4 law can do this, that geometry beats matrix math in general, or
anything about RRG's physics. The pieces here are prototype maps (radial-basis readout), which are mathematically
ordinary; "geometry" means the knowledge sits in point positions. The composite also receives extra supervision (each
piece is taught its own job), which is the point of the idea but makes the comparison one-sided; the specification
reports data-to-match to keep that visible.

Files: `SPECIFICATION.md` (design, predictions, rules, self-audit), `SPEC.json` (entropy and constants), `demo.py`, `test_demo.py`,
`dev_piece_sizes.py` and `dev_piece_sizes.json` (the one-time development calibration of the pieces' sizes).
