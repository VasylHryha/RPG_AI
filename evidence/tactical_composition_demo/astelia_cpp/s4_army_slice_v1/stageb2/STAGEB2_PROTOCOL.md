# Stage B2: network decides, exact functions compute

Prepared under owner decision 0039 and the explicit build request. Development implementation only; **no training, fights, or measured behavioural outcome in this delivery**. Stage B round-0 is running and every Stage A/B/rev2 source stays untouched. B2 owns local Python snapshots, source-only manifests, a new binary and variant-specific data/checkpoints. Source references: decisions 0035, 0036, 0038 with both addenda, 0039; Stage B diagnosis/protocol; STAGE2_REWARD_TRAINING_RESEARCH.md. These are authority/context, never living-document hash pins. The copied origins and protected-source baseline are separate code-only inventories.

0038 addendum 2 takes precedence: leader parked, Stage 2 main route ES, no privileged teacher permission, physical-tick action/state cadence and 5 Hz entity encoding retained. B2 implements the current imitation repair stage. It does not implement reward training, growth, search or a new tactical leader. B2 is used after Stage B results establish that aim/movement still need this intervention.

## Tool versus policy boundary

`tools.py` and `tools.h` expose mathematical computations with no world handle, RNG, teacher labels, state mutation, fire rules or policy decisions. `candidates.py`/`.h` enumerate the same public-state options in persistent-ID order. Every surviving candidate is visible to a learned score. No closest-target, threat-minimum, react activation, V2/P16 planner or teacher fire rule selects a deployed command. Best splash maximizes a geometric count; **the network still chooses whether to use that option, whom to target and whether to fire**. Candidate generation intentionally supplies a finite vocabulary; it is an inductive bias, not proof of arbitrary action expressiveness.

The shared Stage A attention, N1/N1r recurrence and N2 mode/geometry dynamics are copied unchanged. New learned aim/movement queries score 16-dimensional candidate descriptors; categorical choice plus tanh-bounded offsets produces coordinates. Fire, multiplier, pointer, phase feedback and N2 spacing drift retain their existing learned paths. Aim offset is at most 12 px per axis; movement offset 24 px per axis. Movement adds N2 drift then body-bound clamps. Artillery landing projects the selected point plus offset into the exact legal annulus/arena intersection; an empty intersection supplies no aim. Projection ensures legality, not an attack opportunity or hit guarantee. Required artillery aim with an empty legal bank rejects training/native inference; coverage still retains masked no-candidate audit rows. Unused non-artillery aim may remain undefined. Validity is unconditional in categorical selection: only valid scores enter argmax, and max-valid shifting keeps finite padded parity outputs.

All living enemies are enumerated. Aim: legal fallback, direct/lead point for each enemy; for artillery, connected-component centres and best splash point. Movement: hold current point; each enemy's nearest range band, outer-range approach, both 45-degree flank points and outward retreat point; behind each friend relative to the enemy centroid; both lateral dodge directions per enemy and public shell/shot/cast/field. "Retreat to safety" means a retreat candidate with its threat estimate as a feature; no function asserts that it is safe. "Behind friend" is geometric cover, not occlusion/armor proof. With no enemies, hold and legal fallback remain available. Overflow fails instead of dropping candidates. The bounds are 194 aim and 996 movement options at 64 enemies, 64 own units and public-bank limits 64/64/32/32.

### Mathematics and units

| Tool | Definition | Units and limits |
|---|---|---|
| Lead | `p + v*t` | p px, v px/s, t s; constant-velocity public extrapolation, not hidden enemy intentions |
| Own flight time | `distance(own,target)/effective_lob_speed + remaining_windup` | s; snapshot lobSpeed already includes launch multiplier; remaining windup `(windup-prep)+ / timeRate`; positive effective speed required; current-distance flight estimate, not a quadratic moving-endpoint intercept solve |
| Range projection | Euclidean closest point in `lo <= ||q-origin|| <= hi` intersect rectangle | px; considers rectangle projections, radial circle points and circle/edge intersections; returns None if empty; no clamp-then-illegal-inner-band fallback |
| Splash coverage | count of predicted enemy centres within splash radius, including boundary | count; centre metric, not damage simulation or friendly-fire evaluation |
| Best splash | max coverage over the disk arrangement intersect legal annulus/rectangle | equal splash radii; enemy-centre projections, pairwise disk intersections, range-ring/disk and wall/disk intersections; nearest-origin then x/y tie only among enumerated count-maximizing witnesses; does not promise the globally nearest point in a whole count-maximizing region; pure optimization, no policy rule |
| Cluster centres | arithmetic mean of each distance-linked connected component | px; edge at distance <= twice own splash; transitive membership; deterministic ID order |
| Predicted dodge | `own + side*clearance*perpendicular(unit(lead(enemy,t)-own))` | px; both sides emitted; zero direction defaults +x; no activation trigger and no react script |
| Behind friend | friend plus clearance away from supplied threat, projected into supplied target band | px; clearance friend radius + own radius +12; centroid anchor is supplied by enumeration, not a selected target |
| Threat estimate | sum `damage/cycle / (1+(distance_to_predicted_enemy/max(1,reach))^2)` | damage/s; public cycle from cdMax floored at .001 s; heuristic geometric exposure, not calibrated expected loss |

Public shells/casts contribute landing points and time-to-impact; fields contribute centre/radius; shots use public direction, speed and remaining travel. The shot horizon is `min(.5, remaining_distance/speed)` in seconds. No unseen enemy cast intent or private recurrent history is read. Public threat visibility retains the original snapshot contract.

## Honest supervised labels and coverage

The loss maps **O's executed** goal and masked aim to the nearest valid candidate (Euclidean distance; first enumerated tie) and retains the full residual. For N2 movement fitting, the detached current spacing drift is subtracted before selecting the label candidate. The model learns categorical CE plus residual SmoothL1 in 100 px units; actual movement SmoothL1 also trains N2 drift. Out-of-bound residual labels are neither clipped nor relabelled as covered. Coverage has two separate readings: candidate-only distance <=20 px and representable by the bounded per-axis residual. It reports no-candidate counts, denominators, mean/max distance, per-role/head/split/occupancy arm and executed O-react dodge rows separately. Low coverage requires changing the vocabulary before interpreting training failures as architecture failures. Missing aim labels stay masked; absent dodge classes are unavailable evidence, not zero error.

`coverage.py` reads complete existing trajectories under live cap, lock and measured first-fight projection. It runs on round 0 before timing; later rounds include each student's own full-fight DAgger occupancy. DAgger retains O executed dodges and student history, not oracle history; O acts only on a cloned predecision world. Four windows per fight remain the declared optimization budget, so full-prefix label coverage and the actual fitting sample distribution are different denominators. Coverage demonstrates availability of nearby actions, not that the linear candidate scorer can learn every label or that a fixed memory state is sufficient.

Target balancing is Stage B's train-only None/nonzero balancing per role. Fire uses ordinary CE and validation-only per-role thresholds, with precision/recall, ties and unchanged-threshold test reports. In learned-dodge calibration, O's reaction flag is not treated as a student safety veto, because the student has react OFF. Guard/body-busy holds remain shared.

## Arms and later execution

Core N1, N1r, N2; optional N1h via `B2_N1H=1` consistently across an entire revision. Architecture parameter and timing reports must state added candidate-head capacity and compute; this is network+tools versus network-only, not a same-capacity superiority claim. N2J0 remains dropped. Baseline binding uses completed Stage B calibrated exports and its full-sequence parity proof. A separate **zero-combat** full-validation bridge verifies that B2's preserved ARMYA1 branch exactly reproduces Stage B native outputs/fire classes before paired readout.

Round 0 retains Stage A sealed splits; ten epochs, four 90-tick windows, fixed training seed 41001. Full-sequence state refresh, completed-epoch resume, per-arm own occupancy, concurrent measured lanes, 20% projection margin, process/RAM/disk checks, unique invocation receipts and original validation/test splits follow Stage B patterns. Each fit and resumed epoch persists the actual initialized law, K, force hash and (for OFF) frozen parent checkpoint/readiness identity. Current parent look, outcome ledger, complete paired receipts, calibrated fit/export/checkpoint and parity must all agree before dodge eligibility is written. Default at most three one-thread workers (optional fourth N1h); RAM/cost can reduce slots. One DAgger round by default; optional second after measurements. Every round needs current coverage, measured budget, complete calibrated fits and full native parity before fight work. No cap is fabricated here: B2 needs its own owner cap authority and authenticated Claude-authored TRAIN_CAP; the Stage B approval is not reused as B2 training approval.

Fresh seeds are paired across B2, same-architecture Stage B network-only, O and T, on regular and all C3 tactics. Look 20 then 50 per panel: 100–200 pairs total at look 50, individual checkpoint evaluation, not training replications. Reports contain wins, own deaths, enemy body deaths, own-attributed enemy damage/death sources, kills per own death, timeouts and per-tactic breakdown. Body death count is not own-attributed kill count. The series streak is explicitly not run. Harm progression reports the existing >=2 deaths/kill threshold.

### LEARNED-DODGE

`B2_VARIANT=learned_dodge` has separate roots, budgets, checkpoints and receipts. Enable only after a complete non-harmful react-ON look 50 and at least one win per core arm in both panels. That eligibility rule prevents zero-win experimentation; it is not teacher-level acceptance. It starts from the frozen matched react-ON B2 checkpoints. Teacher O still has react ON, so executed dodge movement labels are present. The student's shared movement react and automatic reflex dash are OFF; guard, participation and other body behavior stay active. Disabling dash removes a body skill: the network must anticipate/avoid threats through normal movement; it cannot teleport by copying a goal. Command coverage does not establish representability of body teleport events. The controlled experiment is explicitly a safety-layer ablation plus learning, not learned reproduction of that unavailable dash action.

Its paired readout includes matched frozen react-ON network+tools parent, learned-dodge network+tools, Stage B network-only and O/T. All use identical scenario seeds/orientations. Do not call surviving body guards learned dodges. Static native seams and no-combat inference are light-tested now; safety arbitration, body dash suppression and shadow isolation still require later real host validation before a behavioural claim. In particular, participation can project away a raw dodge goal that O would execute via react precedence. The first host arbitration check must measure raw, post-participation and executed errors on O-dodge-labelled rows; raw candidate coverage is not executed-action coverage.

## RRG note and normalization ledger

Mode/state affects the learned candidate score, the selected tool computes geometry, and subsequent public geometry/motion affects the next physical-tick mode/state update. N2's copied phase coupling/spacing closes a local geometry↔mode feedback path. N1/N1r use the **same** toolbox. Verified primitives can become reusable interfaces for future composition. This implementation does not establish `B_n -> R_n -> B_(n+1)` causal background transformation, recursive resonator formation, runtime self-recreation, hierarchy advantage, superiority to a trained recurrent control, reward improvement or growth. Tool reuse alone is not source recursion. Current audited source identity is research/rrg/CURRENT.md; no new source qualification or experimental execution is claimed.

| Quantity | Level | Normalization |
|---|---|---|
| Candidate dx/dy, distance, residual loss | unit geometry | /100 px uniformly across roles/arms |
| Splash descriptor | unit geometry | covered enemy centres / max(1,living enemies) |
| Threat descriptor | unit geometry | damage/s /100 damage/s |
| Candidate type and fire/pointer logits | unit mode/decision | dimensionless, CE; logits dot /sqrt(16)=4 |
| Movement multiplier, None/nonzero weights | unit decision | dimensionless; MSE and train-only class balance |
| Encoder coordinates, output coordinates | public observation/interface | x/W, y/H; head offsets converted px before output |
| Candidate distance / coverage tolerance | evaluator | raw px, 20 px same for all roles |
| Phase law and neighbour geometry | unit mode↔geometry | inherited Stage A /100 px distance, max eight neighbours within 300 px; unchanged law |
| Outcome time, deaths, wins, attribution | evaluator | seconds/counts; paired means and ratios with zero-denominator handling |

No upper-level prediction API or descendant reads are introduced. All underlying public elements continue evolving; no leader promotion is claimed.

## Yes/no stop ledger

| Condition | One action | Responsible role |
|---|---|---|
| Stage B still running or results not reviewed for need? | Defer B2 host jobs | Owner |
| B2 cap authority / authenticated Claude cap missing or invalid? | Stop before timing | Implementer |
| Source/binary/request/data/parent identity mismatch? | Preserve revision and stop | Implementer |
| Empty candidate bank for required aim / overflow / nonfinite value? | Reject affected revision | Implementer |
| Coverage materially incomplete or no executed dodge rows? | Revise vocabulary or defer dodge claim | Drafter |
| Live cap / measured projection / RAM / disk bound exceeded? | Stop resumably | Implementer |
| Native candidate/head/fire parity or baseline bridge mismatch? | Fix before fighting | Implementer |
| Learned-dodge eligibility false? | Keep react OFF work parked | Implementer |
| Shadow/controller/safety validation failure on host? | Fix before behavioural claim | Implementer |
| Look 20 incomplete? | Resume unchanged look | Implementer |
| Look 50 harm stop true? | End progression and report | Implementer |
| Independent reviewer finds gaps? | Fix and record disposition | Implementer |

Self-audit/disposition is in OWNER_RECHECK_STAGEB2.md, overriding the usual PLAN_CURRENT tracking location under the explicit task restriction. UNCOMMITTED_STAGEB2.txt lists paths only. Host commands and unmeasured expected times are in HOST_COMMANDS_STAGEB2.md.
