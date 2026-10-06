# Design 0h, revision 6: an input-to-output path grown on purpose (consolidated; supersedes `DESIGN_0H_REV6_DRAFT.md` sections 2–6)

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
