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
