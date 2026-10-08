CHANGES_REQUIRED
Reviewer family: Codex
Reviewed commit: 1187a8745c0acb233a98de8c7c2e4e5aeb6168e0
Review date: 2026-10-08

Revision 2 repairs the owner-order, interface, clone-semantics and literature-summary problems. The ranked engineering sequence is appropriate: establish contracts and teacher/shadow baselines, copy react, compare V1 timing, copy V2 geometry, then consider supporting changes and conditional search/distillation. Three corrections remain before the note guides evaluator or curriculum implementation: the new series proxy is not a valid expected-streak calculation as written; its projectile-tail and cost definitions disagree; and the proposed hard-opponent sampling input reverses difficulty. These do not justify replacing the owner's primitive order or commissioning general search first.

Owner request received verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

## Scope and identity

Read AGENTS.md, the complete research note revision 2 and its self-audit, round-1 findings F1–F8/N1, SHAPE_LAB_SPEC.md §§1–12, KILLERS_V7_REGULAR.txt, and selected delivered native interface/decision/branch sources. Spot-checked primary papers, publisher metadata and upstream tool documentation through browsing. No project code, tests, fights, pilots, benchmarks or mutation probes ran. No file inside the concurrent `s4_shape_lab_v1/` build was read or edited. Findings concern the note and its future proposals, not that build.

The three task inputs were clean against HEAD when reviewed. SHA256 identities:

- Research note: `37c7f25801b382dede9ac8847c7f0bc4b1b27b517df08ea54e3d315590d02549`.
- Shape-lab spec: `a19136ae4b973e259cdb38258a40a0ce023f0e8bb8df26fdab897cd1f709cd1b`.
- Killers summary: `ae99f065393aea642757d45bf03df5bd0e7ee2a28c08d2e198fe0b5d39cf6257`.

Line references below are to the research note at the reviewed commit unless stated otherwise.

## Round-1 disposition

| Finding | Round-2 check |
|---|---|
| F1: owner sequence/oscillator | Resolved (§§0,4,9). React → V1 → V2 is explicit; central-sync comparison, landing/launch spread, hold cost and one/two-gun cases are included. The later selector cannot replace local coupling. |
| F2: primitive interface/composition | Resolved at research-prerequisite level (§3.2; spec §12). Projectile/cast observations, aim/hold/release commands, arbitration, separate shadow state/RNG, joint volley labels and sparse-army coverage are required. Rotation is constrained rather than presumed compliant. Actual adapter/arbitration contracts remain a future design gate. |
| F3: series objective | Partially resolved. Correct series rules, streak-primary reporting, denominators and healed-survivor distinction are present. The newly introduced proxy creates R2-F1/F2 below; the self-audit must not call this an executable evaluator yet. |
| F4: clone/information boundary | Resolved as a declared gate (§6). Default branch thinking suppression, parity or ranking-error requirement, oracle/deployable separation and sampled continuation caveats are retained. The source expression at line 293 should be `thinkTeams & (1 << me)`, not `thinkTeams & team`; the prose interpretation is correct. |
| F5: feasibility/accounting | Substantially resolved (§7): no measured branch-cost claim, continuation factor included, expensive shadow/disagreement work acknowledged, pilot deferred. Correct the new tail and dimensional mismatch under R2-F2. |
| F6: SSS/SSS+ counterexample | Resolved (§2.2). Fixed SSS failure, SSS+ recovery and the POE small-case minimum match Table 1. |
| F7: curriculum versus yardstick | Official-pool separation, independent draws, survivor states and stress distributions are resolved (§8). The hard-sampling input has a new polarity defect, R2-F3. Fit/validation split and holdout-use rules remain N1. |
| F8: universal claims/scoping | Substantially resolved. BC is a baseline, not a ceiling; PPO regressions, historical splash scope, enemy-range kiting caveat, teacher-free AlphaZero and model-speed tradeoffs are explicit. Launch-count causality still needs N2's qualification. |
| N1: tools | Main corrections resolved: EvoTorch/PyTorch, OpenSpiel simultaneous actions, individual licenses, irace development version/CRAN uncertainty and native tree constraints. Snapshot links and attribution nits remain N3. |

## Required findings

### R2-F1 — High: repair the expected-streak proxy and its loss preference

Locations: lines 256–273, 279–282, 447, 492, 530.

The proposal calls `J = P̂_win × (1 + V(m̂,k))` expected fights won, but `m̂` is a mean survivor vector, not a distribution conditional on winning. In general, `V(E[M])` differs from `E[V(M)]`; role counts were introduced precisely because continuation value can be nonlinear at the last gun. Survival probabilities evaluated only from HP/threat also do not specify the final, victory-conditioned composition. These are substantive approximation choices, not normalization details.

Illustrative counterexample, not a measured engine result: both candidates win the current fight with certainty. A retains either two or zero guns with equal probability; B always retains one. Both have mean one gun. If future wins require at least one gun, their continuation expectations differ by a factor of two while the proposed mean-composition proxy ties them. A lookup on integer counts also has no defined treatment for fractional expected counts.

The fallback at line 272 is independently invalid: raw `√hp × dpf` is not a probability and may exceed one; a side-difference LTD2 can be negative. Replacing `P̂_win` with it destroys both the stated bounds and expected-fights units. Calling it a heuristic does not make substitution into this formula valid.

Finally, at fight 10, `V(·,10)=0`, so this objective treats all certain wins identically whether one unit or nearly the entire army dies. The owner asks to avoid losses. Reporting casualties as secondary metrics does not specify how candidate selection handles equal streak estimates, uncertain comparisons or the final fight.

**Concrete fix:** define a reference value under a fixed, named continuation policy π and the official random-series rules:

`Jπ(s,a,k) = Eπ[ I(current fight won by elimination) × (1 + Vπ(M,k)) | s,a ]`.

Here M is the actual healed survivor composition at the canonical fight terminal, and `Vπ(M,10)=0`. Estimate the joint win/composition outcomes by sampled continuations, or label a fitted approximation explicitly. A factorization is acceptable as `P(win) × (1 + E[Vπ(M,k) | win])`; replacing that conditional expectation by a value at mean composition needs measured error bounds. Name the policy/data identity that V evaluates; changing the deployed policy can invalidate its calibration. Document any retained survivor attributes that make role counts an insufficient state summary.

Keep LTD2 as a separate, unit-labelled ranking baseline until a held-out calibration maps features to bounded win probability. Define a streak-primary, loss-aware selection/tie rule before use, including final-fight survivors, retained gun capability, uncertainty and a non-passive timeout treatment. Do not invent a tolerated casualty budget. The existing ranking-validation gate remains necessary, but cannot repair an undefined formula or substitute for probability calibration. These are future design/validation requirements, not authorization to collect data now.

### R2-F2 — Medium: define projectile-tail semantics and charge for the actual branch

Locations: lines 259–273, 320–345, 348–358; delivered `world.cpp:126–128`.

§5.2 extends a branch beyond H until pre-H shells land, but evaluates `s_H` and charges only H/Δt ticks. It does not say which actions/controllers continue during the extension, whether post-H launches are included in the tail state, or which time the probability and composition estimators consume. Continuing controllers can introduce more committed damage; freezing their actions changes the model. The delivered world's `done()` stops on elimination/timeout, so a drain instruction must also resolve whether terminal state wins precedence over in-flight shells. Healing immediately on enemy elimination and then applying delayed damage would be a different series rule.

The worked-cost line 332 also uses `H × c_tick` for a quantity in core-seconds although c_tick is defined per tick; the formula correctly uses `(H/Δt) × c_tick`. The 0.96–7.2 and 86–648 arithmetic is correct only if 0.02–0.1 denotes the total CPU cost of one rollout. No branch timing was measured here.

**Concrete fix:** name the canonical elimination/timeout event and precedence, including simultaneous elimination and elimination on the timeout tick. Preserve that terminal rule; do not let a search-only drain redefine carry-over. For non-terminal branches choose and document a bounded extension under the same stated continuation, or a separately labelled pending-projectile tail estimator. Distinguish nominal H, actual evaluation time H_eff, pre-H tracked projectiles and post-H actions/projectiles. Account for aimed shots as well as shells where their delayed damage matters. State a maximum extension and fallback.

Use measured actual tick/decision counts through H_eff (and any nested search) in the cost formula, and replace line 332 with `(H/Δt) × c_tick ≈ 0.02–0.1 core-s per rollout` if that is the intended revision-1 assumption. The pilot must measure tails, teacher shadowing and recording for the actual label path. Comparing S=2 with S=3 measures short-sample stability, not accuracy against a reference; include a bounded stronger-reference comparison or retain accuracy as unverified.

### R2-F3 — Medium: correct the polarity of hard-opponent curriculum sampling

Locations: lines 68, 391–393, 396, 534.

The note defines `f_hard(x) = (1−x)^p`, then proposes x as the probability that a cell ends the series or an own-loss fraction. Both increase with difficulty. The formula therefore prioritizes easy/low-loss cells. For p=2, failure probabilities 0.9 and 0.1 get weights 0.01 and 0.81 respectively. The uniform mixture prevents zero coverage but does not fix this inversion.

The cited [PFSP survey §3.2.5](https://arxiv.org/pdf/2408.01072) defines the input as the training agent's **win probability** against that opponent. The note's proposed substitutions need a complement or a changed priority function.

**Concrete fix:** use success/survival probability x with `(1−x)^p`, or use a bounded difficulty d with `d^p`. Define perspective, normalization across cells, ε in `(0,1]`, and an all-zero-weight fallback. Use a Bernoulli/Beta model for series-ending events; do not treat correlated per-unit deaths or a continuous role-weighted loss fraction as independent Bernoulli observations without a stated observation model. Retain separate training/stress reporting and the uniformly sampled regular-skill yardstick.

## Non-blocking notes and design gates

**N1 — Medium, before fitting/tuning:** §5.2 says V is fitted from series data, and §8 defines D/T/L/R, but it does not allocate proxy-fit, calibration and ranking-validation data or define reuse. Ten descriptive series per arm cannot support an unrestricted composition lookup over many role-count combinations. Repeatedly selecting on D/R makes them training information even when no parameters are directly fitted to them. Specify splits, full-series grouping (ticks within a series are not independent examples), sample projection, unsupported-composition fallback, uncertainty and promotion rules before a future authorized fit. Refresh final reporting draws after selection; freeze held-out doctrine-family stress cases until the declared evaluation. This is a missing protocol, not evidence that leakage already occurred. Fresh seeds from the same 19 scripts do not establish transfer beyond those scripts.

**N2 — Low, causal language/primitive fidelity:** line 432 infers single-gun inefficiency from launch counts and similar kills. The supplied file has no launch/impact timing or counterfactual synchronization measurement. Unequal casualty timing, target types, damage and opportunities can also produce this ratio. Treat it as a diagnostic lead; V1 benefit remains a hypothesis until paired timing/coverage evidence. React remains the right first intervention because artillery dominates received damage and own recorded reactions are zero; that does not promise a particular gain. Before copying, define legal inputs and effective intent per primitive, including own cooldown/preparation, release eligibility, reaction latency and attack interruption. Compare teacher-driven and student-driven state distributions and joint battery decisions, not only agreement averaged over inactive ticks. Require damage/loss benefit and retained useful participation alongside agreement. A full T-elite reference may violate the participation rule; keep that fact visible and label any constrained variant separately.

**N3 — Low, citations:** the Pareto paper is first-authored by **Dubey**, and the co-evolution paper by **Adhikari**, with Liu a coauthor in both ([Pareto source](https://arxiv.org/abs/1803.10316), [co-evolution source](https://arxiv.org/abs/1803.10314)). Correct bibliographic labels. The Gin Rummy paper reports an empirical failure and its authors' causal-confusion interpretation, not a general DAgger limit. Keep that attribution explicit. Pin version-specific publisher pages or release tags for the tool snapshot; moving `latest`/`master` links are useful browsing links but do not preserve the audited version. Mirollo–Strogatz's theorem concerns a particular identical, all-to-all, excitatory integrate-and-fire model; it does not establish synchronization of an arbitrary sparse battery graph with cooldown/readiness heterogeneity. The note already requires few-gun tests; name graph and assumptions in the future V1 design.

## Primary-source spot-check ledger

Sources below were accessed in this review. Confirmed numerical rows do not establish their effectiveness in Astelia.

| Claim | Check |
|---|---|
| microRTS BC versus Mayari | [Goodfriend Tables 4/28, §4.3](https://arxiv.org/html/2402.08112v1): BC overall 71%, versus Mayari 44%; BC-PPO 88%/84%. TwoBasesBarracks against POLightRush 100→0; BloodBath against Mayari 40→5. Revision 2 correctly separates this from the competition winner's training. |
| SSS/SSS+/POE/PGS+ | [Lelis Table 1/§5.2](https://www.ijcai.org/proceedings/2017/0522.pdf): fixed SSS at the 56-unit four-type case is 0.46 versus POE, 0.16 versus PGS+; SSS+ is 0.96/0.95, and 0.93 versus SSS. POE minimum 0.56; PGS+ versus PGS range 0.72–1.00. Candidate first joint action followed by NOKAV continuation is correct. These use a 40-ms decision budget. |
| GAB/SAB | [Moraes & Lelis Tables 1–2](https://arxiv.org/html/1711.08101): GAB versus PGS 0.82 at 8 Zealots + 8 Dragoons, 0.81 at 32 Zealots; SAB versus SSS 0.90 at 50 Zealots. AV+ and N=4 belong to the tested configurations, as now stated. |
| Focus-fire scaling | [Usunier Table 1/§7.3](https://arxiv.org/html/1609.02993): m15v16 wc/nok_nc/c/ZO .10/.68/.81/.79; w15v17 .02/.12/.20/.49, 1,000 test battles. The implementation's damage reservations can fail when attackers die. Correct numbers and scoped interpretation; the table discussion is §7.3 rather than the note's §7.2. |
| ECSLBot | [Liu, Louis & Ballinger Table II, Eqs. 3–4, conclusion](https://www.cse.unr.edu/~simingl/papers/publish/CIG2014IMPFMicro.pdf): 14 parameters, about 21 h adaptation, unit-difference plus time fitness, additional destruction-score fitness, five-Vulture comparisons and Dragoon mention all supported. Mixed own-army composition remains the identified limitation. |
| SMAC default reward | [Official source, constructor/reward_battle](https://raw.githubusercontent.com/oxwhirl/smac/master/smac/env/starcraft2/starcraft2.py): positive-only dense default, raw enemy-death value 10, win 200, scaling enabled; no direct allied damage/death deduction in that mode. Correctly qualified in revision 2. |
| Splash mini-game | [SC2LE Table 1 and training setup](https://ar5iv.labs.arxiv.org/html/1708.04782): DefeatZerglingsAndBanelings best agent mean 96, human means 729/727; 600M agent steps (eight game steps per action). Scores, not win/dodge rates. Revised scope is correct. |
| PGS real-engine caveat | [Churchill et al. publisher abstract](https://ojs.aaai.org/index.php/AIIDE/article/view/12962) supports model sensitivity. Full PDF retrieval failed in this round; the per-scenario numbers and 10→40 ms result are not independently reverified here. They were checked in round 1 and are now scoped; this review does not claim a fresh full-table check. |
| Our stored artillery gap | KILLERS file directly supports 41.8 own deaths over all 40 fights; 74.1% artillery attribution, 77% received damage, 86% ranged/63% melee deaths, 2,940.5 enemy dodge records and 184.4/104.9 launches per fight. The 40.7 wins-only figure is separately attributed to the spec. Decision-record counts do not establish unique shells avoided. |

## Tool metadata check

The listed release versions and license mappings match current publisher records checked in this round:

| Tools | Verified snapshot |
|---|---|
| [cma](https://pypi.org/project/cma/), [ribs](https://pypi.org/project/ribs/), [Optuna](https://pypi.org/project/optuna/) | 4.5.0 / BSD-3-Clause (2026-09-13); 0.12.0 / MIT (2026-07-22); 5.0.0 / MIT (2026-09-07). ribs license also checked [upstream](https://raw.githubusercontent.com/icaros-usc/pyribs/master/LICENSE). |
| [Nevergrad](https://pypi.org/project/nevergrad/), [scikit-learn](https://pypi.org/project/scikit-learn/), [LightGBM](https://pypi.org/project/lightgbm/) | 1.0.12 / MIT; 1.9.1 / BSD-3-Clause; 4.7.0 / MIT ([license](https://raw.githubusercontent.com/microsoft/LightGBM/master/LICENSE)). |
| [evosax](https://pypi.org/project/evosax/), [EvoTorch](https://pypi.org/project/evotorch/), [QDax](https://pypi.org/project/qdax/) | 0.3.1 / Apache-2.0; 0.6.1 / Apache-2.0; 0.5.0 / MIT. [EvoTorch documentation](https://docs.evotorch.ai/latest/) explicitly says PyTorch. |
| [neat-python](https://pypi.org/project/neat-python/), [PettingZoo](https://pypi.org/project/pettingzoo/), [Ray](https://pypi.org/project/ray/) | 2.0.0 / BSD-3-Clause; 1.27.0 / MIT; 2.59.0 / Apache-2.0. |
| [CleanRL](https://pypi.org/project/cleanrl/), [imitation](https://pypi.org/project/imitation/), [d3rlpy](https://pypi.org/project/d3rlpy/), [OpenSpiel](https://pypi.org/project/open-spiel/) | 1.2.0 / MIT; 1.0.1 / MIT; 2.8.1 / MIT; 2.0.2 / Apache-2.0. [OpenSpiel API](https://openspiel.readthedocs.io/en/latest/api_reference.html) supports simultaneous joint `apply_actions`. |
| [irace upstream DESCRIPTION](https://raw.githubusercontent.com/MLopez-Ibanez/irace/master/DESCRIPTION) | Development 4.5.0.9000 / GPL (>=2). Current CRAN release remains unverified, correctly disclosed. |
| [SparCraft](https://github.com/davechurchill/SparCraft), [UAlbertaBot license](https://raw.githubusercontent.com/davechurchill/ualbertabot/master/License.md), [microRTS license](https://raw.githubusercontent.com/Farama-Foundation/MicroRTS/master/LICENSE) | SparCraft repository identifies MIT; UAlbertaBot MIT; microRTS GPL v3. No dependency was installed or code copied. |

Retain pycma and conditional adoption. This is a metadata check, not an environment compatibility or dependency-installation review. The note's expressly secondary landmark compute summaries were not exhaustively audited; they should not determine our engine's budget.

## Disposition and delivery

The Claude drafter should repair R2-F1–F3 and record each cause in the self-audit before evaluator/curriculum work relies on the note. Keep react → V1 → V2, participation constraints, joint volley labels, byte-identical shadows and conditional general search. Concrete contracts, measured branch costs and fresh paired series evidence remain future gates; this review authorizes no run, implementation change, source qualification, scientific acceptance or milestone update.

PLAN_CURRENT.md was neither edited nor staged. The drafter/owner should record this round and its disposition at B8. Existing unrelated dirty files were preserved. `.git` is not writable in this session, so only this new review file is delivered, uncommitted; no alternate repository or hook bypass was used.

Supplemental owner recheck: the verbatim request above was sent to separate Codex reviewer `review_recheck`, which checked the evaluator/cost/curriculum findings and then this complete draft read-only. It corroborated R2-F1–F3, agreed that N1 is a missing protocol rather than demonstrated leakage, and found no blocking correction. Its clarity finding was fixed: the gun-survival counterexample now explicitly gives both candidates certain victory in the current fight. This is a same-family check of the review, not another cross-family acceptance. Tracking/disposition in PLAN_CURRENT.md remains with the drafter/owner under the user's file-only scope.

Concurrent-work boundary: during final identity checking, another session advanced HEAD to `d4b8dbca7a5857b25e537e33788d6be53c464489` and appended spec §13/Amendment 6 in `14aff105a174ace5429fd020574f36ba1cf27032`. The requested §§1–12 are unchanged. This review remains of the commit and input hashes named above; it does not audit the new impact-ranking amendment or the concurrent build. The research-note and killers hashes remained unchanged at delivery.
