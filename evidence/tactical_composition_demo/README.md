# Tactical composition demo (Stage 0)

Plain version of what this folder is. Not a milestone and not C6 evidence.

**The idea:** build an AI unit from small pieces, each with one job, instead of one big learned block. Here a unit is two pieces: **AIM**
(which enemy to hit) and **MOVE** (where to step). They are wired together. The question is whether the wired pieces play as well as one big
controller of the same size taught on the same examples, whether they cope with a unit type nobody trained on, and how quick they are to build.

**How it is judged:** a small game with three kinds of unit; a team of three of our units against scripted teams; win rate; 20 independent seeds;
the bars were written down before the run (`SPECIFICATION.md`). A "rush the nearest enemy" rule is the floor.

**Why this exists and where it is going:** see `MOTIVATION.md`. The change-cost test (Stage 0c) has its own `SPECIFICATION_CHANGE.md`, `change.py`, `test_change.py`, `SPEC_CHANGE.json` and `dev_doctrine*`.

**Files:** `PROPOSAL.md` (why and the bigger plan), `SPECIFICATION.md` (the exact design, bars, history of corrections), `tactics.py` (the game,
the scripted experts, the pieces), `demo.py` (the run), `test_*.py` (mechanics checks), `dev_calibration*.json` (how the game and piece sizes were
set, on separate randomness), `history_ability_attempt/` (the first design with the mage's burst, kept), `REPORT.md` (results, after the run).
