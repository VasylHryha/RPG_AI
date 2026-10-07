# Memo: how self-organizing media form and hold chains, and what fits our medium

Scope: a web literature check, building on `opin_research_memo.md`. Each claim is marked [S] (stated by the source) or [I] (my inference). No project code was read or run. Our law, as described: an element moves by the mean over its ≤8 nearest neighbours within 3 units of `A(1+J cos dphi)·û − B/r·û`, with A=1, J=0.8, B=1; phases are Kuramoto-coupled with weights `exp(-r²)`; growth adds elements at a tip with spacing 0.556.

## 0. Diagnosis

[I] The earlier memo showed that our kernel works like curvature flow. A tip has all its neighbours in a cone behind it, so it feels the largest net inward pull, and the structure relaxes to a disc. Every chain-forming system below breaks this in one of four ways:
- **(a) Inheritance**: the attraction that drives aggregation is not felt by elements already inside the structure.
- **(b) Persistent bonds**: links have memory and resist the mean-field pull.
- **(c) A field**: an external gradient advances the tips faster than curvature relaxes them (a Mullins–Sekerka-type instability).
- **(d) Reinforcement**: links that carry use or flux persist, and unused ones decay.

Our medium currently has none of the four.

## 1. Survey: mechanism, target, mapping, risk

**Contact-inhibited chemotaxis (Merks et al. 2008).**
- [S] Their cellular Potts model of endothelial cells: "By itself, this behavior [chemotaxis to a self-secreted attractant] causes simulated cells to accumulate to aggregate into large, round clusters." The paper also says it reduces to Keller–Segel, which forms "isolated vascular islands".
- [S] The fix is VE-cadherin contact inhibition, in which "only interfaces between cells and ECM respond to the chemoattractant". Then "Chemotaxis produces a continuous, inward, normal force at the cluster boundary, creating a buckling instability", and clusters sprout into networks ([PLoS Comput Biol 4:e1000163](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1000163); [arXiv q-bio/0505033](https://arxiv.org/abs/q-bio/0505033)).
- Target: none needed.
- [I] Mapping: an element counts in-phase attraction only from neighbours it is not already bonded or embedded with. Equivalently, stalk elements drop the non-bonded attraction term. This is mechanism (a).
- Risk: it changes the element law. Without bonds, the unattracted stalk elements drift apart under repulsion.

**Preferential attraction to elongated structures (Szabó, Perryn & Czirók 2007).**
- [S] Cells attracted preferentially to stretched cells evolve into "a quasistationary pattern containing linear segments". There, "the generation of new branches offset the coarsening driven by surface tension" ([PRL 98:038102](https://link.aps.org/doi/10.1103/PhysRevLett.98.038102); [arXiv q-bio/0612035](https://arxiv.org/abs/q-bio/0612035)).
- Related: Palm & Merks show vascular-like networks from elongated cells ([arXiv 1210.7164](https://ar5iv.labs.arxiv.org/html/1210.7164)).
- Target: none.
- [I] Mapping: weight neighbour j's attraction by a local elongation index e_j, such as the eigenvalue anisotropy of j's neighbour covariance.
- Risk: it is a shape-based term with no resonance basis. It also yields nets, not a single directed bridge.

**Wandering activator peak (Meinhardt 1976).**
- [S] "the differentiated cell repels the activator peak and drives it to a neighbouring cell which then also differentiates … forces the activator peak to move ahead of the tip of the extending filament."
- [S] On targets: "a growing filament can 'home in' on a particular target cell if the target cell produces the substrate s … If the distance between the growing tip and the target is large, homing may be inaccurate since the gradient is shallow" ([Differentiation 6:117, PDF](https://www.davidmoore.org.uk/21st_century_guidebook_to_fungi_platinum/REPRINT_collection/Meinhardt_Morphogenesis_lines_and_nets1976.pdf)).
- [I] Meinhardt's filament is a trail of differentiated cells that do not move. It is held because its cells are a different state, not by cohesion.
- Mapping: a tip state that leaves stalk-state elements behind it.
- Risk: if stalk elements are fully frozen, that conflicts with the requirement that all underlying elements keep evolving.

**Tip and stalk cells with Notch lateral inhibition (angiogenesis).**
- [S] Tip cells extend filopodia and migrate up a VEGF-A gradient, while stalk cells follow and proliferate ([Gerhardt et al., J Cell Biol 161:1163, 2003](https://doi.org/10.1083/jcb.200302047)).
- [S] Dll4/Notch lateral inhibition selects one tip and its neighbours become stalk cells. VEGF concentration, its gradient and filopodia set how robust that patterning is ([Bentley, Gerhardt & Bates, J Theor Biol 250:25, 2008](https://doi.org/10.1016/j.jtbi.2007.09.015)).
- Target: a gradient source, which in vivo is a tissue, not a point.
- [I] Mapping: an element with bond degree ≤1 at the front, and the largest guidance signal among its bonded neighbours, is the tip. Its bonded neighbours are inhibited from becoming tips.
- Risk: it adds state machinery. It solves "who moves", not "what holds".

**Physarum flux reinforcement.**
- [S] Tero et al. 2010: `Q_ij = D_ij (p_i − p_j)/L_ij`, with Kirchhoff balance and "dD_ij/dt = f(|Q_ij|) − D_ij … in the absence of flow the tubes will gradually disappear", where `f(|Q|) = |Q|^γ/(1+|Q|^γ)`. Random food sources drive the flow ([Science 327:439](https://pdodds.w3.uvm.edu/files/papers/others/2010/tero2010a.pdf)).
- [S] The agent version, in which particles deposit trail and follow it, forms networks that show "circular contraction of network lacunae" ([Jones, Artif. Life 16:127, 2010](https://uwe-repository.worktribe.com/output/980579)).
- Target: needs fixed sources and sinks.
- [I] Mapping: in a Kuramoto chain between a driven root and the rest, the coupling term `w_ij sin(φ_j − φ_i)` is a conserved phase current, analogous to Kirchhoff flux. Reinforce bond stiffness by it. This is mechanism (d), and it is the most "geometry follows resonance" rule here.
- Risk: perfectly in-phase links carry zero current and would decay. The current needs a frequency mismatch along the path.

**Army-ant bridges.**
- [S] Bridges "lengthen, widen, and change position in response to traffic levels and environmental geometry". They stop at a cost–benefit point, set by the workers locked into them ([Reid et al., PNAS 112:15113, 2015](https://www.pnas.org/doi/10.1073/pnas.1512241112); [record](https://researchwith.njit.edu/en/publications/army-ants-dynamically-adjust-living-bridges-in-response-to-a-cost/)).
- [S, from memory, not re-fetched] Garnier et al. 2013 model living structures in which ants stay locked while being walked on and leave when traffic drops ([PLoS Comput Biol 9:e1002984](https://doi.org/10.1371/journal.pcbi.1002984)).
- [I] This is use-dependent bonding: bond while used, release when idle. It maps onto bonds gated by coupling or current.

**Robot self-assembly.**
- Kilobots [S, as reported in secondary summaries of the Science paper]: robots edge-follow until they are about to leave the shape, or until they meet a stopped robot with a higher gradient value. Then they stop, and seed robots fix the frame ([Rubenstein et al., Science 345:795, 2014](https://seas.harvard.edu/news/self-organizing-thousand-robot-swarm)).
- TERMES [S]: blocks are placed by stigmergy and stay put ([Werfel et al., Science 343:754, 2014](https://kavlifoundation.org/news/robotic-construction-crew-needs-no-foreman)).
- Swarm-bots [S]: s-bots self-assemble physically with grippers ([Groß et al., IEEE T-RO 22:1115, 2006](https://infoscience.epfl.ch/handle/20.500.14299/235022)).
- Robot chains [S]: chains between a nest and a prey ([Nouyan et al. 2009](https://sheffield.ac.uk/media/23017/download)).
- Turing protrusions [S]: grown in 300-robot swarms ([Slavkov et al., Sci. Robot. 2018](https://www.cwi.nl/en/news/cwi-researcher-fredrik-jansson-in-science-robotics-on-growing-bio-inspired-shapes-with-hundreds-of-tiny-robots/)).
- [I] In every case, an element that has joined the structure stops responding to the gathering drive. This is mechanism (a) or (b) again.

**DLA and Laplacian growth.**
- [S] DLA uses irreversible sticking on contact and produces fractal branches ([Witten & Sander, PRL 47:1400, 1981](https://doi.org/10.1103/PhysRevLett.47.1400)). Tips in a diffusion field grow faster than flat fronts, and surface tension counteracts this ([Mullins & Sekerka, J. Appl. Phys. 35:444, 1964](https://doi.org/10.1063/1.1713333)).
- [I] This is the cleanest statement of our competition: field-driven tip advance against curvature relaxation. Our system has the relaxation term and no destabilizing field.
- Risk: irreversible sticking is frozen and fractal, which is not a single bridge.

**Patchy and dipolar particles.**
- [S] Two-patch (Kern–Frenkel) particles form polymer chains, and higher valence gives branched networks. Dipoles assemble head to tail into chains and rings ([review, arXiv 1705.04383](https://arxiv.org/pdf/1705.04383); [dipolar ABPs, arXiv 1907.13430](https://arxiv.org/pdf/1907.13430)).
- [I] The key ingredient is limited valence: at most two strong partners. Mapping: cap the strong attraction or bonds at 2 per element (3 at branch points).
- Risk: it adds an orientation or valence variable that our elements lack.

**Tensegrity and prestress.**
- [S] Connelly and Whiteley: a framework with a suitably signed self-stress is prestress-stable, which implies rigid, even when it is first-order flexible ([SIAM J. Discrete Math. 1996, PDF](https://pi.math.cornell.edu/~connelly/pdf/10.1137_S0895480192229236.pdf)).
- [I] A chain anchored at both ends under tension is a taut string, with lateral restoring stiffness about 2T/a per node. A cantilever, anchored at one end, is not. Prestrain can hold a bridge only after closure. During growth, something else (a or c) must stop retraction.

**Neural CA.**
- [S] Growth does not imply persistence: "some tend to die out, some don't seem to know how to stop growing, but some happen to be almost stable!" Persistence needed separate training, the sample pool ([Mordvintsev et al., Distill 2020](https://distill.pub/2020/growing-ca/)).
- [I] Holding a structure is a separate capability from growing it, and it needs its own mechanism and test.

**Swarmalator variants.**
- [S] With a finite cutoff, the static states repeat in space, and bar-like states appear only as phase waves at K=0 ([Lee et al., arXiv 2103.11584](https://ar5iv.labs.arxiv.org/html/2103.11584)).
- [S] Local coupling with chirality and non-identical frequencies gives vortex lattices, beating clusters and interacting phase waves ([Ceron, O'Keeffe & Petersen, Nat. Commun. 14, 2023](https://ideas.repec.org/a/nat/natcom/v14y2023i1d10.1038_s41467-023-36563-4.html)).
- [S] The 1D solvable model is in [Yoon et al., PRL 129:208002, 2022](https://www.doi.org/10.1103/PhysRevLett.129.208002). A review is [arXiv 2208.14803](https://arxiv.org/pdf/2208.14803).
- [I] I found no swarmalator variant whose in-phase state is a stable chain. Staying inside the kernel family will not give us filaments; an added mechanism is required.

## 2. Ranked prototypes

These are layers that can be ablated separately. Ranking is by expected effect on *holding*, closeness to "geometry follows resonance", and change size.

### Rank 1: resonance-gated bonds with contact-inhibited cohesion, and prestrain at closure

Coupling strength of a pair: `c_ij = exp(−r_ij²)·cos(φ_j − φ_i)`. This is the same weight the Kuramoto term uses. In phase, it is 0.73 at r = 0.556, 0.37 at r = 1 and 0.20 at r = 1.27.

- **Bond formation:** when `c_ij ≥ c_on` (e.g. 0.6) for a dwell time `τ_on`, and both elements have degree below 2 (3 at a branch). The valence cap comes from patchy particles.
- **Bond breaking:** when `c_ij < c_off` (e.g. 0.2) for `τ_off`, or strain `|r−ℓ_ij|/ℓ_ij > ε_max`. The hysteresis mirrors the ant rule "hold while used".
- **Bond force, added outside the neighbour mean:** `F_i += Σ_bonds k (r_ij − ℓ_ij) û_ij`.
  - `ℓ_ij` = r at formation during growth, so there is no prestrain and no pull on the free tip.
  - At closure, when a bond to O forms, set `ℓ_ij ← (1−ε) r_ij` with ε ≈ 0.1 along the root→O path. This puts the chain under tension, making it a taut string (prestress stability).
- **Contact inhibition (Merks):** an element with degree ≥1 drops the attraction term `A(1+J cos dphi)` for all non-bonded neighbours. It keeps the repulsion and the Kuramoto coupling, so it still evolves in phase and position.
- **Optional Physarum layer:** `dk_ij/dt = [f(|w_ij sin Δφ_ij|) − k_ij]/τ_k`, with f sigmoidal as in Tero. Bonds on the driven current path stiffen; dead branches soften and break.

What to measure:
- tip retraction speed during growth (baseline 0.3–0.6 u/s; target ≈ 0);
- bridge lifetime after closure;
- lateral deflection and recovery after an impulse;
- maximum holdable gap, sweeping O at 2, 3, 4 and 5 units;
- disc compactness C = 4πA/P² of the rest of the body;
- the share of bonds formed versus broken by the coupling gate rather than the strain gate.

Ablations: bonds without contact inhibition; contact inhibition without bonds; ε = 0 versus 0.1; gate on distance only versus gate on c_ij. The last shows whether resonance matters or only proximity.

Main risk: bonds alone, without contact inhibition, will probably lose to the mean-field pull of 7 cluster members. Contact inhibition is a law change and must be declared as one.

### Rank 2: tip/stalk differentiation with lateral inhibition

- **Tip:** an element with degree ≤1 on the growth front. Among bonded candidates, the one with the largest guidance signal wins, and it inhibits tip status in its bonded neighbours for a refractory time (Notch-like).
- **Tip dynamics:** it keeps the full swarmalator law plus guidance.
- **Stalk dynamics:** it follows rank 1, with bonds plus repulsion and no non-bonded attraction. Optionally add extra damping `v ← v/(1+η)` instead of freezing, so stalk elements keep evolving.
- **Growth placement:** a new element goes at `tip + 0.556·n̂`, as in Runions' space colonization (normalized sum of directions toward attractors within a radius of influence) ([Runions et al. 2007](https://www.algorithmicbotany.org/papers/colonization.egwnp2007.html)).

What to measure:
- tip count over time (expect 1 per front);
- branch count;
- path tortuosity (path length divided by straight distance);
- the same holding metrics as rank 1.

Risk: a status flag is a designed rule. Kilobots and Meinhardt show it works, but they freeze joined elements, which conflicts with continuous evolution unless only damping is used.

### Rank 3: guidance field from O, applied to tips only

- **Field:** `u(x) = Σ_O exp(−|x−O|/λ)`, or the steady state of `∂u/∂t = D∇²u − u/τ + s δ_O`. Use λ ≈ 2–3 so it reaches the face. Meinhardt warns about shallow gradients at long range.
- **Tip force:** `G ∇u/|∇u|`, with constant magnitude like our attraction. Choose G so that G exceeds the residual backward pull (≈1–1.5 without rank 1, much less with it).
- **Stalk:** gets no guidance.

What to measure: time to reach O; angular error of tip heading; whether a guided tip without rank 1 still retracts after closure (expected yes).

Risk: it is a target-specific force, so it is a task prior and must be registered as one. Merks shows that a gradient alone produces round clusters. Guidance helps reach O; it does not help hold the bridge.

Suggested order: build ranks 1 and 3 together (reach, then hold), run a 2×2 ablation, and add rank 2 only if multiple tips or branching cause trouble.

## 3. Has our exact failure been documented?

[S] The closest documented match is Merks et al. 2008. A cohesive, self-attracting cell population "accumulate[s] to aggregate into large, round clusters". Contact inhibition, where "only interfaces between cells and ECM respond to the chemoattractant", turns this into sprouting and networks. That is a cohesive collective failing to hold elongated structures, fixed by removing the aggregating drive from embedded members.

[S] Szabó et al. 2007 name the opposing force directly: "the coarsening driven by surface tension", offset only by continual branch generation.

[S] Mordvintsev 2020 documents that grown patterns "die out" or overgrow unless persistence is trained separately.

[I] I found no source on a swarmalator or a k-nearest-neighbour cohesive swarm growing one filament toward a fixed point and retracting. Our failure is the particle-level version of the Merks round-cluster result and of Mullins–Sekerka surface-tension stabilization. The fixes in the literature are inheritance or contact inhibition, bonds or valence, field-driven tips, and use-dependent reinforcement. Cohesion tuning alone does not appear in them.
