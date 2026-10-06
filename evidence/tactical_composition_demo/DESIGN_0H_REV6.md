# Design 0h, revision 6.4 (Codex round 6: APPROVE_WITH_NOTES; its two low notes applied in 18.5): an input-to-output path grown on purpose (consolidated; supersedes `DESIGN_0H_REV6_DRAFT.md` sections 2–6)

**Revision 6.1** answers the second Codex review (`docs/reviews/tactical_0h_rev6_design_review_codex_r2.md`, R2-1 … R2-11). **Section 12 replaces the clauses it names and governs wherever it conflicts with sections 1–11.** Section 13 is its self-audit. **Revision 6.2** answers the third review (`…_r3.md`, R3-1 … R3-6). **Section 14 governs over section 12 and over sections 1–11 wherever they conflict.** Section 15 is its self-audit. **Revision 6.3** answers the fourth review (`…_r4.md`, R4-1, R4-2): **section 16 governs over everything before it**, and section 17 is its self-audit. **Revision 6.4** answers the fifth review (`…_r5.md`, R5-1): section 18 governs over everything before it.

**Status:** drafted by Claude for the second Codex review. Not approved, and no execution is authorized. The base is `DESIGN_0H.md` revision 5.1: every rule not changed below stays as written there. The failure report of the 5.1 run is `DESIGN_0H_REV6_DRAFT.md` section 1, as corrected by section 4 there and by section 9 here. The 5.1 verdicts and evidence are unchanged.

**Claim scope** (Codex review finding 8):
- Revision 6 tests a **basic task response through a grown path**. A medium that grows from scratch must route its inputs to a designated output and select among them, measurably better than doing nothing, than random actions, and than the same medium fed someone else's input.
- It does **not** test a learned structural transformation, library reuse or composition. Those need a later revision with a new task, which needs owner approval.
- H-BG, H-PS and H-RBG stay NOT_TESTED.

## 1. What changes, in one table (the supersession map)

| Base section | Revision 6 | Reason (finding) |
|---|---|---|
| 3 read-out | **Designated output oscillators**, drive-masked, read wherever they are (section 3) | The output disk overlapped direct drive (C1); an empty geometric port caused the 5.1 failure |
| 3, 4 motion | C4 law unchanged, plus a **soft arena wall** at r = 6 (engineering confinement, labelled) | Groups drifted to radius 246 (D5); site attraction was a new, unit-incomplete law (C4) |
| 5 growth | Deaths D1, **D4**, D3; births **B-out**, **B-path**, B1, in that order with a capacity rule (section 4) | No rule could build a path (C2, C3); D4 defined on the directed influence graph (C5) |
| 11 G0 | Against **control M**, mirroring only B1, with every other rule common and exact matching required (section 6) | Control M was confounded (C6) |
| 11 G0' | One authoritative row (section 7) | C11 |
| 11 (new) | **G2**, task response through the grown path, on one primary task with registered statistics and interventions (section 7) | C7, C8, C10 |
| 12 stop rows | Section 8, yes/no rows with one role each, and a fixture list | C13 |
| (new) | The normalization ledger (section 2) and the related-work and claim ledger (section 10) | C12, C14 |

## 2. Normalization ledger (AGENTS.md; R5 section 4)

| Quantity | Level | Units | Estimator and window | Normalization or cutoff | Owner and access |
|---|---|---|---|---|---|
| θ_i, ω_i | element | rad, rad/s | the state; ω̂ over 10 s (base) | ω clipped to π·[0.5, 1.5] | medium |
| x_i | element | m.u. | the state | wall at r = 6 (section 3) | medium |
| C4 pair motion | element pair | m.u./s | A(1 + J cos Δθ) − B/r, mean over k ≤ 8 neighbours with r < 3 | frozen C4 constants A = B = 1, J = 0.8 | medium (frozen C4 code, read-only) |
| C4 phase coupling | element pair | rad/s | K · exp(−r²) · sin Δθ, mean over neighbours | K = 1 | medium |
| Site drive | site → element | rad/s | g_i · k_s · K_d(r) · sin(ψ_s − θ_i), K_d = exp(−r²/2), r < 3 | **zero for output members (the mask)** | world → medium |
| Wall | element | m.u./s | −γ_w (r − 6) r̂ for r > 6 | γ_w = 1 /s, a fixed engineering constant | medium |
| Influence graph G_t | medium | edges | j → i when j is in i's held phase-neighbour list (k ≤ 8, r < 3) at world step t | strict r < 3 | evaluator-side diagnostic and growth rules |
| Roots R_t | medium | set | elements with k_s > 0 and K_d(\|x_i − q_s\|) > 0 for some active site s; output members are never roots | strict reach | growth rules |
| Output members O | medium | set | elements born by B-out (an immutable role flag) | at most 4 alive | read-out |
| Read-out Z | medium | dimensionless | Σ_{o∈O} e^{iθ_o} / \|O\|; C = \|Z\| | abstain if O is empty or C < 0.05 (base) | decoder |
| Path exposure | medium | fraction | the share of world steps with a directed path from R_t to O in G_t | per episode | evaluator-side |
| Scores, n | task, seed | oriented, normalized | the base section 9 calibration (validation 0–255, **reused development evidence, labelled**) | frozen | evaluator |
| Paired Δ | task, seed | normalized score difference | per episode, paired (section 7) | none | evaluator |

Descendant reads (path exposure, lesion results) stay evaluator-side. The medium's rules see only R_t, O, G_t and the base's lock statistics.

## 3. Read-out, masking and confinement

- **Output members.** Elements born by B-out carry an immutable output flag. **The site drive term is zero for them**, whatever their position: the mask replaces geometric separation (finding C1, option 3).

  An output member's phase can change only through C4 coupling from its neighbours: through a path. Each output member logs its frame-level direct-drive exposure. It is zero by construction, which a test checks.
- **The read-out** is the circular mean over living output members, decoded by the base's task-to-action table. With no output member, the medium abstains (scored with the defaults).
- **Output members take part in the C4 law** like any element: in motion, in coupling as sender and receiver, and in neighbour lists. They differ in two things only: the drive mask, and that they are never roots. They are subject to D1, D3 and D4.
- **The wall.** For r > 6 the motion gets −γ_w (r − 6) r̂, with γ_w = 1 /s. It is an engineering confinement, task-independent and labelled. No element of the law is resonance-based. Its contribution is reported (wall-time exposure per element).

  The radius is 6 because sensors sit at 4 and drive reaches less than 3, so nothing beyond 7 can be driven.
- **Sites stay drive-only.** The draft's site attraction is **withdrawn** (finding C4): it was a new law with incomplete units. Without it, nothing anchors structure to a site except the wall and D4's liveness. Whether structures stay near the sites is then measured, not assumed (fixture F5).

## 4. Growth and death (every growth check, every 20 s; in this order)

All rules use G_t, R_t and O at the check's world step, recomputed after each removal and each birth.

| Step | Rule | Condition | Action |
|---|---|---|---|
| 1 | D1 | unchanged (base) | remove |
| 2 | **D4, cut off** | D4 timer ≥ 120 s | remove (unprotected only) |
| 3 | D3 | cost > 64 (base) | unchanged |
| 4 | **B-out** | \|O\| < 1, or the B-out timer ≥ 20 s and \|O\| < 4 | one output birth (below) |
| 5 | **B-path** | some active site s has roots, none of which reaches O in G_t | up to 2 bridge births (below) |
| 6 | B1 | unchanged (base): up to 2 births | (base) |

**The capacity rule** (finding C3): steps 4–6 are tried in this order. Each birth checks the cap (N + 1 ≤ 64) and the cost (≤ 64), and is otherwise rejected with its reason logged. Path rules come first on purpose: an output and a path are preconditions of any task response. At most 5 births happen per check (1 + 2 + 2). Birth demand, acceptance and rejection are reported by role.

**D4 timer** (continuous, per world step, finding C5): it rises by dt_w while the element is **neither** forward-reachable from R_t **nor** backward-reaching O in G_t. It resets to 0 otherwise.
- During a memory task's hidden interval, R_t is empty, so the timers run. 120 s spans more than seven hidden intervals.
- Newborns are protected for 20 s (base).
- **Liveness is not function.** D4 can keep a sensor island alive that never reaches O. The functional path is measured separately (path exposure, G2's lesions).

**The B-out timer** rises while \|O\| ≥ 1 and the output coherence over the last 100 samples is below 0.05. It resets on any B-out birth.

**B-out placement:** the first point of the fixed spiral at the origin (base spiral, j = 0 … 49) at least 0.05 m.u. from every element. Its phase is the circular mean of the phases of the elements within r < 3 of that point. If there are none, or their resultant is below 0.1, the phase is uniform from the `rev6_growth` entropy domain. Otherwise it is a normal newborn: ω = π, g = 1, empty histories, 20 s protection.

**B-path** (finding C2; a frontier rule, not a midpoint):
1. For each active site s **without a directed path** from its roots to O, in site-id order:
   - let F = the set forward-reachable from s's roots;
   - let T = the set of elements that reach O, with O included.
2. Pick the pair (a ∈ F, b ∈ T) with the smallest distance, ties by lowest ids.
3. Place the newborn on the segment from a to b, at distance r* = 0.556 m.u. from a.

   r* is the C4 in-phase equilibrium spacing B / (A (1 + J)). There the coupling weight is exp(−r*²) ≈ 0.73, against 0.018 at r = 2. This answers the bandwidth finding C3.
4. **Clearance:** if that point is closer than 0.05 m.u. to an element, try the points at r* along directions rotated ±15°, ±30° … ±90° from the segment, in that order.
5. **Progress check:** the birth is accepted only if the newborn's distance to b is smaller than \|a − b\|. Otherwise it is logged as `no_progress`, and that site is skipped for this check.
6. **Phase** of the newborn: θ_a (it copies its source, so the signal continues).
7. If \|a − b\| < r*, no birth is made: the pair should already be within coupling range. A missing edge (k-nearest saturation) is logged as `saturated`.

At most 2 B-path births happen per check, across all sites.

**What this does not guarantee** (stated, then tested): that the chain persists under C4 motion (it may clump), and that coupling across it is fast enough within a 16 s episode. Fixtures F1–F5 (section 8) measure both before any development run.

**Memory** (finding C3): under the inherited 80-of-100-samples eligibility, the 4 s visible window can never make a site eligible. remember_static therefore gives **no** B1 demand and no reward eligibility. It is evaluated only. This is declared as a limitation, not repaired.

**Reward arm credit:** unchanged (base). Output and bridge members without direct drive have e_i = 0, and output members have no drive at all, so g has no effect on them. Their survival is structural viability, not task credit (finding C9). Revision 6 makes **no claim that reward learns the action.**

## 5. World step order (complete; finding C12)

1. Read the observation, and set the drives (masked for O).
2. 5 × RK4 of the C4 RHS plus drive and wall, with neighbours held per step. The same RHS runs in live training, frozen-growth evaluation copies and both recovery futures.
3. Append sample k (base contract).
4. Adaptation (base).
5. Timers: D1, B1, D4 and B-out.
6. Every 20 s, the growth check (section 4).
7. Every 60 s, qualification (base, unchanged; collinear chains are excluded by the base's degenerate-hull rule, so a bare relay chain is not an atom).
8. Decode and act from O.

## 6. Controls (finding C6)

**The causal question of G0:** with output and path provisioning common to both, does **need-driven B1 placement and phase** beat **random B1 placement and phase**?

**Control M (registered):**
- All rules of the intact run are common: D1, D4, D3, B-out, B-path, the wall and the mask.
- **Only B1 differs.** At each check, after steps 1–5, control M attempts exactly as many B1 births as the intact run **accepted at that check**. Each goes to a uniformly random site's spiral (base placement rule), with a phase uniform in [0, 2π) from the `g0_matched` domain.
- **The same cap and cost checks apply.** No arm gets extra resources.
- **Exact matching is required:** a seed with any B1 birth that control M could not place is **G0-INCONCLUSIVE for that seed**. It is not deleted or replaced, and its matched fraction and timing are reported.
- The downstream differences (deaths, ages, path births) are outcomes, and are reported.

**Control U (descriptive, never in a verdict):** the base 5.1 queue control, with B1 off, run under revision 6's other rules.

**Cost** (corrected arithmetic): 2 arms × 8 seeds × 3 policies (intact, M, U) = 48 trainings, 50% more than the 32 of 5.1. The evaluator and the interventions add more, projected from fixture timings before any approval request.

## 7. Read-outs (seed = unit; INVALID first in every row)

**Entropy namespaces** (finding C13): `rev6_fixture`, `rev6_dev` (training), `rev6_eval` (world validation episodes **512–639**, a fresh panel), `rev6_donor`, `rev6_growth` and `g0_matched`. The old panels 0–127 are not reused for evaluation. The calibration (validation 0–255) is reused and labelled.

**The paired estimator** (finding C10):
- For a task, a seed and a comparator: d_e = n(intact, e) − n(comparator, e) over the 128 panel episodes. The statistic is the mean and the one-sided 95% lower bound of a paired t (127 df).
- **Zero variance:** a positive constant d counts as above 0, and zero counts as not above.
- The episodes are paired evaluation draws. The seeds are the independent training units. "≥ 6 of 8" is a declared development rule, not a population confidence statement.

**The primary task is perceive** (fixed now, before any data): direction selection among K visible items.
- move, remember_static and choose are reported as secondary rows, with Bonferroni-adjusted bounds (α/3 each). They never decide G2.
- The choose row requires the random comparison as well, because the old default superiority is not assumed.

**Comparators and interventions for G2** (perceive), each on the same panel and episodes, with the same carrier clock and decoder:
1. **default:** the base default actions;
2. **random:** the base random policy, from the `rev6_eval` entropy;
3. **donor input** (finding C7): the medium receives the drive sequence of a donor episode (e + 64 mod 128, the same task, a map frozen now) and is scored against the recipient's truth. Perceive is open-loop, so the donor's observation stream replays exactly. Physical-site permutation stays as the base's robustness feature and is **not** used as an intervention;
4. **path lesion:** C4 phase coupling **into** output members is set to zero for the whole episode;
5. **sham lesion:** the same number of randomly chosen non-output receiver nodes get their incoming coupling zeroed (from the `rev6_eval` entropy).

**G2, task response through the grown path** (whole final medium, both arms):
- **Task use in a seed** means all of these hold:
  - the lower bound > 0 against default, random and donor input;
  - **and** the lower bound > 0 of (sham-lesion score − path-lesion score), so the path mediates the response.
- **PASS:** task use in ≥ 6 of 8 seeds. **FAIL:** in ≤ 2. **INCONCLUSIVE:** otherwise.
- **Reported beside G2, descriptive:**
  - an **ideal single-site relay** (output = the phase of one fixed physical site): it scores near chance for perceive, because sites are permuted each episode;
  - a **strongest-site oracle relay** (output = the phase of the site with the largest k_s): it is the ceiling a pure "select the strongest" medium can reach.

  These show where the medium stands between chance and the selection ceiling. Neither is a pass condition.

**G0:**
- **The estimand:** per seed, the paired perceive difference between the intact run and control M on the `rev6_eval` panel; and coverage, as in the base.
- **PASS:** the lower bound > 0 on perceive and coverage higher than M's, in ≥ 6 of 8 seeds that are exactly matched and valid. **FAIL:** the upper bound < 0 on perceive in ≥ 6 of 8 matched seeds. **INCONCLUSIVE:** otherwise. Unmatched seeds count as INCONCLUSIVE units.

**G0', the authoritative row** (finding C11):
- **The claim:** count trend under the declared budget only.
- **The estimand:** the OLS slope of N per 100 episodes over the growth checks of the last 20% (400 episodes).
- **PASS:** |slope| ≤ 0.5, no placement rejection and no protected-over-budget state, in ≥ 6 of 8 seeds. **FAIL:** a violation in ≥ 3 of 8. **INCONCLUSIVE:** otherwise.
- **Reported per seed, never in the verdict:** cost-limited and cap-limited flags, which may both hold; demand by birth role with the exposure denominator; rejection rates; turnover; count range; uncovered-sensor exposure; path exposure.

**G1, G1c and G5:** unchanged (base). G1c copies keep the base's origin and absolute positions. **They have no output members unless a snapshot contains some**, so G1c remains descriptive structure competence, not task use. The library's functional role is deferred (finding C9).

## 8. Fixtures and stop rows (finding C13)

**Engineering fixtures** (run under `rev6_fixture`, never training or evaluation entropy; they need the owner's approval of this revision and of the fixture run):
- **F1, hand-built positive path:** a site, a chain at r* spacing and an output member. The output phase must follow the site's drive within one episode. The fixture measures the delay and whether the chain persists under C4 motion over 160 s.
- **F2, negatives:** no path, and an empty O. Both must give the default and zero path exposure.
- **F3, mask leakage:** an output member placed at a sensor must have exactly zero drive contribution.
- **F4, relays:** the single-site and oracle relays produce their declared outputs.
- **F5, growth from the initial state:** 50 episodes of the full rules from the base initial state. They must show B-out and B-path firing, a path to O for at least one site, sustained output coherence ≥ 0.05 after warm-up in perceive episodes, and a non-default output.
- **F6, hidden memory:** after visible encoding, the output during the hidden interval depends on the encoded angle under the donor intervention (descriptive, since memory is secondary).

**Stop rows:**

| Yes/no question | Yes → one action | Role |
|---|---|---|
| Is owner approval of this revision, or of its fixture run, missing? | Do not execute it | implementer |
| Does F1, F2, F3 or F4 fail its declared criterion? | Block F5 and the development run; report | implementer |
| Does F5 show no path to O, or no sustained non-default output, after warm-up? | Block the development run; write the failure report | drafter |
| Is control M unable to match exactly in the F5 pilot of the controls? | Block G0 as registered; report the feasibility failure | implementer |
| Is a source identity, unit or endpoint definition missing or mismatched? | Block execution | implementer |
| Has any protocol element changed after results were seen? | Draft a new revision with fresh development seeds, and identify any reused evidence | drafter |
| Has development stopped, and is a next step needed? | Ask the owner | owner |

**Projection:** before asking for the development run, the implementer reports the measured fixture costs, the projection for 48 trainings plus the evaluator and the interventions, and the awake and elapsed time accounting. Unattended runs use `caffeinate -i -s`. Ledgers stay outside git in chunks under 50 MB.

## 9. Corrections to earlier prose (finding C14)

- The draft's section 1 says every evaluation episode abstained. **What is confirmed:** the saved final states had no read-out member, and the aggregate scores equal the defaults. **What is not:** episode-long abstention, which was not retained, and 13 initially empty snapshots did score off the floor (`DEVELOPMENT_RECHECK_REPORT.md`).
- The draft's section 3(b) claim that G1c reads each structure at its own centre is **wrong**: G1c uses the origin read-out (review addendum 2, item 3).
- The draft's section 6 claim of "no new law" for site attraction is withdrawn, together with the term.
- Commit references use the post-cleanup hashes (`docs/HISTORY_CLEANUP_2026-10-06_MAP.tsv`). For example, the 5.1 run's import is `a9cbe83`, formerly `7e5f6b0`.

## 10. Related work and claim ledger (finding C14)

| Element | Known as | What is ours | Claimed here? |
|---|---|---|---|
| Phase-dependent attraction plus geometry-dependent synchrony (C4) | **swarmalators** (O'Keeffe, Hong and Strogatz, 2017); C4 is a local k-nearest Gaussian variant | none new | no |
| Output oscillators read by synchrony | oscillatory neural networks | the drive mask; no trained read-out | no |
| Insertion where an error persists | growing neural gas (Fritzke, 1994) | frontier insertion on a directed influence graph under a geometric law | engineering, not a claim |
| Frequency adaptation | adaptive-frequency oscillators (Righetti et al., 2006) | a windowed rate estimator (an analogy, not that mechanism) | no |
| **A grown path that routes and selects inputs, measured causally** | — | the combination, with lesion and donor tests | **G2 only** |
| Reusable qualified structures, library reuse, composition | — | the long-term aim | **not in revision 6** |
| Causal background transformation B_n → R_n → B_{n+1} | the RRG requirement | — | NOT_TESTED |

The potentially distinctive contribution is **causal, reusable geometry ↔ mode organization**, not synchrony or insertion by themselves. Revision 6 tests only its first step.

## 11. Self-audit: Codex revision-6 review findings

| # | Finding | Disposition | Cause of the drafter's error |
|---|---|---|---|
| C1 | The output disk overlaps direct drive (4 < 3 + 2) | Output members are drive-masked; geometry is no longer relied on | Checked a point, not a disk |
| C2 | B-path neither detects missing paths nor progresses | A directed influence graph; frontier insertion at r*; a progress check; boundary cases | Used distance as a proxy for connectivity |
| C3 | The bridge is too weak at distance 2–3; birth order; memory eligibility | Spacing r* = 0.556 (weight 0.73); path rules first with a capacity rule; memory declared as no-signal | Ignored the C4 coupling kernel and the spacing |
| C4 | Site attraction was a new, unit-incomplete law | Withdrawn; a labelled engineering wall instead | Called a new term "no new law" |
| C5 | D4 admits islands; graph unspecified | A continuous timer on the directed graph; liveness separated from function | Under-specified |
| C6 | Control M confounded; cost skip; 5% tolerance; arithmetic | Only B1 mirrored, everything else common, the same budget, exact matching, 48 trainings (+50%) | Did not name the causal question |
| C7 | Scrambling sites keeps the input | A donor-input intervention; permutation stays as robustness | Confused a permutation with information removal |
| C8 | G2 admits an echo or a single phase hold | Scope narrowed to task response; a path lesion against a sham; relay baselines reported | Overclaimed |
| C9 | D3 credit and the library role missing | Declared out of scope; no claim that reward learns the action | Overclaimed |
| C10 | Statistics not executable | A paired t lower bound; one primary task; Bonferroni for the others; cut rules | Under-specified |
| C11 | G0' classification | One authoritative row; flags reported | Inconsistent wording |
| C12 | No normalization ledger, step order or versioning | Sections 2 and 5; new RHS versioned (`rev6_rhs_v1`) and used in every mode | Omitted |
| C13 | No stop rows or fixtures; entropy reuse | Section 8; fresh namespaces and a fresh evaluation panel | Omitted |
| C14 | Prose corrections; novelty | Sections 9 and 10 | Overstated |

## 12. Revision 6.1 amendments (each replaces the named clause)

### 12.1 B-path acceptance by directed progress (replaces section 4 "B-path", R2-1)

**Fair order.** The site order at a check starts at a pointer p and wraps around. p advances by 1 at every check, whatever happens. No site waits more than 8 checks for first access.

**For each active site s** without a directed path from its effective roots (12.3) to O:
- F_s = the set forward-reachable from s's effective roots;
- T = the set of elements that reach O, O included.

**Skip codes** (logged; no birth):
- `no_output`: T is empty (O is empty);
- `no_root`: F_s is empty.

**The deficit** δ_s = min over u ∈ F_s and v ∈ T of |x_u − x_v|: the Euclidean gap between what the site reaches and what reaches the output.

**Candidates:**
- The (a, b) pairs, a ∈ F_s and b ∈ T, are tried in increasing |a − b|, ties by lowest ids, up to 8 pairs.
- For each pair, up to 13 placements are tried: on the segment from a to b at distance r* from a, then rotated ±15°, ±30° … ±90°.

**Trial.** Each placement is tested on the **post-insertion state**: the newborn is added, and every neighbour list (k ≤ 8, r < 3) is recomputed from current positions. It is accepted only if **all four** hold:
1. a is in the newborn's neighbour list, so a → newborn is a real edge and the newborn is in F_s;
2. no site that had a directed path to O before the trial loses it;
3. δ_s strictly decreases, **or** s now has a directed path to O;
4. the clearance is ≥ 0.05 m.u.

**Outcome:**
- The first accepted placement is born, with phase θ_a and the normal newborn contract.
- If every candidate fails, the site is logged `exhausted`, with the failure counts per condition.
- Pairs closer than r* are not skipped; they are tried like any other (the old `saturated` stop is removed).

At most 2 B-path births happen per check.

### 12.2 Bandwidth is a hypothesis (replaces the "answers C3" sentence in section 4, R2-2)

- r* = 0.556 m.u. is the in-phase **pair** equilibrium of C4. Its link weight is 0.73 before division by the receiver's neighbour count: about 0.09 rad/s with 8 neighbours, a local time scale of about 11 s.
- Whether a chain carries a changing input within a task interval is **a hypothesis tested by F1** (12.7), not a property claimed.
- A weak but connected path triggers no growth. It shows up as an F1/F5 failure or a G2 failure.

### 12.3 Roles, measurements and the template (replaces base section 7's member schema and section 3's role sentences, R2-3, R2-4)

**Role by measurement:**

| Measurement | Ordinary element | Output member |
|---|---|---|
| Site phase drive | g_i · k_s · K_d (base) | **0** (the mask) |
| Sensor partners: eligibility, PLV, P_i, e_i | base | **none**: the mask applies to these histories too; P_i is undefined and e_i = 0 |
| Lock L(i) and D1 | base, over sensor and C4 partners | C4 neighbours only |
| Coverage of a site | base | **never** counts |
| Effective root | k_s > 0, K_d > 0 **and g_i > 0** | never |
| Geometric exposure (diagnostic) | recorded | recorded: the time within any site's reach, kept apart from the mask |

**Template schema `rev6_template_v1`:**
- per member [rel x, rel y, phase offset, ω, g, **role**], with role ∈ {"element", "output"};
- the binding rule;
- the version identifiers `rev6_rhs_v1`, `rev6_eval_v1` and `rev6_template_v1`.

The content hash covers all of these, so two media that differ only in roles hash differently.

**Role preservation.**
- Roles are copied through extraction, reindexing, carrier shifts, recovery clones and evaluation copies. They are **never inferred from position.**
- Frozen evaluation copies keep the base rule: histories and timers are inactive, and growth and plasticity are off. Live clones (recovery futures) copy histories and timers.

**Implementation checks (later, authorized batch):**
- a round trip;
- a role-only hash difference;
- an old-template identity regression, with 5.1 templates loading unchanged under their own version.

### 12.4 The output is one oscillator (replaces section 3's output sentences and section 4's B-out timer, R2-5)

- **O is intentionally a single output oscillator,** as in oscillatory-network read-outs. B-out fires at a check exactly when O is empty, with no timer. The cap is 1.
- C = 1 whenever O exists. So the perceive magnitude is 0 and move's magnitude is 1 by the inherited action table.
- **Perceive's primary score is angular** (base). The distance error is reported, and no distance perception is claimed.

### 12.5 Donor inference and bounds (replaces section 7's donor map and estimator details, R2-6)

**Panels:**
- recipients: world validation episodes 512–639 (local j = 0 … 127);
- **donors: a disjoint panel, episodes 640–767.** Recipient j gets donor 640 + π(j), with π a fixed permutation drawn now from the `rev6_donor` entropy.

Every donor is used once and is independent of the recipients, so the 128 differences are independent paired draws and the 127 df paired t applies.

**The donor drive** is replayed relative to the recipient's carrier clock: ψ = φ(t) + α_donor(t), with the donor's k_s(t) and slot permutation.

**Bounds**, with d̄ and s_d over the 128 differences:
- lower = d̄ − t_{0.95,127} · s_d / √128;
- upper = d̄ + t_{0.95,127} · s_d / √128.

**Dispositions:**
- zero variance: a positive constant counts as above 0, a negative constant as below 0, and zero as neither;
- any non-finite value makes the seed unit INVALID.

The episode bounds are conditional on a trained seed. The ≥ 6 of 8 seed rule is a development rule.

### 12.6 G2: the output-channel necessity test, without a selection claim (replaces section 7's G2 and its scope sentence, R2-7, R2-8)

**The claim:** input-dependent angular response through the grown output channel. **Selection among inputs is not claimed.**

**Task use in a seed (perceive) requires all four** lower bounds > 0:
1. intact − default;
2. intact − random;
3. intact − donor input;
4. **intact − output-channel lesion**, where all C4 coupling into O is zeroed at every RK4 stage for the whole episode.

Plasticity and growth are off in evaluation (base), and roles are preserved, so this lesion removes the only route by which input can reach the output.

**G2:** PASS if task use holds in ≥ 6 of 8 seeds, FAIL if ≤ 2, otherwise INCONCLUSIVE. INVALID comes first.

**Reported, descriptive only:**
- **G2-sel:** intact − the fixed-site relay of physical site 0, which outputs that site's phase while it is active and the default angle 0 otherwise. It is evaluated on the same panel, not assumed. A seed whose lower bound > 0 here is reported as showing selection beyond a fixed relay.
- The strongest-site oracle relay.
- A destructive receiver lesion: the incoming coupling of an equal number of random non-output nodes, chosen without replacement at episode start from `rev6_eval` and held for the episode.

### 12.7 Fixtures, frozen now (replaces section 8's fixture list; all run under `rev6_fixture`, all owner-gated)

**F1, chains:**
- Pure chains of 1, 3 and 5 links at r*, from a site to O. Each receiver has only its predecessor as a neighbour. ω = π for all members, with zero detuning, plus a descriptive ±0.1π detuning case.
- The site angle steps by π/2 at t = 8 s.
- **PASS:** for 1 and 3 links, the output angle error is ≤ 0.3 rad within 8 s of the step, and the chain's directed path persists in ≥ 80% of samples over 160 s of free C4 motion. The 5-link case is descriptive.

**F2, negatives:**
- (a) Empty O gives exactly the default.
- (b) A disconnected singleton O with θ(0) = α is run twice from the same state under two different input streams. The output phase sequences must be **bitwise identical**, with zero path exposure. A non-default constant angle is expected and allowed.

**F3, mask:** the drive term of an output member at a sensor is exactly 0, bitwise, at every RK4 stage.

**F4, relays and lesions:**
- the fixed-site and oracle relays emit their declared outputs exactly;
- the channel lesion zeroes the coupling into O at every stage.

**F5, growth from the initial state:** 50 perceive episodes under the full rules. Episodes 1–40 are warm-up; 41–50 are measured. Two starts:
- (i) the base initial state;
- (ii) a controlled start with O present and no path, which exercises B-path.

**PASS needs all of:**
- B-out fired in (i);
- ≥ 1 accepted B-path birth in (ii);
- in episodes 41–50 of both, at least one site has path exposure ≥ 0.5;
- the mean absolute wrapped difference between the own-input and donor-input output angles is ≥ 0.3 rad (input dependence).

**F6, memory (descriptive):** the circular correlation between the encoded angle and the hidden-interval output angle, own input against donor input.

**F7, control-M feasibility:** control M paired with F5 (i). **PASS:** zero unmatched B1 births.

**F8, the memory block boundary (descriptive):** P_i, e_i and reward updates in the first memory episode after a move block, against within-block episodes (R2-11).

### 12.8 The complete stop table (replaces base section 12 and section 8's table)

| Yes/no question | Yes → one action | Role |
|---|---|---|
| Is owner approval of this revision or of its fixture run missing? | Do not execute it | implementer |
| Does F1, F2, F3 or F4 fail its criterion? | Block F5 and the development run; report | implementer |
| Does F5 fail its criterion? | Block the development run; write the failure report | drafter |
| Does F7 show any unmatched birth? | Block G0 as registered; report the feasibility failure | implementer |
| Is a source identity, unit or endpoint definition missing or mismatched? | Block execution | implementer |
| Is a read-out INVALID? | Report it with raw evidence; do not reinterpret it | implementer |
| Does G1 FAIL in the task-blind arm? | Write the failure report; stop development | drafter |
| Does G0' FAIL? | Write the failure report; stop development | drafter |
| Is G2 FAIL or INCONCLUSIVE? | Write the failure or diagnosis report; stop development | drafter |
| Has any protocol element changed after results were seen? | Draft a new revision with fresh development seeds, and identify any reused evidence | drafter |
| Has development stopped, and is a next step needed? | Ask the owner | owner |

### 12.9 G0' window and taxonomy (refines section 7's G0', R2-10)

- **The late window** is the growth checks with t ≥ 25,600 s (the last 20%), inclusive. The slope, placement rejections and protected-over-budget states are all evaluated on it.
- **Placement-type rejections (they count against G0'):** `placement` (B1 and B-out spiral) and `exhausted` (B-path).
- **Functional demand codes (reported, never counted):** `no_output`, `no_root` and the B-path conditions 1–3.
- **Cost and cap rejections** are reported per role, with denominators:
  - **opportunities:** checks where the rule's condition held;
  - **attempts;**
  - **accepted.**

  A flat count with unmet B-out or B-path demand is reported as such. It is never called settling.
- Statistics undefined during warm-up are reported as undefined, and excluded.

### 12.10 Smaller clarifications

- **Graph timestamp.** At a growth check, G_t is recomputed **fresh** from the current positions, not from the last held substep topology. It is recomputed again after every removal and birth.
- **Memory (R2-11).** Zero memory eligibility is an **established-block** limitation. The first memory episode after a move block can inherit eligibility through carried histories; it is reported separately (F8). Histories are not reset.
- **Control U** enqueues the intact run's **accepted B1** events.
- **The wall** is a soft restoring term, not a hard bound. The maximum radius, penetration time and loss of sensor access are reported.

## 13. Self-audit: Codex round-2 findings

| # | Finding | Disposition | Cause |
|---|---|---|---|
| R2-1 | B-path accepted births that need not extend the directed frontier | 12.1: a post-insertion trial (a real a → newborn edge, no lost paths, δ_s decreases or the site connects), alternate pairs and directions, empty-set codes, a fair round-robin | Used a Euclidean proxy again |
| R2-2 | r* does not answer bandwidth | 12.2: labelled a hypothesis; F1 tests it with a step input, a deadline and a tolerance | Overclaimed from a pair equilibrium |
| R2-3 | The template lost the output role | 12.3: `rev6_template_v1` with role and version ids in the hash; role preservation everywhere | Forgot the inherited schema |
| R2-4 | The mask was missing from eligibility and coverage | 12.3: a role-by-measurement table; effective roots need g > 0 | Under-specified |
| R2-5 | The B-out estimator was ambiguous, and singletons cannot grow O | 12.4: O is one output oscillator, born when O is empty | Under-specified |
| R2-6 | Reciprocal donors break 127 df | 12.5: a disjoint donor panel 640–767 with a fixed permutation; bounds and dispositions | Did not check the dependence |
| R2-7 | Sham − lesion is not a decrement from intact | 12.6: intact − channel lesion > 0; the sham becomes descriptive | Wrong contrast |
| R2-8 | Selection was overclaimed | 12.6: the claim is narrowed to input-dependent response; G2-sel against a fixed relay is descriptive | Overclaimed |
| R2-9 | F2 contradicted the law; criteria were missing | 12.7: F2(b) bitwise input independence; numeric F1/F5 criteria; F7 and F8 added; 12.8 a complete stop table | Under-specified |
| R2-10 | G0' window and new codes | 12.9 | Under-specified |
| R2-11 | Memory eligibility at a block boundary | 12.10 and F8: a limitation, reported separately | Missed carried histories |

## 14. Revision 6.2 amendments (each replaces the named clause)

### 14.1 Graph sampling (R3-6; applies everywhere)

**At every world step**, after integration and before the timers:
- G is computed **fresh from the endpoint positions** (k ≤ 8 nearest, strict r < 3). It does not use any substep's held lists.
- The effective roots come from the current drives (12.3).

D4 timers, path exposure, F-fixture diagnostics and growth checks all use this graph. At growth checks it is recomputed again after every removal and birth. The convention is identical in intact, control and fixture runs.

### 14.2 B-path trial, completed (amends 12.1 condition 1, R3-2)

**Conditions 1 and 2 of 12.1 are replaced by** (conditions 3 and 4 stay):
1. a → newborn is an edge of the post-trial graph;
2. **the newborn is in Reach(the post-trial effective roots of s, the post-trial graph)**;
3. **a itself stays in that reach**;
4. no site that had a directed path to O loses it.

**A rejected trial restores the complete pre-trial state** (positions, neighbour lists, ids, counters) before the next candidate is tried.

The implementation batch includes **Codex's saturated-receiver counterexample** (`…_r3.md`, R3-2) as a unit test. The candidate c = (0.556, 0) there must be **rejected**.

### 14.3 F1, honest scaffolds under intact C4 (replaces 12.7 F1, R3-1)

**Common settings** (neighbour lists always come from intact C4; nothing is forced):
- one active site at q = (4, 0) with constant strength k = 2;
- growth, D-rules and adaptation off (η_ω = η_g = 0);
- every member has ω = π and phase 0 at t = 0;
- the site angle is 0 until t = 8 s, then π/2.

**Members:**
- **S** (source): at (3.2, 0), g = 1, an ordinary element.
- **Intermediates:** ordinary, at the listed positions, with **g = 0** (no drive channel, though in reach).
- **O:** the output.

**Configurations:**
- **F1a, direct:** S, with O at (3.2 − r*, 0).
- **F1b, dense scaffold:** S, two intermediates at r* spacing toward the origin, and O next. All are mutual neighbours.
- **F1c, long chain (descriptive):** S, then intermediates at r* spacing along the x axis down to x = −1.25, then O at x = −1.25 − r*. **O is farther than 3 from S**, so no shortcut exists from S.

**Recorded:** every neighbour list per world step; the link weights; the direct-drive exposure (zero for g = 0 and for O); the output angle.

**PASS** (F1a and F1b): the output angle is within 0.3 rad of π/2 + φ(t) by t = 16 s, and the directed S → O path exists in ≥ 80% of the world steps of a 160 s run. F1c reports its delay and persistence only.

**This tests output response on dense scaffolds.** It does not test the serial bandwidth of long chains; F1c only describes that.

### 14.4 F2 settings (amends 12.7 F2)

F2(b) uses the F1 common settings, with **growth and adaptation off**. The single output member sits at (−3, 0), more than 3 from every ordinary element. Ordinary elements are F1b's members shifted to (+3.2, …). The two input streams are: the site angle constant at 0, and a step to π/2 at t = 8 s.

### 14.5 F5, a paired frozen assay (replaces 12.7 F5, R3-3)

**Growth phase (full rules)** under fixture medium slot `F5/i` or `F5/ii` (seeds as in 14.6): 50 perceive episodes on the fixture world episodes (14.6).

**Starts:**
- **(i)** the base initial state.
- **(ii)** a hand-built state:
  - six ordinary elements, g = 1, on a hexagon of radius r* around (3.4, 0) (an effective-root frontier at site 0, physical site 0 fixed at (4, 0));
  - **one output at (−0.5, 0)**, more than 3 from every ordinary element, so the output route is missing.

  Any other site starts empty.

**Checkpoints:** the full state after episodes 40, 45 and 50.

**Assay at each checkpoint** (growth and plasticity off, carrier offset 0, roles preserved), with frozen paired copies of **the same** checkpoint:
- **own input** on 10 recipient episodes;
- **donor input** on the paired donor episodes (14.6);
- **own input with the channel lesion** (12.6).

**Gate quantities, pooled over 3 checkpoints × 10 episodes = 30 assay episodes:**
- A = the mean absolute wrapped difference between the own-input and donor-input output angles, over each episode's 160 decisions;
- B = the mean absolute wrapped difference between the own-input and lesion output angles;
- E = per site, path exposure pooled over the 30 own-input assay episodes.

**PASS** (both starts): B-out fired in (i); ≥ 1 B-path birth was accepted in (ii); E ≥ 0.5 for at least one site; A ≥ 0.3 rad; B ≥ 0.3 rad.

A checkpoint without an output member counts its episodes as A = B = 0.

### 14.6 The entropy inventory (R3-4; frozen now, without running anything)

**Seeds:**
- Every non-world seed is **uint64 = the first 8 bytes (big-endian) of SHA-256 of the ASCII string** `0h-rev6/<domain>/<key>`.
- Domains: `medium`, `growth`, `matched`, `random_policy`, `lesion` and `donor_perm`.
- Keys: `<arm>/<slot k>` for development, `F5/i` and `F5/ii` for fixtures, or as named below.

**World episodes** (the native world API, namespaces `dev` and `validation` only, never `judging`):

| Use | Namespace | Episode ids |
|---|---|---|
| 5.1 (for reference) | dev | 0–1999 |
| Revision-6 training, slot k (0–15, both arms) | dev | **1,000,000 + 10,000·k + e**, e = 0–1999 (disjoint from 5.1) |
| Calibration (reused, labelled) | validation | 0–255 |
| Evaluation recipients | validation | 512–639 |
| Evaluation donors | validation | 640–767, through π |
| Fixture recipients | validation | 768–777 |
| Fixture donors | validation | 778–787, paired one to one |
| Fixture growth episodes (F5) | dev | 2,000,000 + e |

**Donor permutation:** π(j), for j = 0 … 127, is the rank of j when the 128 values SHA-256(`0h-rev6/donor_perm/` + decimal j) are sorted ascending as big-endian integers. Donor = 640 + π(j). It is deterministic, and **the implementer writes the 128 entries into the fixture receipt before any evaluation.**

**Bindings:** the inherited permutation(episode) on the episode ids above.

**Sharing:**
- intact, M and U of a slot share the training world episodes, bindings and medium seed;
- M uses `matched/<arm>/<k>`;
- own and donor copies share the checkpoint state and carrier;
- random-policy, lesion and growth draws use their own domains.

### 14.7 F6 estimator (amends 12.7 F6)

- **The estimator:** the Jammalamadaka–SenGupta circular correlation between the encoded angle (the last visible frame) and the mean hidden-interval output angle, over the assay episodes.
- **Undefined** (zero circular variance on either side, or fewer than 5 episodes with an output): the result is null with its reason.
- It stays descriptive.

### 14.8 G2-sel label (amends 12.6, R3-5)

It is reported as **"superiority to the site-0 relay"**, with no selection interpretation. Avoiding empty sites can produce it. No stronger selection diagnostic is registered.

### 14.9 Stop table additions (amends 12.8)

| Yes/no question | Yes → one action | Role |
|---|---|---|
| Is the medium's design-specific integration for revision 6 (the new RHS, masks, roles, graph, B-path trial and template v1) not implemented, tested and reviewed? | Do not start any fixture or development run | implementer |
| Did a fixture's measurement fail (a crash, a non-finite value, a missing record)? | Report it INVALID; block the next stage | implementer |
| Is perceive not usable under the frozen usable-task rule? | Block G2 and G0; do not substitute another primary task | implementer |
| Does any seed of the full run have an unmatched control-M birth? | That seed is G0-INCONCLUSIVE (F7 does not guarantee full-run matching) | implementer |

## 15. Self-audit: Codex round-3 findings

| # | Finding | Disposition | Cause |
|---|---|---|---|
| R3-1 | F1's predecessor-only chains cannot exist under C4 | 14.3: honest dense scaffolds, intermediates with g = 0, a long-chain case without a shortcut (descriptive), and neighbour lists from intact C4 | Ignored C4's k-nearest radius rule |
| R3-2 | The trial could disconnect its own source | 14.2: post-trial reach of the newborn and of a, a full restore on rejection, and Codex's counterexample as a unit test | Inferred reachability from one edge |
| R3-3 | F5 was not a paired procedure | 14.5: checkpoints, frozen paired copies, own, donor and lesion assays, pooled quantities, a concrete (ii) start | Under-specified |
| R3-4 | Entropy names without derivations | 14.6: SHA-256 seeds, world-id ranges, the donor permutation recipe, the sharing rules | Under-specified |
| R3-5 | G2-sel overinterpreted | 14.8: label only | Overclaimed |
| R3-6 | Graph sampling convention | 14.1: a fresh endpoint graph every world step | Under-specified |

## 16. Revision 6.3 amendments

### 16.1 The F5 and F7 arm and start states (R4-1)

**Arm:** F5 and F7 run the **task-blind arm only**, with no reward update. They test growth and the output channel, not reward.

**F5(i) start:** the base initial state (base section 4), drawn from medium key `F5/i` (16.2). Its rates have ±0.1π detuning and its phases are uniform.

**F5(ii) start (literal; no random field):**

| id | role | position | phase | ω | g |
|---|---|---|---|---|---|
| 0–5 | element | (3.4 + r* cos(60°·m), r* sin(60°·m)), m = id | 0 | π | 1 |
| 6 | output | (−0.5, 0) | 0 | π | 1 (inert under the mask) |

- r* is the **declared constant 0.556 m.u.**
- **Initial conditions:** clock t = 0; empty histories; all timers 0; all seven members protected for 20 s, as newborns; the id counter starts at 7.

**Bindings and logging (both starts):** observations use the normal permuted bindings; no item is forced onto any site. The log records every world step where the hexagon's site (physical site 0) is active, and every B-path opportunity, attempt and outcome.

**F1c coordinates (exact):** S at x = 3.2; intermediates at x = 3.2 − 0.556·m for m = 1 … 8 (the last at −1.248); O at x = 3.2 − 0.556·9 = −1.804; all at y = 0. The recorded neighbour lists govern any interpretation, since free motion may create shortcuts.

**Trial restore** (14.2): B-path trials consume **no randomness**, so the restore covers positions, neighbour lists, ids and counters. It has no RNG state to restore.

### 16.2 The seed-consumer table (R4-2)

**Slot mapping:** task-blind local seed k (0–7) → global slot k; reward local k → global slot 8 + k. Training worlds are World(task, 1,000,000 + 10,000·slot + e, 'dev').

**Seed:** seed(key) = the first 8 bytes of SHA-256(`0h-rev6/` + key), big-endian. Python-side generators are `numpy.random.Generator(PCG64(seed))`.

| Consumer | Key | API | Created | Shared by |
|---|---|---|---|---|
| Medium initial state | `medium/<arm>/<k>` | PCG64 | once at run start | intact, M and U of the slot (the same initial state) |
| Growth draws (B-out's uniform-phase fallback, and any other growth randomness) | `growth/<arm>/<k>/<policy>`, with policy ∈ {intact, M, U} | PCG64 | once per run; advanced in event order | none |
| Control-M placements | `matched/<arm>/<k>` | PCG64 | once per run; advanced in event order | none |
| Control-U placements | `control_u/<arm>/<k>` | PCG64 | once per run (replaces the inherited U recipe) | none |
| Recovery kicks | `recovery/<arm>/<k>/<policy>` | the inherited per-check sub-derivation (seed + check index), with this master seed in place of the old one | per check, as inherited | none |
| Random comparator | `random_policy/<task>/<world episode id>` | native Policy(task, seed, 'random', 'validation') | fresh per evaluation episode | every seed, arm and checkpoint (one fixed random comparator per episode) |
| Destructive receiver lesion (descriptive) | `lesion/<arm>/<k>/<world episode id>` | PCG64 | fresh per evaluation episode | none |
| Donor permutation | `donor_perm/<j>` | the SHA-256 rank (14.6) | fixed | all |
| Fixtures F5 and F7 | medium `F5/i`; growth `F5/<start>/intact`; matched `F5/i` | as above | once per fixture run | own, donor and lesion copies share the checkpoint |

**Inherited exceptions kept:** the world's own episode generators and permutation(episode), on the new episode ids.

**Receipts:** the implementer writes the instantiated seed inventory (key → uint64) into the receipt before any evaluation result exists.

### 16.3 Base prerequisites kept (stop table)

The base's stop row stays in force alongside section 14.9's integration row: the world, remember_static and the medium's design-specific follow-up must all be READY and reviewed.

## 17. Self-audit: Codex round-4 findings

| # | Finding | Disposition | Cause |
|---|---|---|---|
| R4-1 | F5 and F7 arm and start state not frozen | 16.1: task-blind only; a literal (ii) table; the (i) seed key; logging; exact F1c coordinates; restore scope | Left the fixture recipe partly implicit |
| R4-2 | Seed consumers incomplete | 16.2: a slot mapping and a consumer table with keys, APIs, lifetimes and sharing | Gave a hash formula without its consumers |

## 18. Revision 6.4 amendments (R5-1 and the carried notes)

### 18.1 Fixture consumers (replaces the "Fixtures F5 and F7" row of 16.2)

| Fixture run | Medium initial state | Growth stream | Matched stream | Recovery master | Notes |
|---|---|---|---|---|---|
| F5(i), intact | `medium/F5/i` (PCG64, once) | `growth/F5/i/intact` (PCG64, once per run, in event order) | not used | `recovery/F5/i/intact` | task-blind |
| F5(ii), intact | not used (literal start, 16.1) | `growth/F5/ii/intact` | not used | `recovery/F5/ii/intact` | task-blind |
| F7, control M | **the same initial state as F5(i)**, drawn again from `medium/F5/i` in a separate generator instance | `growth/F5/i/M` (its own seed) | `matched/F5/i` (PCG64, once) | `recovery/F5/i/M` | paired with the F5(i) intact run, which it mirrors; task-blind |

- **The assay copies** (own, donor, lesion) have growth off and consume no growth, matched or recovery stream.
- **Random comparators** are not used in the fixtures.
- **The descriptive receiver lesion** is not used in the fixtures.

### 18.2 The recovery derivation (corrects 16.2's "Recovery kicks" API cell)

The inherited recipe is kept **exactly**, as `runner/run.py` and `runner/protocol.py` implement it:
- the generator is `numpy.random.default_rng(entropy(master, "kick:<world-step index>"))`;
- entropy(seed, domain) = the first 8 bytes, **little-endian**, of SHA-256 of the string `"<seed>:<domain>"`, with seed in decimal;
- the master is seed(`recovery/<…>`) from 16.2 (big-endian, as defined there).

The sub-derivation is **not** "seed + check index"; that parenthetical in 16.2 is withdrawn.

### 18.3 Stable names and counter units (Codex's carried notes)

**B-path trial conditions** have stable names, used in every log and report:
- `edge_a_to_new`;
- `new_reached`;
- `a_reached`;
- `paths_kept`;
- `deficit_or_connect`;
- `clearance`.

**Terminal outcomes:** `accepted`, `exhausted`, `no_output` and `no_root`.

**Counter units:**
- a **request** is one rule-and-site opportunity at a check: a B-out need, one B-path site, or one B1 site;
- an **attempt** is one candidate placement tried;
- an **acceptance** is one birth.

G0' counts terminal requests (`placement`, `exhausted`), never attempts.

### 18.4 Self-audit

| # | Finding | Disposition | Cause |
|---|---|---|---|
| R5-1 | The fixture consumer row omitted F7-M growth and the fixture recovery masters; the recovery recipe was misdescribed | 18.1: an explicit per-fixture table; 18.2: the exact inherited call, byte order and domain string | Summarized the inherited code instead of reading it |

### 18.5 Codex round-6 low notes (applied)

**R6-1, birth outcomes.** 18.3's terminal list is the **frontier-search** outcome list for B-path only. Every processed birth request (B-out, B-path site or B1 site) gets exactly one terminal record from this schema:
- `accepted`;
- `cap`;
- `cost`;
- `placement` (B1 and B-out spiral);
- `exhausted` (B-path geometric search);
- `no_output`;
- `no_root`;
- `quota`: the request was not processed because the per-check birth limit was reached. It is **not** a placement failure.

A candidate that passes the geometric conditions but is refused for cap or cost records `cap` or `cost`, never `exhausted`. G0' still counts only `placement` and `exhausted`. Per-candidate failures stay attempt diagnostics.

**R6-2, the F6 mean direction:**
- The within-episode summary is the circular mean of the decoded, carrier-demodulated angles β over the hidden interval, with its resultant R recorded.
- If R < 0.05 (degenerate), the episode has **no defined mean direction**, and is reported as such.
- The minimum of 5 counts episodes with a defined mean, not episodes with an output.
- If the correlation cannot be formed, the result is null with its reason.
- Raw β and R traces are kept. F6 stays descriptive.

| # | Finding | Disposition | Cause |
|---|---|---|---|
| R6-1 (Codex round 6) | The outcome list was ambiguous for resource refusals | One terminal schema with `cap`, `cost` and `quota` | Listed only search outcomes |
| R6-2 (Codex round 6) | F6's within-episode mean could be undefined | A resultant threshold of 0.05 and a defined-mean count | Missed a degenerate mean |
