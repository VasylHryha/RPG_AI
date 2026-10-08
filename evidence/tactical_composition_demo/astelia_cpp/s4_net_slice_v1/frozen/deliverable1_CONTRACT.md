# NS1 guns-only engineering contract — deliverable 1

Status: implementation/fixture delivery, **not** teacher-data execution, training, lab qualification, registration, scientific acceptance or release. The owner approved direction and "Build now, contract first" in the frozen design. This contract prospectively resolves R2-F1–F10. Historical draft/revision-2 stop tables, Gaussian heads, Stuart–Landau ancestry, ES ranking and unbounded claims are superseded here. Design defects in those living proposals remain the drafter's responsibility; this folder does not rewrite them.

## Scope, dispatch and claim

Own artillery alone is learned. Own non-guns are stationary, target-none, no-release scaffolding; they still receive native body/collision/damage mechanics. Abilities are off on both sides. Enemy guns' decisions/physics and the opponent's planner remain native; the slice hook explicitly assigns stationary no-target/no-release scaffolding to enemy non-guns. Other combat changes are hooks belonging to `Host`. Network gun decisions never instantiate v7/P16, REACT, E1/R1 or an artillery policy. `Host` directly derives from `control::Controller`; `public_mechanics::participate` is an explicit geometric legality/never-leave projection, not a policy teacher. `teacher` and `shadow` are named separate pathways; shadow output cannot write policy cache/state or living world.

Slice cells: D1-static and D2-shellfire, each with 1, 2 and 10 own guns; two fixed own infantry dummies; 1/2/10 enemy guns, respectively, plus two static enemy infantry dummies in D1. Arena 1400×800 px, own guns x=400, enemy guns x=650; y=400+30*(index-(n-1)/2). Own infantry x=440, y=360/440; enemy infantry x=630, y=360/440. D2 enemy guns wind up/fire natively, supplying actual incoming shells; it is not v6 V2D2. Enemy non-guns use the stationary scaffold in every slice cell; enemy guns retain native decisions. Both orientations are paired horizontal reflections of placements, seeds and threats. No scripted dodge in network arms. D1/D2 request constructors are supplied; sealing the fresh collection inventory is next-deliverable work. No dataset run is authorized by this delivery.

N2 is a **geometry-coupled oscillatory policy projection** testing a local phase/commanded-motion/actual-geometry loop. C4 equations inspire this projection; accepted C4/C5 code is read-only. H-M requires later matched causal probes, not merely task ablation harm. H-U/H-COMP/H-BG/H-PS/H-RBG, effective-unit formation, ports, recovery and hierarchy are NOT_TESTED. C5 detection alone would not establish hierarchy: original-member recovery, direct-part validity, publication, size-weighted rates, coarse/full transfer and reopening would also be required. Imitation is not assumed to have a universal ceiling; stage 2 is optional after useful stage 1.

## R2-F1: allowlist, normalization, support and decoder

Wire version `NS1`, `schema.py`/`schema.cpp`; exact key sets, unknown keys rejected rather than ignored. Root: version, fight (opaque string), tick (integer physical tick >=1), side (0/1), self (persistent own gun ID), t, dt, width, height, units, threats. IDs, fight and tick are join metadata, never numeric learned features. Only live units are emitted. Own/enemy distinction is physical team==side. No tactic/doctrine ID, profile, skills, plan/search scores, private energy, RNG, hidden enemy preparation or future simulated trajectory enters the wire. Changing those internals cannot change the public wire except through later actual public consequences. Public enemy cooldown is permitted.

Unit keys common to both sides: id, team, role (0 melee/1 ranged/2 gun), x/y, vx/vy, hp/maxhp, radius, speed, range, min_range, damage, cooldown/cooldown_max, target. Own-only keys: prep, windup, time_rate, energy, cost, guard_until, busy, lob, splash, last_launch, consumed. Enemy **never** has own-only keys. Enemy winding state appears only as a `cast` threat for a living gun winding at a living friendly target; release/landing times follow the existing public adapter calculation. No other enemy preparation publication.

Normalization scales are fixed across levels/rosters; no per-level calibration. t=game seconds since this fight (reset between fights), dt=actual native seconds. No wall time. Lengths px, velocities px/s, phase radians, rates rad/s, energy engine EP. Feature division does not clip lawful finite values; model bounds handle their effects. Masked absent values are zero.

Flat layout is **1008** values: self32, friend12×32, enemy12×32, threat8×24, global16. Features stored float32; parity calculations and training/native model state use float64; encoding tolerance 1e-12 in double, export/forward/state tolerance 1e-9 absolute + 1e-9 relative. CPU only.

| Unit column | Quantity / normalization | Own | Enemy |
|---|---|---|---|
| 0 | presence mask | 1 | 1 |
| 1–3 | role one-hot | yes | yes |
| 4–5 | self-relative dx,dy /100 px | yes | yes |
| 6–7 | velocity /200 px/s | yes | yes |
| 8 | hp/maxhp | yes | yes |
| 9 | radius /100 px | yes | yes |
| 10 | speed /200 px/s | yes | yes |
| 11–12 | range,min_range /1000 px | yes | yes |
| 13 | damage /200 HP | yes | yes |
| 14–15 | cooldown,cooldown_max /10 s | yes | yes |
| 16 | target slot: none=0, supported=(slot+1)/12, unavailable=-1 | yes | yes |
| 17 | targeting self bool | yes | yes |
| 18 | own-private-field mask | 1 | 0 |
| 19–20 | prep,windup /10 local s | yes | zero |
| 21 | time_rate /4 | yes | zero |
| 22–23 | energy,cost /1000 EP | yes | zero |
| 24–25 | max(0,guard_until-t)/10 s, busy bool | yes | zero |
| 26–27 | actual lob speed /1000 px/s, blast radius /100 px | yes | zero |
| 28–29 | start-ready, release-ready (public target reach+body, distinct from permission) | yes | zero |
| 30–31 | launch age/10 s (-1 never), last-tick consumed bool | yes | zero |

Friend self excluded. Friends and enemies sorted by squared distance then persistent ID, first12, padded zero. Enemy target pointer only this enemy support. Teacher uses this same nearest12; pending targets outside support are unavailable, never labelled none for training. Slice roster cap <=12 each side (<=10 guns+2 scaffolds), so ordinary slice targets fit; general encoder records friend/enemy overflow. Input enemy pointer unavailable=-1 remains distinct from target-none=0; an unsupported pending teacher label invalidates collection.

Threat keys exact: kind, ordinal, x/y, dx/dy, born, at, radius, speed, left, from, until, release_at, landing_at, caster, target, slow. Irrelevant typed fields are zero (and remain known through kind masks). Ordinal is stable within the snapshot's native source order, tie-break only, not a feature.

| Threat columns | Meaning / scale |
|---|---|
| 0;1–4 | presence; shell/aimed-shot/field/enemy-cast one-hot |
| 5–6;7–8 | relative point /100; shot unit direction |
| 9–10;11–13 | age/10; (at-t)/10; radius/100; speed/1000; remaining distance/1000 |
| 14–17 | (from-t),(until-t),(release_at-t),(landing_at-t), all /10 s |
| 18–21;22–23 | caster enemy pointer; targeting self; inside radius+body+4; slow; two reserved zeros |

Shell point=landing point, shot point=current origin, field point=center, cast point=current public target position. Rank threats by inside first, then nonnegative time-to-impact (shot along-ray/speed; active field time0; shell landing; cast landing), kind index, ordinal. Keep8. Overflow count diagnostic, not tensor. A clean slice collection has <=64 raw threats and records omitted counts; dropped relevant threats remain a representation limitation, measured later against full public teacher.

Global16: t/150, dt*30, four border distances/1000, six team×role live counts/64 (own then enemy), own/enemy centroid dx/dy /100 (empty=0). Mirror x offsets, x velocity and shot x direction with sign=-1 for side1; y unchanged. Swap left/right border columns. Inverse transform applies the same sign once and adds the current self position; native caches absolute points. Reflection fixtures swap teams and x coordinates; arbitrary reflected team0 deployments remain a distinct orientation, not silently recanonicalized.

81 outputs: move33, target13 (none+12), request-start1, permit-release1, aim33. Move candidates: hold index0; 16 directions at .6×speed×1s then 16 at 1×speed×1s, j*pi/8. Aim: target center index0; 16 directions at .5×min(200,splash), then full radius. Move candidates clipped to arena body inset; aim candidates masked unless in arena and current gun's min/max reach. Ties select lowest index. No random sampling at deployment and no mean of modes. Finite output clipping/projection is logged separately from nonfinite failure. All nonfinite observation/state/output failures invalidate a clean engineering/data receipt.

Native participation projection keeps an endpoint in some public enemy engagement band when feasible; if outside, closes toward a reachable band, capped at one second of current travel. It cannot bypass cooldown, energy, body, cast, target or aim gates. Network's categorical goal plus N2 drift is capped to one second of speed and arena; projected and raw intent both recorded. Future reporting must distinguish ordinary finite projections per gun-tick from target/aim support losses, numeric and boundary failures.

## R2-F2: time and cast state machine

First observation/decision tick=1, after time/cooldown/energy/field/reflex updates, immediately before `prepareControllers`; t=dt. Decision ticks1,7,13,...; cached command expires **before** snapshot at t+6 ticks. Cache absolute goal/aim and persistent target ID; no per-tick offset addition. On variable dt<=.2s cadence is still six physical ticks, not falsely called exactly5Hz; 5Hz applies to default dt=1/30. All networks have the same action cadence. N2/N1r memory updates each physical tick using current joint positions and sample-held decision features. No fast phase firing channel. A positive fire logit is latched by the six-tick cache; no separate crossing pulse can be lost between decisions. Launch acknowledgement resets N2 phase on actual launch only, not permission/consumption.

Authoritative prep is the native engine's prep, not a separate simulated clock. Cooldown/energy are consumed on native start. Existing prep advances even under Hold. Target locks on actual start. Aim starts as an absolute provisional point; it locks on the first cached positive release permission (possibly at start). Until then, a later 5Hz decision can supply an aim; changing it does not restart preparation. Once locked, no replacement/retarget until consumption. Native prepared hold lasts at most6 ticks from first observed readiness: this is a **new automatic-release rule**, shared by all slice arms including teacher. Native illegality overrides the bound; at expiry, cancel/consume without launch and without energy refund, never force a shot through an illegal gate. Target death during winding does not stop native windup; the completed blocked cast is then cancelled by the same bound. No cooldown or energy refund.

| State / condition | request-start | permit-release | Native transition / acknowledgement |
|---|---|---|---|
| idle/cooldown (or insufficient energy) | ineffective | ineffective | wait; cooldown/EP native |
| start-ready, target+aim+body legal, no prep | true starts | independent | `gamePrep`; lock target; record cast_start; cooldown/EP paid |
| start-ready, Hold | blocks new prep | no launch | remain ready |
| winding, prep<windup | ignored | cached; does not skip windup | `gamePrep` advances native local dt; pending target retained |
| prepared, legal, Hold, age<6 | ignored | false | prepared hold |
| prepared, legal, permit or age>=6 | ignored | true or automatic bound | released via native action; consumed before launch |
| blocked prepared: body/absent target/target range/aim range | ignored | vetoed | hold until6-tick ready bound, then cancel without launch |
| released | ignored | attempted | actual fireShellAt hook records aim/born/landing and resets phase/latch |
| consumed-without-launch | ignored | no shot | native pre-walk target reach can fail after permission; finishTick clears pending; never claim launch |
| dead own unit | no | no | identity pruned; no reincarnation via physical slot |

Precedence: finite/schema validity → living own body → pending identity/aim lock → native target resolution → target min/max reach → explicit aim arena/reach → cooldown/energy/attacker cap/start permission → native prep progression → release permission/bound → native pre-walk target reach/action gate. Gun body block and explicit aim gate remain lawful every tick. Walking follows native pre-walk artillery target reach, while the explicit aim gate is checked at act entry. `released` is consumption, not launch; collector observes both hooks and a no-launch completion. Later branch dt is limited to <=.2; no inheritance of v6 complex bounds.

## R2-F3: constrained public teacher and causal join

Name: **NS1 public-nearest/REACT/ready-projection teacher**. Components: nearest supported live enemy by distance/ID; ordinary move to its engagement annulus (then same candidate-direction support/participation); copied adapter public REACT (dodgeShots .12s, smartShells/castDodge, fields) overrides ordinary movement and suppresses start/release; body/participation projection; start if public cast-ready and not reacting; release when scratch prep+dt*time_rate reaches windup and not reacting; v6 `project()` plus copied output-only native artillery candidate planner for those ready guns. No clone of the student World and no advancing physical time. Neutral seed1 public projection; enemy energy=1000,cost0,time_rate1, no player/ability/private profile, public raw velocity; own guns use public windup/lob/splash; ordinary target retained during pending prep. No full elite equivalence.

Planner options copied from v6: artyPlan true, exact false, robust .5, herd0, battery true, follow false, rollout disabled, raw lead; enemy dodgeShells true. Only eligible-ready guns have scratch prepared state; coming guns excluded. Delayed output throws. Native queue/projection output is collected, not launched in the living world. No persistent teacher formation/search/RNG history; same-state oracle is this stateless joint policy. Six-tick teacher cache and the same native cast machine apply during actual collection. The unconstrained 30Hz teacher/full elite may later be reference-only arms; neither labels the slice by default.

Public planner aims may exceed action support: snap to the nearest **legal supported categorical aim**, count every snap/distance; retain original planner output only in teacher diagnostics. This is deliberately a constrained teacher, not parity with unquantized elite aims. Timing-ready geometry cannot revise an already locked aim; the effective projection is separately visible. Ready scratch planning at a decision tick may be one tick ahead of readiness; this is specified local `gamePrep` arithmetic, not a future simulation. New starts are not treated as magically prepared.

| Join key / point | Training label | Separate outcome/diagnostic |
|---|---|---|
| fight,decision_tick,unit; pre-policy snapshot | public o, legal masks | support/overflow |
| same key; teacher candidate/arbitrated intent | target/move/start/release/aim categorical intent | raw vs projected; REACT precedence |
| fight,cast_tick,unit → originating decision key | cast/aim identity; pending mask | actual start/time/EP consumed |
| fight,tick,unit,volley; native released hook | **not** an earlier fire label | consumption |
| same cast identity; fireShellAt hook | **not** an earlier aim label | actual launch aim,born,landing |
| ready-bound cancellation / no-launch native consumption | no invented negative permission | reason and consumed_without_launch |
| damage/kill/landing | no fit labels | task mechanism/outcome only |

`labels.join` requires chronology, unique stages, originating decisions/casts and snapshots; it never backfills decision labels from future releases. Undefined/unsupported labels masked or stop collection, never silently relabelled none. Joint volley ID=tick on the planner's ready joint assignment; native outcome retains decision/cast identity even if the cache changes before release. Shadow labels are a balanced same-state oracle only, with no advancement; short fixtures verify action/launch parity separately from shadow byte identity.

## R2-F4/F5: architectures, gradients, joint state and new numerical envelope

All heads share a 64-wide tanh encoder and linear81 readout. N1 flattens the fixed masked tensor (intentionally a compact deterministic comparator, not an attention architecture); N1r adds self8 and normalized local message8, tanh recurrence8. N2 adds sin/cos(theta), local mean sin/cos, and12 normalized previous-target group alignment scalars. Exact stored parameter counts: **N1 69,841; N1r 71,385; N2 71,880** (includes forcing1009 and six bounded raw law parameters;71876 active imitation coordinates after the four-coordinate law mask). Radius fixed3 dimensionless during imitation; no disconnected radius gradient. A later radius search requires a separately declared search subset, not silently replacing the matched16-dimensional slice ES.

N1r/N2 own-gun graph: nearest8 within strict r<3, distance then persistent ID, degree normalized, self excluded. With <=10guns+2scaffolds these peers fit the friend support. For N1r, self8 + mean-neighbor memory8; add each candidate's previous-target peer mean rolled by slot mod8 /12; normalize by2. For N2 target groups, previous accepted assignments at tick start; local own-gun peers only, self excluded; unit-circle mean normalized; empty/length<1e-6 =>0. Simultaneous readouts and simultaneous assignment/memory commit. No current-decision circular dependence or global attackers channel. N1r has the same graph/public target-group access, but a larger bounded memory; equality is access/cadence, not identical representation or FLOPs.

C4 projected law, engine authoritative positions frozen through each physical tick's RK4 stages:

r_ij=||p_j-p_i||/L0, **L0=100px**, eps=.1 (10px), local degree normalization.
phase rate = omega + forcing + mean[K exp(-r²) sin(theta_j-theta_i)].
C4 motion proposal v = mean[delta/max(r,eps) * (A(1+J cos(delta_theta)) - B/max(r,eps))].
engine goal contribution = movement_share * current_speed * v/(1+||v||), px over a1s goal horizon. Engine collisions/separation determine the next true p. No fictitious integrated C4 positions are substituted for native motion.

A,B,J in[0,1], K in[0,2] rad/s; omega in[-2,2] rad/s; forcing=tanh(linear(o)) in[-1,1] rad/s; share in[0,.25]. Sigmoid/tanh transform six raw trainables; no parameter clipping after an optimizer step needed. Isolated elements have v=0, phase rate=omega+forcing. Unwrapped radians retained; sin/cos only in outputs; ID initial phase=(id mod16)*pi/8; new IDs initialize, deaths prune, no slot-based transfer. Reset all history per fight, including series fights; actual launch resets theta=0. Previous assignment starts none, N1r memory zero.

Derived bounds: |phase rate|<=2+1+2=5rad/s; infinity-norm phase Jacobian <=2K<=4/s (one diagonal plus degree-normalized neighbor derivatives). For fixed inputs, sensitivity <=exp(4t); over3s this is exp12, a finite bound **not** evidence of well-conditioned gradients. Repulsion proposal norm <=A(1+J)+B/eps<=12; smooth bounded motion <=.25*speed. Motion phase derivative norm <=2AJ before smooth bounded map; geometry derivative is regularized and topology remains a discrete switch. Graph derivative/radius inclusion is deliberately absent.

Substeps n=max(1,ceil(dt*4/.25)), cap4 for dt<=.2; default tick needs1 RK4 step. Hold topology and weights for all stages; joint phase reads synchronous; stage and final increment envelope5dt+1e-9, finite checks, atomic accepted state only. The valid analytic envelope makes bound enlargement/retry unnecessary: failure returns an error with original state untouched; no partial optimizer/inference update. This adopts v6's monitoring/atomic architecture, not its cubic amplitude constants. Phase freeze and K0 are explicitly different. Python uses the same RK4 and stage checks. Long sparse numeric fixtures, refinement, finite gradients/finite-differences away from switches and exported native forwards check this envelope, not fight usefulness.

N2 logits start/release =6*tanh(base_logit/6)+2*cos(theta), finite and bounded[-8,8]; native threshold>=0, latched six ticks. This is the exact differentiable head, not a straight-through crossing surrogate. Target/move/aim CE gradients reach shared encoder/readout and recurrent phases through the sin/cos/message channels; start/release BCE also reaches cos(theta); forcing/law receive phase/dynamics paths. Offline recorded positions are constants: no gradients through native physics, target argmax, collision or body/reflex outcomes. The command drift's law has no teacher categorical loss unless an auxiliary drift/goal loss is explicitly added later; A/B/J/share remain fixed during initial imitation (a registered gradient mask zeros their coordinates; imitation optimizer weight_decay must be0 and frozen-coordinate optimizer moments must start fresh/zero; `assert_imitation_optimizer` rejects violations) and receive no falsely claimed gradient. K/omega/forcing and phase-conditioned readouts are trainable.

Recurrent fit: joint all-live-gun windows,90ticks/3s; batch4 worlds/windows; previous assignments, launch reset events and all30Hz geometry stored once per tick; decision forcing/features held six ticks. Windows use full chronological prefix reconstruction under current weights (no_grad burn-in), then detach once at window start; no zero initialization of arbitrary windows. Joint neighbor gradients remain attached within window. Fight/death/launch resets are explicit constants; no identity reuse. Clip global gradient norm1 after finite loss/grad check; zero bad windows tolerated: stop fit on first numerical failure, no partial optimizer update. Training implementation/optimizer loop is next deliverable, not run here.

## R2-F6: interventions

`K0`: coupling removed only; `frozen_phase`: memory frozen only; `topology_only`: initial persistent-ID phase graph retained but weights recalculate current distances. `no_geometry_to_mode`: initial graph + distance weights1; geometry-derived forcing frozen at matched initial value throughout the causal probe (Python caller supplies held_force). Motion still sees actual geometry. `no_mode_to_geometry`: J=0 and the entire movement readout uses zero phase/field/group channels; observation-only movement retained. Decoder, normalization, resource bounds and all other heads unchanged. These are direct phase/motion channel interventions; task-level target/fire decisions can still indirectly change later battlefield geometry. Thus do not call task harm alone a complete physical causal closure proof. Matched geometry kicks and phase kicks in fixed recorded contexts test phase-rate/motion responses; no-harm means inconclusive about use, never proven non-use/formation.

## R2-F7: losses, DAgger and sealed splits

Categorical CE for move,target,aim, BCE-with-logits for start/release. Head weights1,1,1,.5,.5 respectively. No Gaussian/mixture variance exists, so variance floors are N/A; categorical probability floor1e-9 applies only to exported diagnostics, CE uses logsumexp directly. Deterministic argmax selects one candidate, never averages opposite safe directions. Mask padded/illegal aim/target options; undefined aim (target-none or no legal aim), body-blocked movement, pending-locked target and non-opportunity start/release are excluded. Count excluded and unsupported labels; unsupported non-none teacher actions stop. Fire positive-class weight=neg/pos from **training only**, bounded[1,10], fixed before fit. Report active/opportunity precision,recall and missed readiness, not pooled accuracy.

Two DAgger rounds; per round10 whole trajectories per visitor N1,N1r,N2 (30 total), no teacher action mixing, <=150s each, <=10 guns, <=225,000 gun-row queries/round. All arms refit on the **same union**, visitor-balanced1/3, round-balanced1/3 including initial data. Sampling preserves joint chronology and coupled rosters; equal per-visitor trajectory cap, no flattening. Round cells include1/2guns and recovery after incoming shells; exactly two visits per sparse cell per visitor, remaining6 medium/10-gun trajectories. Full constrained same-state oracle at decision ticks; complete30Hz joint positions/lifecycle recorded. Checkpoint=min validation weighted masked loss, ties earliest; at most10epochs per fit, three fits/arm. Held-out heads are diagnostics; ceiling/undefined heads cannot block play. Numerical/schema/support/parity failures can.

Seal whole-fight IDs/whole-series IDs and entropy before windowing: `split(group)` fixed SHA256 namespace modulo10:0–6train,7–8validation,9test. A series shares one group, never split by fight/window. Reporting draws independently allocated and excluded from all fitting/selection/DAgger; no validation/test/reporting refit. Hash immutable split inventory, model export, dataset and sources before future run. No entropy/dataset allocated in this delivery.

## R2-F8: resources and reproducibility

Separate CPython3.11.15 CPU environment `_local/mlenv`, requirements.lock with exact transitive versions; no workspace lock changes. Torch4 threads, interop1, DataLoader workers0; one native collector process; no concurrent collection/training. Network download may fail; `setup_env.py` can copy selected exact distributions from an existing read-only local cache into the isolated env. ENVIRONMENT.json binds offline distribution trees; online install command is in README. Never silently use the project's .venv or MPS/CUDA.

`project.py` supplies exact arithmetic, not measured feasibility:200 total fights including both orientations,40s expected/150s hard timeout,<=10 own guns,<=24 units,<=64 raw threats. Expected400,000 decision rows; hard1,500,000. Feature1008float32+160 label/ID/mask bytes/row; joint30Hz tick record128+24*96+64*128bytes (once per tick). Expected decision1,676,800,000bytes plus joint2,549,760,000; hard6,288,000,000+9,561,600,000. DAgger60 additional trajectories adds30%; Raw collector wire stores one shared joint snapshot per tick, with snapshot events reduced to self-ID references (`unpack_frame` reconstructs joins). It enforces a65,536-byte JSON record cap and <=24units/64threats. Include raw JSON at that hard cap **plus** two converted copies+3GiB environments/exports/checkpoints; no assumed gzip savings. The JSON reserve is intentionally conservative and can exceed60GB at the hard-duration bound. Dataset is streamed; do not preload it into RAM.

Peak allowance512MiB per training step (batch4×90ticks×<=10guns, float64); params/grad/two Adam moments about2.3MiB max; retained RK4/intermediates dominate. This is a conservative declared cap requiring later real-path measurement, not a proof of Torch allocator behavior. Log actual peak RSS/CPU/wall/RHS counts/latency/disk. Epoch and query counts equal, not equal CPU: N2 RK4 may cost more. Projection formulas cover collection+teacher, student+shadow, nine fits, export, ES, baseline/reporting; unknown seconds remain symbolic until authorized <=20fight/<=20step timing. Any projected >1h before22:00 goes to owner resource gate. No time sample run here.

## R2-F9: slice optimizer contract (not executed)

Use the implemented diagonal **centered-rank antithetic ES**, not inaccurately named CMA-ES:16candidates (8 Gaussian noise vectors and negatives),20generations, sigma=.1, learning rate=.05, centered rank utility with exact ties equal; mean and candidate coordinates bounded[-2,2]. Each arm's matched16 subset consists of start/release biases2, eight movement direction biases, five aim biases and target-none bias1; encoder, all other heads, N2 law/radius and memory frozen. Prospective mapping: move indices1,3,5,7,9,11,13,15; aim indices0,1,5,9,13. Radius derivative-free exploration is deferred to a separate design and cannot expand this budget.

Drill-training surrogate, not series/streak objective: eligibility requires opportunities>0, launches/opportunities>=.25, enemy_kills>0 and >=8/10 fights task-completed by strict elimination before150s. Ineligible candidates rank behind all eligible; equal ineligibility ties retain incumbent. Eligible lexicographic raw own_gun_deaths across all10 fights; exchange ratio of totals (zero deaths =>null, separate raw kills then rate, no infinity); kills/time. No win rate primary. Zero-loss productive policy outranks losing guns, without letting always-hold win. Ratio null never compared numerically; raw counts/time always visible. Exact ranking ties preserve incumbent; retain incumbent unless candidate wins the same common10draw panel and has no survival deterioration across that panel. No reevaluation repetitions; uncertainty of10training draws is descriptive, never a0033 outcome verdict.

Uniform slice sampling, **no PFSP**. Common immutable10draws per generation shared across candidates and arms; independent draw RNG separate from ES perturbation and engine RNG. Per-arm3200candidate+200incumbent fights; three-arm max10,200, plus four-arm fresh report200each=800 =>hard**11,000 physical fights** total. No extra baselines/repeats/architecture selection; exceeding cap requires new owner design. Fresh report50/100/200 is never reused for selection. Ten-fight series later descriptive; surrogate/series association not validated or claimed. Stage2 remains deferred until useful imitation/DAgger.

## R2-F10: decidable prospective readings and authoritative stops

Drafter-proposed, not misquoted owner margins: survival loss normalized by initial own gun roster; offense enemy kills/initial enemy roster; participation launches/opportunities, all bounded[0,1]. Compare matched same-seed/tactic/placement/orientation arms vs **timing-matched constrained teacher**, full all-fight totals including failures/timeouts. Differences sign positive=benefit (teacher losses-network losses for survival). Proposed noninferiority margin=.10 per normalized axis (one-gun survival .1gun/fight, two-gun .2, ten-gun1). Report kills/minute, exchange ratio of totals (null/raw when deaths0), own-gun deaths, both axes and absolute cell outcomes separately; bounded offense does not replace exchange/streak for later full-army0034 decisions.

Paired uncertainty: distribution-free bounded-difference Hoeffding interval, alpha=.05/9 (three metrics×three looks, familywise<=.05 by union bound), halfwidth=sqrt(2*log(2/alpha)/n) on[-1,1] contrasts; paired unit=whole draw, not a gun/tick. Conservative, no empirical bootstrap tuning. Looks50/100/200: negative if any upper CI<-.10; positive if all lower CIs>=-.10 and at least one>.10; noninferior if all lower>=-.10 without superiority; otherwise continue, park unclear at200. With these conservative bounds small effects may park; never extend to thousands to resolve decimal gains. Stratified sparse/cell/tactic summaries descriptive. Ten series descriptive only, not repeated to optimize. Actual Claude review approves/revises these prospective margins before any report inventory is frozen.

Mechanism10–20paired drills precedes report looks: zero numeric/boundary/parity failures; launch/opportunity>=.25 and enemy kill>0 in each armed cell; compare useful benefit as above, not merely one fire/move. Denominator of finite projections=all own-gun physical ticks; clean-error denominator=all attempted observations/forwards; separately report target support and relevant-threat omission. <1% applies **only** to unsupported/illegal raw target/aim attempts per decision, never routine finite participation clipping; zero tolerance for numeric/boundary/parity failures. Shadow identity short fixtures is not whole-fight scientific acceptance.

Terminal precedence deliberately follows selected v6 rule: strict elimination requires own survivors>0, enemy0 and time<150; timeout at150 (even same tick as elimination) and simultaneous extinction are not wins. Each later series arm heals/carries its own survivors; no cross-arm survivor reuse.

| Yes/no stop | One action | Responsible role |
|---|---|---|
| Network gun calls a scripted candidate policy? | fix host before execution | implementer |
| Any numeric/boundary/schema/parity failure? | invalidate receipt and fix before execution | implementer |
| Non-none teacher label unavailable or unsupported without declared aim snap? | fix representation/teacher before collection | implementer |
| Resource projection exceeds1h before22:00 or512MiB/step/disk allowance? | decide resource exception | owner |
| Proposed contract/margins/splits not cross-family reviewed? | review delivery before data execution | reviewer |
| Ceiling/undefined diagnostic head at baseline? | report diagnostic without blocking play | implementer |
| Non-ceiling head has masked accuracy at/below its named baseline? | report for mechanism review | implementer |
| Armed-cell launch fraction<.25 or zero enemy kills? | redesign before outcome/ES | drafter |
| Negative paired reading after DAgger? | redesign before ES | drafter |
| Ambiguous effect at200? | park candidate | drafter |
| Ablation has no measurable harm? | record inconclusive use/claim result | reviewer |
| Collection/training requested without timing/split/model/source admission? | complete admission first | implementer |

The separate Codex owner's verbatim recheck is a same-family implementation check. Claude's next review is the cross-family build gate; neither may self-accept a research milestone.
