# Experiment 0f — bottom-up structure by measured connections (DRAFT design record; development approved, recorded run not yet)

Exploratory line under decision 0028 (items 11 and 12). The owner's idea: "start from level 1 — connect each one with each other or even with itself and try to measure — only two
things connected as a pair, then add something 3rd, 4th; when we get a good number and cannot go further or lose performance, connect bigger things together." This record turns that
into a procedure that can fail, using the lessons of the 0e recheck as rules.

## 1. The question

Can a fixed, simple procedure build a working unit from a pool of pieces **without being told the wiring**, by measuring connections by performance alone, and does the same
procedure then build the next level from units? This is the first test in this line in which the author does not choose the structure. It still chooses the pieces, their declared
ports and the procedure: discovery here means selection among declared, type-compatible connections, not unconstrained emergence.

## 2. Level 1: a pool of pieces with declared ports (task V3, `tactics_e2.py`)

| Piece | Consumes | Produces | Role |
|---|---|---|---|
| AIM (learned scorer, as 0e's L) | observation | a living target | useful |
| HP (learned scorer trained on a different job: the enemy's missing health) | observation | a living target | plausible alternative |
| NEAR (scripted) | observation | the nearest living target | default |
| RAND (scripted) | observation, its own randomness | a random living target | decoy |
| MOVE (learned, as 0e's L) | a target's position message, own preferred range | a step | useful |
| APPROACH (scripted: walk at the message until within 90% of own range) | a position message, own range | a step | default |
| DRIFT (scripted: a fixed step) | nothing | a step | decoy |
| SELF (a self-connection) | a target producer's own previous output | keep the previous target while it lives | memory (the owner's "with itself") |

An **assembly** fills two slots: the attack target (any target producer, optionally with SELF), and the step (any step producer, whose position message comes from any target producer).
The **default** assembly (NEAR attack, APPROACH step fed by NEAR) is exactly the rush rule, and the procedure starts from it.

## 3. The procedure (fixed before any measurement)

1. **Pairs.** Measure every coherent pair (target producer feeding both the attack and the step producer): 4 x 3 = 12 assemblies, plus SELF variants. This is the owner's "connect each with each other" table.
2. **Grow (greedy).** From the default, try every single change (swap one producer, rewire one message, add or remove SELF); keep the best change if it beats the current assembly by more than the margin on the selection games; repeat; stop when no change clears the margin.
3. **Confirm.** Evaluate the final assembly once on fresh games and seeds never used in selection.
4. **Level 2 (conditional, section 5).** Treat the confirmed unit as one piece; repeat steps 1 to 3 with squad-level pieces.

**Controls:** exhaustive search over every type-compatible assembly (the ceiling the greedy procedure should reach); random wiring (the floor); the hand-wired 0e unit (L); the scripted teacher.
**Rules from the 0e recheck:** every comparison is against a coherent alternative; the margin is set from measured noise (development: the paired spread of one cell); a claim is registered only if
an ideal procedure could pass it (checked on development data); selection and confirmation use different seeds and games; fidelity to the teacher is not used as a score (win score is).

## 4. Falsifiable predictions (to be registered after development)

- **P1 (finds the useful structure):** the greedy procedure ends at AIM attacking and feeding MOVE, without RAND or DRIFT anywhere, in at least a registered share of seeds.
- **P2 (no worse than design):** the confirmed assembly plays no worse than the hand-wired unit by more than a margin, and well above random wiring.
- **P3 (greedy is enough):** greedy reaches the exhaustive optimum (or within the margin) on held-out games.
- **P4 (memory only if it pays):** SELF is added only if it improves held-out play; otherwise it is left out (either outcome is a result).

Each can fail: the procedure may wire in a decoy, stop early at a coherent but weaker unit (for example NEAR with MOVE), overfit selection noise, or fail to confirm.

## 5. Level 2 (conditional)

Pool: three copies of the confirmed unit; FOCUS (a squad piece that publishes one shared target, for example the most dangerous enemy seen by any unit) that can be connected to any unit's attack
port; a decoy squad piece. Same procedure: connect FOCUS to 0, 1, 2 or 3 units, grow, stop, confirm. **Gate:** in development a scripted focus-fire squad must beat three independent teacher units by a
registered margin; if it does not, level 2 is not run on this task and the report says so (coordination does not matter here).

## 6. Not in scope

Learning pieces from outcomes; another task; RRG, geometry, oscillators. The pieces and ports are declared by the author; the search is over declared connections.

## 7. Order

Development on its own entropy (pieces, noise and margin, a small greedy pilot, attainability, level-2 gate), committed with raw results → specification and registration → Codex review →
owner approval naming the specification → one recorded run → report.
