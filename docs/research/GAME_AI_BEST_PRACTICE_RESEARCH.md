# Game-AI best practice for Astelia: what landmark systems did, what transfers to one laptop, and a ranked plan

**Status:** research note for plan step B8 (`docs/PLAN_CURRENT.md`). It informs `evidence/tactical_composition_demo/SHAPE_LAB_SPEC.md` §§9–12:
- Amendment 2: teacher arms and shadow actions;
- Amendment 3: primitives, and losses avoided, not budgeted;
- Amendment 4: coordinated artillery volleys;
- Amendment 5: the interface prerequisite.

**Revision history:**
- **Revision 1:** commit `db404c2`.
- **Revision 2:** this file. It fixes the cross-family recheck `docs/reviews/game_ai_research_recheck_codex.md` (CHANGES_REQUIRED, F1–F8, N1); see §12, the self-audit.

**Ground rules:**
- No project code, fight, benchmark or pilot was run for this note.
- Engine facts come from reading delivered sources, the spec and the stored killers summary.
- Every external claim carries a link. Statements marked **[inference]** are this note's reasoning, not a source's finding.
- Nothing here authorizes a run; any pilot proposed below needs owner authorization under decision 0031.

**Date:** 2026-10-08. **Drafter family:** Claude.

---

## 0. Our problem in the literature's terms

| Our term | Closest literature term | Source |
|---|---|---|
| Shape (per-role behaviour) and its primitives (move, attack, aim, react, rotate, volley; spec §10) | **Script** in a **script portfolio** | Churchill & Buro's line ([Lelis, IJCAI 2017](https://www.ijcai.org/proceedings/2017/522)) |
| **Battery oscillator** (spec §11, V1): each gun's firing phase is pulled towards its neighbours' and released at a shared firing point | Pulse-coupled oscillators ([Mirollo & Strogatz 1990](https://www.iasi.cnr.it/~vbonifaci/semcn/Mirollo1990.pdf)); the [Kuramoto model](https://en.wikipedia.org/wiki/Kuramoto_model); military [time on target](https://en.wikipedia.org/wiki/Time_on_target) | Spec §11 names these as the closest methods |
| The **old commit/escape gate** (v7) | A hand-written meta-controller | **Superseded** (spec §11): no gain (v7 32/40 against always-commit 31/40), and it violates the owner's never-leave rule |
| ~11 knobs tuned by CMA-ES | Parameterised micro tuned by evolution | ECSLBot ([Liu, Louis & Ballinger 2014](https://www.cse.unr.edu/~simingl/papers/publish/CIG2014IMPFMicro.pdf)) |
| Engine clone plus forward play (the elite's 2-s volley rollouts) | Forward model for playout-based search, **with the caveats in §6** | SparCraft, PGS, SSS |
| 19 enemy doctrines at regular skill (the owner's series) | Fixed scripted **opponent pool** | AlphaStar's PFSP is a *training* distribution, not our yardstick (§8) |
| Teacher arms and shadow actions (spec §9) | Expert labelling; **behaviour cloning** when the teacher drives, **DAgger** when our policy drives *and* the labels are aggregated and refitted | [Ross, Gordon & Bagnell 2011](https://arxiv.org/abs/1011.0686) |

**The closest known method to what we already have is ECSLBot** ([Liu, Louis & Ballinger, CIG 2014](https://www.cse.unr.edu/~simingl/papers/publish/CIG2014IMPFMicro.pdf)).
- It encodes micro (influence maps, potential fields, kiting, target selection, fleeing) in fourteen parameters, tuned by a GA in "about 21 hours".
- Its main fitness (Eq. 3) is units remaining on each side plus a time term. A second scoring (Eq. 4) is used for a kiting scenario.
- The main comparisons control five Vultures. Similar Dragoon results are mentioned. Mixed own-army composition is named as "still an open research question".
- **How we differ:** per-role shapes, a battery oscillator for gun synchrony, CMA-ES, and three mixed roles with lobbed splash.

**What the yardstick measures** (spec §5):
- **The rules:**
  - 10 fights;
  - fresh full enemy 50 each fight;
  - tactic drawn uniformly with replacement from the 19-entry POOL at regular skill;
  - abilities off;
  - survivors healed to full;
  - the dead stay dead.
- **The run ends at the first fight not won by elimination,** including losses, draws and timeouts.
- **The streak is primary.** Losses matter because they shrink later armies, but cumulative loss alone does not decide the streak: a timeout with few deaths also ends it.
- **The stored v7 data** (`KILLERS_V7_REGULAR.txt`, 40 fights against regular): own deaths average **41.8 per fight over all 40 fights**. The spec's 40.7 is the separate mean over won fights only.

**Literature that scores only damage and kills therefore transfers partly.**
- SMAC's default reward is positive-only: damage dealt + 10 per kill + 200 per win, with reward scaling on ([environment source](https://raw.githubusercontent.com/oxwhirl/smac/master/smac/env/starcraft2/starcraft2.py)).
- It has no direct penalty for allied damage or deaths, although own casualties still affect outcomes indirectly.

---

## 1. Landmark game AIs: what they did, and what might transfer at 10^5–10^6 fights

**Throughput** [inference from the brief]: about 1,350 fights/min on 10 workers, i.e. about 81,000 fights/hour or about 0.44 core-s per whole 50v50 fight. **Branch cost is not measured** (§7).

| System | What it did | Transfer candidate for us | What we defer, and why |
|---|---|---|---|
| **AlphaGo** ([Nature 2016](https://research.google/pubs/mastering-the-game-of-go-with-deep-neural-networks-and-tree-search/)) | Supervised policy on expert moves (57% prediction per a [secondary summary](https://blog.acolyer.org/2016/09/20/mastering-the-game-of-go-with-deep-neural-networks-and-tree-search/)); self-play RL; value net; MCTS | A teacher-first bootstrap, then improvement by search | Deep nets over raw state |
| **AlphaZero / KataGo** ([KataGo](https://arxiv.org/abs/1902.10565)) | Self-play + MCTS **from random play, no teacher**; the network learns search visit counts and outcomes. KataGo cut compute about 50× against ELF OpenGo, still about 1.4 GPU-years. | Distilling a search into a cheaper policy ([ExIt](https://arxiv.org/abs/1705.08439)); planning with few simulations ([Gumbel, ICLR 2022](https://iclr.cc/virtual/2022/poster/6418)) | AlphaZero self-play is about 21 M games ([EfficientZero paper](https://arxiv.org/abs/2111.00210)), far beyond our budget |
| **MuZero** ([arXiv 1911.08265](https://arxiv.org/pdf/1911.08265)) | Learns a dynamics model and plans in it | Nothing now | **Deferred, not dismissed.** We have an engine clone with known semantics (§6). A learned model could trade accuracy for speed, but that is not our current bottleneck. Learned models can misjudge unseen policies ([arXiv 2306.00840](https://arxiv.org/html/2306.00840v3)). |
| **AlphaStar** ([DeepMind](https://deepmind.google/discover/blog/alphastar-grandmaster-level-in-starcraft-ii-using-multi-agent-reinforcement-learning/)) | Imitation from human replays (beat 84% of players); a league with main agents, main exploiters and league exploiters; **PFSP**: f_hard(x) = (1−x)^p ([arXiv 2408.01072](https://arxiv.org/pdf/2408.01072)); distillation towards human play | Teacher bootstrap; PFSP-style *training* sampling (with a uniform floor, §8); script-level exploiter search as a separate *stress* test | The neural policy and the learning league. Each agent took 44 days on 32 TPUv3 ([secondary](https://gamesbeat.com/deepminds-alphastar-final-beats-99-8-of-human-starcraft-2-players/)). |
| **OpenAI Five** ([arXiv 1912.06680](https://arxiv.org/abs/1912.06680)) | PPO at scale, about 2 M frames per 2 s for 10 months; about 80/20 current/past-self opponents ([survey](https://arxiv.org/pdf/2111.07631)); "team spirit"; "surgery" | A past-self (hall-of-fame) regression pool; a per-unit against team term in fitness design | PPO scale |
| **microRTS BC experiment** ([Goodfriend 2024 §4.3](https://arxiv.org/html/2402.08112v1)) | Post-competition experiment, not the winning agent's recipe. RAI-BC copied the scripted Mayari: 71% overall, 44% against Mayari. PPO fine-tuning: 88% overall, 84% against Mayari, but it **regressed** on some map/opponent pairs: TwoBasesBarracks16x16 against POLightRush 100→0; BloodBath against Mayari 40→5. | Copying a scripted teacher can be a cheap **initial baseline**; per-cell paired checks are needed | **Not evidence of a ceiling.** A copy can fall short (features, approximation, distribution shift) or exceed its teacher in some matchups. Aggregate gains can hide cell regressions. |
| **Programmatic synthesis** ([AAAI 2021](https://ojs.aaai.org/index.php/AAAI/article/view/16114); [2L, IJCAI 2023](https://arxiv.org/abs/2307.04893)) | Local search over DSL programs with chosen reference opponents; beat the two latest microRTS winners in a simulated tournament | Closest in *spirit* to our principle: small readable programs found by search | |

**What we propose to copy** [inference]. The landmarks use different recipes: AlphaZero has no teacher, and AlphaStar's league has no tree search. The workflow we propose combines pieces of them:
1. copy a teacher's primitive;
2. improve it by measured comparison, optimisation or search;
3. distil anything expensive into a named shape.

This is **our proposal**, not a core shared by every landmark.

---

## 2. StarCraft micro-combat research

### 2.1 Simulators, scripts and the LTD2 heuristic
- **SparCraft** ([GitHub, MIT](https://github.com/davechurchill/SparCraft)) is a StarCraft combat simulator without collisions, fog or acceleration ([Lelis 2017](https://www.ijcai.org/proceedings/2017/522)).
- **Scripts** ([Churchill, Lin & Synnaeve 2017](https://ojs.aaai.org/index.php/AIIDE/article/view/12962)):
  - c AttackClosest;
  - w AttackWeakest;
  - k Kiter: moves away while reloading;
  - h Hold;
  - n NoOverkill.
- **NOKAV:** no-overkill with attack value dpf/hp.
- **LTD2** ([Churchill, Saffidine & Buro 2012](https://ojs.aaai.org/index.php/AIIDE/article/view/12527)) sums √hp × dpf over living units. It is a **candidate heuristic** for us, not our series objective, because current HP does not carry over when survivors heal (§5).

### 2.2 Search over scripts

| Method | Mechanism | Reported effect (scoped) |
|---|---|---|
| ABCD ([2012](https://ojs.aaai.org/index.php/AIIDE/article/view/12527)) | Alpha-beta with durations; script move ordering and playouts | Beats scripts up to 8v8 |
| UCTCD, PGS ([CIG 2013](https://experts.mcmaster.ca/scholarly-works/1941877)) | PGS hill-climbs unit→script assignments, scored by playouts | PGS beats alpha-beta and UCT up to 50v50 at 40 ms (abstract-level record; the PDF returned 404) |
| POE ([AIIDE 2016](https://ojs.aaai.org/index.php/AIIDE/article/view/12862)) | Evolves script assignments | In Lelis's Table 1, POE beats PGS **0.56–1.00**; the low end is the six-unit mixed case |
| PGS+ ([Lelis 2017](https://www.ijcai.org/proceedings/2017/0522.pdf)) | Same search; the evaluation plays the candidate for the first action only, then NOKAV | Beats PGS 0.72–1.00. **The evaluation design alone changed the outcomes.** |
| SSS (fixed type system) | Units of a type share a script; search over types | Strong with mid-size armies. **Fails at the largest mixed case:** Zea14/Dra14/Ling14/Mar14 (56 per side), SSS against POE **0.46** and against PGS+ **0.16**. |
| SSS+ (adaptive granularity) | Coarsens or refines the type system so a full pass fits the time budget | Same 56-unit case: SSS+ against POE **0.96**, against PGS+ **0.95**, against SSS 0.93 |
| GAB / SAB ([AAAI 2018](https://arxiv.org/abs/1711.08101)) | A few highest-attack-value units (AV+) get full actions under alpha-beta; the rest are script-restricted | GAB against PGS 0.82 (8 Zealots + 8 Dragoons) and 0.81 (32 Zealots); SAB against SSS 0.90 (50 Zealots). N≈4 was best **in that experiment** |
| Puppet Search ([2015](https://ojs.aaai.org/index.php/AIIDE/article/view/12779)) | Scripts expose choice points to search | Matches or beats its scripts against 2014 bots |
| NaiveMCTS ([2013](https://ojs.aaai.org/index.php/AIIDE/article/view/12681)) | Combinatorial-bandit MCTS | Better than other MCTS as branching grows |

**Lessons, scoped:**
- (a) The **evaluation and continuation design** can matter as much as the search algorithm (PGS→PGS+).
- (b) **Exhausting the time budget breaks fixed granularity** at scale. Adaptive granularity (SSS+) is the design lesson, not "coarse role types always win".
- (c) None of this proves that a search beats its scripts in our engine; that must be measured.

**PGS in the real StarCraft engine** ([Churchill, Lin & Synnaeve 2017, Table 1](https://ojs.aaai.org/index.php/AIIDE/article/view/12962)):
- In simulation, against AttackClosest, PGS won all battles in the four test scenarios.
- In the real engine it scored 0.72 (d2z3), 0.88 (m5v5), **0.22 (m15v16)** and 0.94 (w15v17, flying units, no collisions).
- The authors attribute the m15v16 loss to SparCraft not modelling collisions, and conclude that PGS "relies heavily on the accuracy of the underlying model".
- Raising the search time from 10 ms to 40 ms did not significantly help.

### 2.3 Learned multi-agent RL (SMAC and others)
- **QMIX test win % against the built-in AI** at "level 7, very difficult" ([SMAC](https://ar5iv.labs.arxiv.org/html/1902.04043)): MMM2 69, 27m_vs_30m 49, corridor 1, 6h_vs_8z 3.
- **MAPPO** matches QMIX on most maps with up to 10 M steps ([Yu et al.](https://arxiv.org/abs/2103.01955)).
- **Emergent behaviours:**
  - kiting in 3s_vs_5z;
  - BiCNet's "hit and run", "cover attack" and "focus fire without overkill" ([Peng et al.](https://arxiv.org/abs/1703.10069));
  - a SMAClite baiter that backs out at low HP ([SMAClite](https://arxiv.org/abs/2305.05566)).
- **Open-loop caveat:** many SMAC scenarios can be won by open-loop, timestep-only policies ([SMACv2](https://arxiv.org/abs/2212.07489)).
- **The splash mini-game** ([SC2LE Table 1](https://ar5iv.labs.arxiv.org/html/1708.04782)): DefeatZerglingsAndBanelings scores (scores, not win rates) were best agent mean **96** against human means **729 / 727**, after 600 M training steps.
  - **Scope:** this is one historical benchmark. It does not isolate splash avoidance as the cause, or compare modern methods.
  - **[inference]** Our preference for copying react first rests on our own data, not on this benchmark: we have zero reaction, and a teacher rule exists in the engine.

### 2.4 Unit preservation in the literature
- **Explicitly loss-aware objectives:**
  - LTD2 rewards many surviving units;
  - ECSLBot's Eq. 3 counts units remaining;
  - multi-objective micro keeps a Pareto front of damage done against damage received ([Liu et al. 2018](https://arxiv.org/abs/1803.10316)).
- **Damaged units cycling back:** Churchill 2017 observed in *simulation* that kiting cycled low-HP units "to the back lines, taking them out of range of the enemy… causing units to stay alive much longer". That is **out of enemy range**, which does not show they stayed in their own useful range.
  - **[inference]** It is a rotation *candidate*. It must pass the owner's participation rule (§4.3).
- **No paper found reports a series-with-carried-losses measure.**

---

## 3. Learning from a teacher per role, and what our interface must carry first

### 3.1 Methods

| Technique | Mechanism | Evidence | Fit for us |
|---|---|---|---|
| **BC** | Fit to the teacher's (state, action) pairs on the teacher's trajectories | RAI-BC (§1); AlphaStar SL | Spec §9 "teacher in control, ours shadowed" supplies BC data |
| **DAgger** ([2011](https://arxiv.org/abs/1011.0686)) | Run our policy; the teacher labels visited states; **aggregate and refit**; iterate | Fixes BC's compounding error. A 2026 Gin Rummy study found it did not help there (causal confusion; [arXiv 2607.06854](https://arxiv.org/html/2607.06854v1)). | Spec §9's reverse arm is DAgger-style *collection*; DAgger also needs aggregation and refitting |
| **AggreVaTe** ([2014](https://arxiv.org/abs/1406.5979)) | Imitation weighted by the teacher's cost-to-go | Regret guarantee under its assumptions | **[inference]** At disagreement states, clone rollouts give an **estimated, continuation-dependent disagreement cost**: neither exact cost-to-go nor an AggreVaTe guarantee (§6) |
| **Comparison training / MMTO** ([Tesauro 1988](https://papers.neurips.cc/paper/1988/hash/a8baa56554f96369ab93e4f3bb068c22-Abstract.html); [Hoki & Kaneko 2014](https://jair.org/index.php/jair/article/view/10871)) | Fit a scoring function so the teacher's choice outranks alternatives | MMTO tuned more than 40 M shogi weights from expert moves | Fits shapes whose decision is a choice among candidates: gun target score V, post, escort point |
| **Privileged teacher → student** ([Learning by Cheating](https://arxiv.org/abs/1912.12294)) | A teacher sees privileged state; the student does not | CARLA results | Basis for separating **oracle** and **deployable** teacher arms (§6) |
| **Search → policy** ([ExIt](https://arxiv.org/abs/1705.08439); [Barriga et al. 2017](https://arxiv.org/abs/1709.03480)) | A network learns from Puppet Search labels which script to run | Beat either component alone in microRTS | Later: a selector over *named volley patterns or movement policies* (§9, item 5). It must not replace the battery oscillator's local coupling. |
| **Per-unit counterfactuals** ([difference rewards](https://arxiv.org/pdf/2012.11258); [COMA](https://microsoft.com/en-us/research/wp-content/uploads/2017/03/Whiteson.pdf)) | D_i = G(z) − G(z with i's action replaced by a default) | The counterfactual "requires … a resettable simulator" | Clone replays give **sampled** counterfactuals under a stated continuation; not unbiased in expectation without coupled random streams (§6) |

### 3.2 Interface prerequisites (spec Amendment 5, adopted here)

These are integration prerequisites, not "a few extra fitted weights".

**Today's gap:**
- The delivered `controller.h` Observation has time, arena size and unit records only: no incoming shells, shots or slow fields, and no enemy cast preparation.
- `UnitDecision` has movement, target and failure fields only: no aim point, no hold/release, no volley membership.
- The scripted side's `dodge.cpp` reads shell and cast state.
- So **target/goal agreement alone cannot copy react, aim or volleys.**

**Required, in new files only, with pinned interfaces unchanged:**
1. **An observation adapter** with immutable, legally observable projectile and cast data:
   - in-flight shells: position, predicted landing point and time, radius;
   - aimed shots and slow fields;
   - enemy guns winding up: target and release time.
   It carries the same information `dodge.cpp` uses, no more.
2. **A command adapter** with an explicit aim point, hold/release intent per gun, and volley membership.
3. **Arbitration rules:**
   - react takes temporary precedence over movement;
   - it is defined which attacks stay possible during a dodge;
   - units return to their useful position after a dodge;
   - reacting affects volley readiness;
   - copied rotation is constrained to the participation rule (§4.3).
4. **Recording**, next to targets and goals:
   - primitive activation;
   - candidate and executed intent;
   - arbitration winner and reason;
   - readiness;
   - volley membership.
5. **Shadow state:**
   - the teacher's and the student's state and RNG are separate, initialised and advanced consistently on the same decision state;
   - the spec's byte-identical shadow-on/off check still applies;
   - students are trained on their own available features, including sparse late-army states.
6. **Battery-level labels for volleys.** Per-unit marginal agreement can copy individually plausible shots that fail jointly. A volley is labelled as one joint decision: members, release times, aim points.

---

## 4. Primitives in the owner's order: react → V1 timing → V2 geometry

### 4.1 React (first labelled change)
- **Teacher:** `dodgeShells: "smart"`, `castDodge`, `dodgeShots` (spec §10). Copy the rule as a named shape on the observation adapter.
- **Measure:**
  - hit probability per shell landing within splash of our units;
  - damage and deaths avoided;
  - time and firepower cost of dodging (attack opportunities lost);
  - interaction with volley readiness.
- **Do not maximise event counts.** The stored ~2,940.5 per fight are positive dodge-goal *decision records* (`observer_v1.cpp`), not distinct shells avoided. The gap is our **zero** reaction.

### 4.2 V1 timing: the battery oscillator
- **The comparison:**
  - (a) the copied central sync (`holdFire: {sync}`, `waves`);
  - (b) the RRG shape: local coupled phases in Kuramoto or pulse-coupled form, where a firing gun advances its neighbours' phases ([Mirollo & Strogatz](https://www.iasi.cnr.it/~vbonifaci/semcn/Mirollo1990.pdf) prove almost all initial conditions synchronise for identical integrate-and-fire oscillators).
- **The owner's difference:** timing emerges from local coupling, not a central scheduler.
- **Report:**
  - spread of launch times **and** of landing times (time on target is about landing within seconds of a planned impact; [TOT](https://en.wikipedia.org/wiki/Time_on_target));
  - effects of cooldown, windup and flight time;
  - hold-induced firepower loss;
  - enemy dodge success against our shells;
  - hits per shell and shells per kill;
  - behaviour with **only one or two guns left**.
- **[inference] Caveats:**
  - Different ranges give different flight times, so synchronising launches does not synchronise impacts; the phase should target landing time.
  - Kuramoto's coherence threshold is an N→∞ result and "breaks down" for small N ([Kuramoto model](https://en.wikipedia.org/wiki/Kuramoto_model)), so few-gun behaviour must be specified and tested, not assumed.
  - Synchrony alone does not prevent escape; that is V2's job.

### 4.3 V2 geometry, and the supporting changes
- **V2 geometry:**
  - copy the existing teacher planner first: `artyFire: plan` (trap, sweep, net, wall), `artyHerd`, `artyRollout` (2-s look-ahead), `artyModel: exact`;
  - then compare and simplify.
  - Score **joint** volley coverage, enemy units caught per volley, damage per volley and delayed herd/trap patterns. Do not optimise guns independently.
  - **Closest landmark:** playout-scored choice among script patterns (Puppet Search choice points; PGS-style playouts). **[inference]** The elite's planner already is such a search over volley patterns. Use it before commissioning any general SSS/GAB teacher.
- **Rotation (supporting, measured separately):**
  - `saveWounded` (`decisions.cpp:6–12`) backs towards home with **no own-range constraint**;
  - `decideUnit` returns as soon as it activates (line 44), before attack-release selection;
  - **Eligibility:**
    - HP at or below the threshold;
    - more than 2 enemies;
    - our survivors fewer than 4× theirs;
    - wounded fewer than half our survivors;
    - the nearest enemy within its range + 1.5 × speed + 60.
  - **Movement:** it steps 60 px directly away from that enemy, plus 20% of the way towards the home edge.
  - A copied rotation must therefore be constrained to the owner's rule: stay within own useful range, never leave. Check time out of own range per activation.
- **Aim (`lead`):** a supporting change, measured separately, on the command adapter's aim point.

---

## 5. Evaluation: the series is primary; any proxy is defined and validated first

### 5.1 Primary and secondary measures (spec §5)
- **Primary:** the streak S ∈ {0,…,10} under the rules in §0. The first fight not won by elimination ends the run.
- **Secondary, always reported with denominators:**
  - the probability of reaching each fight k;
  - the completion (10/10) frequency;
  - survivors by role (melee, ranged, guns) before each fight;
  - losses on **won** and **failed** fights, reported separately;
  - per-tactic losses.
- **Never optimise only losses conditional on wins.**
- The spec's 10 development series per arm are descriptive evidence, not a precise population estimate. More sampling needs its own projection and authorization.

### 5.2 A candidate proxy for search and tuning [inference, unvalidated]
An unconstrained weighted sum of deaths and damage can favour passive survival or short failed fights. So the proxy targets the expected streak contribution directly.

- **Branch end:** a branch from state s runs for horizon H under a stated continuation policy (§6). It then continues stepping until every shell launched before H has landed, so damage already committed counts.
- **Terminal rules inside a branch:**
  - enemy eliminated → fight won; survivors are the living own units (to be healed);
  - own army eliminated, or the fight clock reaching the timeout → the series ends here (value 0 for later fights);
  - otherwise non-terminal: apply the tail estimate.
- **Tail estimate:**
  - P̂_win(s_H) is the estimated probability this fight is won by elimination.
  - m̂ = (m̂_melee, m̂_ranged, m̂_gun) is the expected surviving count per role. Each living unit counts with a survival probability q(hp fraction, threat), and threat includes incoming shells.
  - Survivors heal, so a surviving unit counts fully whatever its HP. Low HP matters only through q.
- **Series continuation value:**
  - V(m, k) is the expected number of further fights won, starting at fight k+1 with role composition m. It is fitted from series data as a lookup or monotone regression on role counts, with V(·, 10) = 0.
  - This is the **role-capability** term: losing the last effective gun can cost more than losing another escort.
- **Proxy:** J(s_H) = P̂_win · (1 + V(m̂, k)). Its unit is expected fights won, so it needs no free weights.
  - Before V is fitted, LTD2 (√hp·dpf) may stand in for P̂_win as a labelled heuristic.
- **Validation before any use:** on paired candidates, J's ranking must predict the paired series outcomes above a pre-registered agreement threshold (§7 stop row). Otherwise J is not used.

### 5.3 Normalization ledger

| Quantity | Level | Units | Normalization |
|---|---|---|---|
| Streak S | series | fights | none (0–10) |
| Survivors by role m | between fights | unit counts | raw counts per role; healed to full |
| P̂_win, q | inside a fight | probability | bounded [0,1] |
| V(m, k) | series | expected fights | fitted on the same rules; no per-level hand tuning |
| Hit probability per shell, landing-time spread | per volley | probability; game-seconds | per shell; per volley |
| Branch cost | engine | core-seconds | per decision, per fight (§7) |

---

## 6. The engine clone: what it is and is not, and the information boundary

### 6.1 Branch semantics
Read from the delivered sources:
- `World::copyAuthorityFrom` (`world.cpp:274–279`) sets `thinkTeams=0`, and clones are `branch` worlds.
- In a branch, `artilleryVolley` takes a **lighter** candidate path (`artillery.cpp:61`, `light = w.branch && !(thinkTeams & team)`).
- `lookahead` (`search.cpp:26`) and the director (`director.cpp:48`) are **suppressed** unless thinking is enabled for that team.
- **So a copied world does not reproduce the scripted opponent's own future search behaviour by default.**

**Before any search pilot:**
- document branch thinking, enemy continuation, timestep, and all controller memory and RNG semantics;
- test **continuation parity**: same actions and settings, main against branch trajectory;
- or label the reduced-policy model and measure its **ranking error** against full-thinking continuations.

### 6.2 Randomness
- Copying RNG state scores **one realised future**, not an expectation.
- Use several sampled continuations with **coupled random streams** across alternatives. Identical initial seeds alone do not align action-dependent draws.
- Call results "estimated disagreement cost" and "continuation-dependent counterfactuals". Never call them exact, ideal or globally optimal.

### 6.3 Information boundary: two separate teacher arms
- **The oracle arm** may use the true enemy tactic and skill, hidden state and clone rollouts. It is used for diagnosis and as an upper reference only.
- **The deployable arm** uses only declared public fields:
  - unit records and the projectile/cast data of §3.2;
  - **no** tactic ID, RNG state or enemy internals.
- **Students learn from observations,** or from a declared, measured *inference* of doctrine, never from hidden IDs.

---

## 7. Cost: formula, uncertainty, and a proposed (not run) pilot

**Per decision:**

C_dec = P × K × S × (c_copy + (H/Δt) × c_tick) + c_select + c_record

where:
- P = hill-climb passes;
- K = candidate evaluations per pass (types × shapes);
- S = stochastic continuations;
- H = horizon in game-s, at Δt = 1/30 s per tick;
- c_tick = the per-tick branch cost, which depends on unit count, projectiles and the branch-thinking setting.

**Per fight:** C_fight = (T_fight / Δ_dec) × C_dec + c_base_fight.

**With revision 1's assumptions [inference, arithmetic only]:**
- P = 1, K = 24, S = 2–3, H × c_tick ≈ 0.02–0.1 core-s;
- C_dec ≈ **0.96–7.2 core-s**, re-planned every Δ_dec = 1 s;
- a 90-s fight costs ≈ **86–648 core-s**;
- ideal 10-core throughput ≈ **0.9–7 teacher fights/min**.

**This excludes:**
- extra passes;
- the GAB layer;
- state-copy cost;
- **nested enemy search** if branch thinking is enabled, which multiplies c_tick;
- recording;
- the counterfactual replays at disagreement states.

The whole-fight average (0.44 core-s per fight, about 0.16 ms per tick) understates dense early states.

**Proposed branch-cost pilot** (owner authorization required; not run):
- **States:** about 20 each of early-dense, mid, late-sparse and projectile-heavy states, from stored fights.
- **Measure:**
  - CPU and wall time;
  - c_copy and c_tick with branch thinking off and on;
  - controller, teacher and recording time;
  - peak memory.
- **Sweep:** small K, S and P values.
- **Output:**
  - a cost table;
  - ranking stability (does S = 2 against S = 3 change the chosen assignment?);
  - a per-label and total budget.
- **Projection:** reported before the run (decision 0031).
- **Until it is measured,** prefer the directly copied react and the existing gun-only teacher planner. Cache labels, and screen disagreements cheaply (target/goal/intent mismatch) before any counterfactual rollout.

**Stop rows:**

| Yes/no | Action | Role |
|---|---|---|
| Does branch continuation fail parity with the main trajectory under identical actions and settings? | Label the reduced model; measure ranking error before using it as a teacher | implementer |
| Does the measured cost per teacher fight exceed the owner-set budget? | Restrict search to guns, or drop T-search and keep copied primitives | drafter |
| Does any student input include an oracle field (tactic ID, RNG, enemy internals)? | Remove it; use observation-only or a declared, measured inference | implementer |
| Does a copied rotation leave a unit outside its own useful range beyond the declared tolerance? | Reject or constrain the copy | implementer |
| Does the proxy J fail to predict paired series outcomes at the pre-registered threshold? | Do not use J; redefine it | drafter |
| Does any projected run exceed 1 h before 22:00? | Ask the owner | Claude |
| Would any change edit a pinned or frozen file? | Stop; use a new file | implementer |

---

## 8. Seeds, curriculum and the owner's series kept apart

### 8.1 Separate seed sets
| Set | Purpose |
|---|---|
| **D** | The owner's development series; untouched, comparison only |
| **T** | Tuning |
| **L** | Teacher label generation |
| **R** | Fresh reporting |

- Pair the enemy tactic sequence and placements across arms from a **separate draw stream**, so controller RNG consumption cannot change later draws.
- Late fights have survivor compositions that ordinary full-army drills never see. Include reduced-survivor states in L and T.

### 8.2 Curriculum and pool weighting (training only)
- PFSP over 19 doctrines × skills, prior selves (hall of fame; [Liu et al. 2018](https://arxiv.org/abs/1803.10314) found co-evolution with fitness sharing, shared sampling and a hall of fame produced better micro faster) and exploiter cells can be **training or stress distributions**. They are not the yardstick.
- **Sampling:** use p(cell) = ε·uniform + (1−ε)·PFSP with ε > 0.
  - f_var(x) = x(1−x) is zero at both extremes, so a "floor" from f_var alone does not guarantee coverage.
  - f_hard needs a bounded x, e.g. the estimated probability that this cell ends a series, or role-normalised own-loss fraction in [0,1]. It also needs uncertainty, e.g. a Beta posterior.
- [Prioritized Level Replay](https://arxiv.org/abs/2010.03934) is the analogue for choosing training cells.
- **Noise handling:** UH-CMA-ES ([Hansen et al. 2009](https://cs.utexas.edu/~shivaram/readings/b2hd-HansenNGK2009.html)) via `cma.NoiseHandler`; paired seeds; racing ([irace](https://iridia.ulb.ac.be/irace/)).
- **Accounting:** series multiply the fights per candidate, and noise handling adds re-evaluations. Every budget states fights per candidate × candidates × series.
- **Report separately:**
  - the uniform regular-skill series (the owner's objective);
  - weighted-training results;
  - skill, self-play and exploiter stress results.
- **Stress tests, labelled and separate** (they never change the official pool):
  - held-out doctrine families and parameter perturbations;
  - placement and orientation variation;
  - react × volley interaction ablations;
  - reduced survivor compositions.

---

## 9. Ranked plan (owner's order kept; each item one labelled change, owner-approved, on fresh seeds)

**Step 0 (prerequisite, not a gain item):**
1. Define the participation rule check (§4.3), the evaluation (§5) and the interface adapters (§3.2).
2. Establish the T-elite baseline and the shadow logging (spec §9).
3. Fix the seed sets (§8).

Evaluation design precedes every comparison. It does not displace the owner's primitive order.

### 1. React: copy the engine's reaction rule as a named shape
- **Closest landmark:** the supervised-copy stage (AlphaStar/AlphaGo SL) in its simplest form: adopt the teacher's rule (spec §9.3 option 2), not learn it.
- **Expected gain:** the largest known gap.
  - Enemy artillery causes 74.1% of our deaths and 77% of damage taken (86% of our ranged deaths, 63% of melee).
  - We make zero reactions.
  - Measured by hit probability and losses avoided (§4.1).
- **Cost:** low once the observation adapter exists.
- **Risk:**
  - dodging costs firepower and breaks volley readiness;
  - the arbitration rules (§3.2) must be explicit.
- **Shapes kept:** Yes, a named react primitive citing `dodgeShells`/`castDodge`.

### 2. V1 timing: the battery oscillator against copied central sync
- **Closest landmark:** time-on-target doctrine; Mirollo–Strogatz pulse coupling; Kuramoto; the engine's `holdFire.sync`.
- **The difference:** local coupling, not a scheduler.
- **Expected gain:** shells landing together leave less room to dodge one shell into another's footprint. Our 184.4 launches per fight against the enemy's 104.9, for similar kills, suggest single-gun fire is inefficient.
- **Risk:** hold-induced firepower loss; few-gun degeneracy; launch ≠ landing synchrony (§4.2).
- **Shapes kept:** Yes; the oscillator *is* the shape's synchrony.

### 3. V2 geometry: copy the teacher's volley planner, then simplify
- **Closest landmark:** playout-scored pattern choice (Puppet Search choice points; PGS playouts). The engine's `artyFire: plan` with `artyRollout` already does this for guns.
- **Expected gain:** coverage, herding and trapping beat independent aiming against dodging units (owner, spec §11).
- **Cost:** that of the existing gun-only planner. Its branch cost needs the §7 pilot if extended.
- **Risk:** joint labels are required (§3.2 item 6); the branch semantics of §6.1 apply to its rollouts.
- **Shapes kept:** Yes; named volley patterns.

### 4. Supporting changes, each measured separately
- **Changes:**
  - participation-constrained rotation (§4.3);
  - aim (`lead`);
  - series-aware tuning of the existing knobs, using the §5 proxy only after validation, §8 sampling and noise handling.
- **Closest landmarks:** ECSLBot-style fitness, PFSP and hall of fame, UH-CMA-ES.
- **Risk:** rotation leaving the fight; proxy mis-ranking. Both are covered by stop rows.

### 5. Conditional: budgeted adaptive portfolio search and distillation
- **Only if** the §7 pilot fits the budget **and** a paired comparison shows a measured low-loss series benefit over items 1–4.
- **Design:**
  - SSS+-style adaptive granularity, not fixed role types (§2.2 failure row);
  - a PGS+-style first-action-then-default evaluation, with its rankings checked against longer continuations;
  - a deployable teacher arm only for labels.
- **Distillation:** into a small, depth-limited, readable selector over **named volley patterns or movement policies**, with a native (C++) deployment path. It must not replace the oscillator's local coupling.
- **Closest landmarks:** PGS/SSS+/GAB, ExIt, Barriga et al.

**Deferred (last):** a doctrine repertoire (pyribs CMA-ME plus an early doctrine classifier).
- It is considered only if a cross-table shows per-doctrine gains over one robust policy that exceed misclassification and latency costs.
- Sources: [Cully et al.](https://arxiv.org/abs/1407.3501); [CMA-ME](https://arxiv.org/abs/1912.02400); [Tavares et al.](https://ojs.aaai.org/index.php/AIIDE/article/view/12857).

### The owner's "ideal runs", restated
- **T-elite** is the in-engine reference line per role and primitive: deployable where it uses only public data.
- **T-search** is an optional, budgeted improvement candidate, oracle or deployable as declared. It is **not** an ideal or optimal player (§6).
- **"Split and compare"** = shadow intents per primitive (§3.2), reported as agreement **and** estimated disagreement cost.
- **"Repeat"** = one labelled copy per primitive, re-measured in drills and the series.

### What does not transfer now, and why (scoped)
- **End-to-end deep-RL controllers:**
  - compute;
  - opaque policies, against the project principle;
  - default reward shaping that does not penalise own losses directly.
- **Learned dynamics models:** deferred while the clone is available and branch cost is unmeasured; not universally dismissed.
- **Leagues of learning agents:** our opponent is a fixed scripted pool. Only sampling ideas and script-level stress tests transfer, kept apart from the yardstick.
- **SparCraft-tuned behaviours:** no collisions, splash or lobbed shells. Copy the algorithms and lessons, not the tuned scripts.

---

## 10. Low-loss techniques: evidence and scope

| Technique | Evidence (scoped) | Note for us |
|---|---|---|
| Concentration of force | Lanchester models fitted to StarCraft battles ([Stanescu et al. 2015](https://ojs.aaai.org/index.php/AIIDE/article/view/12780)) | Kill speed compounds |
| Focus fire and overkill | Against the built-in AI, 1,000 battles ([Usunier et al. §7.2, Table 1](https://ar5iv.labs.arxiv.org/html/1609.02993)): m15v16 weakest-closest (wc) **.10**, no-overkill-no-change (nok_nc) **.68**, closest (c) **.81**, learned ZO **.79**; w15v17 .02/.12/.20/.49. The paper warns that "if our units die without doing their expected damage… 'no overkill' can be detrimental (as it is implemented)". | Naive weakest-first focus collapsed at scale. No-overkill helped against weakest-first but was not best; the best rule is scenario-dependent. |
| Target priority (dpf/hp) | NOKAV in SparCraft searches; optimal 1-vs-n orderings exist ([Furtak & Buro 2010](https://ojs.aaai.org/index.php/AIIDE/article/view/12410)) | Compare our splash value V with AV-plus-splash on clone branches |
| Kiting | SMAC 3s_vs_5z; [Uriarte & Ontañón 2012](https://ojs.aaai.org/index.php/AIIDE/article/view/12544); ECSLBot | Ranged (reach 280) against melee (reach 64) |
| Damaged-unit rotation | Churchill 2017 (simulation, out of *enemy* range); ECSLBot "knowing when to flee" | Candidate only, under the participation rule (§4.3) |
| Splash: react, timing, geometry | SC2LE splash mini-game gap (scores, one benchmark); potential-field unit control ([Hagelbäck](https://ojs.aaai.org/index.php/AIIDE/article/view/12365); splash-specific repulsion not verified) | Owner's order §4: react, then V1, then V2 |
| Damage dealt against received | Pareto micro ([Liu et al. 2018](https://arxiv.org/abs/1803.10316)) | Report both. The series proxy (§5.2) folds them into expected fights won. |

---

## 11. Tools (checked 2026-10-08; one license and link per tool)

**Policy:** keep pycma now. Add any other dependency only on a measured need from items 1–5.

| Tool | Version, license | Verdict |
|---|---|---|
| [pycma](https://pypi.org/project/cma/) | 4.5.0 (2026-09-13), BSD-3-Clause | **Keep;** use `NoiseHandler` and paired seeds |
| [pyribs](https://pypi.org/project/ribs/) | 0.12.0 (2026-07-22), MIT | Only for the deferred repertoire |
| [Optuna](https://pypi.org/project/optuna/) | 5.0.0 (2026-09-07), MIT | Optional for categorical choices and pruning, if a need is measured |
| [Nevergrad](https://pypi.org/project/nevergrad/) | 1.0.12 (2025-04-23), MIT | Optional cross-check |
| [irace](https://raw.githubusercontent.com/MLopez-Ibanez/irace/master/DESCRIPTION) | upstream dev 4.5.0.9000, GPL (≥ 2); current CRAN release **not verified** | Use the racing idea in Python; skip the R dependency |
| [scikit-learn](https://pypi.org/project/scikit-learn/) | 1.9.1, BSD-3-Clause | Small selectors and ranking fits, **with explicit depth/size limits and a native export path** |
| [LightGBM](https://pypi.org/project/lightgbm/) | 4.7.0, MIT | As above; boosted trees are readable only with strict limits |
| [evosax](https://pypi.org/project/evosax/) | 0.3.1, Apache-2.0 (JAX) | Skip: the cost is C++ fights, not the optimiser |
| [EvoTorch](https://docs.evotorch.ai/latest/) | 0.6.1, Apache-2.0 (**PyTorch**) | Skip, same reason |
| [QDax](https://pypi.org/project/qdax/) | 0.5.0, MIT (JAX) | Skip |
| [neat-python](https://pypi.org/project/neat-python/) | 2.0.0, BSD-3 | Skip: opaque networks |
| [PettingZoo](https://pypi.org/project/pettingzoo/) | 1.27.0, MIT | Defer |
| [Ray/RLlib](https://pypi.org/project/ray/) | 2.59.0, Apache-2.0 | Defer |
| [CleanRL](https://pypi.org/project/cleanrl/) | 1.2.0 (2023-05-22), MIT | Defer |
| [imitation](https://pypi.org/project/imitation/) | 1.0.1, MIT | Skip: our policies are not torch nets |
| [d3rlpy](https://pypi.org/project/d3rlpy/) | 2.8.1, MIT | Skip, same reason |
| [OpenSpiel](https://openspiel.readthedocs.io/en/latest/api_reference.html) | 2.0.2, Apache-2.0 | **Supports simultaneous joint actions** (`apply_actions`, `is_simultaneous_node`). Deferred because the action-abstraction and wrapper cost is high, not because it lacks simultaneous moves. |
| [SparCraft](https://github.com/davechurchill/SparCraft) / [UAlbertaBot](https://github.com/davechurchill/ualbertabot) | MIT | Read the algorithms (PGS+, SSS, NOKAV, LTD2) |
| [microRTS](https://github.com/Farama-Foundation/MicroRTS) | GPL-3.0 | Read only; do not vendor |

---

## 12. Self-audit (revision 2): each recheck finding, the fix and its cause

| Finding | Fix in this revision | Cause in revision 1 |
|---|---|---|
| **F1 (High):** owner sequence and battery oscillator | Scope extended to spec §§9–12. §0 separates the superseded commit/escape gate from the battery oscillator. §4 and §9 follow react → V1 → V2 with the teacher volley planner before any general search. V1 metrics include landing-time spread, hold loss and few-gun behaviour. The selector may choose named patterns only, never replacing local coupling. | I read Amendments 2–3 but did not re-read the spec for Amendment 4. I carried the old "gate" role into the plan. |
| **F2 (High):** observation/action interface; saveWounded | §3.2 adopts Amendment 5: adapters, arbitration, recording, separate shadow state, battery-level labels. DAgger is described as collection + aggregation + refit. §4.3 records saveWounded's lack of an own-range limit, its early return and its eligibility cap, and constrains rotation to the participation rule. | I assumed target/goal agreement could carry react, aim and volley copying, without reading `controller.h`. I trusted the teacher rule's name ("backs away, still near"). |
| **F3 (High):** series primary; explicit evaluator | §5: streak primary with exact terminal rules (any fight not won by elimination ends the run); secondary measures with denominators; a candidate proxy J = P̂_win·(1+V(m̂,k)) with shells-in-flight resolution, healed-survivor and role-capability terms, and terminal rules; a validation gate and a normalization ledger. LTD2 is labelled a heuristic. | I compressed "losses carry over" into "the streak measures cumulative losses". I named "own-loss-weighted LTD2" without defining it. |
| **F4 (High):** clone semantics and information boundary | §6: branch thinking off by default (`thinkTeams=0`; light volley path; lookahead and director suppressed), verified in the sources; a parity or ranking-error requirement; coupled random streams; oracle against deployable arms; no hidden IDs for students. "Exact" and "ideal" removed. | I equated cloning world state with an exact teacher, without reading the branch code. |
| **F5 (Medium):** cost | §7: full formula with all factors; corrected arithmetic (0.96–7.2 core-s per decision; 86–648 core-s per fight; 0.9–7 fights/min); listed exclusions; a proposed, not-run pilot; stop rows with action and role. | Revision 1 omitted the continuation factor S, which it had itself proposed, and stated feasibility from whole-fight throughput. |
| **F6 (Medium):** SSS and SSS+ | §2.2 separates SSS and SSS+ and adds the 56-unit failure row (0.46 / 0.16 against 0.96 / 0.95). POE against PGS corrected to 0.56–1.00. PGS-in-StarCraft results given per scenario. "Searches always beat their scripts" removed. Rows re-checked against the fetched IJCAI PDF text. | I summarised ranges from the larger scenarios and skipped the last table block and the small-army rows. |
| **F7 (Medium):** curriculum against the yardstick | §8: seed sets D/T/L/R; paired draw streams; an ε-uniform mixture (f_var is zero at the extremes); bounded f_hard input with uncertainty; separate reporting; stress tests kept outside the official pool. | I treated the 76 skill × doctrine cells as the yardstick. I reused one pool for tuning, labels and reporting. |
| **F8 (Medium):** ceilings and universal claims | RAI-BC is described as a baseline, with per-map regressions (re-verified: 100→0, 40→5). The SC2LE result is scoped (scores, 600 M steps, one benchmark). The kiting quote is scoped to enemy range. AlphaZero is described as teacher-free. MuZero is deferred, not dismissed. The three-step loop is called our proposal. The Usunier caveat is quoted. ECSLBot's scope is corrected (Vultures, Dragoon mention, Eq. 4). The SMAC reward description is corrected. Killers denominators are stated (41.8 over all fights, 40.7 wins-only; about 2,940 are decision records). | Interpretation ran ahead of the sources. I generalised single experiments into rules. |
| **N1 (Low):** tools | EvoTorch is PyTorch (re-verified); OpenSpiel supports simultaneous moves (re-verified); one license per tool; irace version from upstream with CRAN marked unverified; tree selectors need depth limits and a native path; extra dependencies only on a measured need. | One shared license cell; I assumed JAX for EvoTorch and turn-based for OpenSpiel without checking. |

**Re-verified for this revision (WebFetch or fetched-PDF text):**
- Goodfriend per-map regressions;
- SSS Table 1 rows;
- Churchill 2017 Table 1 and the 10/40 ms note;
- SC2LE: 600 M steps, scores;
- the Usunier caveat and that results are against the built-in AI;
- ECSLBot Eq. 3/4 and the Dragoon mention;
- OpenSpiel simultaneous API;
- EvoTorch on PyTorch;
- irace DESCRIPTION;
- SMACv2 open-loop claim;
- Mirollo–Strogatz, the Kuramoto model and TOT definitions;
- engine branch semantics and saveWounded, read in `evidence/tactical_composition_demo/astelia_cpp/src/native/`.

**Still from secondary summaries:** AlphaStar compute, the f_hard exponent, OpenAI Five's 80/20 split, AlphaGo's 57%, and the PGS 2013 abstract-level claim (the PDF returned 404).

**This revision should get the owner's verbatim recheck again** (AGENTS.md), preferably by Codex, before B8 acts on it.
