# Memo: placing the output body O relative to the first driven root

Scope: literature check and mechanism reasoning for the candidate fix "place O once, 1.0 unit from the centre toward the first driven root, then freeze it". Each section separates what the sources say [S] from my inference [I]. No project code was read or run for this memo.

## 1. Related work

**Swarmalators.** [S] O'Keeffe, Hong and Strogatz (2017) use an attraction kernel of constant magnitude, `(x_j - x_i)/|x_j - x_i| * (A + J cos dtheta)`, with repulsion `(x_j - x_i)/|x_j - x_i|^2`, averaged 1/N over all pairs. In the in-phase ("static sync") state the swarm forms "a circularly symmetric, crystal-like distribution": a compact disc. The other static states are a uniform disc or an annulus, and none of them is a filament ([Nat. Commun. 8:1504, PMC5686229](https://pmc.ncbi.nlm.nih.gov/articles/PMC5686229); [arXiv:1701.05670](https://arxiv.org/abs/1701.05670)). Lee, Yeo and Hong add a finite cutoff r_c with neighbour-count normalisation, which is close to our mean over up to 8 neighbours within 3 units. In that variant the sync discs survive. When r_c is below the pattern diameter they become "anomalous" discs with a thinning edge, and with large r_c several separate discs can form. Bar-like patterns appear only at K = 0 with r_c ≈ 1–1.8, as phase-wave states, not as in-phase chains ([arXiv:2103.11584](https://arxiv.org/abs/2103.11584)). Sar, O'Keeffe and Ghosh find that a short coupling range splits sync states into several "sync dots" ([arXiv:2411.14851](https://arxiv.org/abs/2411.14851)). [I] Our law is the O'Keeffe kernel with A = 1 and J = 0.8, made local by the k-nearest-neighbour rule. Its in-phase pair spacing, 1/(A+J) = 0.556, matches that kernel. The literature therefore predicts compact in-phase discs or clumps, not stable chains. That matches the observed failure.

**Correction (2026-10-07, answers Codex owner-recheck R3; the text above is kept as written).** The Lee, Yeo and Hong comparison above is inaccurate. In their equations 1–2 ([arXiv:2103.11584v1](https://arxiv.org/html/2103.11584v1)):
- **Attraction is proportional to the separation,** `[(1 + J cos Δθ) − 1/r²](r_j − r_i)`, averaged over the N_i(r_c) neighbours within the cutoff. It is not O'Keeffe's constant-magnitude attraction with only a cutoff added.
- **The phase coupling is global,** `K/N Σ_j sin(θ_j − θ_i)/r_ij`, with no cutoff.
- **The bar-like patterns appear at K = 0,** that is without phase coupling.

So their system differs from ours in the attraction law and in the phase coupling. Our phase coupling is local: k-nearest and distance-weighted. **Neither paper proves that a filament is impossible** in our driven, pinned, neighbour-capped, growing system, which also has sensor forces. The papers support the analogy that in-phase cohesion favours compact clusters. The "curvature flow" reasoning in §2 is a heuristic analogy, not a derived theorem. **The mechanism in this memo is a plausible explanation of the failures tested, not an identified one.** The tests that would distinguish mechanisms are listed in `validation_712/OPIN_VALIDATION_REPORT.md` §3. They include a no-growth control and site-order permutations, which have not been run, so not every condition in this memo has been met.

**Physarum.** [S] In Nakagaki et al. (2000), *Physarum* first fills a maze, then retracts its dead ends and keeps the shortest tube between two food blocks fixed by the experimenter ([Nature 407:470](https://www.nature.com/articles/35035159)). Tero et al. (2007, 2010) model this as tube conductance reinforced by the flux between fixed sources and sinks ([J. Theor. Biol. 244:553, PDF](https://www.iasi.cnr.it/~vbonifaci/semcn/Tero2007.pdf); Science 327:439, 2010, the Tokyo rail network). [I] In *Physarum* both endpoints are exogenous, and the tube is stabilised by transport through it, not by cohesion. Our system has no flux-based maintenance term, so a bridge relies on mechanical cohesion alone.

**Army-ant bridges.** [S] *Eciton* bridges lengthen and move toward shortcuts. They then stop before the shortest route because the workers locked into the bridge cost more than the extra distance saves ([Reid et al., PNAS 112:15113, 2015](https://www.pnas.org/doi/10.1073/pnas.1512241112); [summary](https://www.princeton.edu/news/2015/11/30/ants-build-living-bridges-their-bodies-speak-volumes-about-group-intelligence)). Individual rules depend on local traffic and on how many attached neighbours an ant has. [I] This shows that a self-assembled span has a length limit set by the available material and its upkeep. The spanned gap is an outcome of the dynamics, not a given.

**Swarm robots.** [S] Nouyan et al. (2009) build robot chains between a nest and a prey object, both fixed ([IEEE TEC 13:695, PDF](https://sheffield.ac.uk/media/23017/download)). Kilobots self-assemble shapes by growing from a small set of seed robots that fix the coordinate frame ([Rubenstein et al., Science 345:795, 2014](https://seas.harvard.edu/news/self-organizing-thousand-robot-swarm)). Slavkov et al. (2018) grow protrusions in 300-robot swarms from local Turing-type morphogens ([Sci. Robot. 3:eaau9178](https://www.cwi.nl/en/news/cwi-researcher-fredrik-jansson-in-science-robotics-on-growing-bio-inspired-shapes-with-hundreds-of-tiny-robots/)). Self-assembling robot bridges are optimised and taken down by distributed rules ([RSS 2022, p030](https://roboticsproceedings.org/rss18/p030.pdf)). [I] Each of these systems that reliably grows protrusions adds something beyond pure cohesion: a chemical pattern, a fixed frame or a chain-holding rule.

**Neural cellular automata and morphogenetic engineering.** [S] Growing NCA starts from one seed cell, and the target is learned rather than placed ([Mordvintsev et al., Distill 2020](https://distill.pub/2020/growing-ca/)). Doursat, Sayama and Michel review "self-architecturing" systems in which the architecture is programmed into local rules ([Nat. Comput. 12:517, 2013](https://www-users.york.ac.uk/~ss44/bib/ss/nonstd/naco13ed.pdf)).

**Axon guidance.** [S] The classical model: targets secrete long-range cues such as netrin from the floor plate ([Tessier-Lavigne & Goodman, Science 274:1123, 1996](https://www.jci.org/references/scholar/35728/B79)). Two 2017 Nature papers revised this. Netrin-1 from the floor plate is dispensable, and ventricular-zone netrin laid along the path acts locally by haptotaxis ([Dominici et al. 2017](https://pmc.ncbi.nlm.nih.gov/articles/PMC5576449); [Varadarajan et al. 2017](https://pmc.ncbi.nlm.nih.gov/articles/PMC5786155)). Guidepost cells split a long pioneer trajectory into short segments, and ablating them misroutes the axons ([Bentley & Caudy, Nature 304:62, 1983](https://www.nature.com/articles/304062a0)). [I] Biology bridges long gaps with intermediate, short-range anchors more than with one long reach toward a distant target. That favours shortening the gap over strengthening the target.

## 2. Mechanism

[S] Cohesion makes thin structures retract or break up. Liquid jets do this by surface tension (Plateau–Rayleigh). Cohesive granular streams, with an effective surface tension 10^5 times weaker, still break into clusters ([Royer et al., Nature 459:1110, 2009](https://jfi.uchicago.edu/~jaeger/group/JaegerGroupPapers/granular/2009RoyerGranStreams.pdf)). Whether a swarm forms a compact aggregate or collapses depends on the shape of the pair potential, through H-stability ([D'Orsogna et al., PRL 96:104302, 2006](https://arxiv.org/abs/cond-mat/0509502)).

[I] Why tips retract under our law:
- **Distant members pull as hard as near ones.** Because the attraction has constant magnitude, a member 2.5 units away pulls as hard (1.8) as one at 0.6. Each neighbour j contributes a net pull of about 1.8 − 1/d_j toward itself.
- **The closing element is outweighed.** It averages over 8 neighbours: O plus about 7 cluster members behind it. O is about 1.4 away and contributes roughly 1.8 − 0.7 = 1.1 forward. The 7 members behind are 0.6–3 units back and each pulls 0.0–1.47 backward, all roughly in one direction. The mean points back toward the cluster.
- **It behaves like curvature flow** (a heuristic analogy; see the correction in §1). Interior elements are balanced. An edge element feels the pull of a half-plane. A tip element has all its neighbours in a narrow cone behind it, so it feels the largest net inward pull. This is the discrete form of line tension: high-curvature tips move fastest, and the blob relaxes to a disc. That matches the static-sync discs in the swarmalator papers.
- **A pinned O cannot hold the tip.** O is only 1 of 8 averaged neighbours, so it cannot balance the backward pull. Since O is pinned, its own net force is discarded. Unlike a free partner, it does not move toward the cluster.

[I] **Why a gap of 3 instead of 4 can change the outcome qualitatively.** The observed face distance of 1.5–2.4 units from a centred O is the key number.
- **O may land within reach of the face.** If O moves 1.0 unit toward the root side and the face settles in that direction at much the same place, the face–O distance becomes about 0.5–1.4. That is inside the strong-edge range (r ≤ 1.44 at degree 8). The link would then rest on a compact blob face at equilibrium, not on a protruding filament.
- **The fix may be geometric.** If so, it works by putting O where the cohesive blob already ends, not by making bridging stable. It is a geometric fit, not new growth capability.
- **The cutoff overlap adds to this.** With a gap of about 3 and a motion cutoff of 3, O's whole neighbourhood lies within interaction range of the grown cluster. No element has to protrude beyond the cluster's own range.

Both readings predict success. They differ in what the claim may say, so the tests below should tell them apart.

## 3. Is the placement rule a defensible prior?

[S] Precedents:
- Seeds and reference frames fixed from the initial state are standard: Kilobot seed robots, the single NCA seed cell.
- In *Physarum* and robot-chain experiments, the endpoints are placed by the experimenter.
- Army ants choose where to build from local trail geometry.
- Intermediate targets placed relative to the pathway are a recognised biological strategy (guidepost cells).

[I] Assessment:
- **What makes it defensible.** The rule reads only the medium's own state: which root appears first and where. It does not read task scores, it is applied once and then frozen, and it is the same rule for both starts.
- **Risk 1: post-hoc choice.** The rule was chosen after seeing failures. It must be registered before final seeds, and its tests must be pre-specified.
- **Risk 2: it can hide the real limit.** It may hide that the element law cannot bridge more than about 1.5–2.4 units beyond its equilibrium face. The claim should state that limit explicitly.
- **Risk 3: site bias.** Putting O near one root makes that site's path the shortest. A and B responses may then reflect closeness to the first site rather than processing. Check response per site and per input, not only in aggregate.

**Recommended controls and tests (registered in advance):**
1. **Distance sweep.** Place O at offsets of 0, 0.25, 0.5, 0.75, 1.0, 1.25 and 1.5 toward the first root, for both starts. Report path formation, hold time and A/B/E against offset. Expect a threshold. Report its location and how sharp it is, not only the 1.0 point.
2. **Filament or face.** At path closure and at the end, record the face–O distance and the number of hops from the last cohesive member to O. Run a no-growth control: freeze growth once the cluster settles and test whether the strong link forms anyway.
3. **Direction controls with the same rule shape.** Offset O by 1.0 toward (a) a randomly chosen driven root, (b) the last root to appear, (c) a root that is not driven, (d) the opposite direction. This shows whether "first root" matters or only "closer to mass".
4. **Fresh seeds and site permutations.** Vary which sensor drives first, so that O's angle is not confounded with one site.
5. **Matched starts.** Apply the same rule, with the same parameters, to both the empty and the seeded starts. Report the seeded start with a centred O as a reference.
6. **Hold test.** After the first closure, measure the time to break with and without the strong-edge gate. A link that breaks within seconds should fail.
7. **Contact check.** Confirm that the frozen O does not overlap any element or lie inside the cluster. A repulsive term of 1/r against a pinned body can create artefacts.

## 4. Alternatives and trade-offs

| Option | Literature analogue | Gain | Cost / risk |
|---|---|---|---|
| Distance-decaying attraction (e.g. Morse-type) | D'Orsogna 2006; finite-cutoff swarmalators | Weakens the pull of distant members on tips | Changes the element law; the morphology may still be compact |
| Persistent bonds / springs once a link closes | Ants locking into bridges (Reid 2015) | The chain holds along its axis | Central-force chains are laterally floppy (Maxwell counting); they need prestress or triangulation, as in tensegrity (Calladine, Int. J. Solids Struct. 14:161, 1978; see review [Seventy years of tensegrities, Arch. Appl. Mech. 2022](https://link.springer.com/10.1007/s00419-022-02192-4)) |
| Growth from both ends (O also recruits elements) | *Physarum* between two food sources; robot chains from the nest | Halves the protrusion each side must sustain | O becomes an active body; this needs a rule for O's material |
| Target cue (O attracts more strongly or over a longer range) | Classical netrin chemoattraction | A direct fix | The 2017 netrin revisions show the long-range target cue was overstated; it adds a task-specific force |
| Intermediate anchors | Guidepost cells | Splits a 4-unit gap into spans under 2 units | Who places the anchors becomes the same prior question |
| Flux-reinforced persistence | Tero 2007 *Physarum* model | Paths that carry phase flow persist; ties structure to function | A new dynamic law; tuning risk |
| O placed relative to the first root (candidate) | Seeds/frames; ant bridge siting | Element law unchanged; minimal | May work only by putting O inside the blob's reach; must be stated as a geometric prior |

[I] The candidate is the least invasive option and is defensible as a geometric prior if tests 1–3 pass. The registered claim should say what tests 1–2 show: either the system bridges a gap, or O is placed within the cohesive face's reach.
