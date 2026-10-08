PASS_WITH_NOTES
Reviewer family: Codex
Reviewed commit: 0141ca2cc0280583ee14bc91dc67ea5d46248607
Review date: 2026-10-08

Revision 3 resolves the round-2 blocking defects at the research-note level. The recommended order remains appropriate: establish the legal interfaces, teacher/shadow baseline and measured series evaluation; confirm the owner-requested impact ranking; copy react; compare V1 timing; copy V2 geometry; then consider supporting changes and conditional search/distillation. No checked result justifies putting general portfolio search or a repertoire ahead of those mechanisms. The notes below must be addressed at their stated future design gates; this verdict does not qualify an evaluator, authorize a run or accept the concurrent lab implementation.

Owner request received verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

## Scope and identity

Read AGENTS.md, the complete research note revision 3 including §§12.1–12.2, both previous Codex reviews, SHAPE_LAB_SPEC.md §§1–13 and KILLERS_V7_REGULAR.txt. Read selected delivered native sources to check the cited interface, branch and terminal facts. Browsed primary papers and publisher/upstream tool records. No project code, tests, fights, pilots, benchmarks or mutation probes ran. No file in `astelia_cpp/s4_shape_lab_v1/` was accessed. Only this review file was created; docs/PLAN_CURRENT.md was neither edited nor staged.

The three task inputs matched HEAD with no working-tree diff. Reviewed SHA256 identities:

- Research note: `efd0155df99da4f22923d1da687d958dc668efe751e5e697fb2238ef7a0e79f4`.
- Shape-lab spec: `132398a7c1a369f91316e8658ca845a5d33372aa7268eba485630a315b65a5e7`.
- Killers summary: `ae99f065393aea642757d45bf03df5bd0e7ee2a28c08d2e198fe0b5d39cf6257`.

Line references below name the research note at the reviewed commit unless stated otherwise.

## Previous findings and regression check

| Finding | Round-3 disposition |
|---|---|
| R2-F1: invalid expected-streak proxy | Resolved in §§5.2–5.3: named continuation π; actual terminal survivor composition; joint win/composition expectation; explicit conditional factorization; no uncalibrated LTD2 probability substitution. Fight-10 losses and uncertainty are now considered. The gun-first tie preference still needs N1 below before implementation. The note explicitly calls this a future design requirement, not an executable evaluator. |
| R2-F2: projectile tail and cost | Resolved in §§5.4,7: canonical terminal precedes in-flight damage; simultaneous elimination and timeout classification are explicit proposals to confirm against the runner; pre-H shells and aimed shots, post-H behavior, bounded extension and fallback are distinguished; actual ticks, shadowing and nested search are charged. Stronger-reference accuracy is separated from short-sample stability. N2 corrects one remaining bound. Runner conformity was not checked in the excluded build. |
| R2-F3: hard-sampling polarity | Resolved in §8.2: x is our elimination-win probability; difficulty is its complement; normalization, positive uniform floor and zero-weight fallback are explicit. Bernoulli observations are fight outcomes, not correlated unit deaths or continuous loss fractions. |
| Round-2 N1: fitting and holdouts | Addressed in §5.5: separate fit/calibration/ranking sets, whole-series grouping, projection, unsupported-composition fallback, refreshed reporting after selection and frozen stress cases. These are protocol requirements, not evidence that a fit is validated. |
| Round-2 N2: causal language and primitive fidelity | Addressed in §§3.2,9: launch ratio is only a diagnostic lead; no react gain promised; active/effective intents, legal inputs, release eligibility, latency, interruption and joint labels are required. Teacher/student distributions and useful participation accompany agreement. |
| Round-2 N3: attribution and snapshots | Dubey/Adhikari author lists, Usunier section numbers, scoped Gin Rummy interpretation, scoped Mirollo–Strogatz theorem and shifted team-bit expression are corrected. Version-specific PyPI links replace the package browsing links; irace remains an explicitly unverified CRAN snapshot. Retain N4's small audit cleanup. |

Round-1 F1–F8 and N1 remain repaired at this level: owner order/local coupling, interface/arbitration, streak-primary evaluation, clone/information boundaries, full cost accounting, fixed-SSS counterexample, official-pool separation, scoped literature interpretations and corrected tool capabilities. No return to an elite-copy ceiling, guaranteed search superiority, a loss budget or counting dodge records as unique shells avoided was found in the actionable plan. Amendment 6 is incorporated in Step 0 despite the stale opening scope label.

## Findings and concrete fixes

### N1 — Medium, before evaluator implementation: gun-first is not the same as fewer deaths

Locations: lines 293–299; spec §§5,10,12.

The loss-aware tie rule says fewer expected own deaths, but orders P(≥1 effective gun survives) before total survivors. Consider fight 10, two certain elimination wins: A loses twenty units but retains a gun; B loses one unit, its last gun. Jπ is equal and has no continuation value left, yet the written rule selects A. This is an illustrative counterexample, not an engine result. Retaining a gun can have future value earlier in the series; that does not establish an unconditional gun-first preference after the series ends, or an owner-selected exchange against other deaths.

**Fix:** at fight 10, break genuinely tied win estimates by fewer expected total own deaths, then retained role capability if deaths also tie. For earlier fights, let the continuation value account for role capability and explicitly define any remaining role-versus-total-loss tradeoff before use. A gun-first exception requires an owner decision rather than being presented as synonymous with fewer losses. Keep losses on failed fights visible and retain the non-passive timeout rule. Distinguish uncertainty from equality: interval overlap is inconclusive, not proof of equivalent streak performance; define a paired decision criterion and incumbent fallback in the future protocol.

This is non-blocking for the research sequence because §5.2 expressly leaves the selection rule to be fixed before use. It is not ready to be copied literally into an evaluator.

### N2 — Low: allow an early terminal in the actual horizon bound

Locations: lines 335–341,389–398.

Line 395 states H_eff ≥ H, but the canonical terminal can occur before H. The tail section correctly stops there. The cost formula should describe actual elapsed rollout time in both cases.

**Fix:** generally use 0 ≤ H_eff ≤ H + E_max, with H_eff ≥ H only when a non-terminal branch reaches H and is extended. Charge measured tick/decision counts through the earlier terminal. Preserve terminal precedence; do not simulate extra ticks merely to satisfy the inequality. No measured timing result is invalidated here because none was produced.

### N3 — Low, sequencing and inference: separate immediate measurement from optional fitted machinery

Locations: lines 343–353,494–502; spec §13.

Step 0 references the whole evaluation and fit/validation protocol before react. A reader could interpret that as requiring a fitted Vπ before copying an available dodge rule, although §§5.2,7 correctly defer that machinery. The owner-requested impact ranking also estimates effects conditional on elite/novice baselines, not intrinsic mechanism values or guaranteed gains when copied into v7. The spec's JS spacing/escort history is a staged, baseline-dependent history, not an isolated ranking of mechanisms.

**Fix:** explicitly put canonical outcomes, paired draw streams, streak/loss reporting, legal adapters, arbitration and non-mutating shadows before the first copied primitive. Keep the mandated C++ impact ranking after the lab run. Require Vπ fitting/calibration only before a method actually uses that estimate. Label leave-one-out/add-one-in effects by baseline, preserve known interactions and cost, and confirm transfer through the already proposed paired v7 comparisons and react × volley ablations. Do not silently change the owner order from an elite ablation ranking.

### N4 — Low: finish the scope and historical self-audit cleanup

Locations: lines 3–7,623,587–611,656.

The opening still names §§9–12 although Step 0 uses Amendment 6 (§13). The round-1 F3 row says “Fix in this revision” and retains the withdrawn mean-composition proxy; §12.2 supersedes it, but the row reads as current guidance. “One version-pinned link per tool” also has explicit exceptions: irace is a moving development DESCRIPTION, and the three source repositories have no commit/tag snapshot. Two versioned PyPI pages could not be fetched in this review, so this review cannot corroborate the historical claim that all sixteen returned HTTP 200.

**Fix:** extend the opening scope to §§9–13; label the §12.1 F3 proxy as revision-2 history superseded by §12.2; state the snapshot exceptions rather than making the table heading universal. Before any dependency adoption or code reuse, capture the specific release/source identity and license. Retrieval failure here is not evidence that the listed EvoTorch/QDax versions are wrong: publisher release records corroborate them.

## Primary-source spot-checks

Confirmed numbers concern those sources' experiments, not demonstrated Astelia effectiveness.

| Load-bearing claim | Round-3 check |
|---|---|
| microRTS BC versus Mayari | [Goodfriend §4.3, Tables 4/28](https://arxiv.org/html/2402.08112v1): 71% overall/44% versus Mayari for BC; 88%/84% after PPO; TwoBasesBarracks–POLightRush 100→0 and BloodBath–Mayari 40→5. Post-competition experiment, correctly separated from the competition winner's training. No copy-quality ceiling follows. |
| SSS/SSS+/POE/PGS+ | [Lelis §5.2, Table 1](https://www.ijcai.org/proceedings/2017/0522.pdf): 56-unit four-type fixed SSS 0.46 against POE, 0.16 against PGS+; SSS+ 0.96/0.95 and 0.93 against SSS; POE minimum 0.56; PGS+ versus PGS 0.72–1.00. Both players' first joint action uses candidate script assignments, then NOKAV continuation; 40-ms decision limit. Correct evaluation and adaptive-budget lesson. |
| GAB/SAB | [Moraes & Lelis Tables 1–2](https://arxiv.org/html/1711.08101): GAB–PGS 0.82 for 8 Zealots + 8 Dragoons, 0.81 for 32 Zealots; SAB–SSS 0.90 for 50 Zealots. AV+ and N=4 are experiment-specific configuration choices. |
| Focus-fire scaling | [Usunier §§7.2–7.3, Table 1](https://arxiv.org/html/1609.02993): wc/nok_nc/c/ZO .10/.68/.81/.79 on m15v16, .02/.12/.20/.49 on w15v17; 1,000 battles against built-in AI. Scenario-dependent results and attackers dying before reserved damage are correctly scoped. |
| ECSLBot | [Liu, Louis & Ballinger Table II, Eqs. 3–4, conclusion](https://www.cse.unr.edu/~simingl/papers/publish/CIG2014IMPFMicro.pdf): fourteen parameters, approximately 21-hour adaptation, unit-difference/time fitness and a second destruction-score fitness; five-Vulture comparisons and Dragoon mention. Mixed own-army composition remains the stated open question. |
| SMAC reward | [Official environment constructor/reward_battle](https://raw.githubusercontent.com/oxwhirl/smac/master/smac/env/starcraft2/starcraft2.py): dense positive-only default, raw enemy-death value 10, win 200, scaling enabled, no direct allied damage/death subtraction in that mode. The note acknowledges casualties' indirect effect. |
| Splash mini-game | [SC2LE Table 1](https://ar5iv.labs.arxiv.org/html/1708.04782): best-agent mean 96, human means 729/727, 600M training steps. Scores, not win rates or isolated splash-avoidance evidence. Correct scope. |
| PFSP and changed author labels | [Survey §3.2.5](https://arxiv.org/html/2408.01072) defines the training agent's win probability as the priority input. [Pareto paper](https://arxiv.org/abs/1803.10316) lists Dubey, Ghantous, Louis, Liu; [co-evolution paper](https://arxiv.org/abs/1803.10314) lists Adhikari, Louis, Liu, Spurgeon. Changes are accurate. |
| DAgger negative example | [Gin Rummy paper](https://arxiv.org/html/2607.06854v1) reports failure and its authors' causal-confusion explanation. Revision 3 correctly attributes that interpretation rather than declaring a universal DAgger limitation. |
| PGS in the real engine | [Publisher abstract](https://ojs.aaai.org/index.php/AIIDE/article/view/12962) supports model sensitivity. Full PDF retrieval failed in this round; the per-scenario .72/.88/.22/.94 and 10→40-ms result were checked in round 1 but are not freshly table-verified here. Retain that limit rather than claiming a complete new audit. |
| Our stored artillery gap | Killers file directly supports 41.8 own deaths across all forty fights, 74.1% artillery death attribution, 77% received damage, 86% ranged/63% melee attribution, 2,940.5 enemy dodge records and 184.4/104.9 launch records per fight. The spec separately attributes 40.7 to wins. Launch counts do not identify timing or establish a synchronization benefit. |

The team-bit expression and saveWounded behavior match the delivered native sources. World::done() supplies stop conditions, not outcome-classification precedence; the note now correctly requires confirmation against the runner. No excluded runner was inspected. Physics analogies and secondary landmark compute summaries were not exhaustively re-audited; the actionable plan does not depend on their numerical compute claims or a theorem covering a heterogeneous sparse battery.

## Tool versions, licenses and capability checks

| Tools | Verified publisher/upstream metadata |
|---|---|
| [cma](https://pypi.org/project/cma/4.5.0/), [ribs](https://pypi.org/project/ribs/0.12.0/), [Optuna](https://pypi.org/project/optuna/5.0.0/) | 4.5.0/BSD-3-Clause (2026-09-13); 0.12.0/MIT (2026-07-22); 5.0.0/MIT (2026-09-07). |
| [Nevergrad](https://pypi.org/project/nevergrad/1.0.12/), [scikit-learn](https://pypi.org/project/scikit-learn/1.9.1/), [LightGBM](https://pypi.org/project/lightgbm/4.7.0/) | 1.0.12/MIT (2025-04-23); 1.9.1/BSD-3-Clause; 4.7.0 with [upstream MIT license](https://raw.githubusercontent.com/microsoft/LightGBM/master/LICENSE). |
| [evosax](https://pypi.org/project/evosax/0.3.1/), [EvoTorch](https://pypi.org/project/evotorch/), [QDax](https://pypi.org/project/qdax/) | 0.3.1/Apache-2.0; 0.6.1/Apache-2.0; 0.5.0/MIT. EvoTorch/QDax versioned-page fetches failed; the publisher pages identify the specific release files. [EvoTorch docs](https://docs.evotorch.ai/latest/) confirm PyTorch. |
| [neat-python](https://pypi.org/project/neat-python/2.0.0/), [PettingZoo](https://pypi.org/project/pettingzoo/1.27.0/), [Ray](https://pypi.org/project/ray/2.59.0/) | 2.0.0/BSD-3-Clause; 1.27.0/MIT; 2.59.0/Apache-2.0. |
| [CleanRL](https://pypi.org/project/cleanrl/1.2.0/), [imitation](https://pypi.org/project/imitation/1.0.1/), [d3rlpy](https://pypi.org/project/d3rlpy/2.8.1/), [OpenSpiel](https://pypi.org/project/open-spiel/2.0.2/) | 1.2.0/MIT (2023-05-22); 1.0.1/MIT; 2.8.1/MIT; 2.0.2/Apache-2.0. [OpenSpiel API](https://openspiel.readthedocs.io/en/latest/api_reference.html) confirms simultaneous joint apply_actions. |
| [irace DESCRIPTION](https://raw.githubusercontent.com/MLopez-Ibanez/irace/master/DESCRIPTION) | Development 4.5.0.9000/GPL (>=2); current CRAN release still unverified. |
| [SparCraft](https://github.com/davechurchill/SparCraft), [UAlbertaBot license](https://raw.githubusercontent.com/davechurchill/ualbertabot/master/License.md), [microRTS license](https://raw.githubusercontent.com/Farama-Foundation/MicroRTS/master/LICENSE) | MIT, MIT, GPL v3 respectively. No code was copied or dependency installed. |

This corroborates the listed metadata, not compatibility of the packages with the project environment. Keep pycma; there is no measured reason here to introduce another optimizer, RL wrapper or classifier dependency.

## Remaining design gates and delivery

The note now covers the requested missing areas: actual engine branch-cost measurement, loss-aware series evaluation, teacher copying through effective react/volley intents, joint labels, late-survivor states, selection leakage and scripted-pool overfitting. Those requirements have not yet been fulfilled experimentally. Fresh seeds from the same nineteen scripts establish no beyond-pool transfer. The next useful work is the specified lab/impact evidence and bounded primitive integration, with per-change fresh paired comparisons. Keep forward-model search optional until measured cost and additional low-loss series benefit justify it.

Supplemental owner recheck: the verbatim request above was sent to separate Codex reviewer `review_recheck`, read-only. It corroborated N1–N3 and PASS_WITH_NOTES, with no blocking correction. This is a same-family recheck of this review; the main cross-family review remains Codex reviewing the Claude-authored note. The drafter/owner should record this review and the dispositions at B8 in docs/PLAN_CURRENT.md; this session is explicitly excluded from editing that file.

Delivery: `.git` is read-only in this session, so the requested single review file is left uncommitted. No staging, alternate repository, hook bypass or commit attempt was used.
