# Game-AI best practice for Astelia: what landmark systems did, what transfers to one laptop, and a ranked plan

**Status:** research note for plan step B8 (`docs/PLAN_CURRENT.md`). It informs the shape-lab spec Amendments 2–3 (`evidence/tactical_composition_demo/SHAPE_LAB_SPEC.md` §9–§10). No project code was run for this note. Every external claim carries a link. Statements marked **[inference]** are this note's reasoning, not a source's finding. Numbers about our engine come from the task brief and the spec, not from new measurements.

**Date:** 2026-10-08. **Author family:** Claude.

---

## 0. Our problem in the literature's terms

| Our term | Closest literature term | Where it comes from |
|---|---|---|
| Shape (per-role behaviour: gun focus, spacing, escort, melee law) | **Script** in a **script portfolio** | Churchill & Buro's portfolio search line ([Lelis, IJCAI 2017](https://www.ijcai.org/proceedings/2017/522)) |
| Oscillator gate choosing when a shape acts | Script-selection policy, or a hand-written meta-controller | [Barriga et al. 2017](https://arxiv.org/abs/1709.03480) learn this selector |
| ~11 knobs tuned by CMA-ES | Parameterised micro tuned by evolution | ECSLBot: [Liu, Louis & Ballinger 2014](https://www.cse.unr.edu/~simingl/papers/publish/CIG2014IMPFMicro.pdf), 14 parameters, GA |
| Engine clone + forward play (elite's 2-s volley rollouts) | **Forward model** for playout-based search | [SparCraft](https://github.com/davechurchill/SparCraft) (MIT); PGS, SSS, POE |
| 19 enemy doctrines × 4 skills | Fixed **opponent pool** | AlphaStar league / PFSP, without the learning opponents |
| 10-fight series, dead stay dead | Attrition objective (own losses matter as much as winning) | LTD2 evaluation ([Churchill et al.](https://ojs.aaai.org/index.php/AIIDE/article/view/12527)), ECSLBot fitness |
| Teacher arm and shadow actions (spec §9) | Expert labelling of states (**behaviour cloning**, or **DAgger** when our policy drives) | [Ross, Gordon & Bagnell 2011](https://arxiv.org/abs/1011.0686) |

**Closest known method to what we already have:** ECSLBot ([Liu, Louis & Ballinger, CIG 2014](https://www.cse.unr.edu/~simingl/papers/publish/CIG2014IMPFMicro.pdf)).
- It encodes micro (influence maps, potential fields, kiting, target selection, fleeing) in **fourteen parameters**.
- A GA tunes them in "about 21 hours" per unit type.
- Its fitness is **units remaining on each side** plus a time term: F = (N_F − N_E)·S_u + (1 − T/MaxT)·S_t.
- The evolved player beat UAlbertaBot and Nova "in kiting efficiency, target selection, and knowing when to flee to survive".

**How we differ:**
- per-role shapes rather than one parameter set per unit type;
- a per-unit oscillator gate;
- CMA-ES instead of a GA;
- mixed melee, ranged and artillery with splash.

ECSLBot was tested on one unit type. The authors themselves list mixed unit types as "still an open research question".

**One fact about our yardstick drives most of this note [inference].** In the series, survivors heal and the dead stay dead. A win that loses 41 of 50 units leaves 9 units for the next fight, so in practice the streak measures **cumulative losses**, not the per-fight win rate. This is why literature that optimises win rate alone, such as SMAC's default reward, transfers only partly. In [SMAC's code](https://raw.githubusercontent.com/oxwhirl/smac/master/smac/env/starcraft2/starcraft2.py), `reward_only_positive=True` by default, so own damage is ignored. Methods with a loss-aware evaluation (LTD2, ECSLBot's fitness) transfer directly.

---

## 1. Landmark game AIs: what they did, and what transfers at 10^5–10^6 fights

Our budget [inference from the brief]:
- **Throughput:** about 1,350 fights/min on 10 workers, so about 81,000 fights/hour. That is about 0.44 core-seconds per 50v50 fight.
- **Budget:** 10^5 fights is roughly 1.2 h, and 10^6 roughly 12 h.
- **Cost of one rollout:** a full fight of 30–150 game-s is 900–4,500 ticks. A 2-s rollout (60 ticks) therefore costs roughly 0.005–0.03 core-s.

| System | What it actually did | Compute | Transfers to us | Does not transfer |
|---|---|---|---|---|
| **AlphaGo** ([Nature 2016](https://research.google/pubs/mastering-the-game-of-go-with-deep-neural-networks-and-tree-search/)) | Supervised policy net on expert moves (57% move prediction per [secondary summary](https://blog.acolyer.org/2016/09/20/mastering-the-game-of-go-with-deep-neural-networks-and-tree-search/)), then self-play RL, a value net, and MCTS combining them | Large GPU/TPU clusters | **Imitate a teacher first, then improve by search.** Search uses the policy as a prior and an evaluator at the leaves. | Deep nets over raw state; human game records (we have none, but we have the engine's elite AI as a teacher) |
| **AlphaZero / KataGo** ([KataGo, Wu 2019](https://arxiv.org/abs/1902.10565)) | Self-play plus MCTS; the network learns the search's visit distribution (policy) and the outcome (value). KataGo cut compute about 50× versus ELF OpenGo, still about 1.4 GPU-years. | AlphaZero: about 21 M games ([EfficientZero paper](https://arxiv.org/abs/2111.00210)) | **Expert-iteration loop:** search produces better labels and a cheap policy learns them ([Anthony et al. 2017](https://arxiv.org/abs/1705.08439)). Gumbel planning keeps policy improvement with few simulations ([Danihelka et al. ICLR 2022](https://iclr.cc/virtual/2022/poster/6418)). | 21 M games of self-play is 1–2 orders of magnitude over our budget. Discrete-move tree search does not fit 100 simultaneous continuous units without action abstraction (see §2). |
| **MuZero** ([arXiv 1911.08265](https://arxiv.org/pdf/1911.08265)) | Learns a dynamics model and searches in it | As above | Nothing core. MuZero exists for when "a perfect simulator" is **not** available. We have one: the engine clone. | Learning a model when the exact engine is available is pure loss. Learned models also misjudge unseen policies ([What model does MuZero learn?](https://arxiv.org/html/2306.00840v3)). |
| **AlphaStar** ([DeepMind blog](https://deepmind.google/discover/blog/alphastar-grandmaster-level-in-starcraft-ii-using-multi-agent-reinforcement-learning/)) | 1) Imitation from human replays, which beat 84% of active players. 2) League: main agents, main exploiters and league exploiters. 3) Main agents sample opponents by **PFSP**: weight f(P[win]), with f_hard(x) = (1−x)^p focusing the hardest ([survey, arXiv 2408.01072](https://arxiv.org/pdf/2408.01072)). 4) Distillation towards human play throughout, against forgetting. | Each agent 44 days on 32 TPUv3; 12 core agents; about 900 players created ([secondary](https://gamesbeat.com/deepminds-alphastar-final-beats-99-8-of-human-starcraft-2-players/)) | (a) **Start from a teacher** (our elite AI). (b) **PFSP weighting** over our 19×4 opponent pool. (c) **Exploiter idea:** search for the enemy settings our AI loses to. (d) **Keep a pull towards the teacher** while tuning (an anti-forgetting regulariser). | The neural policy, the league of *learning* agents and the compute. [AlphaStar Unplugged](https://arxiv.org/abs/2308.03526) shows that even offline RL from replays needs millions of games. |
| **OpenAI Five** ([arXiv 1912.06680](https://arxiv.org/abs/1912.06680)) | PPO at scale: about 2 M frames per 2 s, 10 months. 80% of games against the current self and 20% against past selves ([survey summary](https://arxiv.org/pdf/2111.07631)). "Team spirit" blends individual and team reward. "Surgery" carries training across code changes. | Very large | (a) A **past-self pool** against forgetting: keep a hall of fame of our earlier versions in the evaluation pool. (b) The **team-spirit** idea maps to a per-unit term against a team term in our fitness: units should not trade themselves for team damage. | The PPO scale. |
| **Smaller successors** | [RAISocketAI](https://arxiv.org/html/2402.08112v1) won the microRTS competition at CoG 2023, the first DRL agent to do so (about 70 GPU-days). Its BC variant (**RAI-BC**), trained to copy the scripted winner Mayari, reached 71% overall but only 44% against Mayari itself; PPO fine-tuning raised this to 88% overall. | 23–70 GPU-days | **Copying a scripted teacher is cheap and gets near the teacher, not past it.** Exceeding the teacher needs an improvement step (search or RL). | DRL at 70 GPU-days |
| **Programmatic synthesis** ([Mariño et al. AAAI 2021](https://ojs.aaai.org/index.php/AAAI/article/view/16114); [2L, IJCAI 2023](https://arxiv.org/abs/2307.04893)) | Local search over programs in a DSL, by self-play. With 2L's choice of reference opponents, it beat the two latest microRTS competition winners in a simulated tournament. | Laptop-scale search | **This is the closest landmark to our principle:** small readable programs (shapes) found by search, with the opponent set chosen to sharpen the search signal. | |

**Summary of question 1.** The transferable core of every landmark is the same three-part loop:
1. **Start from a teacher.** (AlphaGo SL, AlphaStar SL, RAI-BC.)
2. **Improve with search or optimisation against a curated opponent set.** (MCTS, the league with PFSP, 2L.)
3. **Distil the improved behaviour back into a cheap policy.** (AlphaZero, ExIt.)

The neural-network scale is what does not transfer. Our "policy" is the shape set with its knobs and gate. Each of the three steps has a shape-level version (§9).

---

## 2. StarCraft micro-combat research (closest to our problem)

### 2.1 Combat simulators and scripts
- **SparCraft** ([GitHub, MIT](https://github.com/davechurchill/SparCraft); also inside [UAlbertaBot](https://github.com/davechurchill/ualbertabot)) is a StarCraft combat simulator built for search. Its abstractions: no collisions, no fog, constant speed ([Lelis 2017](https://www.ijcai.org/proceedings/2017/522)).
- **Standard scripts**, as defined in [Churchill, Lin & Synnaeve 2017](https://ojs.aaai.org/index.php/AIIDE/article/view/12962):
  - **c** AttackClosest;
  - **w** AttackWeakest;
  - **k Kiter:** "moves away from an enemy unit while reloading";
  - **h** HoldPosition;
  - **n NoOverkill:** no unit is assigned to an enemy that is already receiving lethal damage.
- **NOKAV** (no-overkill attack-value): attack value = damage per frame ÷ hit points.
- **LTD2 evaluation** ([Churchill, Saffidine & Buro, AIIDE 2012](https://ojs.aaai.org/index.php/AIIDE/article/view/12527)) is a playout's end value. It sums √hp × dpf over living units, so it rewards keeping **many** units alive, not one healthy unit. **[inference]** This is much closer to our series objective than "win".

### 2.2 Search over scripts (the portfolio family)

| Method | Mechanism | Reported effect |
|---|---|---|
| **ABCD** ([Churchill et al. 2012](https://ojs.aaai.org/index.php/AIIDE/article/view/12527)) | Alpha-beta with durative moves; scripts order moves and evaluate playouts | Beats scripts up to 8v8 |
| **UCTCD**, **PGS** ([Churchill & Buro, CIG 2013](https://experts.mcmaster.ca/scholarly-works/1941877), DOI 10.1109/cig.2013.6633643) | PGS starts every unit on a seed script. It then hill-climbs one unit at a time over the portfolio, scoring each candidate assignment by a playout, and alternates between the two players. | PGS beats alpha-beta and UCT up to 50v50 at 40 ms per decision |
| **POE**, Portfolio Online Evolution ([Wang et al. AIIDE 2016](https://ojs.aaai.org/index.php/AIIDE/article/view/12862)) | Evolves the unit→script assignment | Beats PGS 0.76–1.00 in Lelis's table |
| **PGS+** ([Lelis 2017](https://www.ijcai.org/proceedings/2017/522)) | Same search as PGS, but the **evaluation** plays the candidate script for the **first** action only, then NOKAV to the end | Beats PGS 0.72–1.00 and usually beats POE. **Changing only the evaluation turns the search from losing to winning.** The original evaluation assumes a chosen script runs forever, which wrongly scores non-offensive scripts such as Cluster. |
| **SSS / SSS+**, Stratified Strategy Selection ([IJCAI 2017](https://www.ijcai.org/proceedings/2017/522)) | Partitions units into **types**; all units of a type share a script; searches over types. SSS+ adapts the granularity to the time left. | With more than 16 units: SSS beats PGS 0.90–1.00, POE 0.92–1.00 and PGS+ 0.67–0.92. Example: Zea 8/Dra 8, SSS beats POE 0.92. Up to 56 units per side; 1,000 matches per cell; 40 ms per decision. |
| **GAB / SAB**, Asymmetric Action Abstraction ([Moraes & Lelis AAAI 2018](https://arxiv.org/abs/1711.08101)) | Most units are restricted to script moves. **A few units** (best: the N with the highest attack value dpf/hp, "AV+") get the **full action set**, searched by alpha-beta. | GAB beats PGS 0.82 (Zea 8/Dra 8) and 0.81 (32 Zea); SAB beats SSS 0.90 (50 Zea); the best N was about 4 |
| **Puppet Search** ([Barriga, Stanescu & Buro AIIDE 2015](https://ojs.aaai.org/index.php/AIIDE/article/view/12779)) | Scripts expose **choice points**; search sets them | Matches or beats every script it contains |
| **NaiveMCTS** ([Ontañón AIIDE 2013](https://ojs.aaai.org/index.php/AIIDE/article/view/12681); [JAIR 2017](https://arxiv.org/abs/1710.04805)) | MCTS whose action sampling treats each unit as an arm of a combinatorial bandit | Better than other MCTS variants as the branching factor grows. In microRTS it is a baseline that portfolio methods usually beat. |
| **FRGS** ([Clark & Fleshner AIIDE 2017](https://ojs.aaai.org/index.php/AIIDE/article/view/12955)) | Small-population GA over script assignments | 200v200 within 40 ms |

**The critical lesson on model accuracy.** [Churchill, Lin & Synnaeve 2017](https://ojs.aaai.org/index.php/AIIDE/article/view/12962) put PGS into real StarCraft and found that "performance of PGS relies heavily on the accuracy of the underlying model":
- PGS won everything inside SparCraft.
- It lost in the real engine wherever SparCraft lacked collisions.
- A 10-ms limit was as good as 40 ms, because model error, not search time, was the bottleneck.

**[inference]** Our engine clones its own exact state. This removes the main failure mode of the whole portfolio literature. The remaining model errors for us:
- the enemy's response, which is exact if we roll out the engine's own scripted AI at the drawn tactic and skill;
- random draws such as dodge rolls, which call for several seeds per playout or common random numbers.

### 2.3 Learned multi-agent RL on SMAC

| Item | What the sources show |
|---|---|
| **Setting** | [SMAC](https://ar5iv.labs.arxiv.org/html/1902.04043) scenarios are against the built-in AI at "level 7, very difficult" |
| **Reward** | Damage dealt + 10 per kill + 200 per win; own losses ignored by default |
| **QMIX test win %** | MMM2 69, 27m_vs_30m 49, corridor 1, 6h_vs_8z 3 ([SMAC appendix](https://ar5iv.labs.arxiv.org/html/1902.04043)) |
| **Cost** | 8–16 GPU-hours per run |
| **MAPPO** | Matches or beats QMIX on most maps, up to 10 M steps ([Yu et al.](https://arxiv.org/abs/2103.01955); [BAIR summary](https://bair.berkeley.edu/blog/2021/07/14/mappo)) |
| **Emergent behaviours** | Kiting in 3s_vs_5z (needs recurrent nets). BiCNet reports "move without collision", "hit and run", "cover attack" and "focus fire without overkill" ([Peng et al. 2017](https://arxiv.org/abs/1703.10069)). A baiting stalker that "backs out" at low HP in SMAClite 2s_vs_1sc ([SMAClite](https://arxiv.org/abs/2305.05566)). |
| **Caveat** | [SMACv2](https://arxiv.org/abs/2212.07489) shows SMAC policies can largely replay fixed open-loop sequences |
| **Splash in SC2LE** | In DefeatZerglingsAndBanelings (marines must spread against splash), the best end-to-end agent scored **96** against **727–729** for humans ([SC2LE](https://ar5iv.labs.arxiv.org/html/1708.04782)). **Splash avoidance is among the hardest things for end-to-end RL to discover.** |

**[inference]** SMAC-class RL on a laptop CPU, at 50v50 with three roles, would mean a GPU-week-class effort for one doctrine. It would produce a black-box policy, against the project principle. Not recommended as a controller. A learned **selector over shapes** is the acceptable form (§3, §9).

### 2.4 Which give the most win-efficiency per compute, and which preserve units
- **Most gain per compute** (all in SparCraft at 40 ms per decision): type-level portfolio search (**SSS**) and asymmetric abstraction (**GAB/SAB**). The cheapest single large gain in the table is **PGS → PGS+**, which changes only the evaluation.
- **Explicit unit preservation:**
  - LTD2 rewards survivors (√hp sums).
  - The ECSLBot fitness counts units remaining.
  - [Liu et al.'s multi-objective follow-up](https://arxiv.org/abs/1803.10316) keeps a Pareto front of damage done against damage received.
  - Churchill 2017 observed that the **kiting script "cycl[es] low hit point units to the back lines, taking them out of range… causing units to stay alive much longer"** in simulation: emergent damaged-unit rotation, exactly the owner's rule. In the real engine it failed only because of collisions. **[inference]** Our engine models collisions, so a rotation shape can be judged directly by the clone.
- **No paper reports a "series with carried losses" metric.** Our yardstick is stricter than any benchmark found.

---

## 3. Learning from a teacher, per role ("copy best practice")

| Technique | Mechanism | Evidence | Fit for us |
|---|---|---|---|
| **Behaviour cloning (BC)** | Fit the policy to the teacher's (state, action) pairs on the teacher's own trajectories | RAI-BC copied the scripted Mayari: 71% overall, but only 44% against Mayari itself ([Goodfriend 2024](https://arxiv.org/html/2402.08112v1)). AlphaStar SL beat 84% of players. | Spec §9 "shadow actions, teacher in control" **is** BC data collection |
| **DAgger** ([Ross, Gordon & Bagnell 2011](https://arxiv.org/abs/1011.0686)) | Run **our** policy, have the teacher label the states we actually reach, aggregate, refit. This fixes compounding error (quadratic in horizon for BC, linear for DAgger). | Standard result. A 2026 Gin Rummy study found DAgger did *not* help there and blamed causal confusion ([arXiv 2607.06854](https://arxiv.org/html/2607.06854v1)). | Spec §9 "reverse comparison: our shape in control, teacher shadowed" **is** the DAgger state distribution. Keep it. |
| **AggreVaTe** ([Ross & Bagnell 2014](https://arxiv.org/abs/1406.5979)) | Imitation weighted by **cost-to-go**: what a deviation from the teacher costs, not merely whether it happened | Regret guarantee, stronger than error reduction | **[inference] Our clone makes this exact.** At a disagreement state, clone the state, play the teacher's action and ours for k seconds, and compare LTD2 or own-loss. This turns "agreement %" into "cost of disagreement", which is what matters. |
| **Comparison training / inverse scoring** ([Tesauro 1988](https://papers.neurips.cc/paper/1988/hash/a8baa56554f96369ab93e4f3bb068c22-Abstract.html); MMTO, [Hoki & Kaneko JAIR 2014](https://jair.org/index.php/jair/article/view/10871)) | Learn a **scoring function** so the teacher's choice outranks the alternatives. MMTO tuned more than 40 M shogi evaluation weights to match expert moves and won the 2013 World Computer Shogi Championship. | Strong in chess, shogi, backgammon | **Directly fits our shapes.** Gun focus is already a scoring function (splash value V). Fit V's weights so the teacher's chosen target ranks first: a ranking loss over candidate targets per shot. Same for posts and escort points. |
| **Privileged teacher → student** ([Learning by Cheating, Chen et al. CoRL 2019](https://arxiv.org/abs/1912.12294)) | A teacher with privileged information labels; the student lacks it | 100% success on the original CARLA benchmark | **[inference]** A search teacher that uses clone rollouts is "privileged"; a shape that cannot afford rollouts is the student. |
| **Search → policy distillation** ([ExIt](https://arxiv.org/abs/1705.08439); [Barriga et al. 2017](https://arxiv.org/abs/1709.03480)) | A CNN learns, from **Puppet Search labels**, which **script** to run. Leftover time goes to tactical search for units near the enemy. | Higher win rates in microRTS than either component alone | **Distil a search teacher into a shape selector.** Barriga's net picks a script, which is our gate's job. |
| **Credit per unit, "split the action and compare"** ([difference rewards](https://arxiv.org/pdf/2012.11258); [COMA](https://microsoft.com/en-us/research/wp-content/uploads/2017/03/Whiteson.pdf)) | D_i = G(z) − G(z with unit i's action replaced by a default) | The counterfactual "requires … a resettable simulator", which we have | **[inference]** Measure each shape's per-unit contribution exactly: replace one role's (or one unit's) shape action by the teacher's or by a null action in a clone, and replay. |

**Tool note.** [`imitation`](https://github.com/HumanCompatibleAI/imitation) (MIT, v1.0.1, Jan 2025) implements BC, DAgger, GAIL and AIRL for Gymnasium/PyTorch policies. Our "policies" are parameterised C++ shapes, so the library adds little. DAgger and BC on 11–50 shape parameters, or a small selector, are a few dozen lines with scikit-learn or LightGBM. **[inference]**

**Critical point on the owner's idea ("ideal runs").** The Astelia elite AI is a *good* teacher, not an *ideal* one.
- BC caps near the teacher: RAI-BC won only 44% against its own teacher.
- So "copy the elite" lifts each primitive *up to* the elite's level, which is still very valuable where we are far below it (shell dodging: 0 against about 2,940 per fight).
- **Going beyond** needs the T-search arm. That is the AlphaZero/ExIt step: search over shapes from the teacher's states, with the clone as the judge.

---

## 4. Search over shapes with the forward model

**Evidence that it beats fixed scripts:**
- PGS "outperformed all of its individual portfolio scripts" even in the inaccurate-model case ([Churchill et al. 2017](https://ojs.aaai.org/index.php/AIIDE/article/view/12962)).
- Puppet Search "matches or outperforms all of the individual scripts" ([AIIDE 2015](https://ojs.aaai.org/index.php/AIIDE/article/view/12779)).
- SSS reached 0.80–1.00 against the previous best searches with more than 16 units ([Lelis 2017](https://www.ijcai.org/proceedings/2017/522)).
- Online Evolution in Hero Academy "outperform[s]… by a large margin" ([Justesen et al. 2016](https://pure.itu.dk/en/publications/online-evolution-for-multi-action-adversarial-games/)).
- RHEA evolves action sequences, plays the first, then re-plans ([Gaina et al. 2020](https://arxiv.org/abs/2003.12331)).

**Design for us [inference, sized from the brief's throughput]:**
- **Types:** our three roles, optionally split by HP band (healthy/damaged), giving 3–6 types. This is SSS's type system; Lelis's best coarse system already used melee/ranged.
- **Portfolio per type:** 3–5 shapes. Examples:
  - guns: current focus V, NOKAV-style AV focus, hold volley for synchrony, relocate;
  - ranged: escort screen, kite, focus AV;
  - melee: v6 law, screen guns, rotate damaged.
- **Asymmetric layer (GAB):** the about 4 highest-value units, likely our guns, get a richer candidate set, such as target × aim point × move vector.
- **Evaluation (PGS+ style):**
  - play the candidate assignment for one decision interval, then a **fixed default** (our current shapes) to a horizon of about 5–10 s;
  - score by an own-loss-weighted LTD2;
  - roll the enemy with its real tactic and skill;
  - use 2–3 seeds or common random numbers.
- **Cost:** 6 types × 4 shapes is about 24 hill-climb playouts per pass. At 5–10 s each (150–300 ticks, about 0.02–0.1 core-s), one decision costs about 0.5–2.5 core-s. Re-planned every 1 s of game time, a 90-s fight takes about 45–225 core-s, roughly 100–500× a normal fight.
- **Throughput:** about 3–15 search-teacher fights per minute on 10 cores. That suits **offline ideal runs and label generation**, not mass tuning. Online use in the series is affordable only if restricted to guns (as the elite already does) or distilled (§3).

---

## 5. Quality-diversity repertoires and per-doctrine switching

- **MAP-Elites** ([Mouret & Clune 2015](https://arxiv.org/abs/1504.04909)) keeps the best solution per cell of a behaviour grid.
  - **CMA-ME** ([Fontaine et al. GECCO 2020](https://arxiv.org/abs/1912.02400)) fuses CMA-ES with MAP-Elites. On Hearthstone strategies it found higher quality *and* diversity than either CMA-ES or MAP-Elites.
  - **Repertoire + fast online selection:** [Cully et al. Nature 2015](https://arxiv.org/abs/1407.3501) (Intelligent Trial and Error) adapts from the map in a few trials.
  - **In strategy games:** MAP-Elites over portfolio-MCTS parameters gave distinct play styles in Tribes without losing strength ([Perez-Liebana et al. 2021](https://arxiv.org/abs/2104.08641)).
- **Strategy selection against an opponent:**
  - Treating the choice of bot/strategy as a metagame, and deviating from Nash to exploit weaker opponents, paid off ([Tavares et al. AIIDE 2016](https://ojs.aaai.org/index.php/AIIDE/article/view/12857)).
  - The MegaBot bot uses ε-greedy selection over bots per opponent ([survey](https://www.cs.mun.ca/~dchurchill/starcraftaicomp/2017/survey/MegaBot_Survey.txt)).
  - Opponent strategy classifiers from early observations: [Weber & Mateas CIG 2009](https://dblp1.uni-trier.de/rec/conf/cig/WeberM09.html).
- **[inference] For us:**
  - Our 19 doctrines are known and fixed, so a doctrine classifier from the first few seconds (formation shape, approach speed, whether raiders go for guns) is easy to label in the engine.
  - **But a repertoire only pays if the best knobs differ by doctrine.** Test that first with a cheap cross-table: tune per doctrine, then cross-evaluate. If the off-diagonal loss is small, one robust setting suffices and QD adds complexity for nothing.
  - Behaviour descriptors that fit our goals: gun standoff distance, and ranged screen depth against aggression.

---

## 6. Hard-opponent weighting without full RL

- **PFSP** ([AlphaStar](https://deepmind.google/discover/blog/alphastar-grandmaster-level-in-starcraft-ii-using-multi-agent-reinforcement-learning/); definition in [arXiv 2408.01072](https://arxiv.org/pdf/2408.01072)): sample opponent B with probability ∝ f(P[A beats B]).
  - f_hard(x) = (1−x)^p focuses on the hardest;
  - f_var(x) = x(1−x) on the even matches.
  - **Our version:** weight the 76 (doctrine × skill) cells by our current loss rate, or better by expected own losses, when composing each CMA-ES evaluation batch.
- **The past-self mix** (OpenAI Five's 80/20) and the **hall of fame** ([Rosin & Belew 1997](https://www.cs.utexas.edu/users/nn/downloads/papers/lubberts.coevolution-gecco01.pdf), as summarised). In RTS micro, co-evolution with fitness sharing, shared sampling and a hall of fame produced better micro faster ([Liu et al. 2018](https://arxiv.org/abs/1803.10314)). For us: keep the earlier champions (v6, v7…) as regression opponents in *self-play drills*, not only the scripted pool.
- **Curriculum by learning potential:** [Prioritized Level Replay](https://arxiv.org/abs/2010.03934) samples training "levels" by estimated learning potential and gets an emergent easy-to-hard curriculum. Our "levels" are (doctrine, skill, seed) cells.
- **Noise handling, needed because one fight is a noisy sample:**
  - UH-CMA-ES ([Hansen et al. IEEE TEC 2009](https://cs.utexas.edu/~shivaram/readings/b2hd-HansenNGK2009.html)) re-evaluates candidates and raises the step size when rank changes are noise-driven;
  - racing (irace, [López-Ibáñez et al. 2016](https://iridia.ulb.ac.be/irace/)) drops configurations early once they are statistically worse across instances;
  - paired seeds, i.e. common random numbers across candidates **[inference]**.
- **Main-exploiter analogue without RL [inference]:** run CMA-ES on the *enemy's* tactic parameters (formation spacing, raid timing, skill flags) to minimise our series streak. Then add the found settings to the evaluation pool as "exploiter cells". This copies AlphaStar's exploiters at script level. **Risk:** it can find enemy settings outside the owner's 19 doctrines. Report them separately; never mix them into the yardstick.

---

## 7. Tools (checked 2026-10-08 on PyPI and GitHub)

| Tool | Version, license | Fit | Verdict |
|---|---|---|---|
| [pycma](https://github.com/CMA-ES/pycma) | 4.5.0 (2026-09-13), BSD-3 | Pure Python, CPU. Has noise handling (`cma.NoiseHandler`, i.e. UH-CMA-ES) and a parallel ask/tell API. | **Keep.** Turn on noise handling and paired seeds. |
| [pyribs](https://pyribs.org) | 0.12.0 (2026-07-22), MIT | Python CPU QD: CMA-ME, CMA-MAE, MAP-Elites; ask/tell like pycma | **Adopt if** the per-doctrine cross-table (§5) shows real specialisation |
| [Optuna](https://optuna.org) | 5.0.0 (2026-09-07), MIT | Mixed categorical/continuous; pruners (successive halving/Hyperband); good for *choosing which shapes* (categorical) plus knobs | **Adopt for discrete shape-portfolio selection** and early stopping of bad configurations. CMA-ES stays for continuous knobs. |
| [Nevergrad](https://github.com/facebookresearch/nevergrad) | 1.0.12 (2025-04), MIT | Many noisy-optimisation algorithms, portfolio optimisers | Optional cross-check; overlaps pycma and Optuna |
| [irace](https://iridia.ulb.ac.be/irace/) | CRAN 4.x, GPL ≥2 | R; racing over instances | Optional. The idea (racing) is easy to do in Python; the R dependency is not worth it. |
| scikit-learn 1.9.1, LightGBM 4.7.0 | BSD / MIT | Small selectors, doctrine classifier, ranking loss (LGBMRanker) for comparison training | **Adopt** for BC/DAgger of the *selector* and for fitting scoring weights |
| [evosax](https://github.com/RobertTLange/evosax) 0.3.1, [EvoTorch](https://github.com/nnaisense/evotorch) 0.6.1, [QDax](https://github.com/adaptive-intelligent-robotics/QDax) 0.5.0 | Apache-2 / MIT | JAX/GPU-oriented; their speed advantage needs a JAX-native environment | **Skip.** The cost is in our C++ fights, not the optimiser. |
| [neat-python](https://github.com/CodeReclaimers/neat-python) 2.0.0 | BSD-3 | Evolves network topologies | **Skip:** opaque networks conflict with the shapes principle |
| [PettingZoo](https://pettingzoo.farama.org) 1.27, [RLlib](https://docs.ray.io) (ray 2.59), [CleanRL](https://github.com/vwxyzjn/cleanrl) (PyPI 1.2.0 is from 2023; use from source), MAPPO ([on-policy repo](https://github.com/marlbenchmark/on-policy)) | MIT / Apache | Need a Python env wrapper around the C++ engine; GPU-hungry for 100-agent PPO | **Defer.** Only if a learned *shape selector* via RL becomes the bottleneck after BC/ExIt. |
| [imitation](https://github.com/HumanCompatibleAI/imitation) 1.0.1, [d3rlpy](https://github.com/takuseno/d3rlpy) 2.8.1 | MIT | Neural-policy imitation and offline RL | **Skip:** our policy is not a torch net; BC/DAgger on shapes is simpler by hand |
| [OpenSpiel](https://github.com/google-deepmind/open_spiel) 2.0.2 | Apache-2 | MCTS, PSRO, alpha-zero for turn-based games | **Read, do not adopt.** Simultaneous 100-unit real-time play does not fit its game API without heavy abstraction. PSRO is the formal version of our opponent-pool idea. |
| [SparCraft](https://github.com/davechurchill/SparCraft) / [UAlbertaBot](https://github.com/davechurchill/ualbertabot) (MIT), [microRTS](https://github.com/Farama-Foundation/MicroRTS) (GPL-3.0) | C++ / Java | Reference implementations of PGS, SSS-type portfolios, NOKAV, Kiter, LTD2 | **Read for the algorithms** (port PGS+/SSS logic into our C++). Do not vendor microRTS code (GPL). |

---

## 8. Low-loss victory techniques: size of effect

| Technique | Evidence and size | Note for us |
|---|---|---|
| **Concentration of force** | Lanchester's square law: aimed-fire strength ∝ N², so early kills compound ([Stanescu et al. AIIDE 2015](https://ojs.aaai.org/index.php/AIIDE/article/view/12780) fit Lanchester models to StarCraft battles; [explainer](https://win-vector.com/2010/09/17/lanchesters-law-why-small-advantages-swell-in-starcraft/)) | Why focus fire and kill speed matter more than spreading damage |
| **Focus fire with overkill avoidance** | 15v16 marines, 1,000 battles ([Usunier et al. ICLR 2017](https://ar5iv.labs.arxiv.org/html/1609.02993)): attack-weakest **0.10**; with no-overkill **0.68**; attack-closest **0.81**; learned ZO **0.79**. In 15v17 wraiths: 0.02 / 0.12 / 0.20 / 0.49. | Naive focus fire **collapses** at scale because of overkill and crowding. No-overkill is necessary but not sufficient; the best rule is scenario-dependent, which argues for search or selection over a portfolio. |
| **Target priority by threat/HP** | NOKAV (attack value = dpf/hp) is the default in the strongest SparCraft searches. Furtak & Buro derive optimal kill orderings for 1-vs-n attrition games ([AIIDE 2010](https://ojs.aaai.org/index.php/AIIDE/article/view/12410)). | Our gun focus by splash value V is a different, splash-aware score. Compare V against AV+splash in the clone. |
| **Kiting / hit-and-run** | Learned in SMAC 3s_vs_5z; influence-map kiting ([Uriarte & Ontañón AIIDE 2012](https://ojs.aaai.org/index.php/AIIDE/article/view/12544)); ECSLBot beat Nova and UAlbertaBot on "kiting efficiency" | Relevant for ranged (reach 280) against melee (reach 64) |
| **Damaged-unit rotation** | The kiting script cycled low-HP units to the back and units "stay[ed] alive much longer" ([Churchill et al. 2017](https://ojs.aaai.org/index.php/AIIDE/article/view/12962)); ECSLBot "knowing when to flee to survive"; SMAClite baiter backs out at low HP | Copy the engine's `saveWounded` (backs away, stays near), per spec §10. This respects the owner's never-leave rule. |
| **Splash management and spreading** | End-to-end RL scored 96 against 727–729 for humans on the marine-vs-baneling mini-game ([SC2LE](https://ar5iv.labs.arxiv.org/html/1708.04782)). Potential-field unit control is an established hand-built alternative ([Hagelbäck](https://ojs.aaai.org/index.php/AIIDE/article/view/12365)). Whether his fields include a splash-specific friendly-repulsion term was **not verified**. | **Hand-built spacing and react shapes beat waiting for learning to find them.** Our data: artillery causes 74% of our deaths, and we make 0 shell dodges against the enemy's about 2,940 (spec §10). This is the single largest known gap. |
| **Damage dealt against received, as a trade-off** | Multi-objective evolution gives a Pareto front of micro ([Liu et al. 2018](https://arxiv.org/abs/1803.10316)) | Tune on own losses explicitly, not on win rate |

---

## 9. Ranked plan: top 5 to adopt

The ranking weighs expected effect on the **series** (losses carry over) against laptop cost and risk. Each item keeps shapes as the unit of behaviour; learning and search only fit, select or compose them.

### 1. Copy the teacher, per role and per primitive: shadow actions, DAgger and cost-weighted disagreement
- **What:**
  - Run the spec §9 teacher arm (T-elite) in the per-role drills, with our shapes shadowed. This is BC data.
  - Run the reverse arm (ours in control, teacher shadowed). This is DAgger data.
  - At each large disagreement, use the **clone** to replay the teacher's action against ours for a few seconds. Record the loss difference: the AggreVaTe-style cost of disagreement.
  - Fit each shape's own scoring weights so the teacher's choice ranks first (comparison training / MMTO style), weighted by that cost.
  - **First primitive:** react (shell dodge), then rotate (`saveWounded`), then aim (`lead`), as in spec §10.
- **Copies:** AlphaStar's and AlphaGo's supervised stage, plus DAgger, AggreVaTe and Tesauro/MMTO comparison training.
- **Expected gain and why:** Biggest where we are furthest below the teacher, and the data name it: artillery causes 74% of our deaths, with 0 dodges against about 2,940. Copying gets us **up to** elite level per primitive (RAI-BC precedent), not beyond.
- **Cost:** shadowing costs about one extra controller evaluation per tick, so drills run at near full speed. Fitting is seconds to minutes with scikit-learn or LightGBM.
- **Risk:**
  - "Agreement %" can reward copying irrelevant habits. Weight by the clone-measured cost.
  - Elite-level is a ceiling.
  - The Gin Rummy study's DAgger failure (causal confusion) is a warning: imitate actions conditioned on the features the shape actually uses.
- **Shapes kept:** Yes. The output is either refitted weights of an existing shape, or a new named shape that cites its source (the engine rule).

### 2. A search teacher over shapes (T-search): SSS/PGS+ with an asymmetric gun layer, using the engine clone
- **What:**
  - Offline "ideal runs": at each decision point, search over the per-type (role × HP band) shape assignment by hill-climbing (SSS).
  - Give the about 4 highest-value units (likely guns) a wider candidate set (GAB).
  - Evaluate with PGS+ playouts: candidate for one interval, then current shapes, a 5–10 s horizon, an own-loss-weighted LTD2, the enemy's real tactic and skill, and 2–3 seeds.
- **Copies:** Churchill & Buro PGS, Lelis SSS, Moraes & Lelis GAB, and the search half of AlphaGo/AlphaZero.
- **Expected gain and why:** In SparCraft, type-level and asymmetric search beat the previous best searches at 0.8–1.0. Searches always beat their own fixed scripts. The literature's main failure, model inaccuracy, is absent for us because we clone the real engine.
- **Cost [inference]:** about 100–500× a normal fight, so a few teacher fights per minute on 10 cores. That suits drills and label generation, not tuning loops.
- **Risk:**
  - Horizon and evaluation choices dominate: the PGS→PGS+ evaluation change alone flipped the outcomes.
  - Myopic playouts can undervalue rotation and spacing, whose payoff is late. Test the horizon.
  - A search that exploits engine details can hit a cap set by its RNG.
- **Shapes kept:** Yes. Search only *assigns* shapes; it never emits raw actions, except the small asymmetric layer, which should itself be a parameterised "aim/move" shape.
- **Answers the owner's idea:** This is the "ideal run" beyond the elite. Its per-role good-work numbers become the reference line, and spec §9's split-and-compare runs against it.

### 3. Distil the search teacher into a cheap shape selector (expert iteration)
- **What:** Use T-search's per-state choices as labels. Fit a small, readable selector, such as a decision tree or gradient-boosted trees on a handful of features (role, HP fraction, nearest-threat distance, incoming shells, enemy doctrine), that picks the shape. It replaces or conditions the oscillator gate. Iterate: the next search starts from the distilled selector as its default.
- **Copies:** AlphaZero / ExIt policy distillation; Barriga et al. 2017 (CNN picks scripts from Puppet Search labels).
- **Expected gain and why:** Most of the search's benefit at a normal fight's cost, which makes it usable in the 10-fight series and in CMA-ES loops.
- **Cost:** one batch of T-search drills, then minutes to fit.
- **Risk:** The selector's state distribution shifts once it controls play. Use DAgger rounds with T-search as the labeller (as in item 1). The gate must remain interpretable.
- **Shapes kept:** Yes. The selector chooses among named shapes, and its rules are inspectable.

### 4. Series-aware, noise-aware tuning against a weighted opponent pool (PFSP-lite)
- **What:**
  - The CMA-ES fitness is own losses per fight plus a series-streak simulator (dead stay dead), not single-fight win rate.
  - Sample (doctrine, skill) cells by PFSP f_hard on current expected losses.
  - Keep earlier champions (hall of fame) as regression checks.
  - Use paired seeds and pycma's noise handling.
  - Use racing (Optuna pruners) to drop bad candidates early.
  - Optionally add a script-level "exploiter" search over enemy parameters, reported separately from the owner's yardstick.
- **Copies:** AlphaStar PFSP and exploiters; the OpenAI Five past-self mix; Rosin & Belew's hall of fame; UH-CMA-ES; irace racing; ECSLBot's units-remaining fitness.
- **Expected gain and why:**
  - Aligns the optimiser with the yardstick. Today's 80%-win AI that loses 41/50 shows the current objective rewards costly wins.
  - Focusing on hard cells removes the weakest link, and one loss ends a streak.
- **Cost:** the same fight budget as today, with better spent samples.
- **Risk:**
  - Over-weighting hard cells can trade away easy-cell margins. Keep an f_var floor.
  - Exploiter cells must not leak into the yardstick.
- **Shapes kept:** Yes; this only changes how knobs are scored and sampled.

### 5. Doctrine-aware repertoire, only if specialisation is real (MAP-Elites/CMA-ME and an early doctrine classifier)
- **What:**
  1. First run the cross-table (tune per doctrine group, cross-evaluate).
  2. If off-diagonal losses are material, build a pyribs CMA-ME archive over 2 behaviour descriptors (e.g. gun standoff, screen depth).
  3. Add a classifier from the first seconds of a fight that picks the archive cell.
- **Copies:** Cully et al. repertoire adaptation; Tavares metagame strategy selection; Weber & Mateas strategy prediction; the diversity aim of the AlphaStar league.
- **Expected gain and why:** Specialised responses to raids on artillery against lines and boxes. The literature shows exploiting a known opponent beats one Nash-like policy (Tavares).
- **Cost:** QD needs roughly 5–20× a single CMA-ES run's evaluations [inference]; the classifier is cheap.
- **Risk:** Wasted effort if one robust setting already sits near the per-doctrine optima. A misclassification early in a fight can be worse than a robust default, so include a fallback cell.
- **Shapes kept:** Yes. Each archive cell is a knob vector for the same shapes.

### What does NOT transfer, and why
- **End-to-end deep RL controllers** (AlphaStar, OpenAI Five, MAPPO/QMIX at 50v50):
  - compute in GPU-weeks to TPU-months;
  - black-box policies against the project principle;
  - SMAC's default reward ignores own losses;
  - splash avoidance is exactly where end-to-end RL lagged humans by about 7× (SC2LE).
- **MuZero-style learned models:** we have the exact simulator; a learned model only adds error.
- **Human-replay imitation:** there are no human replays. The engine's elite AI and a search teacher replace them.
- **Leagues of learning agents:** our opponent is a fixed scripted pool. Only the *sampling* idea (PFSP) and *script-level* exploiters transfer.
- **NEAT and neural QD controllers:** they produce opaque behaviour.
- **SparCraft-tuned scripts as-is:** SparCraft has no collisions, no splash-dodging and no lobbed shells. Copy the algorithms (PGS+, SSS, NOKAV, LTD2), not the tuned behaviours.

### Order of work suggested for B8 [inference]
1. Item 1 with the **react** primitive (already the spec's first change).
2. Item 4's fitness change, so later tuning measures the right thing.
3. Item 2 as a drill-only teacher.
4. Item 3 to make it cheap.
5. Item 5 only after the cross-table.

Each step is one labelled change, measured in the drill and in the series, per spec §9–§10.

---

## Source list (primary links used above)
- AlphaGo: https://research.google/pubs/mastering-the-game-of-go-with-deep-neural-networks-and-tree-search/
- AlphaStar: https://deepmind.google/discover/blog/alphastar-grandmaster-level-in-starcraft-ii-using-multi-agent-reinforcement-learning/ ; AlphaStar Unplugged https://arxiv.org/abs/2308.03526 ; PFSP definition https://arxiv.org/pdf/2408.01072
- OpenAI Five: https://arxiv.org/abs/1912.06680
- KataGo: https://arxiv.org/abs/1902.10565 ; ExIt: https://arxiv.org/abs/1705.08439 ; Gumbel: https://iclr.cc/virtual/2022/poster/6418 ; MuZero: https://arxiv.org/pdf/1911.08265 ; EfficientZero: https://arxiv.org/abs/2111.00210
- PGS: https://experts.mcmaster.ca/scholarly-works/1941877 ; PGS in StarCraft: https://ojs.aaai.org/index.php/AIIDE/article/view/12962 ; ABCD/LTD2: https://ojs.aaai.org/index.php/AIIDE/article/view/12527
- SSS: https://www.ijcai.org/proceedings/2017/522 ; GAB/SAB: https://arxiv.org/abs/1711.08101 ; POE: https://ojs.aaai.org/index.php/AIIDE/article/view/12862 ; Puppet Search: https://ojs.aaai.org/index.php/AIIDE/article/view/12779 ; FRGS: https://ojs.aaai.org/index.php/AIIDE/article/view/12955
- NaiveMCTS: https://ojs.aaai.org/index.php/AIIDE/article/view/12681 , https://arxiv.org/abs/1710.04805
- Strategic learning + tactical search: https://arxiv.org/abs/1709.03480
- RAISocketAI: https://arxiv.org/html/2402.08112v1 ; programmatic strategies: https://ojs.aaai.org/index.php/AAAI/article/view/16114 ; 2L: https://arxiv.org/abs/2307.04893
- SMAC: https://ar5iv.labs.arxiv.org/html/1902.04043 ; SMAC code: https://github.com/oxwhirl/smac ; MAPPO: https://arxiv.org/abs/2103.01955 ; BiCNet: https://arxiv.org/abs/1703.10069 ; SMAClite: https://arxiv.org/abs/2305.05566 ; SMACv2: https://arxiv.org/abs/2212.07489 ; SC2LE: https://ar5iv.labs.arxiv.org/html/1708.04782
- Usunier et al. (focus fire table): https://ar5iv.labs.arxiv.org/html/1609.02993
- ECSLBot: https://www.cse.unr.edu/~simingl/papers/publish/CIG2014IMPFMicro.pdf ; multi-objective micro: https://arxiv.org/abs/1803.10316 ; co-evolved micro: https://arxiv.org/abs/1803.10314
- Kiting with influence maps: https://ojs.aaai.org/index.php/AIIDE/article/view/12544 ; Lanchester in StarCraft: https://ojs.aaai.org/index.php/AIIDE/article/view/12780 ; attrition games: https://ojs.aaai.org/index.php/AIIDE/article/view/12410 ; potential fields: https://ojs.aaai.org/index.php/AIIDE/article/view/12365
- DAgger: https://arxiv.org/abs/1011.0686 ; AggreVaTe: https://arxiv.org/abs/1406.5979 ; Learning by Cheating: https://arxiv.org/abs/1912.12294 ; comparison training: https://papers.neurips.cc/paper/1988/hash/a8baa56554f96369ab93e4f3bb068c22-Abstract.html ; MMTO: https://jair.org/index.php/jair/article/view/10871 ; difference rewards: https://arxiv.org/pdf/2012.11258 ; Gin Rummy lightweight-agent study: https://arxiv.org/html/2607.06854v1
- MAP-Elites: https://arxiv.org/abs/1504.04909 ; CMA-ME: https://arxiv.org/abs/1912.02400 ; Cully et al.: https://arxiv.org/abs/1407.3501 ; Tribes play styles: https://arxiv.org/abs/2104.08641 ; Rock-Paper-StarCraft: https://ojs.aaai.org/index.php/AIIDE/article/view/12857 ; Weber & Mateas: https://dblp1.uni-trier.de/rec/conf/cig/WeberM09.html
- PLR: https://arxiv.org/abs/2010.03934 ; UH-CMA-ES: https://cs.utexas.edu/~shivaram/readings/b2hd-HansenNGK2009.html ; irace: https://iridia.ulb.ac.be/irace/ ; RHEA: https://arxiv.org/abs/2003.12331 ; Online Evolution: https://pure.itu.dk/en/publications/online-evolution-for-multi-action-adversarial-games/
- Tools: https://github.com/CMA-ES/pycma , https://pyribs.org , https://optuna.org , https://github.com/facebookresearch/nevergrad , https://github.com/HumanCompatibleAI/imitation , https://github.com/google-deepmind/open_spiel , https://github.com/davechurchill/SparCraft , https://github.com/Farama-Foundation/MicroRTS

**Verification limits:**
- These figures come from secondary summaries:
  - AlphaStar's compute (44 days, 32 TPUs) and the f_hard exponent;
  - OpenAI Five's 80/20 split;
  - the AlphaGo 57% figure.
- The PGS 2013 PDF could not be fetched (404); its claims are taken from the abstract-level record and from the SSS and 2017 PGS papers, which were read in full text.
- No project code was run.
