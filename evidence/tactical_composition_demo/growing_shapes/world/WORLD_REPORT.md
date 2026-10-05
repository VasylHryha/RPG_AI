READY

This is the engine deliverable under decision 0028 item 17, for Claude's
independent review. READY means the engine's stated contracts passed; it does
not accept proposal 0h, any atom, C6, or any growth/learning experiment. No
judging entropy, growth, learning, mutation probe or recorded panel was used.

Built: dependency-free C++17 with `-O2`, opaque per-episode and per-policy
handles, C ABI v1 (`world.h`), thin ctypes wrapper (`world.py`), deterministic
SplitMix64-derived generators, reference/random policies consuming observations
only, native batch rollouts, pytest and a standalone C++ contract. Each handle
owns its state. Distinct handles can run on distinct threads; concurrent access
to the same handle is outside the contract. The build manifest binds source and
binary SHA256 identities; Python refuses a stale or substituted shared library.
Binaries and caches are ignored; this folder is the entire deliverable.

The arena is the continuous square [-10,10] x [-10,10], dt=0.1 seconds,
160 decisions (16 seconds) per episode. Agent speed is 3 arena units/second
times magnitude; walls clamp physical displacement. Enemy velocities are
constant, with specular reflection at walls; HP and visibility are plain values.
There is no collision radius, force, acceleration, agent HP or attack cooldown.
One valid action scores the current observation for perception/remember/choose,
then moves the agent and enemies; movement and damage score that new state.
Terminal observations are inspectable; actions after step 160 return DONE.

Generic interface: relative dx/dy, angle, distance, visible vx/vy, HP, id,
visibility; agent position, task/mode, desired range, clock and arena/occluder
constants. Only move exposes target direction/distance. Every hidden enemy
has all value slots (including HP and velocity) zero, and visible=false;
unused enemy slots are zero. Hidden zero values MUST be masked by visibility.
Enemy identities and slot counts persist during hiding. No evaluator seed tag,
true hidden location, score, rhythm, frequency band or phase encoding enters
observations. Angles here are ordinary geometric radians, not oscillator phase.

Actions: angle in [-pi,pi]. Perceive magnitude is estimated distance in
[0,sqrt(800)]. In all other tasks magnitude is speed in [0,1]; remember/choose
validate but ignore it. choose/focus_fire require a live target id; all other
tasks require choice=-1. NaN, infinities, out-of-range angle/magnitude and invalid
choice are BAD_ACTION, counted once and rejected without advancing time,
physics, RNG or score. No wrapping/clipping of actions occurs. Python rejects
integer overflow/truncation before the ABI and raises explicit errors; malformed
API calls are BAD_ARGUMENT (separate from invalid action submissions). Rejected
actions do not earn scores: reports of an unfinished episode have done=false,
and all benchmark/comparison episodes must finish with zero invalid actions.

Task definitions and generator distributions (uniform draws; ties use lowest id):

1. perceive: agent starts independently uniform in [-1,1]^2, K uniform in
   {3,...,8}. Enemy initial headings uniform [-pi,pi], radius uniform [1.5,8],
   HP uniform [10,100], velocity heading uniform [-pi,pi], speed [0.25,0.65].
   The agent is stationary; each decision outputs the nearest enemy's current
   angle and distance. Scores: mean absolute circular angular error (radians,
   [0,pi]), and mean absolute distance error (arena units). Reference selects
   the visible minimum distance. Random samples angle and distance uniformly
   over their legal domains, independently on each decision.
2. move: no enemies, agent starts in [-1,1]^2, target heading uniform [-pi,pi].
   Modes equiprobable: approach, desired range=0, initial target radius [4,8];
   keep, desired range [1.5,3.5], with initial radius equiprobably [0.2,1] or
   [4,8]. Thus keeping tests both retreat and approach. Score is mean post-step
   absolute (target distance - desired range), in arena units. Settle time is
   the timestamp of the first of ten consecutive post-step errors <=0.25;
   if never settled, it is censored at 16 seconds. Reference moves radially
   toward/away from the point, speed=min(1,abs(error)/(3*dt)); no overshoot.
   Random samples heading and speed uniformly every decision.
3. remember: one enemy, same agent/HP/velocity draws as perceive, initial radius
   [3,6]. Visible at decision indices 0..39, hidden at 40..159. Agent is
   stationary. Score: mean absolute circular pointing error only on the 120
   hidden decisions. Reference stores the last visible position and velocity,
   extrapolates one dt per hidden observation, including known wall reflections,
   then points. Random supplies independent uniform headings.
4. choose: agent starts in [-1,1]^2, K uniform {3,...,8}, stationary enemies
   with uniform headings and HP [10,100]. Equiprobable scenarios: no enemy
   within range, all radii [3.5,8]; or two inside, ids 0/1 at [0.5,2] and all
   others at [3.5,8]. Range=2.5. Agent is stationary; weakest HP within range
   wins; if none, nearest wins. Score: fraction of correct ids. Reference
   applies that rule; random chooses a uniform live id at each decision.
5. chase: same generator as perceive; controlled agent moves. Goal is to
   reach AND maintain exactly range 2 of whichever enemy is currently nearest.
   The post-step nearest enemy is used for scoring, allowing real target switches.
   Scores: mean absolute radial error, fraction within +/-0.25, and settle time
   defined as for move. Reference picks the currently nearest visible enemy,
   predicts its next position from visible velocity and wall reflection, and
   moves radially to desired range; random samples heading/speed independently.
6. pursuit (out of sight): one target starts x uniform [-5,-4], y [-0.6,0.6],
   velocity (uniform [0.55,0.85],0), HP=100. Agent starts x=-8, y [0.8,1.4].
   Closed rectangle [-1.5,1.5] x [-2,2] occludes vision whenever the closed
   agent-target segment intersects it, including either endpoint. Movement
   can pass through it. Goal=range 2 of the single target. Scores: mean absolute
   post-step radial error, fraction within +/-0.25 and settle time; hidden-step
   count is diagnostic. Reference uses the same visible tracking/memory as
   remember plus chase motion, without reading true hidden values. Random
   samples heading/speed independently, with no hidden position access.
7. focus_fire: same agent/K/headings as perceive, enemy radii [3,8], HP [30,80],
   stationary enemies, range=2.5, damage=1 HP/second. Each step the chosen id
   receives 0.1 HP damage only if the agent is within range after physics.
   Nothing is damaged outside range; only the chosen enemy takes damage.
   HP exceeds the maximum episode damage (16), so no death or respawn occurs.
   Score: total damage / elapsed seconds (HP/second); in-range fraction is also
   reported. Reference commits to the initially nearest target and moves to
   range 2.4, then holds. Random samples heading/speed and a live id every step.
   The weakest-in-range rule belongs to choose; focus_fire permits any live id.

Normalization ledger: input/output angles are radians; positions/distances
are arena units; velocities arena units/second; HP health units; dt/time seconds.
Speed actions are dimensionless [0,1]. Angular, distance and goal errors retain
their native units; correct-choice/in-range are fractions; damage rate is
HP/second. No weighted aggregate or normalized learning reward is chosen here.
Unused score fields are zero except settle_seconds (16 when no settling metric
was evaluated). `hidden_steps` in batch means is integer-truncated; continuous
metrics are equally weighted per-episode means, not pooled across hidden steps.

Namespaces: dev, validation and judging use fixed distinct salts combined with
task id and uint64 seed index. World and random-policy streams have different
domain salts; policy draws cannot change generator/dynamics state. Separation
means different deterministic streams for the same task/index, NOT secrecy,
an authorization credential or disjoint supports of possible world states.
Judging is denied at native creation, policy creation and batch evaluation
unless the caller explicitly passes GS_ALLOW_JUDGING (Python allow_judging=True).
No test or verification path supplies that flag. These checks use dev and
validation only; tests check denied judging calls without generating an episode.

Choices requiring Claude's drafter review:

- The proposal names “chase and kite”; the requested deliverable names chase.
  Exact range-keeping covers approach and retreat, without combat/kite rewards.
  A separate damaging kite task would require a later specification.
- The proposal supplies no world constants. The fixed arena/dt/horizon, small
  K, speeds and tolerances above keep this a tiny, fast task bench. These are
  explicit engine defaults, not registered atom pass thresholds or tuned values.
- Visible velocities are supplied as plain values. This makes memory's strong
  baseline exact deterministic extrapolation; removing velocities or adding
  stochastic turns would change the memory task and must be specified first.
- Occlusion is line-of-sight and vision only, rather than an impassable obstacle.
  This isolates perception+memory+motion from path planning. Keep the fixed
  identity visible while coordinates/HP/velocity are masked, so memory has a
  well-defined target. Should the later design require another occlusion model?
- focus_fire uses stationary, nonlethal targets and freely selects an id each
  step. This isolates range-conditioned damage without deaths, respawns or
  choice-rule rewards. Should the later design require moving or lethal targets?
- Angle/distance errors remain separate and settling is a first sustained
  ten-sample window with 16-second censoring. Claude must define any normalized
  reward, atom acceptance threshold and recovery test in DESIGN_0H; this engine
  does not infer them from development scores.

Engine-only comparison seeds: each task, dev 0..255 and validation 0..255,
256 episodes per policy/namespace. Fixed in the verification script before
measurement; no tuning from results. Generator statistics additionally check
dev 0..511. Native speed uses dev 10000..14095 (4096 reference episodes per
task, one timed batch per task); Python per-step speed uses dev 20000..20063
(64 per task). These are implementation checks, not registered experimental
evidence, and do not qualify any resonator or scientific claim.

Reference vs random task scores (reference / random):

| Namespace | Task | Metric | Reference | Random |
|---|---|---|---:|---:|
| dev | perceive | angular_error | 0 | 1.56085 |
| dev | perceive | distance_error | 0 | 11.7215 |
| dev | move | goal_error | 0.215933 | 4.25341 |
| dev | move | settle_seconds | 1.39258 | 15.3723 |
| dev | move | in_range_rate | 0.919214 | 0.0205078 |
| dev | remember | angular_error | 1.18736e-17 | 1.5743 |
| dev | choose | correct_choice_rate | 1 | 0.203955 |
| dev | chase | goal_error | 0.0143623 | 1.32324 |
| dev | chase | in_range_rate | 0.986841 | 0.139038 |
| dev | chase | settle_seconds | 0.282031 | 10.8199 |
| dev | pursuit | goal_error | 0.032982 | 7.14867 |
| dev | pursuit | in_range_rate | 0.965332 | 0 |
| dev | pursuit | settle_seconds | 0.654687 | 16 |
| dev | focus_fire | damage_per_second | 0.976074 | 0.0364258 |
| dev | focus_fire | in_range_rate | 0.976074 | 0.0364258 |
| validation | perceive | angular_error | 0 | 1.56567 |
| validation | perceive | distance_error | 0 | 11.6345 |
| validation | move | goal_error | 0.250129 | 4.57657 |
| validation | move | settle_seconds | 1.50469 | 15.4793 |
| validation | move | in_range_rate | 0.912207 | 0.0218018 |
| validation | remember | angular_error | 1.31623e-17 | 1.56315 |
| validation | choose | correct_choice_rate | 1 | 0.195483 |
| validation | chase | goal_error | 0.0189091 | 1.42686 |
| validation | chase | in_range_rate | 0.983496 | 0.129785 |
| validation | chase | settle_seconds | 0.307812 | 11.8906 |
| validation | pursuit | goal_error | 0.0350573 | 7.22221 |
| validation | pursuit | in_range_rate | 0.963916 | 0 |
| validation | pursuit | settle_seconds | 0.677344 | 16 |
| validation | focus_fire | damage_per_second | 0.975 | 0.0322754 |
| validation | focus_fire | in_range_rate | 0.975 | 0.0322754 |

Speed (one thread; optimized C++17 -O2 build):

| Task | Native episodes/s | Python per-step episodes/s |
|---|---:|---:|
| perceive | 30039.9 | 1983.9 |
| move | 96829.9 | 2090.5 |
| remember | 155380.6 | 2100.9 |
| choose | 52049.2 | 2043.4 |
| chase | 24154.8 | 1918.8 |
| pursuit | 67385.7 | 2042.8 |
| focus_fire | 47842.8 | 2045.0 |

The native batch endpoint avoids per-step Python/ctypes overhead. The Python
per-step numbers include observation copies and policy/action ABI calls; later
learning loops can use native batching when Python overhead limits throughput.
These are single measured samples, not hardware-independent guarantees.

Host: {'platform': 'macOS-26.6.2-arm64-arm-64bit', 'machine': 'arm64', 'processor': 'arm', 'python': '3.9.6'}. Compiler: Apple clang version 21.0.0 (clang-2100.3.34.2).
Verification status: PASS.
C++ contract: native world contract: PASS (7 tasks; no judging access).
pytest: ...................................................................      [100%]
67 passed in 0.31s.
Total verification seconds: 3.313.

WORLD_CHECKS.json preserves source SHA256 hashes, build/binary identities,
the exact comparison metrics, benchmark counts/timings and test output.
WORLD_TEST_LOG.txt preserves build, contract and pytest diagnostics.

Reproduce this bounded check from the repository root:

```sh
.venv/bin/python evidence/tactical_composition_demo/growing_shapes/world/verify_world.py
```

For ctypes use, run build.py once, instantiate Library(), share that binding
between World/Policy handles, and use their context managers. gs_observe
returns a fresh snapshot; gs_step validates and advances a single decision.
No imports start episodes or build artifacts. No other repository folder
is read by the engine or modified by this verifier.

## Additive remember_static (Claude review note 3)

Task id 7 is appended; original task ids 0..6 and ABI layouts are unchanged.
One enemy; stationary agent; initial radius [3,6], HP [10,100],
and the same placement procedure/distributions as remember, with vx=vy=0.
The new task id supplies its own deterministic world and policy streams.
Visible decisions 0..39, hidden 40..159; every hidden value slot is zero.
The target stays at its last visible position. The reference stores that
position and points at it while hidden, without extrapolation. Random uses
the remember policy rule: independent uniform angle [-pi,pi] and magnitude
[0,1] each decision; magnitude is validated but ignored, choice=-1.
Score: mean absolute circular angular error (radians) on 120 hidden decisions.
This implements WORLD_REVIEW.md note 3 only, under decision 0028 item 17.

Engine comparison: dev and validation 0..255, 256 episodes per policy.

| Namespace | Task | Metric | Reference | Random |
|---|---|---|---:|---:|
| dev | remember_static | angular_error | 0 | 1.57837 |
| validation | remember_static | angular_error | 0 | 1.57235 |

Compatibility: PASS for all seven original tasks, both namespaces and policies.
The rerun comparison table is byte-identical (30 rows); all full-precision
batch score fields also match WORLD_CHECKS.json exactly. Side-by-side builds
from aeb75a7 and current source match every observation (including terminal),
action field, seed tag and final score over 7,168 original episodes.
ORIGINAL_COMPARISON_TABLE.md and REMEMBER_STATIC_CHECKS.json retain this proof.
The original report prefix, WORLD_CHECKS.json and WORLD_TEST_LOG.txt keep their bytes.
Original test cases are retained; their invalid task sentinel now follows TASKS
length, receipt identity uses the additive current receipt, and shared memory
contracts cover the new task. No old benchmark was repeated.

Additive verification status: PASS.
pytest (one invocation): ........................................................................ [ 91%]
.......                                                                  [100%]
79 passed in 0.47s.
Elapsed verification seconds: 23.172.
The report above remains the original historical verification; for this revision use:

```sh
.venv/bin/python evidence/tactical_composition_demo/growing_shapes/world/verify_remember_static.py
```

No growth, learning or judging run occurred. Implementation is REVIEW_READY
for Claude; this check accepts no atom, proposal, experiment or milestone.
