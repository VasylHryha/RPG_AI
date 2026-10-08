CHANGES_REQUIRED
Reviewer family: Codex
Reviewed commit: db404c2953c6eb01ac39b803791cd87a1be334e4
Review date: 2026-10-08

The note identifies useful methods, and most requested numerical spot-checks hold up. It is not ready to guide implementation: the proposed order omits the owner's coordinated volleys, the copying plan lacks the necessary observation/action contract, and the evaluation and cost claims are insufficiently grounded for the ten-fight objective. Keep react first, keep search/distillation conditional, and correct the source summaries before using them to justify more machinery.

Owner request received verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Scope: static review and primary-source browsing only. Read AGENTS.md, the complete research note, SHAPE_LAB_SPEC.md §§1–11, KILLERS_V7_REGULAR.txt, and selected delivered native interfaces to assess transfer feasibility. No project code, tests, fights, benchmarks or mutation probes ran. No access to the concurrent `s4_shape_lab_v1/` implementation was needed. Findings concern the research note and its proposed next steps, not acceptance of that build. Line references below are to the research note at the reviewed commit unless another file is named.

Reviewed identities (SHA256):

- Research note: `9e01fea9e440736c352463a0e97160ffa78fea85f2bb61744f3b57fdb0dc6946` (workspace bytes also matched the reviewed commit).
- Shape-lab spec: `5e80c599d86d95009444208272a47cfa16ea2223c4cc929e00f1a7d2f99fb6ea`.
- Killers summary: `ae99f065393aea642757d45bf03df5bd0e7ee2a28c08d2e198fe0b5d39cf6257`.

## Required findings

### F1 — High: restore the owner’s react → V1 timing → V2 geometry sequence

Locations: lines 3, 14, 29, 250, 276, 324–331; spec §§10–11.

The note cites Amendments 2–3 but ignores Amendment 4. It orders react, rotation and aim, then generic search and selector distillation. The owner explicitly stages react, coordinated volley timing, then volley geometry. The oscillator now synchronizes guns; a learned selector replacing or conditioning the old commit/escape gate is not its specified job. Describing a selector as the gate’s job carries forward the superseded design.

**Fix:** update the scope to §§9–11 and distinguish the old gate from the battery oscillator. After the lab’s checks and teacher baseline, copy react as one labelled change, then implement/compare V1 timing, then V2 geometry. Use the existing teacher volley planner before commissioning a general SSS/GAB teacher. Keep rotation/aim as separately measured supporting changes, and do not silently reorder owner decisions. A selector may choose named volley patterns or movement policies later; it must not erase the local coupling claim. For V1 compare copied central synchronization with local coupled phases; report launch and landing-time spread, cooldown/windup/flight-time effects, hold-induced firepower loss, and behavior when only one or two guns survive. For V2 score joint volley coverage and delayed herd/trap patterns, rather than optimizing guns independently. Synchronizing launches alone does not ensure simultaneous impacts or prevent escape.

### F2 — High: define how teacher primitives can actually be observed, copied and composed

Locations: lines 19, 131–140, 246–253, 262–276; spec §§9–11.

The delivered `astelia_cpp/src/native/controller.h` Observation contains time, arena size and unit records, with no incoming shell/shot/field records or enemy cast preparation. UnitDecision contains movement, target and failure fields, with no explicit aim point, hold/release time or joint volley. `dodge.cpp` uses shells and cast state. Target/goal agreement from Amendment 2 therefore cannot by itself reproduce react, aim or coordinated volleys. These are integration prerequisites, not a few extra fitted weights.

The note also treats `saveWounded` as guaranteed to obey the owner's rule. Delivered `decisions.cpp:6–12` backs toward home without an own-range constraint; `decideUnit` returns immediately when it activates, before normal attack-release selection. Its eligibility and actual time out of combat need checking. The cited kiting behavior taking units out of enemy range does not establish that they remain in their own useful firing range.

**Fix:** specify a new, permitted interface/adapter with immutable observable projectile/cast data and explicit aim/hold/release intent, without changing pinned interfaces. Record primitive activation, candidate and executed intent, arbitration winner, reason, readiness and volley membership alongside targets/goals. Define react’s temporary precedence over movement, which attacks remain possible during a dodge, how units return to useful positions, and how reaction affects volley readiness. Constrain copied rotation to the owner's participation rule rather than assuming the teacher already satisfies it. Shadow teacher and student state/RNG must be separate, initialized and advanced consistently on the same decision state; retain the spec's byte-identical shadow-on/off trajectory check. Train on the student’s available features, including sparse-army states. A joint volley needs battery-level labels: marginal per-unit agreement can copy individually plausible shots that fail together. Logging reverse shadows is DAgger-style collection; aggregation and refitting are still required to perform DAgger.

### F3 — High: make series success primary and define a loss-aware evaluator before search/tuning

Locations: lines 18, 35, 76, 165–169, 264, 285–298; spec §§5, 10.

“Own-loss-weighted LTD2” and “own losses per fight plus a series-streak simulator” are not executable objective definitions. LTD2 uses current HP and damage rate, whereas survivors heal between fights: surviving at low HP and dying have very different carry-over consequences. Nor does cumulative loss alone determine the streak; failure to eliminate ends it even with few deaths. An unconstrained weighted sum can favor passive survival or short failed fights. Uniform unit counts also miss composition: losing the last effective gun can matter more than losing another escort. Amendment 3 supersedes the older draft loss budget.

**Fix:** define the elimination/timeout terminal rules and use streak as the primary series comparison, with avoided deaths and retained role capability as explicit secondary measures. State search reward terms, units, normalization, weights, terminal treatment and horizon/tail policy; label LTD2 a candidate heuristic, not a directly transferred series objective. Include shells still in flight and a healed-survivor/role-capability tail estimate, then check whether its candidate rankings predict later series outcomes. Report paired fresh series draws, streak distribution, probability of reaching each fight, completion frequency, and surviving counts by role before each fight. Report losses on failed and won fights separately with denominators; do not optimize only losses conditional on wins. The ten development series in the spec are descriptive evidence, not a precise population estimate or scientific acceptance. Any greater sampling needs its own projection/authorization under repository rules. Keep all runs abilities-off, healed survivors and fresh full enemy armies. The first fight not won by elimination ends the series, including losses, draws and timeouts.

### F4 — High: an engine clone does not establish an exact teacher or a fair information boundary

Locations: lines 97–99, 133, 139, 164–169, 264–273, 276.

The mechanics clone is valuable, but finite-horizon evaluation, assumed continuation policies and stochastic expectations remain approximations. In delivered native code, `World::copyAuthorityFrom` sets `branch=true` and `thinkTeams=0`; `artilleryVolley` takes a lighter candidate path in such branches, and `lookahead` suppresses branch thinking unless enabled. Thus copying the world is not sufficient to reproduce the full scripted opponent's future search behavior. This is a concrete caveat in the delivered engine, not a claim that the concurrent lab has a defect.

Rolling the enemy’s true tactic/skill or exposing “enemy doctrine” as a selector feature can also give a privileged teacher information absent from the deployed shape API. Copying internal RNG state permits scoring a particular future realization; it is not automatically expected cost-to-go or an unbiased counterfactual contribution.

**Fix:** document branch thinking, enemy continuation, timestep and all controller memory/RNG semantics. Before a future search pilot, require continuation parity under identical actions/settings, or explicitly label any reduced-policy model and measure its ranking error. Declare which tactic/skill/state fields are public. Separate oracle teacher and deployable teacher arms; students receive observations or a declared inference of doctrine, not hidden IDs. Define sampled stochastic continuations and coupling of random streams across alternatives; identical initial seeds alone do not ensure action-dependent draw alignment. Call finite rollouts estimated disagreement cost and continuation-dependent counterfactuals. Do not describe them as exact AggreVaTe guarantees or ideal/global-optimal play.

### F5 — Medium: search and shadowing costs omit factors that can change feasibility

Locations: lines 42–44, 170–171, 248, 253, 267, 295.

Whole-fight throughput is not a measured branch cost. The proposed 24 evaluations per pass also need the proposed 2–3 continuations. Using the note's own 0.02–0.1 core-s estimate gives 0.96–7.2 core-s per decision, or 86–648 core-s per 90-s fight, before asymmetric search, multiple passes, state copying, nested enemy search or recording. Ideal ten-core throughput is approximately 0.9–7 teacher fights/minute, rather than 3–15. This is arithmetic on the note's assumptions, not a benchmark. Replaying every disagreement also has a rollout budget; shadowing an elite search teacher need not cost a cheap single controller call. Series multiply fights per candidate, and noise handling adds evaluations, so “same fight budget” needs explicit accounting.

**Fix:** replace point feasibility claims with the full cost formula and uncertainty. Propose, without running it in this review, a bounded owner-authorized branch-cost pilot on representative dense/late/projectile-heavy states: CPU and wall time, copy/step/controller/teacher/recording costs, candidate/pass/continuation counts, nested-search policy and peak memory. Establish a hard per-label and total budget, with cached labels and cheap disagreement screening before counterfactual rollouts. Prefer direct copied react and the existing gun-only teacher until measured extra search benefit justifies the cost. Supply yes/no stop rows with an action and responsible role.

### F6 — Medium: the fixed-SSS result summary drops the failure that motivates SSS+

Locations: lines 84–86, 117, 151, 266.

[Lelis 2017, Table 1](https://www.ijcai.org/proceedings/2017/0522.pdf) confirms PGS+ versus PGS at 0.72–1.00, with the changed first-action/default-continuation evaluation. But at Zea14/Dra14/Ling14/Mar14 (56 units/side), fixed SSS versus POE is 0.46 and versus PGS+ is 0.16; SSS+ instead reaches 0.96 and 0.95. Thus the claimed large-army fixed-SSS ranges against POE and PGS+ omit a critical counterexample. POE versus PGS also reaches 0.56 in the six-unit mixed case, below the stated 0.76 minimum.

**Fix:** separate SSS and SSS+, identify scenario restrictions on ranges, and cite the failure row. Favor adaptive granularity/budget exhaustion handling as the search design lesson, not guaranteed coarse-role superiority. Retain the confirmed PGS+ evaluation lesson; do not transfer its short-horizon effectiveness to our engine without checking candidate rankings. Literature results do not establish that searches always beat their scripts.

### F7 — Medium: separate the owner’s random series from curriculum and scripted-pool robustness

Locations: lines 17, 185–203, 264, 276, 285–309; spec §5.

The owner’s yardstick is 19 doctrines sampled uniformly with replacement at regular skill. PFSP over 76 skill/doctrine cells, prior selves and exploiters can be useful training/stress distributions; they are not that yardstick. Optimization, teacher labeling and doctrine classification on the same fixed pool risk learning policy IDs or scripted rhythms rather than transferable react/volley behavior. Late fights also have a survivor distribution absent from ordinary full-army drill data.

“Keep an f_var floor” does not guarantee coverage: x(1−x) is zero at both extremes. f_hard on expected losses is undefined without converting losses to an appropriate bounded quantity.

**Fix:** preserve untouched development series/order seeds for comparison and separate tuning, label-generation and reporting sets. Pair the enemy tactic sequence and placements across arms without letting controller RNG consumption change later draws. Use a nonzero uniform mixture in curriculum sampling; define bounded loss estimates with uncertainty and role/count normalization. Report the uniform regular-series objective separately from weighted training and skill/self/exploiter stress results. Add held-out doctrine families/parameter perturbations, placement/orientation variation, reaction/volley interaction ablations, and reduced survivor compositions as separately labelled stress tests. These improve diagnosis without changing the official pool or authorizing judging runs. Repertoire/classifier work stays last and requires gains over one robust policy plus misclassification/latency costs.

### F8 — Medium: replace ceilings and universal claims with evidence scoped to the experiments

Locations: lines 50, 53, 56–61, 112, 122–123, 144–147, 252–256, 266, 317–318.

- RAI-BC's aggregate numbers are correct, but they neither guarantee that copied Astelia primitives reach elite quality nor prove an elite-level ceiling. Approximation, features and distribution shift can make copying worse; a student may also exceed its teacher in particular matchups. The paper reports PPO regressions on some maps despite aggregate improvement. **Fix:** call copying an initial baseline, require paired per-primitive/series evidence, and remove the ceiling/“needs T-search” assertion. Search is a candidate improvement method.
- SC2LE's historical splash score gap does not isolate splash avoidance as the cause, compare all modern RL methods, or prove that our hand-built react will outperform them. **Fix:** preserve the exact benchmark numbers and label the practical preference for copied react as an inference from our missing reaction and available teacher.
- The kiting paper discusses retreat out of enemy range, not proof of the owner's never-leave participation rule. **Fix:** use it as a rotation candidate and enforce F2's participation checks.
- AlphaZero does not require an expert-teacher bootstrap. An available exact simulator does not prove that every learned model only adds error; approximation can trade accuracy for cost. **Fix:** present teacher → improvement → distillation as our proposed workflow, not the common mandatory core of every landmark. Keep learned dynamics deferred for this project without universal dismissal.

## Primary-source spot-check ledger

The entries below distinguish confirmed numbers from overextended interpretations. Sources were accessed during this review; no local results were recomputed.

| Claim | Check and disposition |
|---|---|
| microRTS BC versus Mayari | [Goodfriend §4.3, Tables 4/28](https://arxiv.org/html/2402.08112v1): RAI-BC overall 71%, versus Mayari 44%; BC+PPO overall 88%, versus Mayari 84%. Correct. This is the post-competition BC experiment, not the competition-winning agent's training recipe. Fix interpretation per F8. |
| SSS and PGS+ | First-action candidate then NOKAV continuation is correct; the reported PGS+ head-to-head range is correct. Fixed-SSS/POE ranges need F6's corrections. |
| GAB/SAB | [Moraes & Lelis, Tables 1–2](https://arxiv.org/html/1711.08101): GAB versus PGS 0.82 for 8 Zealots + 8 Dragoons and 0.81 for 32 Zealots; SAB versus SSS 0.90 for 50 Zealots. AV+ and N=4 are supported in that experiment, not a universal choice of four artillery units. |
| Focus-fire scaling | [Usunier et al., §7.2/Table 1](https://arxiv.org/html/1609.02993): m15v16 wc/nok_nc/c/ZO = .10/.68/.81/.79; w15v17 = .02/.12/.20/.49, 1,000 test battles. Correct. Name wc as weakest-closest and nok_nc as no-overkill/no-change; these are outcomes against built-in AI, not pairwise tournament results. The paper warns that its static damage reservations can become wrong when attackers die. “No-overkill is necessary” is stronger than this evidence. |
| ECSLBot | [Liu et al., Table II, Eq. 3 and conclusion](https://www.cse.unr.edu/~simingl/papers/publish/CIG2014IMPFMicro.pdf): 14 parameters, approximately 21 h adaptation, unit-difference plus time fitness confirmed. Main comparisons control five Vultures; additional Dragoon experiments are mentioned. “Tested on one unit type” is too categorical. Mixed own-army composition remains an identified limitation. The paper also uses a second destruction-score fitness; Eq. 3 is not its only objective. |
| SMAC reward | [Official environment source, constructor/reward_battle](https://raw.githubusercontent.com/oxwhirl/smac/master/smac/env/starcraft2/starcraft2.py): positive-only dense default, 10 enemy-death value, 200 win bonus and no direct allied damage/death penalty confirmed. These are raw rewards; reward scaling is enabled by default. Calling this win-rate-only optimization is inaccurate: damage/kill shaping remains. Own casualties still affect future damage and winning indirectly. |
| Splash mini-game | [SC2LE Table 1](https://ar5iv.labs.arxiv.org/html/1708.04782): best agent mean 96, human means 729 and 727, trained for 600M steps. Correct. These are scores, not win percentages or successful-dodge counts; scope the conclusion per F8. |
| PGS in the real engine | [Churchill et al. 2017](https://ojs.aaai.org/index.php/AIIDE/article/download/12962/12810/16479): model/collision sensitivity and lack of observed improvement when increasing the tested 10 ms budget to 40 ms are supported. Report scenario-specific results; “won everything”/“failed only because of collisions” are too broad. |
| Our artillery gap | KILLERS_V7_REGULAR.txt supports 74.1% of deaths, 77% of damage, 86% ranged/63% melee attribution, 2,940.5 enemy dodge records and launch counts 184.4/104.9 per fight. Across all 40 fights own deaths average 41.8; 40.7 is the spec's separate wins-only mean. Attribute those denominators. `observer_v1.cpp` records positive dodge-goal decisions, so ~2,940 is not ~2,940 distinct shells avoided. Keep zero own reaction as the gap; measure hit probability, damage/deaths avoided and time/firepower cost instead of maximizing event counts. |

## Tool metadata and adoption notes

The main version/date claims are corroborated by the publisher records:

| Tool | Publisher check |
|---|---|
| cma | [PyPI](https://pypi.org/project/cma/): 4.5.0, 2026-09-13, BSD-3-Clause. |
| ribs | [PyPI](https://pypi.org/project/ribs/): 0.12.0, 2026-07-22; [repository license](https://raw.githubusercontent.com/icaros-usc/pyribs/master/LICENSE): MIT. |
| Optuna | [PyPI](https://pypi.org/project/optuna/): 5.0.0, 2026-09-07, MIT. |
| Nevergrad / imitation | [Nevergrad](https://pypi.org/project/nevergrad/): 1.0.12, 2025-04-23, MIT; [imitation](https://pypi.org/project/imitation/): 1.0.1, 2025-01-07, MIT. |
| scikit-learn / LightGBM | [scikit-learn](https://pypi.org/project/scikit-learn/): 1.9.1, BSD-3-Clause; [LightGBM](https://pypi.org/project/lightgbm/): 4.7.0, [MIT license](https://raw.githubusercontent.com/microsoft/LightGBM/master/LICENSE). |
| evosax / EvoTorch / QDax | [evosax](https://pypi.org/project/evosax/): 0.3.1, Apache-2.0; [EvoTorch](https://pypi.org/project/evotorch/): 0.6.1, Apache-2.0; [QDax](https://pypi.org/project/qdax/): 0.5.0, MIT. Split the shared license cell into explicit tool mappings. |
| neat-python / PettingZoo / Ray | [neat-python](https://pypi.org/project/neat-python/): 2.0.0, BSD-3; [PettingZoo](https://pypi.org/project/pettingzoo/): 1.27.0, MIT; [Ray](https://pypi.org/project/ray/): 2.59.0, Apache-2.0. |
| CleanRL / d3rlpy / OpenSpiel | [CleanRL](https://pypi.org/project/cleanrl/): 1.2.0, 2023-05-22, MIT; [d3rlpy](https://pypi.org/project/d3rlpy/): 2.8.1, MIT; [OpenSpiel](https://pypi.org/project/open-spiel/): 2.0.2, Apache-2.0. |
| SparCraft / UAlbertaBot / microRTS | [SparCraft repository](https://github.com/davechurchill/SparCraft) and [UAlbertaBot license](https://raw.githubusercontent.com/davechurchill/ualbertabot/master/License.md): MIT; [microRTS license](https://raw.githubusercontent.com/Farama-Foundation/MicroRTS/master/LICENSE): GPL v3. No code was copied. |
| irace | [Upstream DESCRIPTION](https://raw.githubusercontent.com/MLopez-Ibanez/irace/master/DESCRIPTION): development version 4.5.0.9000, GPL (>= 2). This confirms the license, but is not verification of the current CRAN release; CRAN mirrors could not be retrieved. |

**N1 — Low, concrete corrections:** [EvoTorch](https://docs.evotorch.ai/latest/) is built on PyTorch, not JAX; the C++ simulation bottleneck still supports deferral. [OpenSpiel's API](https://openspiel.readthedocs.io/en/latest/api_reference.html) explicitly supports simultaneous joint actions (`apply_actions`, `is_simultaneous_node`); action abstraction/wrapper cost is the reason to defer, not turn-based-only support. Give each tool its own license and a versioned link. CRAN irace retrieval failed here; replace the vague “CRAN 4.x” with a retrieved version/package license record or mark it unverified. Keep pycma; defer extra optimizer/classifier dependencies until a measured need. Tree readability also requires explicit size/depth limits and a native deployment path, not merely choosing boosted trees.

## Recommended disposition and boundaries

The Claude drafter should fix F1–F8 in the note and record each cause in its self-audit. The actionable sequence is: define participation/evaluation/primitive contracts and establish T-elite/shadow baselines; react; V1 timing; V2 geometry using the existing teacher planner; then budgeted adaptive portfolio search and distillation if they add measured low-loss series benefit; repertoire last. Evaluation design precedes all comparisons; changing a fitness does not need to displace the owner's primitive order.

These are recommendations for a future authorized development batch. This review authorizes no run, design change to a registered experiment, source qualification, or acceptance. Keep old receipts unchanged. PLAN_CURRENT.md was deliberately neither edited nor staged under the user's scope; the drafter/owner should track this review and the eventual disposition at B8.

Supplemental owner recheck: the verbatim request above was sent to a separate Codex reviewer (`review_recheck`), read-only. This was a same-family check of this review, not another cross-family acceptance. It corroborated the spec/interface/branch findings, SSS counterexample and cost arithmetic, with no blocking corrections. Its low wording finding about the series stop condition was fixed to explicitly include every fight not won by elimination. The main review remains Codex reviewing the Claude-authored note.

Delivery: `.git` is read-only in this session; this new review file is left uncommitted as requested. No alternate repository, hook bypass or broader staging was used.
