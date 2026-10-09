# 0038: 0g reward training beyond the teacher, for RRG and plain nets, with and without connection growth

**Date:** 2026-10-09 (~07:00). **Decided by:** the owner. The owner asked "can we train RRG now without teacher? and make it fight until it wins? and save most of its units? we also should allow it to grow new connections, the same for normal network - so we compare both of them", then chose "Yes, this order (Recommended)". **Recorded by:** Claude (claude-opus-5-5).
**Extends:** decision 0036 (stage 2 beyond the teacher). This record sets the order and the objective.

## Decision

1. **Stage B first.** The full-army unit networks first reach roughly teacher level in real fights, through diagnosis, fire calibration, 10-epoch training and full-fight DAgger.
   - **Why:** imitation then reward is the proven route (AlphaGo, AlphaStar, OpenAI Five).
   - **Why not from zero:** a random 50-vs-50 army almost never wins, so it gets no learning signal.
2. **Stage 2: reward training with no teacher in the loop.** Training starts from the stage B networks.
   - **Reward:** a large win bonus, plus own units saved, plus enemy kills. It rewards winning while losing as few units as possible.
   - **Method:** evolution strategies. They are CPU-parallel and do not need gradients through the RRG oscillators.
   - **Fair comparison:** RRG and plain networks get identical fight budgets and paired seeds.
3. **Stage 2 with growth.** The same training, plus structural growth of new connections and units, in the NEAT style (Stanley & Miikkulainen 2002), for both networks.
   - For RRG, growth adds resonators and links. This is the principle's self-recreation → new options → new geometry.
   - Growth versus no growth is compared at equal budget.
4. **Curriculum.** Fights scale 10v10 → 25v25 → 50v50; each stage starts from the previous one.
5. **Readouts:**
   - paired fights against the regular enemy and the C3 pool;
   - wins (the target is 40/40), own deaths per fight and kills per own death;
   - the ten-fight series streak, with survivors healed.
6. **Cost:** an ES generation (population 64 × 4 paired fights) is about 10–15 minutes at the measured speed. About 100 generations, roughly a day, per network and variant at 50v50; smaller fights are faster. Runs over one hour before 22:00 need the owner's approval (decision 0031).

## Not claimed

No result yet. The stage A networks lose every full-army fight: 0 wins against 10/10 for the script. Stage B must fix that first.

## Addendum (owner agreed to Claude's suggestions, 2026-10-09 ~07:10)

1. **The reward cannot be gamed by stalling.**
   - Units saved count only on a win.
   - A timeout scores badly.
   - A small time penalty rewards finishing fast (rule: win means kill efficiently).
2. **Opponents during training:** a random mix of the regular enemy and all C3 tactics. Later, a small league of the network's own past versions.
3. **Held-out evaluation:** unseen seeds and held-out tactics.
4. **A speed pass before stage 2:** batched C++ inference for all units, with the encoder at 5 Hz. A network fight measures about 20 s per worker, against about 4 s for the script.
5. **Growth after a no-growth baseline,** at equal fight budget, reporting each network's final size.
6. **The series streak enters the reward** once single fights are won reliably.
7. **Arms trimmed after stage B:** N2J0 is dropped (identical to N2). N1h is kept only if it clearly beats N1. The core arms are plain N1, memory N1r and RRG N2.
8. **Targeted outside research before the stage 2 design:**
   - ES vs PPO for RTS micro;
   - neuroevolution with growth;
   - fixes for compounding imitation error;
   - reward design;
   - a low-budget league;
   - training coupled-oscillator networks.

## Addendum 2: clarifications adopted from the owner's outside review (2026-10-09 ~07:45)

Source: `~/Downloads/RRG_DECISION_0038_DIRECTION_REVIEW_2026-10-09.md`, which reviewed main `d35cb61`. Claude evaluated it and adopted the points below; the reply is `~/Downloads/RRG_0038_DIRECTION_REVIEW_FEEDBACK_CLAUDE_2026-10-09.md`. The decision's direction is unchanged.

1. **Precedence.** The main stage 2 route is ES under this decision. Expert Iteration (0036) remains a separately scoped option, not a compulsory extra stage. The leader stays parked. 0037's privileged-teacher permission does not carry into stage B or stage 2.
2. **Stage B readiness is behavioural.** It is measured in closed-loop paired fights (wins, own deaths, kills, timeouts, across the C3 tactics), against both the previous checkpoint and O/T. Epoch count and imitation accuracy are not the test.
   - **First diagnosis:** a bounded first-divergence diagnosis that splits into target choice, cast permit/hold, intent reaching the engine, movement, compounding drift, and history integrity.
   - **Head substitution:** labelled diagnostic hybrids substitute one oracle head (fire, or movement) into the learned policy. They are never deployable candidates.
   - **No scripted repair:** the deployed learner is never fixed by calling the teacher's fire rule.
3. **Cadence.** The entity encoder is already refreshed at 5 Hz; actions and recurrent updates run at the physical tick. A speed pass must keep the action cadence. Any cadence change, such as frame-skip, is a separately declared policy experiment.
4. **The shared safety layer is labelled.** The participation, react and body layer is identical across arms. Dodges are not evidence that a network learned dodging.
5. **The reward contract is frozen before the first ES rollout.**
   - **Terminal rules:** win, mutual elimination, timeout, controller failure, terminal tick and projectile tail are defined exactly as the runner implements them.
   - **Components:** bounded and normalized across 10, 25 and 50 units. Survivors count only on a win.
   - **Synthetic outcome checks** are required, including: a timeout with many survivors never beats a win; a time term never makes an early suicide in a loss profitable; and each kill is counted once.
   - **Deployment criterion:** actual win/loss/streak measurements, not scalar fitness. Potential-based shaping is not used for whole-episode ES ranking.
6. **Evaluation honesty.**
   - **Unseen tactics:** "fresh seeds of known C3 tactics" (the official yardstick) is reported separately from "genuinely unseen tactics". A tactic counts as unseen only if it was excluded from the whole training history, including behaviour cloning and DAgger. Current checkpoints have seen all C3 tactics.
   - **Replication:** evaluation fights of one checkpoint are not training replications. Promising results are replicated from fresh training seeds.
7. **Budgets.** Executed rollouts = P × S × O × G, with antithetic pairs counted as candidates; selection, validation and growth candidates are counted separately. Reports state which is held equal across arms (data, compute or effective capacity) and report the others. ES states exactly which parameters it perturbs, symmetrically across arms.
8. **Curriculum.** Smaller fights start from the stage B checkpoint, never from random weights, with a frozen 50v50 regression check. Each size declares its role mix, arena, density and neighbour radius.
9. **Growth.** Growth means added internal computation (state and links within the per-unit interface), never added soldiers. It is training-time structural search, not a claim of runtime plasticity or recursive self-recreation.
   - **Specify before any growth run:** node semantics; the optimizer across topologies (inner weight ES with an outer structural selection, or a masked superset); and pre/post identity tests for mutations claimed to be neutral. In degree-normalized coupling a zero-weight link is not automatically neutral.
   - **Comparison:** within each architecture, growth vs no growth from the matched checkpoint; a fixed-larger-capacity control comes later.
10. **Correction to the original rationale.** OpenAI Five trained by self-play from random parameters; it was not imitation-first, and Claude's example was wrong. AlphaStar is the correct imitation-then-reinforcement precedent. Warm-starting is chosen for efficiency, not because learning from zero is impossible.
11. **What counts as an RRG result (four separate readings):**
    1. The trained AI works.
    2. It learns beyond the teacher.
    3. N2 beats the trained recurrent control N1r, with mechanism interventions.
    4. Growth beats matched no-growth and is not explained by capacity alone.

    External topology mutation is not reported as evidence of "self-recreation".
