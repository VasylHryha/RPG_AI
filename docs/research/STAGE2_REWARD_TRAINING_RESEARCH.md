# Stage B and stage 2 research: imitation repair, reward training, growth, league, resonator nets, throughput

**Status:** research note for decision 0038 (stage B, then reward training without the teacher, then growth) and its addendum. It does not authorize any run.

**Ground rules:**
- No project code, fight, benchmark or pilot was run for this note.
- Every external claim carries a link and a year.
- Statements marked **[inference]** are this note's reasoning applied to our setting, not a source's finding.
- Statements marked **[unverified]** come from memory of the paper and were not re-checked against the primary text in this session.
- Our numbers used in the arithmetic: 50v50 fights of 150 s; about 4 s per fight for scripts and about 20 s per fight per worker for networks; 8 to 12 CPU cores; Python/PyTorch training; C++ engine with native inference.

**Date:** 2026-10-09. **Drafter family:** Claude.

---

## Summary

### What to adopt

1. **Repair imitation before any reward training.** Our teacher is a script, so labels are free at every state. That makes DAgger (teacher labels on states the network visits) the cheapest and strongest fix we have. Run 5 to 10 DAgger rounds, all 50 units labelled every decision. Add DART-style noise to the teacher's own rollouts as a cheap complement.
2. **Treat "fire" as a structured, masked, calibrated decision, not a rare class in one softmax.** Use a separate fire head or a target head with an invalid-action mask (no target in range or weapon on cooldown means fire is masked out). Weight or logit-adjust the loss for the rare class. Then calibrate the threshold so the closed-loop fire rate matches the teacher's fire rate in the same situations. Report per-class recall and closed-loop fire rate, not offline accuracy.
3. **Check for the copycat problem.** If the input contains the unit's own previous action or a long history, the network can learn "repeat what I did" instead of "fire when the teacher would". Ablate the previous-action input and compare closed-loop results.
4. **Use ES as fine-tuning of the stage-B network, not as training from scratch.** Recent work fine-tunes billion-parameter models with a population of only 30 because it starts from a strong initialisation. Our networks (10k to 200k parameters) are well inside the range where OpenAI-ES or PGPE work. Use antithetic (mirrored) pairs, common random numbers (both members of a pair fight the same scenario seed), centred-rank fitness shaping, and small noise.
5. **Keep a teacher anchor that decays.** Fine-tuning from imitation fails mainly by forgetting what was imitated. Add a decaying penalty for disagreement with the teacher on a fixed state buffer (computed offline, it costs no fights), in the style of AlphaStar's and VPT's KL term (VPT: coefficient 0.2, multiplied by 0.9995 every iteration).
6. **Write the fitness as a lexicographic order and let rank shaping do the rest:** win first, then own units saved, then kills, then speed. With rank-based shaping only the order matters, so the scale fights between terms disappear. Treat a timeout as worse than any win and score it by the HP differential so a stalemate is never a safe harbour.
7. **Run the curriculum mostly at 10v10.** It is several times cheaper per fight, and multi-agent work that scales agent counts (EPC, multiagent HyperNEAT) trains small first and grows. Test transfer to 50v50 without retraining as an explicit outcome.
8. **Minimum viable league:** the scripted doctrines plus a pool of 5 to 10 frozen snapshots, sampled with prioritised fictitious self-play ("hardest first", weight (1 - win rate)^p, p about 1 to 2), with a held-out set of opponents that is never trained against.
9. **Grow networks function-preservingly.** New units get zero outgoing weights (the output is unchanged) and small non-zero incoming weights (so the next perturbation or gradient can make them useful). Protect new structure for a few generations, which is what NEAT's speciation does.
10. **Make throughput cheap first:** one batched inference call per tick for all units (and for all fights in a worker), a decision cadence of about 0.25 to 0.5 s with actions held in between, one thread per worker, and a bounded neighbour count in the observation.

### What to avoid

- Training any of the three architectures from scratch with ES at 50v50. At our throughput this is tens of hours per arm with no evidence it converges. **[inference]**
- Judging stage B by offline accuracy. SMACv2 showed that open-loop policies (conditioned on time only) win many original SMAC scenarios, so high offline agreement can hide a policy that does not react. ([Ellis et al. 2023](https://arxiv.org/abs/2212.07489))
- Fitness made of a single binary win. It is too noisy per fight; ES needs a graded signal.
- Raw per-connection NEAT on a 50k-parameter network. NEAT's direct encoding has never been shown to scale to that size; use block-level growth instead.
- Non-potential shaping bonuses that can be farmed (for example "damage dealt" without bound, or "survival time"), and a time penalty large enough to reward suicidal rushes.
- Several PyTorch threads per worker on top of several workers (oversubscription).

### Open questions

- Does the resonator net have any measurable edge at all? The literature has **no** evidence that oscillator networks beat attention or GRU networks on multi-agent control. The most plausible places for an edge are coordination timing (synchronised volleys), grouping of units by phase, robustness to noise and distribution shift, and transfer across army sizes. These must be measured, not assumed.
- Is ES or PPO the better second-stage learner for us? There is no head-to-head ES-versus-MAPPO study on SMAC. Our back-of-envelope estimate (Section 1) puts them in the same order of fights. A small PPO-with-teacher-KL arm would tell us whether our ES result is an ES limit or a task limit.
- How much does fight cost drop from 50v50 to 10v10 in our engine? This sets the whole curriculum budget and has to be measured.

---

## 1. ES (OpenAI-ES, CMA-ES variants, PGPE) versus PPO, MAPPO and IPPO for cooperative unit micro

### What the sources say

**PPO family on SMAC.**
- MAPPO and IPPO match or beat QMIX on most SMAC maps at the same number of samples, and MAPPO matches or beats RODE on 10 of 14 maps. The authors stress low data reuse (15 epochs on easy tasks, 10 or 5 on hard ones) because more reuse worsens non-stationarity. ([Yu et al., "The Surprising Effectiveness of PPO in Cooperative Multi-Agent Games", NeurIPS 2022 Datasets and Benchmarks; arXiv 2021](https://arxiv.org/abs/2103.01955))
- Typical SMAC budgets in that paper are a few million to about 10 million environment steps per map, more on the hardest maps. **[unverified: exact per-map budgets are in the appendix]**
- Independent PPO with a shared policy is already strong on SMAC with little tuning. ([de Witt et al., "Is Independent Learning All You Need in the StarCraft Multi-Agent Challenge?", 2020](https://arxiv.org/abs/2011.09533))
- On SMACv2, MAPPO and IPPO perform almost identically, so the centralised critic adds little there. QMIX is more sample-efficient but needs much more memory. MAPPO was still improving at the end of training on the 20v20 maps. ([Ellis et al., "SMACv2", NeurIPS 2023](https://arxiv.org/abs/2212.07489))
- SMAC's reward and setup: shaped reward from damage dealt, plus 10 per enemy killed and 200 for a win, scaled so the maximum episode return is about 20. Sight range 9, shooting range 6. ([Samvelyan et al., "The StarCraft Multi-Agent Challenge", 2019](https://arxiv.org/abs/1902.04043))

**ES.**
- OpenAI-ES communicates only scalars (fitness values plus shared random seeds), which lets it scale to over a thousand workers. It solved 3D humanoid walking in 10 minutes and reached competitive Atari scores in one hour. It is invariant to action frequency and delayed rewards and needs no discounting or value function. ([Salimans et al., "Evolution Strategies as a Scalable Alternative to Reinforcement Learning", 2017](https://arxiv.org/abs/1703.03864))
- The same paper reports that ES used roughly 3 to 10 times more environment steps than TRPO on MuJoCo. The humanoid run used about 1,440 CPUs. **[unverified]**
- A plain genetic algorithm evolved networks with over 4 million parameters and trained Atari in about 4 hours on one desktop. ([Such et al., "Deep Neuroevolution", 2017](https://arxiv.org/abs/1712.06567))
- **ES from a strong initialisation needs a small population.** Full-parameter ES fine-tuning of billion-parameter language models used population N = 30, noise sigma = 0.001, learning rate 5e-4, z-scored rewards per iteration, and 500 to 1,000 iterations. The authors report less reward hacking and more stable runs than RL. ([Qiu et al., "Evolution Strategies at Scale: LLM Fine-Tuning Beyond Reinforcement Learning", 2025](https://arxiv.org/abs/2509.24372))
- Low-rank perturbations (EGGROLL) cut ES memory and compute for big matrices and match plain OpenES on RL tasks, including multi-agent ones. This matters only if our networks grow large. ([Sarkar et al., "Evolution Strategies at the Hyperscale", 2025](https://arxiv.org/abs/2511.16652))
- PGPE samples one parameter vector per episode and keeps the controller deterministic during the rollout, which lowers gradient noise; symmetric (mirrored) sampling helped most. ([Sehnke et al., "Parameter-exploring policy gradients", Neural Networks 2010](https://ei.is.mpg.de/publications/6154))
- ClipUp (momentum with gradient normalisation and update clipping) is a simpler optimiser than Adam for PGPE and is insensitive to reward scale. ([Toklu et al., "ClipUp", PPSN 2020](https://arxiv.org/abs/2008.02387))
- evosax's Brax benchmarks used population 256 for OpenAI-ES, PGPE, SNES and Sep-CMA-ES with centred-rank fitness shaping. ([Lange, "evosax", 2022](https://arxiv.org/abs/2212.04180)) A separate benchmark found larger populations always helped. ([NeuroEvoBench, 2023](https://arxiv.org/abs/2311.02394))
- Full CMA-ES keeps a covariance matrix whose cost grows with the square of the parameter count; it is practical up to a few thousand parameters. For 10k to 200k parameters use diagonal or low-rank variants (Sep-CMA-ES, SNES) or OpenAI-ES/PGPE. **[inference from the standard CMA-ES cost]**
- ES gets stuck on deceptive rewards; adding a novelty or quality-diversity term (NS-ES, NSR-ES) helps. ([Conti et al., NeurIPS 2018](https://arxiv.org/abs/1712.06560))
- **No head-to-head ES-versus-MAPPO study on SMAC or SMACv2 was found** in this search.

**Hybrids.**
- AlphaStar initialises every agent from supervised learning on human replays and keeps a KL term towards that supervised policy during RL. ([Vinyals et al., Nature 2019; DeepMind summary](https://deepmind.google/discover/blog/alphastar-grandmaster-level-in-starcraft-ii-using-multi-agent-reinforcement-learning/))
- VPT fine-tunes an imitation-trained policy with PPO plus a KL term: coefficient 0.2, multiplied by 0.9995 every iteration. Without the KL term the learning rate had to drop from 2e-5 to 3e-6 or the agent failed to learn even basic skills. ([Baker et al., "Video PreTraining", 2022](https://arxiv.org/abs/2206.11795))
- Fine-tuning a pre-trained policy mostly fails by forgetting: states not reached early in fine-tuning lose their pre-trained competence. Retention methods (behaviour-cloning loss, kick-starting, elastic weight consolidation) fix it and doubled the NetHack state of the art. ([Wołczyk et al., ICML 2024](https://arxiv.org/abs/2402.02868))
- MERL combines an evolutionary population optimising the sparse team reward with gradient learners on per-agent dense rewards. ([Khadka et al., "Evolutionary Reinforcement Learning for Sample-Efficient Multiagent Coordination", ICML 2020](https://arxiv.org/abs/1906.07315)) **[unverified link and details]**
- In a 2026 RTS result (Generals.io), a plain policy-gradient loop reached first place on a 5,000-player leaderboard on a modest budget without behaviour cloning, potential-based shaping or population self-play. ([Straka and Schmid, ICML 2026](https://icml.cc/virtual/2026/78760))

### What it means for us

**Budget arithmetic [inference].** With 10 workers at 20 s per 50v50 network fight, we get about 0.5 fights per second, or about 1,800 fights per hour.
- **ES:** a population of 64 (32 mirrored pairs) on 2 scenario seeds each costs 128 fights per generation, about 4 minutes. That gives about 14 generations per hour, or about 140 in a 10-hour night. This is enough for fine-tuning a good BC network, not for learning from scratch.
- **PPO:** one 50v50 fight at a 0.25 s cadence gives 600 decisions × 50 units = 30,000 per-unit samples per side. 10 million samples (a SMAC-scale budget) is about 330 fights, plus the extra fights needed because 50 units sharing one team reward give noisy per-unit credit. PPO's raw sample count is therefore not our bottleneck; its credit assignment across 50 units is.
- **At 10v10** both budgets stretch by the measured speed-up factor (to be measured; likely several times).

**ES is viable for us, with conditions:**
- Use it as fine-tuning: start from the stage-B network, with sigma small relative to each layer's weight scale (start around 0.01 to 0.02 of the layer RMS and tune). **[inference]**
- Parameter sharing is an advantage for ES: one perturbation moves all 50 units at once, and the fight result scores the whole team, so there is no per-unit credit problem. **[inference]**
- Control fitness noise. Evaluate both members of a mirrored pair on the same scenario seed (common random numbers), use at least 2 seeds per pair, and rank-shape. Re-evaluate the current mean policy on a fixed seed set every few generations to track real progress.
- ES does not need gradients, so it treats the plain net, the recurrent net and the resonator net identically. That is the main reason it suits a fair architecture comparison at equal fight budgets.

**Pitfalls to expect:**
- A noisy binary win signal (fix: graded lexicographic fitness, Section 4).
- Drift away from the teacher's competence (fix: decaying teacher anchor).
- Exploiting one fixed opponent (fix: opponent mix, Section 5).
- Per-layer scale mismatch, where one sigma is too large for small layers (fix: per-layer sigma).
- Overfitting to the training seeds (fix: held-out seeds).

**Hybrid options, ranked for us [inference]:**
1. ES on the BC network with a decaying teacher-agreement term in the fitness, plus periodic DAgger-style BC steps on states visited during ES (Lamarckian refresh).
2. PPO or IPPO with a shared policy and a decaying KL term to the BC network (AlphaStar and VPT style), as a reference arm that tells us whether ES is the limit.
3. MERL-style split: evolution on the team fitness, gradients on a dense per-unit signal. This is more engineering; keep it for later.

---

## 2. Neuroevolution with structural growth in modern practice

### What the sources say

- **NEAT and rtNEAT.** rtNEAT evolved growing networks in real time while the NERO game ran: a player trained a team of combat robots through exercises, then fought other players' teams. ([Stanley, Bryant and Miikkulainen, IEEE TEC 2005](https://www.cse.unr.edu/~bdbryant/papers/stanley-2005-tec.pdf)) This is the closest historical analogue to our project, at a much smaller network size.
- **TensorNEAT** puts whole NEAT populations into fixed-shape tensors and reports up to 500× speed-ups over NEAT-Python on a GPU (population 10,000, Brax tasks); the CPU gain is smaller. ([TensorNEAT, arXiv 2404.01817 (2024) and 2504.08339 (2025)](https://arxiv.org/abs/2504.08339))
- **NeuroPAL** (NEAT plus punctuated anytime learning) reached competitive StarCraft: Brood War macro play in about half NEAT's training time. ([2025](https://arxiv.org/abs/2506.10384))
- **Multiagent HyperNEAT.** One genome encodes a whole team through its "policy geometry" (each agent's policy depends on its position in the team). Teams trained small scaled to larger teams without further training. ([D'Ambrosio and Stanley, GECCO 2008](https://dx.doi.org/10.1145/1389095.1389256); [D'Ambrosio et al., AAMAS 2010](https://stars.library.ucf.edu/scopus2010/1663))
- **Function-preserving growth.** Net2Net widens a layer by copying a neuron and halving the outgoing weights, and deepens by inserting an identity layer, so the network computes the same function after growth. ([Chen, Goodfellow and Shlens, ICLR 2016](https://arxiv.org/abs/1511.05641)) **[unverified link]** GradMax adds neurons with zero outgoing weights (function unchanged) and picks the incoming weights by SVD to maximise the gradient reaching them. ([Evci et al., ICLR 2022](https://arxiv.org/abs/2201.05125))
- **Quality diversity.** MAP-Elites keeps the best solution per behaviour cell. Plain mutation-based MAP-Elites handles only small networks; PGA-ME and DCRL-ME add policy-gradient operators for large networks. ([Faldor et al., "Synergizing QD with Descriptor-Conditioned RL", 2024](https://arxiv.org/abs/2401.08632)) Combining MAP-Elites with several parallel ES emitters is another route. ([2023](https://arxiv.org/abs/2303.06137))
- **Evolution plus agent-count curriculum.** EPC grows the number of agents in stages (doubling each time) and evolves parallel populations at each stage, keeping the best adapted sets. ([Long et al., ICLR 2020](https://arxiv.org/abs/2003.10423))

### What it means for us

- **Grow by blocks, not by single connections [inference].** A NEAT mutation in our setting should be "add k hidden units to a layer", "add one oscillator with its couplings", or "add one coupling channel", not "add one connection". Classic NEAT innovation numbers are not needed when every individual shares the same architecture and differs only in weights.
- **Function-preserving initialisation.**
  - New units get zero outgoing weights, so the fight result does not change at the moment of growth.
  - New units get small random incoming weights. With all-zero incoming weights and a symmetric activation, a unit has nothing to work with and stays dead under ES as well. **[inference]**
  - Net2Net copying with halved outgoing weights also preserves the function and gives a better starting point, at the cost of symmetry between the two copies; add a little noise to break it.
  - For the resonator net, a new oscillator should start with zero coupling into existing oscillators and zero weight into the decision head.
- **Protect innovation.** NEAT protects new structure through speciation. The cheap equivalent for us: after growth, keep the grown candidate in the population for a fixed number of generations, or compare grown versus ungrown on the same seeds, before deciding.
- **Grow on a schedule tied to plateaus**, for example after N generations without improvement on held-out seeds, and decide by paired comparison (same seeds) at equal fight budgets. This keeps the "with growth versus without growth" comparison fair.
- **ES state after growth.** New parameters need their own sigma and optimiser state (momentum zero); keep old state for old parameters.
- **Use QD later, not first.** A MAP-Elites archive over simple behaviour descriptors (for example mean engagement distance and fraction of losses suffered by ranged units) is a good source of diverse league opponents (Section 5). It is not needed to get the first reward-trained network working.
- **Parameter-shared multi-agent policies and growth.** Growth changes every unit's network at once, which is exactly what we want for a shared policy. Multiagent HyperNEAT shows that position-dependent variation can be encoded as an input (role, position in formation) rather than as separate networks.

---

## 3. Fixing compounding error in behaviour cloning beyond DAgger

### What the sources say

- **DAgger:** run the learner, have the expert label the visited states, aggregate the labels and refit. It has a no-regret guarantee that plain BC lacks. ([Ross, Gordon and Bagnell, AISTATS 2011](https://arxiv.org/abs/1011.0686))
- **DART:** inject noise into the *expert's* own rollouts so the expert demonstrates recovery from perturbed states. The noise level is tuned to match the learner's error. It was up to 3× faster in computation than DAgger on Humanoid and lost only 5% of expert reward during collection, where DAgger rollouts lost 80%. ([Laskey et al., CoRL 2017](https://arxiv.org/abs/1703.09327))
- **Causal confusion:** more information can make BC worse, because the learner latches onto cues that correlate with the expert's action without causing it. Targeted interventions fix it. ([de Haan, Jayaraman and Levine, NeurIPS 2019](https://arxiv.org/abs/1905.11979))
- **Copycat problem:** with observation histories, the imitator learns to predict the expert's previous action instead of the next one, because expert actions are strongly correlated in time. A representation that removes previous-action information helps. ([Wen et al., NeurIPS 2020](https://arxiv.org/abs/2010.14876))
- **Action chunking:** predicting k future actions at once (with temporal ensembling of overlapping chunks) cuts the number of decision points and so the compounding, at some cost in reactivity. ([Zhao et al., "ACT", 2023](https://arxiv.org/abs/2304.13705))
- **Invalid-action masking** is a valid policy gradient and scales far better than penalising invalid actions. ([Huang and Ontañón, FLAIRS 2022](https://arxiv.org/abs/2006.14171))
- **Rare classes:** logit adjustment ([Menon et al., ICLR 2021](https://arxiv.org/abs/2007.07314)) and focal loss ([Lin et al., ICCV 2017](https://arxiv.org/abs/1708.02002)) are standard. Temperature scaling fixes overconfident networks. ([Guo et al., ICML 2017](https://arxiv.org/abs/1706.04599)) **[unverified links]**
- **Continuous-time networks in closed-loop imitation:** liquid / closed-form continuous-time networks trained by imitation kept flying to target out of distribution, where four other recurrent baselines failed; reported success above 90% on a real quadcopter. ([Chahine et al., Science Robotics 2023](https://cap.csail.mit.edu/sites/default/files/research-pdfs/Robust%20flight%20navigation%20out%20of%20distribution%20with%20liquid%20neural%20networks.pdf))

### What it means for us [inference]

- **DAgger is cheap here.** The teacher is a script, so labelling every unit at every decision costs only teacher compute. Plan 5 to 10 rounds. Start with a mixture policy (teacher drives with probability beta, decaying from about 0.5 to 0), aggregate all rounds, and keep a fixed held-out set of closed-loop fights for evaluation.
- **DART complements it.** Add Gaussian noise to the teacher's movement and occasionally replace its chosen target, at a level matching the learner's measured disagreement rate. This collects recovery states without running the weak network.
- **Under-firing is most likely a decision-structure problem.**
  - If fire competes with a dozen move options in one softmax, argmax rarely picks it even when its probability is the largest single "intent".
  - Fix 1: split the action into a movement head and a target/fire head.
  - Fix 2: mask fire when it is impossible (no target in range, cooldown), so the network only learns *when* among feasible moments.
  - Fix 3: logit-adjust the fire class by its prior.
  - Fix 4: calibrate on closed-loop data, choosing the fire threshold so the network's fire rate in situations where the teacher could fire matches the teacher's rate.
- **Copycat check.** If the observation includes the unit's previous action, last target, or a long history, run an ablation without them. A stuck "keep moving" loop that never starts firing is the classic copycat symptom.
- **Chunking is a minor lever here.** Holding a decision for 0.25 to 0.5 s is already a form of chunking; longer chunks reduce reactivity in a fight. Test only if drift persists after DAgger.
- **Measure what matters.** Report closed-loop fire rate versus teacher, per-class recall, time to first shot, and mean distance to target, next to win rate.

---

## 4. Reward design for "win while preserving own units"

### What the sources say

- **Potential-based shaping** F(s, s') = γΦ(s') − Φ(s) leaves the optimal policy unchanged, and it is the only additive shaping that guarantees this. Unconstrained shaping made a bicycle agent ride in loops to farm reward. ([Ng, Harada and Russell, ICML 1999](https://www.cs.utexas.edu/~shivaram/readings/b2hd-NgHR1999.html))
- **SMAC:** damage dealt, +10 per kill, +200 for a win, normalised to a maximum return of about 20. ([Samvelyan et al. 2019](https://arxiv.org/abs/1902.04043))
- **OpenAI Five:** about 28 hand-weighted reward terms. They are made zero-sum by subtracting the opponent's reward, and blended per hero by a "team spirit" weight annealed from about 0.2 to 0.97. ([Berner et al., 2019](https://arxiv.org/abs/1912.06680); team-spirit numbers from secondary slides, **[unverified]**)
- **AlphaStar:** the win/loss reward plus pseudo-rewards for following a sampled human strategy statistic (build order and unit counts), with the KL term towards the supervised policy. ([Vinyals et al., Nature 2019](https://deepmind.google/discover/blog/alphastar-grandmaster-level-in-starcraft-ii-using-multi-agent-reinforcement-learning/)) **[pseudo-reward details unverified]**
- **ECSLBot** (GA-tuned StarCraft micro) scored fights by units remaining on each side plus a time term. ([Liu, Louis and Ballinger, CIG 2014](https://www.cse.unr.edu/~simingl/papers/publish/CIG2014IMPFMicro.pdf))
- ES fine-tuning was reported to reward-hack less than RL in LLM fine-tuning. ([Qiu et al., 2025](https://arxiv.org/abs/2509.24372))

### What it means for us [inference]

**A key fact for ES.** ES scores whole fights. With γ = 1, potential-based shaping summed over a fight telescopes to Φ(end) − Φ(start). So under ES, potential shaping is exactly a terminal bonus and buys nothing extra; only the terminal terms matter. Shaping matters for PPO, which learns from per-step rewards.

**Recommended fitness, as a lexicographic order:**
1. **Outcome class:** win > timeout > loss. A timeout must score below every win, so stalling can never beat winning.
2. **Within wins:** own units saved (or own HP fraction), then speed (time to finish).
3. **Within timeouts and losses:** HP differential (own HP fraction − enemy HP fraction) and kills. This gives a graded signal while the network still loses, which is the case at the start of stage 2.

With centred-rank fitness shaping, implement the order as one scalar with widely separated weights, for example 1000·win + 100·(survivor fraction if win) + 10·(kill fraction) − 1·(time fraction), with a timeout scored as a loss plus HP differential. Only the order matters after rank shaping, so the exact weights do not need tuning.

**Stall-proofing:**
- The timeout must rank below every win and must not out-score an aggressive loss with a better HP differential.
- The time penalty should only break ties between wins of equal survivors, so it cannot push towards reckless rushes.

**For a PPO reference arm:**
- Use a SMAC-like per-step reward from potential shaping, with Φ = enemy HP lost − own HP lost, weighted to the owner's priorities.
- Make it zero-sum against the opponent's HP as OpenAI Five did.
- Add terminal win and survivor bonuses.

**Watch for these hacks:**
- Kiting forever (fix: the timeout rule).
- Saving units by never engaging (fix: survivors count only on a win).
- Kill-stealing behaviour that hurts the team (not an issue with a shared team score).

---

## 5. League and self-play on a small budget

### What the sources say

- **AlphaStar's league** has main agents, main exploiters (which train only against the current main agents) and league exploiters. Main agents pick opponents by prioritised fictitious self-play (PFSP): weight f(win probability), with f_hard(x) = (1 − x)^p focusing on the hardest opponents and f_var(x) = x(1 − x) on even matches. A fixed share of games stays plain self-play. Exploiters are reset to the supervised policy periodically. ([Vinyals et al., Nature 2019](https://deepmind.google/discover/blog/alphastar-grandmaster-level-in-starcraft-ii-using-multi-agent-reinforcement-learning/); summary in [ApproxED, 2023](https://arxiv.org/abs/2301.08830))
- **A faithful AlphaStar reimplementation failed** on limited compute; the TStarBot-X authors needed extra diversity techniques. ([Han et al., "TStarBot-X", 2020](https://arxiv.org/abs/2011.13729))
- **Gym-μRTS:** a single machine (1 GPU, 3 vCPU, 16 GB) trained in about 60 hours an agent that beat every past μRTS competition bot on one map, using invalid-action masking and a fixed set of scripted opponents. ([Huang et al., IEEE CoG 2021](https://arxiv.org/abs/2105.13807))
- **Open-source defaults** (DI-engine) split games 0.5 PFSP, 0.35 self-play and 0.15 verification. Not a published result. ([DI-engine league code](https://huggingface.co/spaces/OpenDILabCommunity/gomoku/blob/main/DI-engine/ding/league/starcraft_player.py))
- **Fixed opponents can be exploited.** SMAC's single default opponent let algorithms overfit; SMAC-HARD adds varied scripted and randomised opponents. ([SMAC-HARD, 2024](https://arxiv.org/abs/2412.17707))
- **A league is not always needed.** The Generals.io agent reached first place without population self-play. ([Straka and Schmid, ICML 2026](https://icml.cc/virtual/2026/78760))

### Minimum viable version for us [inference]

1. **Phase 1:** the opponent set is the 19 scripted doctrines at regular skill, sampled uniformly or PFSP-hard by win rate. No self-play yet. This matches Gym-μRTS's result that scripted opponents alone reach a strong single-map agent.
2. **Phase 2:** add a snapshot pool: freeze the current best every M generations and keep the last 5 to 10. Sample about 50% scripts (PFSP-hard, p = 1 to 2), 30% snapshots (PFSP-hard), and 20% the current policy mirrored. Use a prior of 0.5 for new opponents' win rates and add a small epsilon so a fully beaten pool does not divide by zero.
3. **Phase 3 (only if evaluation shows blind spots):** one exploiter that trains only against the current main policy and is reset to the stage-B network when it stops finding wins.
4. **Always:** a held-out evaluation set (several scripted doctrines and old snapshots never sampled in training) on fixed seeds. Report the series test (10 fights) against it.

Under ES, every candidate in a generation must face the same opponent draw, so differences come from the candidate, not the opponent.

---

## 6. Networks of coupled oscillators

### What the sources say

- **coRNN:** a recurrent network from a discretised system of coupled, controlled non-linear second-order oscillators. It has proven bounds on hidden-state gradients, which mitigate exploding and vanishing gradients, and it performed comparably to the state of the art on sequence benchmarks. ([Rusch and Mishra, ICLR 2021](https://arxiv.org/abs/2010.00951))
- **UnICORNN** is the follow-up (independent oscillators, symplectic discretisation). It is fast and stable on very long sequences. ([Rusch and Mishra, ICML 2021](https://arxiv.org/abs/2103.05487)) **[unverified details and link]**
- **LinOSS:** a linear state-space model built on forced harmonic oscillators. It is stable with only a non-negative diagonal state matrix, is a universal approximator, and is nearly 2× better than Mamba and LRU on a 50k-length task. ([Rusch and Rus, ICLR 2025](https://arxiv.org/abs/2410.03943))
- **AKOrN (artificial Kuramoto oscillatory neurons):** replacing threshold units with Kuramoto-coupled oscillators gave object binding, strong adversarial robustness (about 52% to 59% AutoAttack accuracy versus 0% for ResNet-18 and ViT on CIFAR-10) and good calibration, at somewhat lower clean accuracy (about 89% to 91% versus 94%). ([Miyato et al., ICLR 2025](https://arxiv.org/abs/2410.13821))
- **Phase binding:** complex-valued activations use magnitude for feature presence and relative phase for which features belong together. This gave unsupervised object discovery up to 100× faster to train than slot models, but on toy datasets with few objects. ([Löwe et al., TMLR 2022](https://arxiv.org/abs/2204.02075); [Stanić et al., NeurIPS 2023](https://arxiv.org/abs/2305.15001))
- **Traveling waves** in a recurrent network store the recent input history; wave RNNs learned memory tasks faster than wave-free RNNs and matched GRU/LSTM with fewer parameters. ([Keller et al., ICLR 2024](https://arxiv.org/abs/2309.08045))
- **Oscillators as a control prior:** in CPG-RL the policy sets oscillator amplitudes and frequencies, and the coupled oscillators coordinate the legs. It transferred to a real quadruped and stayed stable with an unseen 115% body-mass load. ([Bellegarda and Ijspeert, 2022](https://arxiv.org/abs/2211.00458)) Explicit inter-oscillator coupling improved robustness to noise and 90 ms delays. ([Visual CPG-RL, 2022](https://arxiv.org/abs/2212.14400))
- **Memory models in RL:** across 13 memory architectures in partially observable RL, the GRU was the best general-purpose model, and older RNNs beat newer linear-transformer-style models. ([Morad et al., "POPGym", ICLR 2023](https://arxiv.org/abs/2303.01859))
- **No paper was found** that uses Kuramoto-style phase coupling as the policy architecture or communication mechanism in multi-agent RL. The Kuramoto-plus-RL literature is about *controlling* oscillator networks, not using them as policies. ([NeurIPS 2024 workshop example](https://neurips.cc/virtual/2024/109133))

### Trainability: gradients versus ES [inference]

- Kuramoto coupling (sums of sin(θj − θi) weighted by distance) is smooth and differentiable, so BC and PPO gradients flow through it.
- Over long rollouts phase dynamics can become chaotic or settle into synchrony, giving very large or vanishing gradients. coRNN and LinOSS avoid this with damping and structured discretisation.
- Through BC with truncated sequences (a few seconds) gradient training should be fine. For reward training over whole 150 s fights, ES avoids back-propagation through time altogether, which is a genuine practical advantage for this architecture.
- Bound the natural frequencies and the coupling gains (for example a tanh or softplus parameterisation) so neither ES noise nor gradients can push the oscillators into numerical blow-up.

### Where a resonator net could realistically show an advantage [inference]

1. **Coordinated timing:** synchronised artillery and ranged volleys, and focus-fire bursts. This is the AKOrN and binding mechanism applied to timing. Measure volley synchrony (spread of fire times within a group) and burst damage.
2. **Grouping:** units whose phases lock form squads. Measure whether phase clusters predict who moves and targets together.
3. **Scale transfer:** distance-weighted local coupling does not depend on army size, much as multiagent HyperNEAT's policy geometry scaled to larger teams. Measure the 10v10-trained network at 25v25 and 50v50 with no retraining, against the plain and recurrent nets.
4. **Robustness:** AKOrN and liquid networks suggest dynamical units resist noise and distribution shift. Measure win rate under observation noise and against held-out doctrines.

**Expectation:** on raw win rate at the training size, POPGym's evidence suggests a GRU or attention net is the bar to beat, and the resonator may not beat it. The fair claim to test is whether it wins on the four metrics above at equal fight budgets.

---

## 7. Engineering for throughput

### What the sources say

- **EnvPool** (C++ thread pool with batched stepping) runs about 1 million Atari frames per second on 256 cores. Its gains are about 3× over Python subprocess vector environments on a 12-core machine and about 2× even for a single environment. ([Weng et al., NeurIPS 2022](https://arxiv.org/abs/2206.10558))
- **JAX-native MARL pipelines** report about 14× faster MAPPO training than PyMARL-style pipelines, up to 12,500× when many runs are vectorised. The gains come from massive parallelism. ([Rutherford et al., "JaxMARL", NeurIPS 2024](https://arxiv.org/abs/2311.10090))
- **Frame skipping:** agents often learn better with large frame skips (Atari games up to 180 frames). The loss from repeating actions is bounded by a task-dependent "price of inertia" and can be outweighed by the shorter horizon. ([Kalyanakrishnan et al., 2021](https://arxiv.org/abs/2102.03718)) Skipping with no-ops instead of repeating can be more stable for high-level decisions. ([2018](https://arxiv.org/abs/1802.00332))
- SMAC agents act every few game frames (step_mul = 8 by default). **[unverified]**
- ES communicates only seeds and scalar fitness values, so workers reconstruct perturbations locally. ([Salimans et al., 2017](https://arxiv.org/abs/1703.03864)) Counter-based random generators regenerate noise on demand. ([EGGROLL, 2025](https://arxiv.org/abs/2511.16652))

### Recommendations for us [inference]

1. **Profile first.** A network fight takes about 20 s against 4 s for scripts, so inference is about 80% of fight time. Measure time per tick in observation building, inference and engine stepping.
2. **One batched call per decision tick.**
   - Stack all live units' observations (both armies, if both are networks) into one matrix and run one forward pass.
   - For small networks, per-call overhead dominates the arithmetic, so batching 50 units into one call typically gives roughly 10× to 40× on the inference part. This is a rule of thumb, not a sourced figure.
   - In C++, write the small matrix multiplications against a contiguous batch, or use a BLAS call per layer.
3. **Decision cadence.** Decide every 0.25 to 0.5 s and hold the action (or the target, with movement re-steered by the engine) in between. If the engine ticks at, say, 0.05 s, this cuts inference calls by 5× to 10×. Confirm with paired fights that win rate does not drop.
4. **Bounded observation.** Keep only the k nearest enemies and allies (for example 8 to 16 each) with a spatial grid for neighbour queries. This keeps attention cost flat as armies grow from 10v10 to 50v50.
5. **Threads.** One process per core with `torch.set_num_threads(1)` / `OMP_NUM_THREADS=1` in workers, and no extra threads inside native inference.
6. **Run several fights per worker in lockstep** and batch their units into the same forward pass. This is the vectorised-environment pattern, and it raises batch size further.
7. **ES plumbing.** Send each worker (seed, sign, scenario id). The worker rebuilds the perturbed weights locally, runs the fight in native inference and returns one fitness row. No weights cross process boundaries except the mean once per generation.
8. **Reuse batches for BC and DAgger.** Recording teacher labels during learner-driven fights costs one extra script call per unit per decision.

Items 2 to 4 together plausibly bring a 50v50 network fight from about 20 s to the same order as a script fight (a few seconds). That would multiply every budget in Sections 1 and 5 by about 3 to 5. **[estimate; must be measured]**

---

## Sources not re-checked in full

These are cited from memory or secondary summaries and should be confirmed before any design relies on an exact number:
- OpenAI-ES CPU counts and the 3 to 10× sample ratio.
- MAPPO's per-map step budgets.
- MERL's details and link.
- UnICORNN's details.
- The Net2Net, logit-adjustment, focal-loss and temperature-scaling links.
- OpenAI Five's team-spirit schedule.
- AlphaStar's pseudo-reward details.
- SMAC's default step_mul.
