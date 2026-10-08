# Full-army units and tactical leader — revision 2

Date: 2026-10-08. Drafter: Codex. Status: development design; only A0 tooling is authorized in this delivery. No fights run in the sandbox. Decisions 0033–0036 and the owner's current instructions govern this work. A0 is a practical decomposition test, not a registered GeoMind milestone or evidence of RRG source recursion.

## A0: the first runnable stage

A0 contains scripts only. It answers whether a group teacher adds enough value to justify building a learned leader. It runs the real 50-versus-50 army: ten melee, thirty ranged and ten guns per side. Abilities are off for this slice. Formation, opponent behavior, combat, preparation and projectile mechanics remain those of the existing engine.

Three arms play paired battles with the same seed, placement, orientation and enemy tactic:

| Arm | What it executes |
|---|---|
| O | The public unit oracle. It includes P16 escort, focus, anchor, approach and repulsion, followed by participation and react/body precedence. Each eligible gun chooses its own best one-gun V2 plan. |
| O+G | The same O. On a release event with at least two eligible guns, V2 chooses the battery's joint points and assignments through the existing validated command interface. |
| T | The complete historical forcedP16+react+V2 teacher, including its inherited v6 state. |

O is deliberately stateless between base decisions except for its held command cache. It selects the nearest legal enemy, or the nearest living enemy when none is legal, with ID ties. Melee approaches body contact; ranged approaches its engagement band. Artillery uses the P16 focus overlay. It does not imitate v6 target memory. This choice is tested against T rather than assumed harmless.

O refreshes its base proposal at 5 Hz. A dead target invalidates the cache immediately. React and body checks run each physical tick. Artillery aim is chosen at the physical prepared-release event, after native preparation has advanced. T retains its historical cadence. Thus O−T measures both the decomposition and cadence gap. Neither arm adds a custom start-target lock, forced six-tick release or cancellation. The bridge retargets on dispatch and native preparation does not lock a target ([controller_bridge.cpp:46](../src/native/controller_bridge.cpp), [combat_rules.cpp:60–68](../src/native/combat_rules.cpp)). Melee/artillery use pre-walk reach and ranged uses post-walk reach ([combat.cpp:11–33](../src/native/combat.cpp)).

First run a separate 18-fight pilot: three paired regular battles and three paired C3 battles against storm, loose and wolfpack, with all three arms. Measure the multi-gun event share before outcome interpretation. Report eligible events, events with at least two eligible guns, joint/applied/rejected assignments, frame bytes and timing. This is a mechanism/timing sample, not a small-sample drop decision. Its entropy is separate from the outcomes.

Then read 50 pairs and, unless stopped for harm or insufficient mechanism coverage, 100 pairs in each panel. Regular has its own panel. C3 has one balanced panel across its twenty cells (regular plus nineteen catalog tactics), not 100 pairs per tactic. At 50, each C3 cell has two or three pairs. At 100, each has five. Orientations alternate within cells. Six arms across both panels mean 300 physical fights at the 50-pair look and 600 cumulative at 100. This follows decision 0033's staged sizing without a precision extension.

Decision 0034 numbers are own deaths per fight and enemy kills per own death over all paired fights. Exchange is the ratio of total kills to total own deaths, with a zero-denominator flag. Also report kills/fight, damage/fight, kills per minute, win rate and won/nonwon results. When kills saturate, report the saturated fraction. Time to enemy elimination is censored for noneliminations: show the eliminated-only mean with its denominator, the elimination fraction, and the mean restricted time using 150 seconds for noneliminations. A0 runs no series; the ten-fight streak is explicitly not run.

The practical usefulness floor is two deaths saved per fight or +0.10 kills per own death. Harm is two extra own deaths or two fewer enemy kills per fight. Both panels must pass the usefulness floor without harm before future leader work is justified. This is a conservative development rule, not a significance or optimality claim. Report paired death SD, approximate descriptive intervals and the planned 80%-power death MDE (2.8 × SD / sqrt(n)) at 50 and 100. The measured O+G−O effect is the leader's ceiling. A ceiling below the floor is parked; it does not receive a large learned outcome panel. Event share alone does not causally attribute deaths saved to single- versus multi-gun events; that attribution is unresolved in these three arms and must not be invented.

| Yes/no condition | Action if yes | Responsible role |
|---|---|---|
| Is multi-gun event share below 1% in either completed 50-pair panel? | Park the leader route and report to owner | drafter |
| Does either completed look show the declared harm? | Park the leader route and report to owner | drafter |
| At 100 pairs, does O+G fail to beat O by the usefulness floor on deaths/fight or kills per own death in either panel? | Park the leader for the full army, report to owner, and continue units-alone training | drafter |
| Is the O−T decomposition gap practically harmful? | Revise the unit oracle before collecting training data | drafter |
| Does a source identity, command legality, completion or pairing check fail? | Stop and repair the tooling | implementer |
| Is process discovery unavailable or another repository heavy job active? | Stop before starting a fight | implementer |
| Does the measured remaining projection exceed the owner cap? | Report the required time to owner | implementer |
| Does child RSS exceed 2 GiB or live free/inactive RAM fall below the 512 MiB reserve? | Stop the invocation and preserve completed fights | implementer |

Use the repository process gate from `s4_net_slice_v1/process_gate.py`, read-only, with receipts redirected into this folder's `_local`. Read the current owner setting from `s4_shape_lab_v1/raw/LAB_CAP.json` on every invocation. The present owner setting is 10,800 seconds; it is an operational setting, not a source identity. The RSS allowance is 2 GiB (the S1FIX_RSSFIX correction), not the retired 512 MiB process cap. Raw requests, entropy, streams and attempts stay under gitignored `_local`. A command holds one advisory execution lock and runs one low-priority child at a time. Each invocation gets a separate compact results file; completed fights are hash-checked and reused on resume. No committed file may reach 45 MB.

Project time from the 18 measured fights, using each arm's slowest full-150-second equivalent and a 20% margin. Compare remaining work with the owner cap before launching a panel. Enforce the wall deadline during every child and live memory checks while it runs. Historical v6 script timing of about 33 serial seconds/fight is only a planning anchor: pilot about ten minutes, 50-pair look about 1.5–2.5 hours serial, cumulative 100 about 3–5 hours. A0's measurements replace these estimates. A cap refusal is retained, never bypassed. There are no measured A0 fight timings in this delivery.

## Why P16 belongs to the unit

Every unit sees all living friends and enemies. The following quantities depend on this public view and no other unit's chosen action:

| Quantity | Source and ownership |
|---|---|
| Ranged escort | Nearest own gun; enemy ranged near it, otherwise enemy-gun centroid. [escort.cpp:20–29](../s4_escort_probe_v1/escort.cpp). Unit O owns it. |
| Gun focus and anchor | Enemy guns ranked by splash value; first reachable by this gun, with the anchor reachable by any own gun. [s4_v7_controller.cpp:20–28](../src/native/s4_v7_controller.cpp), [escort.cpp:4–6](../s4_escort_probe_v3/escort.cpp). Unit O owns them. |
| Approach and repulsion | Preferred focus radius and nearby-own-gun repulsion. [s4_v7_controller.cpp:29–36](../src/native/s4_v7_controller.cpp). Unit O owns them. |
| One-gun V2 choice | A single ready gun can choose Singles or Focus without a joint assignment. [artillery.cpp:64–74](../src/native/artillery.cpp). Unit O owns the entire one-gun choice. |
| Multi-gun V2 assignment | Family scoring and nearest-free allocation couple ready guns. [shapes.cpp:103–124](../s4_shape_lab_v6/shapes.cpp), [artillery.cpp:8–14](../src/native/artillery.cpp), [artillery.cpp:86–91](../src/native/artillery.cpp). G owns this only when at least two guns are eligible. |

No other group decision is admitted without cited source lines establishing its coupling. O evaluates each gun separately even on multi-gun events; O+G changes only their joint aim allocation. G emits gun-bound absolute aim points for the current event. It does not change targets, create escort orders, delay fire or add latent lookahead. Points must satisfy the v6 arena and current/post-move annulus predicate. Illegal points fall back to the same autonomous command and are counted.

## Labels must describe execution

An escort label is not the raw escort point. The oracle passes the P16 proposal through `participate()` ([react.cpp:69–86](../s4_react_adapter_v1/react.cpp)). Then active react replaces movement and holds fire; guard, body ability and failure retain their native precedence ([react.cpp:96–104](../s4_react_adapter_v1/react.cpp)). A present command cannot override react or body precedence. The adapter's `submit()` already implements that rule; the conditioned labels must do so too.

A0 counts raw-to-executed waypoint distance and active-fire label rates. Future collection stores the raw overlay, participation result, react candidate, current command, post-precedence result and post-bridge acknowledgement separately. Targets at start, dispatch and aim reference remain separate fields. Obedience is labelled only on a legal present-command opportunity without a higher-priority winner. It is never labelled “always obey a present command.” For melee/ranged, start/release base rates are reported because much of that label is simply not reacting, guarded or busy. Accuracy on a nearly constant label is not competence.

## Later stages: units first, leaders conditional

These stages are interface commitments, not code in this delivery. Units-alone work may proceed if the group route is parked, after repairing any unacceptable O−T gap. Unit collection uses O as the behavior policy and labels what O executed. Group collection uses O+G and labels that same group oracle on its own trajectories. T is a comparator, not the default training distribution. When learned policies are deployed for collection, budget one prospective on-policy relabelling round on their visited states. Keep that entropy and report separate; never relabel held-out outcome panels to improve a verdict.

Split whole fights into training, validation and test before fitting. Balance all twenty opponent cells and orientation in each split. Transformations inherit the original fight's split. Detect repeated seeds and trajectory fingerprints. Admit a row only when the encoded input contains every fact used by its label. Count exact-input label conflicts by head, opportunity and command presence. Missing required-role coverage or inconsistent labels is a collection defect, not a reason to fit longer.

The public observation covers all 50 friends and 50 enemies with cap 64 per side, including stable identity masks and roles. Threat banks have explicit shell, shot, cast and field capacities and overflow counters. A row whose omitted threat changes a label is rejected. The model receives own preparation, energy, guard/body state, public entity position/velocity/HP/reach and public threats, but no engine handles, RNG, enemy private state, v6 memory or evaluator descendant reads.

The unit heads select movement, current target, start/release intent and artillery aim. Autonomous movement support includes hold, bounded polar candidates and an exact P16 post-participation candidate. Add a distinct exact present-command candidate when needed. Artillery support includes bounded points around its public single-gun choice plus an exact feasible group point. Supports have masks, deterministic ties and rejection counters. A conditioned learned head selects a command; the host does not overwrite its answer with the teacher. React/body safety precedence and the engine's target/reach mechanics remain explicit. Log singleton supports and projection error separately from learned choices.

U-P has bounded recurrent memory. U-R replaces that memory with persistent phase and bounded learned forcing/coupling, with the same encoder, inputs, heads and action bounds. Match U-P/U-R learned parameters within 10%, fixed before fitting. Phase state initializes deterministically per identity, prunes on death and updates once per physical tick. Base heads refresh at 5 Hz; ready-event heads use fresh readiness/physical features and cached world encoding. A new command does not advance recurrence a second time. Replay includes tick, cache age, previous accepted context and acknowledgements so this order can be tested.

For a future group comparison, train R only on U-R contexts. Fit one P on U-P contexts for U-P+P, and another P on U-R contexts for the U-R+P bridge. U-R+P versus U-R+R then holds both children and training data fixed. Match leader parameters within 10%. Report actual rows, updates, FLOPs, time and RSS; matched parameters do not mean matched computation. Do not pool plain-child rows into R while disabling its parent dynamics on half its data.

Direct artillery publications include position, velocity, radius, HP, readiness, current action and bounded mode/rate. For U-R, compose area weights w_i = r_i²/sum(r_j²), centroid X, size L² = sum(w_i (|p_i−X|²+r_i²)), mode m = sum(w_i exp(i theta_i)), size-weighted natural rate and summed eligible port capacities. Parent phase persists with membership changes. A missing/invalid child mode or rate is masked and can veto composition. An empty group emits empty commands. Underlying living units keep evolving. Parent forcing and geometry-dependent coupling must change child actions and later geometry to support even a local loop claim. This development imitation study does not establish recursive background transformation or source qualification.

Report whether K and forcing moved from initialization. Report phase variation explained by attack resets versus phase variation not explained by them. A reset-synchronized clock is not evidence of learned coupling. Phase/model differences without these diagnostics have only a practical behavior reading.

## Compute and normalization contract

Encode the world once per 5 Hz decision frame, shared by all unit queries. Use two width-64 token MLP blocks and single-query pooling; no per-unit re-encoding and no full token self-attention. At most 321 tokens encode entities and threats once. Ready-event heads read cached embeddings plus fresh physical readiness/target features. Per-tick recurrence/phase updates consume only cheap physical features and the last shared embedding.

A conservative forward bound is 20 MFLOP per shared frame, including all 50 unit queries/heads. A 150-second fight has at most 750 base frames: about 15 GFLOP forward, plus event heads and cheap per-tick state. With 180 training fights, ten epochs and backward bounded at three times forward, the unsubsampled bound is about 81 TFLOP before event/optimizer overhead. Subsample base frames by four, preserving every release, reaction transition and command opportunity; this lowers the base part to about 20 TFLOP. Raw float32 encoded features at 321 × 64 × 750 occupy about 59 MiB/fight; stream fight shards, never load the entire dataset. Keep batch activations and optimizer state below 2 GiB measured RSS. These are arithmetic bounds, not measured throughput.

Train in float32. Export to the native float64 path and compare outputs and resulting categorical decisions on stored validation fixtures, including near-ties and masking. A categorical difference is a parity defect; log numeric error and resolve it before outcome execution. Float64 parity replay does not require float64 training.

Target each complete initial fit at no more than one hour and each network fight at no more than twice A0's measured script-fight time. Before a full fit, measure at most twenty optimizer steps on training-only scratch windows. Include packing, validation/refresh cost and startup, then project the declared total steps with a 20% margin. Do not select a checkpoint from this timing sample. Seal equal window/batch settings and at most ten epochs before fitting. Validation loss selects the checkpoint, earliest tie. Test and outcome data never select it. A fit sample projection above one hour or the owner cap forces an architecture/data-budget revision before the full fit.

| Quantity | Level and units | Normalization |
|---|---|---|
| Position, movement, reach and threat radius | unit/world, pixels | coordinates relative to world dimensions; local distances divided by 100 px; decode to pixels |
| Velocity | unit, pixels/second | divide by 100 px/second |
| HP and energy | unit, native units | divide by own maxima with masks for missing/zero maxima |
| Time, cooldown and preparation | unit, seconds | divide by native cooldown/windup where valid; elapsed physical seconds remain explicit |
| Mode and forcing | unit/parent, radians and radians/second | sin/cos mode; bounded forcing ±1 rad/s, coupling [0,2] rad/s; total rate bound 5 rad/s |
| Group size and geometry | direct children, pixels/pixels² | radius-squared weights; geometry uses the same 100 px distance scale |
| Port capacity | direct children, attacks/second | sum valid direct-child eligible rates; no hidden deeper reads |
| Outcome deaths and kills | fight, counts | all paired fights; exchange is ratio of totals; time readouts carry censor masks |

Normalization follows R5 and decision 0007's same procedure constraint, allowing scale ratios and lawful direct-child summaries without hand-tuning physical bounds by level. Any future source claim must first pass `research/rrg/CURRENT.md` and the audited source identity gate.

| Yes/no condition for future work | Action if yes | Responsible role |
|---|---|---|
| Does the pre-build compute bound exceed the fit/fight target at measured throughput? | Revise the architecture before network implementation | drafter |
| Does the ≤20-step projection exceed the fit target or owner cap? | Revise the training budget before fitting | drafter |
| Does float32-to-float64 replay change a categorical decision? | Repair export parity | implementer |
| Does a required head lack opportunities, input facts or conflict-free labels? | Repair collection | drafter |
| Is O−T harmful beyond the declared tolerance? | Repair decomposition before training | drafter |
| Is start/release rate below half the same-state oracle's rate? | Repair autonomous learning | drafter |
| Are R dynamics invalid or reset-only? | Remove the mechanism interpretation from the report | drafter |
| Is a new stage requested without owner authorization? | Defer that stage | implementer |

## Drafter self-audit: review causes and fixes

The drafter owns these fixes. The prior same-family check did not identify the unit/group confound or the label precedence mismatch. That check remains historical; it is superseded by this revision and the new independent recheck.

| Finding | Cause in revision 1 | Revision 2 fix |
|---|---|---|
| H1 | Assumed full-teacher V2 gains transfer to different autonomous units, despite S1FIX harm | A0 pairs O, O+G and T before networks; script ceiling and mandatory park rule |
| H2 | Treated a raw P16 point as the executed escort label | Participation/react/body order is explicit; present commands lose to react; executed labels and waypoint-distance audit |
| H3 | Called public per-unit calculations group decisions | P16 and one-gun V2 move into O; only multi-gun assignment stays in G, with source lines |
| H4 | Chose expensive per-unit float64 encoding before any compute budget | Shared 5 Hz encoding, cheap pooling, float32 training, float64 parity, arithmetic bound and ≤20-step projection |
| M1 | Labelled O on T's behavior distribution | Collect with O and O+G, respectively; reserve a prospective on-policy repair round |
| M2 | Used saturated kills as the only damage readout | Kills/minute, censored elimination time and kill saturation fractions |
| M3 | Expected a learned leader to match the entire historical V2 effect | Measure its actual O+G−O ceiling first; park below threshold and report measured SD/MDE |
| M4 | Bundled schema, collection and fitting before anything runnable | First deliverable is script-only A0; later network interfaces are an appendix |
| M5 | Retained a superseded process RSS limit | 2 GiB child cap, live reserve check and current owner cap file |
| M6 | Pooled R data while disabling its distinctive mechanism on plain contexts | R uses U-R only; separate P fits provide the matched U-R bridge |
| L1 | Only leaders had a parameter tolerance | Both unit and leader P/R pairs match within 10% |
| L2 | Omitted prior K/phase failure diagnostics | Movement from initialization and reset-explained phase diagnostics required |
| L3 | Called largely constant intent accuracy competence | Start/release opportunity and active-label base rates required |
| L4 | Long dense paragraphs hid the first experiment | A0 contract comes first; short paragraphs and later-stage appendix |
| L5 | Committed a stale uncommitted marker | Delete UNCOMMITTED_DESIGN.txt; use a path-only UNCOMMITTED_A0.txt |

The separate owner's recheck and disposition are recorded beside this design. The user explicitly forbids changing `docs/PLAN_CURRENT.md` in this delivery, so that file is untouched.
