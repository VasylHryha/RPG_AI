# Review request (Codex): design 0g, a resonator-based AI judged against Astelia's scripted AI

Repository `/Users/new/RiderProjects/ai_RPG_test`. Read `AGENTS.md`. Time cap about 20 minutes. This is a design review; no code for the controller exists yet. The C++ port
(`evidence/tactical_composition_demo/astelia_cpp/PORT_REQUEST_CODEX.md`) is separate work.

Read:
- `evidence/tactical_composition_demo/DESIGN_0G.md`: the plug, the controller, the score, the arms, the owner's decisions;
- `evidence/tactical_composition_demo/PLAN_RESONATOR_AI.md`: the sessions, the acceptance criteria, section 5b;
- `geomind/c4_model.py` `rhs` (`:82-102`): the C4 element law the controller reuses;
- `docs/decisions/0028-owner-directed-exploratory-composable-shapes.md`: the exploratory line and the owner's goal.

The owner's goal: an AI on a different foundation (the C4/C5 law, things that connect by matching rhythm and form groups that act as one), not a repeat of current AI. It should beat
the game's scripted AI (novice, then regular, veteran, elite) on fresh fights. The score is units left at the end, then the damage difference.

Answer, with file and line references:
1. **Fairness:** does the plug give our controller anything the scripted opponents do not have, or the reverse (the observation table, abilities left to the game's reflex, full sight)? Can
   any arm read hidden state?
2. **Does the test isolate the foundation?** Does "plain morale" (the phase replaced by a number) really separate "the beat matters" from "the smoothing and neighbour averaging matter"? Does
   push-pull fairly represent known swarm control (physicomimetics)? Are equal knob counts and equal tuning budgets enough to keep "tuning wins" out of the comparison?
3. **The controller math:**
   - Is the damage drive (toward 0 for damage dealt, toward π for damage taken) well defined and stable?
   - Can the phase law lock all units into one phase and make the group phase meaningless?
   - Is the C4 scaling (L, τ, one RK4 step per tick) sound?
   - Any degenerate case: no enemies in reach, all enemies dead, a unit alone?
4. **Attainability:** are P1 (beats novice and regular, 60% won), P2 (beats plain morale) and P3 (beats push-pull) testable at alpha 0.01 with 114 paired fights, given that the
   margin's spread per fight is unknown until development?
5. **Simplest improvements or cuts:** anything to drop or change before code is written.

Write `docs/reviews/tactical_0g_design_review_codex.md`. The first line is APPROVE, APPROVE_WITH_NOTES or CHANGES_REQUIRED, followed by `Reviewer family: Codex` and numbered findings
(severity high / medium / low, each with a concrete fix).
