# Experiment 0e — replacement and connection, two-piece first (DRAFT for owner approval; nothing is built or run)

Exploratory line under decision 0028; not a milestone, not C6 evidence. Drafted 2026-10-04 from the owner's direction (messages: "if small part works - we can confirm if they works if we replace them in normal ai … how we define connection … where to become stable or proper structure - min requirement it structure that can function, better it perform - more wins or more stable it is", and "maybe connection first can be 2-3 system connect or more then one and if they work efficiently or improve overall performance … performance as metric of connection quality?"),
then reviewed by GPT (`docs/reviews/tactical_0e_plan_review_gpt.md`, CHANGES_REQUIRED, R1 to R10; a third model family, **not** the Claude-Codex pair `AGENTS.md` names, and its verdict is not owner approval). **Before approval no project code runs.** New code goes in new files only (a new package, not `tcd_common/`, whose files are hashed into the 0d run record); `tactics.py` and every recorded harness stay frozen.

## 1. The questions and what this proposal does not cover

1. **Replacement.** Can our learned pieces replace the scripted ones with bounded loss, and can the components of a competent conventional ("normal AI") policy be swapped with ours?
2. **Connection.** Is there a precise, falsifiable definition of a connection between two pieces, and is the connection used and useful (not only present)?
3. **Stability.** Is the assembly a structure that functions, performs better than conventional baselines, and keeps working under single faults on the connection within a stated envelope?

**Separate studies, not part of this approval:** the three-piece ladder (needs a qualified third behavior, section 9), adapter calibration (old Part C), connection discovery, a large data-efficiency sweep of flat networks, the squad level, learning from outcomes. Performance gain over ablation is an **assembly-quality** endpoint; it does not by itself identify the value of a connection (a second capable piece can raise performance without consuming any signal), so connection value is attributed by **signal cuts with the pieces held fixed**.

## 2. Definitions (what "connection" and "stable" mean here)

A connection is an **identifiable causal path with a contract**: `z_i = f_i(x_i)`, message `m = c(z_i, allowed context)`, `a_j = f_j(x_j, m)`. The contract for the one connection tested here:

| Field | AIM to MOVE |
|---|---|
| Message | identity of a living enemy slot inside one observation snapshot (categorical, not distance-scaled); dead or invalid slot is rejected, never silently routed |
| Connector (gather) | the relative position of that enemy (arena-distance units, own frame) and the unit's preferred range; scaled by the registered feature map, then the frozen training standardizers |
| Receiver output | a dimensionless step vector (speed converts it to distance per tick); direction and magnitude both reported |
| Lifetime, state | one tick; no hidden state; the same decoded enemy identity is used for the attack and the step |
| Other paths | none: MOVE sees no enemy-slot array, only the gathered message and preferred range |

Four things are kept distinct: **structural existence** (the path is implemented), **causal use** (changing only the message, with weights, observations and other paths fixed, changes the downstream response on predeclared message-sensitive states), **usefulness** (the intact path beats a registered cut, default or shuffled path on held-out play), **robustness** (quality retained under registered single faults). "Stable" is a **qualification of a particular assembly inside a tested envelope**, not a requirement for a connection to exist, and a constant losing policy has zero spread: so functioning and quality come first.
Levels: **functions** (legal execution on the declared domain plus a positive held-out advantage over rush), **high-fidelity working assembly** (functions and within 0.05 of the teacher on win score and on joint-action fidelity), **stable within the tested envelope** (functions, seed-repeatable, bounded loss under the registered single faults).

## 3. Task, data, and the comparison set

Task: the unchanged two-behavior sandbox (`tactics.py`, burst off), fresh development and final entropy, fresh pools; opponents rush and kiter, equal weight. **30 fresh independent seed blocks** (training pool, initialization, held-out pool, episode roster, perturbation streams), a starting budget not a verified power. Primary N = 3,000 unique source states; episode-level splits before any row sampling; no silent pool truncation. **Episodes per cell:** at least 200 per opponent, final value set from development precision and a wall budget of about two hours (see section 9); paired episode rosters, stratified over the frozen type mixes, with perturbation draws keyed by seed, episode, tick, unit and edge so they cannot alter the next episode's start.

Implementations of each slot: **O** the scripted teacher piece; **L** our learned piece (frozen after fitting; registered recipe); **J** the conventional conditional policy: a jointly trained target-conditioned policy (the 0d S1 design, stronger recipe tuned on development) whose real AIM and MOVE branches satisfy the contract; **D** degraded controls (nearest-enemy AIM; approach-only or noisy MOVE), used for assay sensitivity and never counted toward a compatibility claim. Separately labelled **hybrid diagnostics**: the argmax and step outputs extracted from a tuned flat network (a flat network's step output is unconditional: it cannot be told which enemy to act on, so this is an *action-channel replacement*, not a target-conditioned module swap) and standalone conventional modules (a different competitive ordinary architecture, trained separately on the same slot labels and inputs). Rush R and the full teacher T are the reference policies.

**Conventional baseline qualification (development only).** Whole flat F*-plus: widths 16/32/64/128, depths 2/3/4, tuned duration and regularization, heads continuous, discrete and mixture, per-slot step heads named honestly as structured conventional policies; selection on closed-loop development score with a fixed tie-break on a macro average over **disjoint** hold, approach and back-off strata; bounded frozen search budget; boundary optima reported. **Gate:** a policy may serve as a replacement host or as a comparator only if the lower bound of its median win-score gain over rush exceeds 0.03 overall and is positive per opponent (0d's F1 failed this, 30 of 30 seeds below rush). A weak F*-plus blocks only the claim against that flat family; J can qualify the ordinary-policy replacement claim; learned-for-oracle replacement and signal attribution do not depend on F*-plus.

## 4. Primary claims, endpoints and verdict rules

Raw win score is primary (win 1, draw 0.5, loss 0, two opponents equally weighted; actual win, draw and timeout shares also reported). **Headroom gate:** `D = median_s[W_s(T) − W_s(R)]`, one D for the task; require `L(D) > 0.15` overall and `> 0.10` teacher-minus-rush per opponent, else normalized endpoints are INDETERMINATE. Normalized gain `Q = median_s[W_s(P) − W_s(B)] / D` (ratio of paired medians; no clipping; never normalize fidelity by win headroom). Joint-action fidelity as in 0d (chosen enemy tied-best and step matches the teacher's step toward it), with strata disjoint (hold, approach, back-off), required counts of at least 100 multi-enemy states with a uniquely best teacher target and 30 per movement stratum per seed.

**Four primary compound claims**, each at error 0.0125 (total 0.05). A positive claim is a **conjunction**: every component must pass at that error; REFUTED needs a within-claim adjusted negative witness; otherwise INDETERMINATE. Intervals: distribution-free binomial order-statistic bounds on sorted per-seed paired differences (the largest admissible index, abstain if none), exact Clopper-Pearson for binary shares, normalized predicates from numerator and denominator intervals each at half the error (denominator lower bound ≤ 0 gives INDETERMINATE). Rules for a lower-bound predicate `x > t`: SUPPORTED if `L(x) > t`, REFUTED if `U(x) < t`, else INDETERMINATE; equality is INDETERMINATE. Ordinary 95% bootstrap intervals are shown as descriptions only.

| Claim | Components (all must hold) |
|---|---|
| **A. Replacement** | prequalification: learned AIM admissible rate `L > 0.85` and learned MOVE success `L > 0.90` with each stratum `> 0.85`; win and fidelity contrasts `L > −0.05` overall and per opponent for (L_AIM,O_MOVE), (O_AIM,L_MOVE) and (L,L), each against (O,O); competent swaps into and out of J: win and fidelity `L > −0.03` for (J_AIM,L_MOVE) and (L_AIM,J_MOVE) against (J,J) |
| **B1. Useful connection** | intact (L,L) against each registered cut with the **same pieces**: (a) default message from the same observation (nearest enemy), (b) wrong living target, (c) zeroed message: raw win gain `L > 0.02` and normalized `L > 0.05` against each; and a directed message-sensitive control (reversing a known approach or back-off message) giving joint-fidelity loss `L > 0.10`, otherwise the assay cannot establish causal sensitivity |
| **B2. Stable within the tested envelope** | functions (`L(W(P) − W(R)) > 0.03`, legal execution); exact share of blocks with `W(P) − W(R) > 0.10` has `L > 0.80`; binomial-quantile `U(IQR of W(P)) < 0.05`; single-fault small envelope (position noise radius 0.02 of a development-calibrated reference distance, wrong living target fraction 0.01, scale factors 0.9 and 1.1): `U(win loss) < 0.03` and `U(joint loss) < 0.03` per fault; the teacher under the same faults is reported as a control |
| **B3. Stronger than a qualified conventional baseline** | gated on the baseline gate above: `L(W(L,L) − W(F*-plus)) > 0.03`; "wins more and is less variable" additionally needs `U(IQR(L,L) − IQR(F*-plus)) < −0.01` (otherwise advantage and repeatability are reported separately) |

Reported, not primary: the full AIM x MOVE matrix (all implementations crossed, descriptive attribution; inference only on the registered finite contrasts), every Delta of every fixed alternative, the full dose grids, the seedwise switching envelope, worst-case losses, and swap results (deliberately degraded implementations are excluded from any interchangeability claim; competence of each recipe family is qualified on development, membership frozen, every final seed kept).

## 5. Perturbation protocol (the wire only)

Fixed-state diagnostics preserve each physical snapshot and its true teacher labels; closed-loop play preserves initial conditions, world rules and the opponent policy and lets trajectories diverge (encountered-state fidelity regenerates evaluator labels from each arm's actual state and never feeds them to the policy). Dose families: position noise uniform in a disk of radius {0, 0.02, 0.05, 0.10} times the reference distance; wrong living target at fractions {0, 0.01, 0.05, 0.10} (whether the attack target or only the step message is wrong is two separate interventions); scale factors {0.5, 0.9, 1, 1.1, 2} on the position message; ordering: an uncompensated wrong-identity message against a consistent encode-decode relabeling (a positive control that must preserve the routed input exactly) and an irrelevant-location sham. Record eligible and applied counts and sham interventions. Out-of-domain handling is registered and its frequency recorded. Combined faults and recovery after a transient fault are not covered unless separately registered. The defensible wording is "bounded loss within this tested envelope", never universal graceful degradation.

## 6. Normalization ledger

| Quantity | Units and normalization |
|---|---|
| AIM message | living-entity identity in one snapshot; categorical |
| Gathered position, preferred range | arena-distance units, own frame; features divided by 10 and 5, then frozen standardizers |
| MOVE output | dimensionless step vector; speed converts it to distance per tick; magnitude reported with direction |
| Fidelity | proportions; 10-degree two-action tolerance retained; strata disjoint with counts |
| Episode score | mean of 0, 0.5, 1 per opponent, equal-opponent aggregate, then paired median over blocks |
| Gain | raw score points; paired-median contrast over the common qualified D; no clipping |
| Seed spread | IQR of raw per-block score |
| Data and work | unique states, scalar labels, counterfactual teacher queries, parameters, optimizer work and wall time reported separately |

One unit-assembly level; no squad quantity; the evaluator's raw state access is not an input to a piece.

## 7. Stop conditions (yes/no, one action, one role)

| Question | Action | Role |
|---|---|---|
| Is the **registered specification** unapproved by an explicit owner message that names it? | no recorded run | drafter |
| Are task, interfaces, defaults, recipes, endpoints, seed derivation and caps not registered before final sampling? | refuse to start | implementer |
| Does development fail the headroom gate? | revise the task proposal | drafter |
| Does a conventional-baseline or piece prequalification gate fail on development? | the dependent claim is INDETERMINATE or the comparator is returned for revision | drafter |
| Is any required pool or stratum undersized, or any seed missing, non-finite, illegal, or a cap reached? | run INCOMPLETE; no seed dropped or replaced | implementer |
| Is the one-minute load above the registered start threshold? | refuse to start (enforced in code and recorded) | implementer |
| Does any gate recorded in the configuration lack code that enforces it? | fix before registration | implementer |
| Is a claim stronger than its recorded scope? | wording correction | reviewer |
| Is the pre-run **cross-family** review of the registered files missing, or has any fix since it not been re-reviewed? | do not start | owner |
| Would a bar, margin or comparator change after a recorded result exists? | no; register a new revision | drafter |

## 8. Development, registration and review order

(1) **Owner approves this scope** (decisions below). (2) Development on its own entropy, committed with raw results: task headroom D; baseline qualification (F*-plus, J, standalone modules) and piece prequalification; perturbation sensitivity (the directed control and shams); precision and cost (episodes per cell, wall budget, and a check that every compound claim is attainable at 30 blocks: the exact lower bound for 30 of 30 successes at confidence 0.9875 is 0.844, above the 0.80 share bar). (3) Specification and `SPEC_0E.json`, new code and tests, committed: the registration boundary, with every recorded gate enforced in code. (4) **Cross-family review (Codex or GPT) of the registered files, fixes, and a re-review of any fix, before the run** (the 0d run started 90 seconds after a fix with no re-review). (5) Smoke. (6) **Explicit owner approval of the registered specification**, quoted in the decision record, then one recorded run from a clean tree with the load recorded and enforced. (7) Report with corrections-first wording and a separate result review. Test timing: tests run once at the end of each change batch.

## 9. The third piece (ladder) is conditional

A three-piece ladder needs a third behavior that is necessary in the teacher. The current sandbox has two active behaviors and the burst is disabled (the ability piece failed earlier on rarity). Recommended third piece: **ABILITY**, a ready/cooldown/target-dependent burst decision, in a **new task revision in new files** (never by flipping `USE_BURST` in the frozen module), with opportunity cost, a necessity gate (switching it off hurts the teacher; both never-fire and always-fire alternatives registered), at least 100 positive and 100 negative eligible held-out decisions per seed, balanced accuracy and class recall rather than overall accuracy, and conventional full-action baselines on the same task. If it qualifies in a bounded development effort, a **separate proposal revision** adds the fixed ladder (prefixes AIM, MOVE, ABILITY; fixed leave-one-piece-out and single-piece alternatives; the signal-cut family as above); otherwise the ladder is deferred and 0e stands as the two-piece study. A fourth piece is deferred: MEMORY or COMMITMENT (needs a partially observed task and a recurrent baseline given the same history) or FOCUS (a squad behavior needing a coordination-necessity gate).

## 10. Review disposition (the drafter's defects, causes and fixes)

| GPT item | Defect in the draft sent to GPT | Cause | Fix |
|---|---|---|---|
| R1 comparator | "best alternative without the connection" mixed three different questions | I used one phrase for single-piece, leave-one-out and signal-cut comparisons | claims A to B3 each name their fixed comparators; connection value is attributed by same-piece signal cuts (B1); no seedwise switching comparator |
| R2 flat as a piece | the flat step output ignores which enemy is chosen | I called an unconditional output a MOVE piece | hybrid diagnostics labelled as action-channel replacement; J (conditional) and standalone modules are the real replacement hosts |
| R3 ladder task | assumed a third necessary behavior | I did not check the task | ladder moved to a conditional separate revision (section 9) |
| R4 normalization | divided by an unqualified teacher-minus-rush | I treated the teacher as a ceiling | headroom gate, common D, raw results first, no clipping |
| R5 stability | seed spread as "stable" | a constant loser has zero spread | functioning first; single-fault envelope with loss bounds; lower-tail share; no smoothness claim |
| R6 adapter | called supervised recovery "connection" | I did not separate calibration from discovery | adapter study separate and renamed calibration; discovery its own proposal |
| R7 bars and gates | loose bars; a recorded gate not enforced in code | drafted as an outline | sections 4 and 7: executable rules, enforced gates, compound claims at 0.0125 |
| R8 baseline strength | 0d's flat baseline plays below rush | tuned to the wrong objective at one N | section 3 qualification gate scoped per claim; selection on play and disjoint strata |
| R9 wording | "without loss" and the "20 times" claim | overreach | corrected in `REPORT_0D.md`, `MOTIVATION.md`, `README.md`, `CORRECTIONS.md` (2026-10-04) |
| R10 governance | review is not approval; run approval was my reading | I treated chat messages as approvals | stop rows require an explicit owner message naming the registered specification; decision record quotes it |

## 11. What this will not show

Not geometry, not oscillators, not "vibration", not an RRG hypothesis (no learned geometry-to-mode loop, no background transformation); not discovery of a connection (the interface is hand-specified and tested); not a statement about all normal AI or all flat networks; not a hierarchy result. A pass shows bounded replacement, a used and useful connection and a bounded-stability envelope for one two-piece unit in one sandbox against a qualified baseline.

## 12. Decisions requested from the owner

1. Approve the scope of sections 1 to 8 (two-piece replacement and connection study, development first), or amend it.
2. Confirm that adapter calibration, connection discovery, the three-piece ladder and the squad level are separate later proposals.
3. Confirm that a cross-family review of the registered files (with re-review of fixes) is required before the recorded run, and which reviewer.
4. Ratify or reject the open **[R]** items in decision 0028 (in particular item 8, the 0d run approval).
