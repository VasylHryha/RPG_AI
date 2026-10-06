CHANGES_REQUIRED
Reviewer family: Codex
Reviewed DESIGN_0H_REV7.md SHA256: 86d13a91747aef55298412b331326bbb35611ab7f43a8e7e96bf304038d2f4e0

Codex (GPT-6), cross-family design review, 2026-10-06. Workspace HEAD: `d71a41af547ae6e2be40f6c714edf2e473fde1f6`. Scope: the owner's adversarial recheck of revision 7, with an approximately 20-minute cap. This is a design verdict, not implementation acceptance or execution authorization. Claude, as drafter, owns the repairs and their self-audit causes (AGENTS.md:19).

Read AGENTS.md; the complete revision-7 amendment; its complete revision-6.5 base through 19.9; the inherited revision-5.1 design; the fixture report; `geomind/c4_model.py`; the supplied toy; and relevant existing adapters, fixture specifications, identity code, R5 and current source guidance. Only the explicitly authorized standalone toy was executed, once, using `python3 -B .../rev7_toy/f1b_toy.py`. It imports only `math`. No project code, imports, tests, native libraries, benchmarks or experiments were executed. No recorded verdict was recomputed. Only this review file was written; unrelated workspace work and historical evidence were preserved. Git metadata is read-only under this session's filesystem policy, so the review is left uncommitted in the workspace.

Evidence notation, with line numbers referring to the inspected bytes:

- **R7:** `evidence/tactical_composition_demo/DESIGN_0H_REV7.md`.
- **R6:** `evidence/tactical_composition_demo/DESIGN_0H_REV6.md`, revision 6.5, SHA256 `ca9c43362e3eebace889c7306784ffe5dd3095a58eb2095473f745eff31b52c5`.
- **Base:** `evidence/tactical_composition_demo/DESIGN_0H.md`, revision 5.1.
- **Report:** `evidence/tactical_composition_demo/growing_shapes/runner/REV6_FIXTURE_REPORT.md`, SHA256 `d530ae6236cb63e978d5224c33db693e446c9242884a5a4751295855158f7fc8`.
- **Toy:** `evidence/tactical_composition_demo/growing_shapes_review_claude/rev7_toy/f1b_toy.py`, SHA256 `3f0513ac76a1dd03a2ed260a3a88d9927d0b0167f8ab730b383b87fc98b076b9`.
- **C4:** `geomind/c4_model.py`, SHA256 `4fafc161b65914a44dccaca6caefb59a5154079f17f564b4cdc4d44f58c59d33`, matching the existing frozen-source adapter pin.
- Other `medium/` and `runner/` references below are relative to `evidence/tactical_composition_demo/growing_shapes/`.

The diagnosis is useful but incomplete. F1b demonstrates eventual transmission that misses the task deadline; F1c demonstrates compaction and degraded sensor access. Faster phase coupling and an explicit anchoring hypothesis are reasonable responses. However, the proposed value is not derived by the stated rule, the new fixtures have conflicting geometry, and the boundary/timer/recovery contracts are not executable without interpretation. These are design blockers, not reasons to reinterpret the revision-6.5 failure.

## Numbered findings

### 1. R7-1 — HIGH: λ = 8 does not satisfy its stated derivation

**Evidence:** R7:34 requires settlement in half the 4-second cue, i.e. 2 seconds. R7:35 supplies approximately 2.9 seconds at λ = 8, then R7:36 calls 8 the smallest power of two meeting the criterion with margin. The authorized toy actually prints absolute entry times:

| λ | Absolute first entry, s | Delay after the t = 8 step, s | Error at t = 16, rad |
|---|---:|---:|---:|
| 1 | 31.04 | 23.04 | 1.029 |
| 2 | 19.52 | 11.52 | 0.540 |
| 4 | 13.76 | 5.76 | 0.141 |
| 8 | 10.88 | 2.88 | 0.009 |

R7's table is substantially correct when read as **delay**, but its selection rule is not: λ = 4 already meets the inherited 8-second deadline, while λ = 8 misses the proposed 2-second deadline. The fixed-geometry, zero-detuning toy is forward Euler at 0.002 seconds (Toy:5–19), not the mobile engine's RK4 assay. It does not measure response to a four-second cue starting from arbitrary trained phases.

**Fix:** choose one explicit engineering requirement, initial-condition class, tolerance and settling definition. If retaining the toy's 2-second rule, exact zero-detuning time scaling suggests the next power of two, 16, as a candidate; that is an analytic extrapolation, not a tested recommendation or authorization to double the gain. If retaining 8, explain an explicit margin criterion that selects it and withdraw the unsupported 2-second claim. Derive the choice on the eventual fixture geometry and freeze it before authorized execution. Call it fixture-calibrated engineering, rather than “not a tuned task parameter”: it is selected using task timing, although not task scores. Phase and geometry are two clocks of the same element state here, not evidence of different recursive levels.

### 2. R7-2 — MEDIUM: the phase equation preserves the carrier, but changes locking as well as speed; the causal diagnosis is overstated

**Evidence:** R7:29–39 scales coupling and drive but not intrinsic ω or motion. In the carrier frame, with β_i = θ_i − πt,

    β̇_i = (ω_i − π) + λ F_i(β, x, α, g).

At fixed geometry, ω_i = π and constant input, this is a time dilation of the relative-phase dynamics. That explains the toy's approximately inverse-λ delays. With detuning, adaptation, moving geometry or changing input, it is not a time rescaling of the full system. For one driven oscillator with effective amplitude a, locking requires |ω_i − π| ≤ λa; its locked offset satisfies sin(α − β_i) = −(ω_i − π)/(λa). Larger λ broadens the locking range and reduces detuning offsets. Scaling both terms preserves their **instantaneous coefficient ratio**, not every balance against ω or every equilibrium in the coupled moving system. Rapid internal synchrony may also produce an input-weighted consensus rather than selection; the input-only phasor remains essential.

Report:48 explicitly says the measurements do not isolate motion as the causal explanation of F1b's delay. F1c has 1117 element-seconds without sensor access (Report:44), whereas its S→O graph remains present throughout. That is evidence of changing drive access, not simply a slow phase clock. R7:68's mobile λ comparison measures the total λ effect under anchoring, including changed phase-dependent motion.

**Fix:** retain unscaled ω_D = π; multiplying ω as well would break the existing demodulator and task clock. State the locking and geometry consequences above. Label the diagnosis as supported hypotheses. Define F1d's output as delays, deadline errors, effective-root/drive exposure and topology/geometry histories, conditional on the pinned design. If pure rate isolation is desired, specify a separate fixed-position comparison on identical coordinates; any such future execution requires authorization. Do not present F1d as proof that the old failure had one cause. Keep the zero-detuning fixture and clearly reported detuning diagnostics separate.

### 3. R7-3 — HIGH: “at the origin” conflicts with the inherited literal starts and destroys the direct fixture's initial link

**Evidence:** R7:43 fixes O at the origin, R7:45 permits a spiral fallback, and R7:63 keeps F1a/b's old positions “but with O pinned.” R7:59 keeps F5(ii)'s literal start. Those mean different pin coordinates. R6:469–471 puts F1a O at x = 2.644, F1b O at 1.532, and F1c O at −1.804 (exactly specified at R6:591). F5(ii) has O at −0.5 (R6:579–587).

If the global origin rule overrides F1a, S stays initially at x = 3.2, beyond the strict r < 3 coupling radius, with no intermediate. It is no longer a one-link positive fixture. Initially its in-phase site force points **toward** q = 4: A(1+J) − B/0.8 = 0.55 m.u./s. The proposed anchoring does not supply the missing phase edge. Moving F1b's O also changes the distances used to derive λ. If O instead remains at each literal coordinate, F1c cannot satisfy “final radius exactly 0.” An origin-occupied B-out fallback likewise contradicts that equality.

**Fix:** publish literal coordinate/pin tables for F1a–d, F2/F3, F5(ii), B-out and copies. A clean option is to pin inherited F1a/b at their specified positions as bounded local response fixtures, explicitly exempt them from the live-origin rule, and define a separate origin-output multi-hop F1c with sufficient intermediate nodes and no initial S→O shortcut. Alternatively redesign all three scaffolds. Preserve F5(ii)'s −0.5 pin as an explicit exception or replace its literal table. Pin at the accepted B-out coordinate, or reserve the origin and reject occupied placement; do not silently relocate an existing element. Check pin invariance against its stored coordinate, not a contradictory universal radius.

### 4. R7-4 — HIGH: the sensor-body extension lacks separate motion and phase topology/normalization contracts

**Evidence:** R7:47–51 counts sites in the “same k ≤ 8 nearest list” and “same mean normalization,” but gives them no phase-coupling term and says the directed graph is unchanged (R7:75–76). C4:71–101 uses one neighbour list and its count for both equations. Inherited graph, B-path trial, PLV histories and cost assume element neighbours (R6:35,255–259,435–449; `medium/rev6_design.py`:41–93,207–216).

A union list can displace an element phase neighbour when a site takes one of eight slots. Even if a site's phase term is zero, dividing internal coupling by the union count dilutes it. Both effects change the phase law and can invalidate the unchanged graph/trial acceptance. This would also undermine the advertised unchanged drive-to-coupling balance. “Motion only” does not specify which interpretation applies.

The pair expression can be dimensionally sound: A is m.u./s, B is m.u.²/s, J is dimensionless, and the full velocity is the pair expression times the unit displacement vector. K and site strength are rad/s; Gaussian length scales must remain explicit. Matching units alone does not specify neighbour selection or boundary strength.

**Fix:** define N_i^x over elements plus active pinned sites, with its own mean count, and N_i^θ over elements only, with its own count and the existing phase graph. Hold each list over all four RK4 stages and advance ψ_s on the carrier clock at those stages. Define active-site insertion/removal, deterministic cross-type tie breaking, empty lists, silent/lesioned roles, and endpoint diagnostics. Apply the phase list to graph reach, lock eligibility and every B-path trial. State explicitly that sites are external boundary inputs, excluded from element N, qualification membership, templates as members, and the element-pair budget, while their interactions are reported. If a shared list is intended instead, declare that additional phase-topology change and amend all dependent contracts.

### 5. R7-5 — HIGH: existing births can coincide with a pinned sensor body

**Evidence:** Base:161 and `medium/rev6_design.py`:191–197 place B1 at the first clear spiral point, starting at q_s itself; clearance is checked against **elements**, not sites. R7 adds a repulsive B/r sensor-body term but leaves placement unchanged. In an empty start the first B1 at an otherwise empty site is therefore permitted at r = 0. C4:87–91 regularizes r with eps, but the displacement vector is exactly zero at coincidence: it supplies no separating direction. Near coincidence the force and stiffness become large. This is a deterministic birth-boundary collision, not a rare random draw.

**Fix:** define site-body collision handling before implementation. Prefer a deterministic nonzero source placement toward the output, with clearance from every physical sensor location, including currently inactive sites that can activate later. State the minimum distance or a smooth repulsion regularization and its units; apply it to B1, M/U placements, B-path trials and perturbation admissibility. Merely using the inherited 0.05 clearance does not certify 0.02-second stability: B/r² there is about 400/s before mean normalization. Preserve placement/resource refusal codes and measure numerical convergence for the chosen contract only after authorized implementation.

### 6. R7-6 — MEDIUM: two fixed positions do not make a C4 network a string, and the new boundary carries task information

**Evidence:** R7:54 says the chain is held “like a string between two pins.” C4 has k-nearest attraction/repulsion, not permanent tensile bonds or preserved ordering. One selected site neighbour has no guaranteed force dominance over seven element neighbours. Links can disappear, and the in-phase pair spacing is not universal: B/[A(1+J cos Δθ)] ranges from about 0.556 to 5 m.u.; the latter is beyond the interaction radius. Only **active** sites anchor (R7:47–48), so the source anchor disappears during a hidden cue and changes at item/site rebindings.

Using ψ_s in the cosine adds a direct observation→motion input for ordinary elements even when g_i = 0. A tiny positive k_s activates a full-strength body; k_s = 0 removes it. This is an additional, discontinuous salience convention. R6:19.6 already excludes a stronger internal-path interpretation, but “drive stays the site's only phase channel” must not be read as “the only information channel.”

**Fix:** call persistence an engineering hypothesis, remove the string guarantee, and explicitly disclose activity-gated, unweighted boundary forces. Keep the output phase mask and exclude sites from its phase list. At the live origin every site is at distance 4, so there is no literal direct site→O phase echo; a two-element driven relay can still suffice for G2, whose claim remains only input-dependent terminal-channel response. Retain phasor, relay, K=0 and fixed-position comparisons. If distinguishing phase-drive routing from the new geometric input is intended, add a descriptive intervention that removes/phase-blinds sensor-body forces while preserving drives; otherwise disclose the mixed mechanism. Do not promote that diagnosis into an unregistered primary claim.

The cited [Sar, Ghosh and O'Keeffe paper](https://arxiv.org/pdf/2211.02353), equations (1)–(2), studies sinusoidal position and phase pinning on a one-dimensional ring. It is useful related work, not validation of this two-dimensional fixed-body C4 extension. R7 correctly denies transfer of accepted C4 evidence; keep that distinction.

### 7. R7-7 — HIGH: F1c's new gate has no explicit entry deadline and its compaction check is tautological

**Evidence:** R7:65 requires tolerance “from its first entry through t = 24” but does not require an entry by 24 or specify missing entry. An empty interval after a later entry must not pass. R7:66 asks for a directed path over 160 seconds, while Report:17,44–48 already demonstrates that a path can persist despite failing transfer and sensor access. The output's final radius is exactly zero by pinning (R7:67), regardless of what all ordinary elements do. These conditions do not establish the claimed prevention of compaction. R6:780's explicit inclusive sustained-entry contract applied to F1a/b; F1c was descriptive.

**Fix:** state a finite deadline t_entry ∈ (8,24], the no-entry FAIL disposition, inclusive endpoint sampling and tolerance at every subsequent sample to 24. If the clock rule requires a tighter deadline, use that declared rule rather than silently substituting 24. Define the 160-second path metric using **effective driven roots**, not just the named source's geometric reach. Add an explicit source-drive/access persistence cut and a functional response requirement during the intended persistence interval, or label long-term persistence as topology-only. Record source-site distances, span/radius of ordinary nodes, minimum distances, shortcuts and link weights. A pin-position invariant checks implementation; it cannot be the compaction endpoint. Add the F1c failure/INVALID and F1d descriptive dispositions to the yes/no stop table.

### 8. R7-8 — MEDIUM: dt = 0.02 may resolve the carrier, but faster corrections and 0.1-second estimators need new numerical qualification

**Evidence:** The unscaled carrier advances π·0.02 ≈ 0.063 rad per RK4 substep, so λ does not alias the carrier itself. However the correction rate bound becomes

    |θ̇_i| ≤ 1.5π + λ [K + g_i Σ_s k_s K_d(r_is)].

The choose binding has the conservative bound k_s ≤ 4 under its 0–100 health normalization, and g_i ≤ 2 (Base:61,109). With λ = 8 the corresponding single-site drive bound is 64 rad/s; with internal coupling and maximal ω the bound is about 76.7 rad/s. These are encoding bounds, not measurements or claims that a generated episode attains them or sustains these rates for a whole sample. They nevertheless defeat a carrier-only sampling argument. A phase mode at that drive bound has local stiffness up to 64/s; h·stiffness ≈ 1.28 at h = 0.02 is not itself proof of RK4 instability, but neither is it an accuracy certificate. Motion near the new pins adds the separate stiffness in R7-5.

The histories/PLV/qualification sample at 0.1 seconds. The inherited alias screen wraps differences before testing π/2 (Base:170; `runner/rev6_qualification.py`:28–30); it explicitly cannot see full turns. Faster transient corrections can be missed between those frames even when integration is stable. Conversely, a large transient increment need not be a wrongly integrated trajectory.

**Fix:** keep the world clock, but specify authorized numerical qualification at h = 0.02 versus a finer substep on declared high-gain, detuned, conflicting-input and near-boundary cases. Compare demodulated trajectories, gate-relevant entry/error, topology and pin invariance. Set tolerances before execution. Store or bound **unwrapped** per-substep relative increments and accumulate a conservative intra-frame excursion for estimator validity; define INVALID/not-qualified outcomes rather than relying only on the wrapped screen. If a sufficient bound cannot be met, refine integration and/or measurement sampling in a new adapter. No numerical failure is asserted solely from λ = 8.

### 9. R7-9 — HIGH: adaptation and qualification need a clock policy; inherited position kicks violate the pin constraint

**Evidence:** R7:33,80 keeps adaptation and other rules unchanged. Base:104–124 uses an unwrapped 10-second realized-rate estimate, a 10-second/80-sample site PLV, and η = 0.05/s (20-second adaptation time). Base:171–179 keeps a 60-second qualification window and recovery horizon, 0.005 rad/s frequency tolerance, 0.1-rad lock/pattern cuts, and position/phase kicks. These are executable physical-time cuts, but they are not dynamically equivalent after selectively scaling phase coupling. For example λKW changes eightfold, while the geometric clock and carrier do not. A phase step compressed into the estimator window contributes its phase displacement divided by 10 seconds to ω̂; the estimator measures realized frequency, not intrinsic ω. Stronger forcing also makes driven restoration easier.

More decisively, `runner/rev6_qualification.py`:119–124 applies `c4.kick` to every candidate member's position; C4 detector source `geomind/c4_detect.py`:130–139 does so without a pinned-role mask. If O belongs to a candidate, its kick moves the boundary. Leaving it there changes the prescribed boundary, snapping it back creates artificial instantaneous recovery, and silently omitting the displacement changes the promised kick RMS.

**Fix:** give phase relaxation, geometric relaxation, carrier, estimator windows, adaptation and structural dwell separate ledger rows. Keeping the 10/60-second windows and existing angular/world-frequency cuts is defensible as fixed engineering admission rules for **new driven, anchored snapshots**; say so and quantify the changed dimensionless ratios. Do not blindly divide every horizon by 8 or multiply 0.005 by 8: geometry and ω were not rescaled. Preserve the established distinction from accepted C4 evidence and autonomous resonators.

Define a constrained recovery adapter: pin positions are identical in both futures at every stage; position kicks act on free members only with an explicitly declared RMS denominator, actual achieved kick, and no-free-member disposition. Phase kicks can still include O. Keep external pins out of cohort membership. Report anchor-relative displacement alongside shape-relative metrics where needed. Preserve output roles/pin coordinates in every live/frozen/recovery/extracted copy, and use the same changed RHS in every mode. These are new adapter contracts; do not edit frozen C4 functions.

### 10. R7-10 — HIGH: freeze-not-reset is underspecified, and B-path has no inherited demand timer

**Evidence:** R7:58 changes “B1 and B-path” timers. B1 has a timer (Base:150), but current B-path is an immediate active-site/no-path rule (R6:241–266; `medium/rev6_design.py`:233–269), with no timer threshold or reset contract. Freezing B1 also allows a threshold to persist into an inactive interval. The existing birth check tests the accumulated threshold without an activity guard (`medium/rev6_design.py`:272–285), then takes the current site's phase. A retained request can therefore fire at a 20-second growth check while its site is inactive, which the old reset rule had prevented.

Freezing demand does **not** fix gain/reward eligibility: an established memory cue supplies only 40 active samples in a 100-sample window, below the unchanged 80 threshold (Base:106,142; R6:413,756). It can accumulate uncovered active time over cues, but cannot make P_i or e_i defined. The draft's memory-demand repair is narrower than a memory-learning repair.

**Fix:** specify B1's recurrence exactly: increment by dt_w when active and uncovered; reset when active and covered or after an accepted birth; freeze when inactive; retain the value after quota/resource refusal. State whether births require the site to be active at the growth check; preferably defer inactive requests until a visible input supplies a legitimate phase. Keep accounting for queued demand separate from attempts. Either remove “B-path” from this timer amendment or introduce a complete new timer rule with threshold, resets, fair ordering and eligibility. Retain P/e's memory limitation and F8's carried-history distinction; the memory row remains descriptive. Include threshold-during-cue/check-during-hidden and activity-resumption cases in the eventual authorized contract checks.

The empty start is a sound attribution choice, provided it applies to intact, M and U, with t = 0, empty histories/timers, id counter 0 and the first growth check explicitly stated. No initial ±0.1π detuning exists when there are no elements; newborn ω remains π. The medium seed then has no initial-state draws, while growth/world streams still supply seed variation. F5(ii)'s literal state remains an explicit separate fixture; it must obey the chosen pin contract from R7-3.

### 11. R7-11 — MEDIUM: “every world-id range moves” contradicts reused calibration and historical-reference rows

**Evidence:** R7:3 globally shifts all ranges by 10,000,000, but leaves the 6.5 comparator/evidence rules unchanged (R7:81–83). R6:522–529 includes both historical 5.1 ids and calibration 0–255 explicitly **reused and labelled**. R6:707,713 adds F6 and F8 ranges outside the original inventory table. A blanket replacement can mislabel the old calibration as newly generated or miss those later consumers.

**Fix:** publish an instantiated revision-7 inventory, not just a textual replacement. Shift new training to `11,000,000 + 10,000·slot + e`, evaluation recipients to validation 10,000,512–10,000,639, donors to 10,000,640–10,000,767, F5 assays to 10,000,768–10,000,787, F6 to 10,000,788–10,000,807, F5 growth to dev `12,000,000 + e`, and F8 to dev `12,100,000 + e`. Change all master-key prefixes, donor ranks, random-policy and lesion consumers, retaining the documented byte order and recovery sub-derivation. Check actual disjointness against prior inventories before execution. Explicitly exempt reused calibration 0–255 and historical-reference rows, preserving their identities and labels. Deterministic F1 scaffolds have no entropy to refresh; report that honestly instead of calling them independent fresh-seed evidence. Instantiate/hash the complete inventory before results.

### 12. R7-12 — HIGH: unchanged identity/version language is insufficient for changed dynamics and boundary semantics

**Evidence:** R7:82 keeps the identity scope, while R6:287–301 specifies `rev6_rhs_v1`, `rev6_eval_v1`, `rev6_template_v1`, copied roles and versioned loaders. `runner/rev6_protocol.py`:9–11,36–46 binds those versions into template identity. R6:782 covers the governing design file and revision-6 sources/native images. A revision-7 file that inherits two earlier designs needs their exact bytes in its dependency identity. A reused rev6 version cannot identify λ, pins or the new timer/qualification semantics. Existing integration readiness is for the previous RHS, not this extension.

**Fix:** define revision-7 RHS, evaluation/template and qualification-adapter versions; bind λ, topology/normalization, pin policy/coordinates and timer/start rules into their configuration identity. Include R7 and both inherited design files, revision-7 sources, exact native images/build inputs and instantiated seeds in the one-time execution-start pin. Preserve legacy loading under legacy versions; no silent migration. Implement the extension in new files, leaving accepted C4 and historical receipt-bound evidence unchanged (AGENTS.md:67–74,92).

Replace the inherited revision-6 integration stop row with a revision-7-specific yes/no readiness row, and explicitly incorporate the repaired F1c and numerical/measurement validity rows. Keep separate owner approval of the revision, implementation/integration readiness, fixture execution and later development. Decision 0030 approves only one revision-6.5 fixture execution at its pinned integration; it does not authorize revision 7. This review authorizes no execution and changes no milestone status. Any later registered experiment remains subject to AGENTS.md's registration, pipeline and independent-review gates.

## Repair sequence and retained limits

The drafter should first fix the literal pin/scaffold tables and the separate neighbour laws, then choose a birth-boundary collision contract. Only then does the phase-clock derivation refer to the actual proposed system. Finish timer, sampling, recovery, entropy and identity contracts as one design batch before implementation or tests. Preserve the recorded F1b FAIL and all NOT_RUN rows. Do not tune thresholds using a new failed fixture and relabel that same revision successful.

The existing mask remains useful, the unscaled carrier is correct, and a pinned output plus external bodies does not by itself trivialize the declared terminal-response task. It also does not prove long-chain maintenance, selection, computation beyond an input phasor, reusable atoms, learned structural transformation or RRG background recursion. Those stronger claims remain outside this revision. The smallest defensible next step is a repaired, explicit engineering design whose authorized fixtures can fail meaningfully.

Assisted-by: Codex:GPT-6
