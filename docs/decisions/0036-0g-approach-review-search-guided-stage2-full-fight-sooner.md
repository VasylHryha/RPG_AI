# 0036: 0g approach review: search-guided stage 2, full fight sooner, RRG tested at the leader, lighter development process

**Date:** 2026-10-08 (evening). **Decided by:** the owner ("ok, overall seems solid, just document it for history so we can recheck"), on Claude's suggestions in reply to the owner's standing question "do you agree with my ideas/approach? anything to change, make better or drop?". **Recorded by:** Claude (claude-opus-5-5).
**Extends:** decisions 0033 (big levers, lighter tooling reviews), 0034 (two-axis evaluation) and 0035 (units act alone; tactical leader on top). The network design `evidence/tactical_composition_demo/NETWORK_POLICY_DESIGN_0G.md` is not edited here; its stage 2 is redirected by this record.

## State when decided

- **First trained networks** (`d82b505`): N1 ×3 seeds, N1r and N2 by imitation. Export parity passed.
- **First fights** (`b5cc3cf`), as corrected by the cross-family recheck `a919155`:
  - 10 of the 12 drill draws are saturated: the outcome is the same for every policy.
  - In the only contested cell, D2 with 10 guns, the networks trail the teacher badly: kills 11 (teacher), 6 (N1r), 2 (N1), 2 (N2), mostly because they hold fire.
  - The aim head collapsed to the centre: the label is the teacher's group volley spread, which no single unit can see.
  - The N2 phase effect is not shown. K stayed at its initial value. The fixed J=0.5 motion term confounds the ablations.
- **Scripted levers:** dodge (26 → 46/50 wins) and V2 (deaths −2.75 per fight) earned jobs. V1 volley sync (`b6fe0ad`) and E1 engagement (`7d301ad`) did not. The ten-fight series streak is about 1.2 for the scripted teacher, against the owner's reference of 6–8.

## Decision

**Keep:**
1. The AI is a trained network; scripts are only teachers, data and comparators.
2. Units are competent alone; the leader network adds group commands (0035).
3. Two axes (survival, damage); the decision numbers are deaths per fight, kills per own death and the series streak; paired fights, 100–200 for decisions (0033, 0034).

**Change:**
1. **Stage 2 is search-guided self-improvement (Expert Iteration), replacing ES on the series as the main route.**
   - **The ceiling:** imitation can at best reach the teacher, and the scripted teacher's streak is about 1.2.
   - **The method:**
     1. Short engine look-ahead searches, guided by the network's priors and values, find better actions than the script.
     2. The network is trained on those improved choices.
     3. The cycle repeats.
   - **Closest methods:** Expert Iteration (Anthony et al. 2017) and AlphaZero-style policy improvement, in a much simpler form.
   - **Precedent:** the owner's sandbox look-ahead commander averaged a 6.1–6.5 streak against non-dodging enemies, so search is the known strong teacher in this engine.
   - ES remains a possible comparator.
2. **Move to a full-army fight sooner.** After the units + leader rebuild shows a working result on **contested** drills, the next slice is a full-army fight against the regular enemy, rough but complete, because most losses (mainly from artillery) happen there. Saturated drills are not used for readings.
3. **The RRG claim is tested at the leader level.** The fair test is coordination: who covers which spot and when to fire together. It compares the RRG level-2 group-resonator leader with a plain set-attention leader on the same paired fights. Unit-level imitation of a stateless teacher cannot show an RRG advantage, and is not used as that evidence.
4. **A lighter process for the network development loop** (applies decision 0033 more strongly):
   - simple measured time estimates;
   - one quick recheck per build;
   - the full receipt, gate and independent-review ceremony only for results that will be claimed.
   - **Lesson behind it:** three refusals happened before the first real training run (a quadratic prefix, a work-unit proxy over-estimate, then admission), and they cost hours.
   - The owner recheck after every serious piece of work stays mandatory (AGENTS.md).

**Drop:**
1. Further scripted shape tuning beyond its use as teachers. V1 is parked and E1 is stopped; R1 is not pursued unless it is needed as a teacher.
2. DAgger round 2 on the old unit-only design. Round 1 runs as a diagnostic of on-policy correction of hold-fire.
3. Pooled kills-per-minute readings and "near teacher" claims from saturated drills. Report only cells where outcomes vary.

## How to recheck this decision later

| Question | Evidence that would change it | Responsible |
|---|---|---|
| Does units + leader fix the contested-cell gap? | units+leader kills and fire per chance in D2-10, vs teacher, over paired fights | Claude |
| Does the leader earn its place? | units+leader vs units alone, deaths and kills per own death | Claude |
| Does RRG beat plain at the leader? | RRG leader vs plain leader on the same paired fights | Claude, reviewer |
| Does search beat the scripted teacher? | search teacher vs script on the series streak, 100–200 paired fights | Claude |
| Was the lighter process too light? | any claimed result later found wrong because a removed check was missing | reviewer, owner |
