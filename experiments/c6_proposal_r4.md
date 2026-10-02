# C6 R4: qualified material units change a nonlinear oscillator medium

**DRAFT FOR OWNER APPROVAL.** Drafter: Codex:gpt-6, 2026-10-02. This is a new prospective Arm B design. R3's STOP, evidence and receipt-bound files remain unchanged. R4 support components from commit b43918c are engineering helpers, not prior approval or qualification of this model. No implementation, development worlds, final entropy, registration or panel has run for this design. Lifecycle status lives only in STATUS.json.

Authority: [owner handoff](../docs/RRG_V0_2_1_ALIGNMENT_HANDOFF.md), [current source pin](../research/rrg/CURRENT.md), [R5](../GEOMIND_GEOMETRIC_AI_QUALITY_STANDARD_R5.md), decisions 0007, 0010, 0012 and the [R3 self-audit](../docs/reviews/c6_r3_implementation_self_audit_codex.md). The [research note](../docs/research/c6_r4_background_redesign.md) records primary sources, alternatives and analytic checks. Physical examples supply no additional experiment requirements.

## 1. Question and limits

Can a unit that forms from an unformed material population alter the response of a supplied active medium, change later unit formation, and repeat this operation in the inherited environment? Test B0 → R0 → B1 → R1 → B2, with H-BG and H-PS separately per turn and H-RBG only on the same complete chains.

Arm A remains stopped under decision 0013 and is NOT_RUN. H-COMP, H-PRED, H-AI and H-EFF are NOT_TESTED. This experiment supplies the medium, material populations, drive and output switch. It tests conditional causal recursion, not primordial emergence, unrestricted mutual feedback, increased size, indefinite depth or a universal RRG proof.

The environmental medium has complex amplitude variables on fixed sites; it has no mobile material members that could merge with a unit. Material populations enter unformed and are separate interaction domains coupled through the medium. This physical domain structure is declared, not a discovered hierarchy. The detector discovers subsets inside a population from states; it receives no condition, expected subset or desired answer. This is not a claim of unrestricted whole-world cluster detection.

## 2. Fixed prospective model

Use base length L0=1, time C0=1 and medium amplitude Z0=1 throughout both turns. Numerical values below are hypotheses chosen before new measurements; none are calibrated to a new development outcome.

| Item | Fixed rule |
|---|---|
| Material population | 24 elements; positions uniform in disk radius 3, phases uniform on [-pi,pi), omega_i uniform on [.2-.25,.2+.25]. Independent initial ID permutation. Same generator with a prescribed introduction centre: R0 at (0,0), all R1 episodes at (2,0), all R2 episodes at (4,0). This fixed 2-L0 translation advances toward a different supplied region, never toward an observed group. Paired treatment candidates have identical centres/states. |
| Medium geometry | 25 sites on a 5 by 5 square, coordinates {-4,-2,0,2,4} squared; four-neighbor edges, missing boundary edges omitted. Independently permute site IDs once per world. |
| Initial medium | z_a real and imaginary parts independently normal with standard deviation .05; Omega_a uniform on [.2-.5,.2+.5]. All site positions, frequencies and initial values are paired across treatments. |
| Medium law | dz_a/dt = (-.18 + i Omega_a + |z_a|^2 - |z_a|^4)z_a + .05/4 sum_neighbors(z_b-z_a) + f_a(t) + u_a(t). Two isolated radial basins are supplied; their survival in this network must be measured. No adaptive weights or hidden fitted parameters. |
| External drive | f_a(t) = .02/8 sum_m exp(i[(.2+nu_m)t+psi_am]), with nu=(-.7,-.5,-.3,-.1,.1,.3,.5,.7), independent uniform psi_am. Same analytic drive and absolute clock in every branch; no white-noise discretization or final-outcome-dependent drive. |
| Material geometry law | dx_i/dt = 1/23 sum_j!=i (x_j-x_i)[(1+.8 cos(theta_j-theta_i))/s_ij - 1/s_ij^2], where s_ij=sqrt(distance^2+.05^2). No medium force directly enters this equation. |
| Material mode law | dtheta_i/dt = omega_i + 1/23 sum_j!=i exp(-distance^2)sin(theta_j-theta_i) + .2 Im(g_i exp(-i theta_i)). All pair contributions are smooth; no hard top-k/radius truncation. |
| Incoming medium | K_ai=exp(-|q_a-x_i|^2/(2*2^2)); g_i = sum_a K_ai h(z_ref,a)/sum_a K_ai, h(z)=z/sqrt(1+|z|^2). The denominator must exceed 10^-12; otherwise record INVALID, without moving the population or inventing a value. |
| Outgoing channel | For the fixed selected member set M, u_a=.3/|M| sum_i in M K_ai exp(i theta_i). Compute the entire channel before multiplying by the treatment mask. Nonselected particles remain active but do not emit through this targeted intervention. |
| Previous sources | After their fixed exposure, outgoing masks are zero in all branches. Evolve every original source/carrier state live with its original input law. No later candidate reads their members or receives a direct previous-source drive. |

The independent carrier z_ref starts from the actual environment at introduction and evolves the same medium law with analytic drive and every source output disabled. It is an owner state, evolved concurrently at every RK stage; it is not a coarse replay or a later truth refresh. Current-source motion/phases sample this carrier. The actual medium receives the current source output only after qualification, for the fixed exposure. The carrier boundary preserves identical intact/sham source trajectories while allowing a changed actual environment to affect the next introduced population. This boundary is the same at both turns.

The selected output mask is an explicit experimental intervention on a detected unit, not a natural promotion law or evidence that publication creates a resonator. All initial particles and previous sources keep evolving. Other candidates are independent measurement forks and are not inserted into the recursive main branch.

## 3. Local unit qualification

Run a common prefix for 100 C0 with current output OFF. Save the whole owner state at t=100. Observe the last 30 C0 with frames every C0. Apply the frozen C4 persistence/recovery thresholds, but evolve recovery with this new law in owner forks. Reuse frozen detector/statistic functions read-only; do not call frozen C4 simulation for this model's recovery.

Thresholds: minimum size 3; link factor 1.5; membership Jaccard .95; shape CV .05; lock standard deviation .1 rad; half-window collective-frequency difference .01/C0; pair-pattern difference .1 rad; recovery time 30 C0, position kick RMS .1 times measured median nearest spacing, phase kick RMS .3 rad; all original/control/kicked Jaccards ≥.9 and recovered pair-pattern error ≤.1 rad. Degenerate size/spacing is INVALID. Report every detected candidate and recovery failure. Select the largest structurally accepted candidate, breaking ties by member digest; no retries or scanning for a more favorable causal candidate.

The selected candidate also needs local G→M and M→G causality in independent, paired forks from the saved state:

- G→M: both forks receive the same zero-mean .3-rad phase probe; scale selected positions about their centroid by 1.5 in the treated fork. Over 5 C0 measure RMS wrapped difference between treated/control pairwise phase patterns. Complete ablation freezes all material phase weights and the incoming-medium sampling weights at their common preintervention positions. Motion still evolves. This removes both local and incoming geometry→mode paths.
- M→G: replace selected phases by uniform phases in the treated fork, holding all positions fixed. Over 10 C0 measure RMS treated/control displacement of the selected elements divided by their saved radius of gyration. Complete ablation sets J=0 throughout the material population; there is no other mode-dependent material force.
- Both intact effects must exceed 10^-8 in their stated units. Ablated effects must be ≤max(10^-12,.2 times the minimum intact effect across numerical grids). Use nonnegative response distances, not a signed improvement statistic. All three grid effects must remain positive and their spread must be ≤.1 times the smallest intact effect.

These forks validate the t=100 snapshot; they do not advance or replace its main state. Record their elapsed computational work and future simulated time separately. The full qualification snapshot includes actual medium, carrier, every source, rates, selected IDs and the absolute clock. A finite candidate-linked publication is diagnostic and does not affect the full dynamics.

## 4. Post-qualification operation and controls

Only a qualifying common-prefix snapshot can start treatment. Clone that exact whole state into three branches and run another 100 C0:

| Condition | Material law after the common prefix | Current outgoing channel |
|---|---|---|
| INTACT | Unchanged | Full selected-member output |
| NO-BACKREACTION | Unchanged, same independent carrier | Compute full output, then multiply by zero |
| NO-R | Set both internal K=0 and J=0; keep external medium input, rates, positions and all particles | Full output of the same fixed member IDs under the ablated law |

The selected-member mask, identity inventory, normalizer definitions and initial state cannot change between branches; treatment masks differ only as declared in the table. Before qualification there is no current output in any branch. Log the first nonzero output time. Measure the sham's actual outgoing norm at every step, and intact/sham source-state equality over the entire operation with tolerance 10^-12. Reapply persistence/closure to the original selected member set at the operation endpoint: intact/sham must retain that source, NO-R must not qualify. A different selected group cannot substitute for a lost original source. A control failure blocks affected claims rather than triggering a replacement control.

The actual environment at operation start is B_before; each operation endpoint is B_after. Record descriptors for every reached prefix and branch, including unsuccessful source worlds through explicit no-treatment diagnostics. Unqualified worlds do not receive an invented treatment or a causal background contrast.

At the fixed operation endpoint, set all outgoing source masks to zero in every branch, without changing any field/source/carrier state. Subsequent response and candidate forks use that state under identical source-free medium laws plus analytic drive. The first source remains active in its own full material/carrier state throughout turn 2, but its switched-off path cannot directly drive a later population. This tests retained change after a finite exposure; it does not test permanent emitting-source mediation. Field history, not continuous forcing or publication, must carry the effect.

## 5. Background response descriptor

Use every one of the 25 medium sites as fixed probe ports. Let alpha be an independently drawn world phase reference, unrelated to the final environment. At each port use two additive impulses .05 exp(i alpha) and .05 i exp(i alpha), each in its own snapshot fork. Run paired perturbed/unperturbed medium trajectories for 10 C0, with outgoing source masks zero and the same analytic drive; a probe cannot feed into any independent carrier or source state. Independent source/carrier components advance on a shared unperturbed owner trajectory, since no probe changes them; count their work and retain the full state.

The response scalar is the mean across fifty probes of RMS |z_perturbed-z_control|/.05 over all 25 sites (including the probed site) and times .1,.2,...,10. It is a dimensionless gain, covering local and transmitted response without outcome-selected ports. Retain raw complex arrays and receiver IDs. Use identical probes and drive phases at B_before and all B_after. No phase-only observable is used near zero amplitude. Global phase/coordinate transformations also transform the declared probes/sites.

Primary world contrast against each control is response_after_intact minus response_after_control. The shared before descriptor is retained and cancels in the contrast. The registered alternative is two-sided CHANGE with margin .01 gain units, a prospective practical cut in this new response normalization rather than a transferred R3 radian threshold. Negative changes are not failures of the abstract RRG interpretation. Mean amplitude, spatial coherence, source output power and state distance are diagnostics; none can substitute for this response endpoint.

## 6. Later candidates and exact recursive continuation

At each B_after expose the same four independently generated unformed populations, one per snapshot fork, for a 100-C0 qualification prefix plus 30-C0 recovery forks. Every source output stays OFF during qualification. The branch carrier starts at that branch's B_after and evolves with the same analytic drive. Thus candidate inputs differ only through the inherited environment, and continuing R0 forcing cannot erase or imitate the mediator. All candidate initial arrays, prescribed centres, clocks and perturbation entropy are paired across intact/controls. The detector and local closure rule are unchanged. Before-background candidates are diagnostics with the same population states and procedure.

World formation response is the fraction of four candidates qualifying. Primary contrast is fraction_intact minus fraction_control, with two-sided CHANGE margin .10. Count every failed/invalid episode explicitly; engineering-invalid evidence makes the affected assay invalid, rather than becoming a physical nonformation.

The intact episode numbered zero is the only R1 that can continue. If it does not qualify, stop that world's chain; episodes 1–3 cannot replace it. Retain its full t=100 qualification state, including the actual medium at that point, carrier, old-source/carrier states and zero outgoing masks, initial episode state, rates and absolute clock. Continue directly from that object into the second post-qualification operation. No resampling, requalification prefix, relocation of the formed source, terminal replay or new carrier is allowed. Treatment copies for turn 2 clone this object; its intact branch is the main recursive continuation.

Absolute main-world times are: R0 introduction 0, R0 qualification 100, first operation end 200, R1 episode-zero qualification 300, second operation end 400, later R2 qualification 500. Recovery and response forks do not alter main-world time. R0 remains active throughout; R1 remains active throughout its operation and later assays. The second operation starts from the environment at time 300, reached by evolving B1 rather than restoring the time-200 snapshot. Store both identities and the complete flow linking them.

Every chain link binds full source state, both medium states, prior source/carrier states, IDs, rates, clock, selected candidate and actual continuation inputs. Field geometry/parameters and array shape are included in identity hashes. Preserve the original introduction state and actual qualification state separately; equal member digests do not establish continuity.

## 7. Numerical and kernel qualification

Production dt=.005 C0, half .0025, quarter .00125. Use RK4 with all fields/carriers/sources evaluated together at each substage. Recompute smooth spatial weights at substages. No sampled replay interpolation is involved. Derive analytic external forcing from the absolute time at each substage.

An independent NumPy implementation and prospective native implementation must agree within 10^-10 on normalized full states. Isolated unforced medium sites must match the exact zero/constant-radius periodic solutions and cubic/linear limiting cases in the research note. Test zero source masks, J/K path removal, constant-field sampling, symmetry, permutations and time continuity. The new smooth particle law needs its own reference and cannot inherit C4's numerical acceptance.

For each recorded world, cover the entire reached qualification and operation horizons, all reached treatment modes, background probes, candidate qualification/recovery and local causal forks. Independently integrate the full owner state at each grid from the same initial arrays/drive parameters; a fine run cannot consume a coarse carrier. Compare states at matching absolute times, recording maxima across the full scope rather than two short windows.

Maximum position error divided by the scope's fixed initial material radius of gyration ≤.05; wrapped material phase error ≤.05 rad; complex medium/carrier error divided by Z0 ≤.05. Record full raw errors for coarse/quarter and half/quarter, as well as local causal effect refinement. Require candidate selections, binary qualification decisions and continuation IDs to agree across grids. Any unresolved grid-dependent formation decision blocks affected inference. Zero source size/invalid normalization is a visible failure.

The state tolerance alone does not qualify the small response impulse. Separately require every background response gain and paired world gain contrast to differ by ≤.001 between production and quarter grids, one tenth of the .01 practical margin. Require the registered contrast verdicts to agree under the production and quarter-grid analysis using the same bootstrap draws. Record both, without choosing a grid that gives support. A grid-dependent decision is INCONCLUSIVE with numerical qualification failed. These are empirical finite-grid checks, not a certified continuum error bound.

Permutation, common translation/rotation of source and sites, and common phase rotation of states/drive/probes must agree to 10^-9. The fixed finite site layout transforms with the scene; this is covariance of the declared apparatus, not arbitrary rotational invariance of a stationary grid. Cache the loaded native binary identity in the owner and receipt; changing disk code cannot silently keep an old loaded kernel.

Use streaming paired comparisons and checkpointed owner states; retain detector/response raw samples and complete maxima with scope/time/IDs. Do not retain every fine-step trajectory solely for diagnostics. Report peak memory and serialized bytes; do not silently substitute returned-array bytes for peak memory.

## 8. Normalization and access ledger

| Quantity / level | Estimator, units and normalization | Owner and access |
|---|---|---|
| Site geometry, material positions, kernel width, soft core | L0=1; sigma=2 L0, eps=.05 L0; same constants both turns | Full owner; no upper predictor exists |
| Introduction location | One fixed translation step 2 L0 along the supplied scene axis per new population generation; coordinate transformations also transform that axis | Generator, independent of observed groups or outcomes |
| Material unit size | Radius of gyration of the selected set at the saved snapshot, L; must be positive | Evaluator; publication carries finite size |
| Geometry kick and recovery spacing | Measured median nearest spacing within selected material set, L; RMS kick .1 spacing | Evaluator; no per-turn tuning |
| Timing and rates | C0=1 fixed model time, frequencies radians/C0; horizons 100/30/10/5 C0 | Full owner; no claimed increasing-scale law |
| Material phases/lock | Wrapped radians; lock .1, frequency .01/C0, pattern .1 rad | Same detector every population/condition/turn |
| Medium and carrier values | Complex amplitude/Z0, Z0=1 fixed model amplitude; no data-dependent amplitude normalization | Owner; medium sites never enter material membership lists |
| Incoming/outgoing channels | Bounded complex input; incoming coefficient .2/C0, output .3 Z0/C0 per selected-member mean | Full owner; all members/weights/masks in receipt |
| G→M / M→G effects | RMS pair-pattern distance in radians / RMS material displacement divided by saved selected size | Evaluator-only interventions; complete path ablations |
| Background response | Receiver/time RMS amplitude difference divided by the .05 Z0 impulse; dimensionless gain | Independent evaluator snapshot forks |
| Later formation | Qualified fraction of exactly four paired episodes; probability contrast | Evaluator; no expected membership passed to detector |
| Numerical errors | Positions/scope initial measured size, phases/rad, medium/Z0; one recipe at every reached scope | Full owner/evaluator; invalid scales stop |
| Costs | Wall/CPU seconds, native and reference work, peak resident memory, serialized/storage bytes, I/O and failed-world work | Orchestrator; H-EFF not assigned |

Descendant reads and member scans belong to the full owner/evaluator only. A publication is a read-only report, not a new dynamics owner or a predictive API. Direct parts and deeper hierarchies are absent from Arm B; no downstream inference about them is claimed.

## 9. Registration, endpoints and statistical rules

After approval, write a versioned protocol, manifest and milestone config with every rule here before final seeds. Implementer family Codex; final independent reviewer family Claude. Fresh development entropy 46034001, smoke 46034002 and bootstrap 46034003 are reserved prospective namespaces, disjoint from R3. Final entropy is generated once only after development/runtime readiness and committed registration, following the existing gate. No final entropy exists now.

One fixed development gate: ten worlds, exactly one run. Require ≥5 qualifying initial sources and ≥5 complete numerically/control-valid two-turn chains, complete raw coverage and a measured resource/runtime estimate. This gate checks apparatus readiness, not whether primary effect directions pass. A zero/negative scientific contrast is not an engineering failure or permission to retune. Any stop preserves raw results. No second development attempt for the same design.

Final panel: forty independent worlds, four paired later episodes per condition/turn; world is the independent sampling unit. At least ten valid worlds are needed for each inferential contrast. Complete-chain contrasts use exactly the same world-ID mask at both turns. Frames, sites, probes and episodes are averaged inside a world; none inflate sample count.

Primary endpoints are exactly sixteen: two control comparisons times two quantities (background response and later formation) times two turns, plus the same eight comparisons restricted to the exact complete-chain set. Names: b_response_vs_{control}_turn{1,2}, b_later_formation_vs_{control}_turn{1,2}, and their b_chain_ variants. Controls are no_r and no_backreaction. No primary position-response alias or hidden additional primary is used.

Use 10,000 original-world bootstrap resamples, with fixed draws shared across contrasts and invalid/missing rows preserved. Nominal CI .95 is diagnostic. Primary percentile CI level is .996875 = 1-.05/16. Each contrast has PASS when its entire primary CI is strictly above +margin or below -margin; FAIL when the entire CI is strictly inside (-margin,+margin); otherwise INCONCLUSIVE. Missing CI or fewer than ten eligible worlds is INCONCLUSIVE. Equality is never rounded into a pass/fail. The bootstrap is a finite-sample approximation, not exact simultaneous population coverage.

H-BG per turn combines its two response contrasts: both PASS → SUPPORTED_WITHIN_SCOPE; any FAIL → NOT_SUPPORTED; otherwise INCONCLUSIVE. H-PS has the same rule on formation contrasts, but cannot be SUPPORTED_WITHIN_SCOPE without supported H-BG for that turn. A turn's valid verdict uses its own gates; a late failure cannot erase a valid earlier result. H-RBG requires all four chain-restricted H-BG/H-PS claims supported, at least ten complete chains and valid controls/numerics/provenance across the chain scope. A required valid chain contrast FAIL → NOT_SUPPORTED; unresolved quorum or invalid evidence → INCONCLUSIVE. These are conditional formed-world/complete-chain claims, not population-level recursion rates.

Diagnostics with mandatory coverage: source qualification/candidates/publication per turn, initial and final intact/NO-R/sham source state, measured output masks, B_before/every B_after/raw response, before/control candidate formation, per-episode qualification/recovery/cause, source/chain yield across all forty worlds, exact chain inputs, full-scope numerical errors, costs/build identity and complete audited source pin. All Arm A endpoints are NOT_RUN with decision 0013. H-COMP/H-PRED/H-AI/H-EFF are NOT_TESTED. Every endpoint is evaluated with value/verdict or not_run with a reason.

## 10. Implementation and verification batch

After approval, implement in new files: c6_r4_field.py (typed owner and smooth law), c6_r4_field_reference.py (independent reference), c6_r4_field_assay.py (model-specific qualification/recovery/response), c6_r4_field_protocol.py (timeline and continuation), c6_r4_field_analysis.py (sixteen endpoints and exact evidence contracts), run_c6_r4.py, native/c6_r4/field.cpp, tests/test_c6_r4_field.py, tools/c6_r4_design_gate.py and tools/c6_r4_mutants.py. Register experiments/c6_r4_protocol.json, the C6 manifest and milestone stage commands prospectively. Preserve accepted and R3 files and the existing repair validation hashes.

Reuse c6_r4_integrity identities and finite/inventory checks, plus the repaired change-verdict concept and world-paired bootstrap. The existing phase-specific R4 evaluator is not a drop-in field evaluator: new response units and full-state continuation need explicit new contracts. Frozen C4 detector/statistic primitives are reused read-only; new owner forks supply recovery/causality under the new law. No prediction code or game/UI work enters this batch.

Complex fields need explicit typed validation before reusing real-array helpers. Encode real and imaginary parts as separate named float64 arrays, validate both, and bind their ordered field names/physical schema in digest metadata. Never pass a complex array to the existing real-only array_digest (which would discard its imaginary part), and never silently accept it through the existing finite helper. Round-trip complex checkpoint tests must distinguish equal real parts with different imaginary parts and actual/carrier swaps.

Finish all code, tests, mutants and review-driven fixes before the one test run. Then run the one development gate with announced duration. Development computation has a 1800-second cap; its runtime is currently unknown. Final-stage budget is 10800 seconds via the repaired registered timeout field. Use a measured conservative projection of observed full-chain cost, refinement overhead, build/process/I/O overhead and workload variability; a projection above budget or too uncertain returns a budget decision rather than starting a final panel. Measure worker/concurrency memory before selecting final concurrency.

Once readiness and committed registration hold, use only the ordered pipeline: preflight → final code tests → smoke → parallel mutation probe → recorded panel. The pipeline's required tests are a stage requirement, not optional everyday reruns. Never edit while it runs; successful stages resume for unchanged code. Mutants must exercise early emission, wrong sham mask/denominator, carrier contamination, missing NO-R path removal, incomplete local ablations, unmatched episode state, cherry-picked episode continuation, reset environment/clock, omitted full-state identity, subset-mismatched chain contrasts, duplicate IDs, uncorrected CI, missing endpoints, ignored numerical failures, coarse/refined input mixing, false publication and old native cache identity. Commit evidence, then one ≤20-minute Claude review. Passing engineering checks does not assign scientific support or acceptance.

The final runner calls tools/milestones.py check("c6", "panel") itself. Development and final outputs have distinct receipt kinds and paths; the development gate cannot generate a final hypothesis verdict or final entropy. Registration fingerprints include the proposal/protocol, source inventories, new sources/native build and relevant read-only support dependencies.

## 11. Stop table

| Yes/no stop condition | One action | Responsible role |
|---|---|---|
| Completed R4 proposal approved by owner? No | Await approval before implementation or new experimental execution | Drafter |
| Audited source identities complete and consistent? No | Resolve source access before execution | Drafter |
| A measured normalization or input denominator invalid? Yes | Record INVALID and stop the affected assay | Implementer |
| Current output starts before common qualification? Yes | Return the implementation defect before any panel | Implementer |
| Sham fails full source preservation or output-zero check? Yes | Return CHANGES_REQUIRED for the apparatus | Implementer |
| NO-R still qualifies or local ablation leaves the named path? Yes | Return the control defect without replacing the control | Implementer |
| Numerical scope, refinement, symmetry or selection stability fails? Yes | Record the block and preserve evidence | Implementer |
| Development source/complete-chain quorum below 5/10? Yes | Preserve STOP and request a fresh prospective design | Implementer |
| Episode zero fails qualification? Yes | Stop that world's continuation without replacement | Implementer |
| Budget projection unknown or above the approved cap? Yes | Decide budget or scope before final registration/execution | Owner |
| Scientific contrast is zero or negative with valid assays? Yes | Apply the registered CHANGE rule unchanged | Implementer |
| A design defect is found after results were recorded? Yes | Withdraw through a new decision and retain all evidence | Implementer |
| Independent final review requires changes? Yes | Return CHANGES_REQUIRED for a fresh revision | Reviewer |

## 12. Drafter self-audit

| Issue found during drafting | Cause | Fix in this proposal / remaining limit |
|---|---|---|
| A fixed linear field would not automatically change additive susceptibility | Confusing a changed state with a changed response operator | Select an explicit nonlinear amplitude medium; retain an empirical response test rather than assert success. |
| A field sampled from coarse replay would repeat R3's accuracy gap | Treating input interpolation as outside the dynamics qualification | Evolve carriers and previous sources live in the full owner at every RK substage. |
| Qualifying with future recovery forks could advance the main branch accidentally | Mixing fork simulation time with main-world chronology | Keep a saved t=100 owner snapshot; qualification forks never replace it. |
| Outgoing contributions from nonselected particles would confound the unit's effect | Treating a material population as the detected resonator | Mask the targeted selected set only, with identical IDs in controls; retain all other full dynamics. This is an engineered intervention. |
| An episode-zero member digest alone would permit a restaged second turn | Incomplete state provenance | Retain actual full qualified source/carrier/medium/old-source state and clock, and continue that same object. |
| Phase response becomes unreliable near zero medium amplitude | Reusing R3's phase-only descriptor on complex fields | Use raw complex impulse gain with fixed amplitude normalization. |
| A .05 state error could overwhelm a .05-amplitude impulse | Treating full-state accuracy as adequate contrast accuracy | Require gain/paired-contrast refinement within .001 and unchanged registered grid verdicts; disclose finite-grid rather than continuum qualification. |
| A single-attractor medium or continuing R0 input could erase the changed environment | Assuming nonlinear response alone supplies retained environmental mediation | Supply a two-basin medium and disable output after each finite exposure; later assays isolate retained state. Bistability is an apparatus assumption, not a measured recursive outcome. |
| Repeated identical location/exposure could saturate the same field region | Equating repeated procedure with repeated location | Translate each new unformed population by the same predeclared 2-L0 step; never relocate a formed unit or follow an observed group. Saturation remains a possible negative result. |
| Medium sites or prescribed material domains could imply label-free whole-world discovery | Conflating typed physical apparatus with discovered memberships | State the domain boundary and restricted detection claim explicitly; no prebuilt unit is supplied. |
| Baseline formation might saturate or source quorum might fail | New coupling parameters are unmeasured engineering hypotheses | One fixed readiness gate, no effect-based tuning; report valid negatives and stop apparatus failures honestly. |
| R4 repair helpers imply a ready field runner | Reusing revision names without matching response units/state shape | New field-specific runner/evaluator files, full registration and new model qualification are required. |
| Real-only digest/finiteness helpers do not support complex medium arrays | Assuming reuse is valid after a state-type change | Validate/encode named real and imaginary arrays explicitly before hashing and check complex round trips; preserve existing helper receipts. |

The design addresses R3's onset, mixing and numerical-contract defects prospectively. Whether it forms usable units, changes response, alters formation or completes two turns remains unmeasured.
