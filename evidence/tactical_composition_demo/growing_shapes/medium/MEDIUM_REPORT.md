READY

Engine implementation and focused validation are complete; ready for Claude's
independent review. READY is an implementation handoff, not acceptance of the
0h design, growth mechanism, experimental predictions or any milestone.

Built only this folder: dependency-free C++17 medium, C ABI, thin ctypes wrapper,
explicit build, C++ contract, pytest contracts and synthetic speed harness.
No growth experiment, task learning, judging entropy, panel or recorded run.
Frozen C4 source and stored reference fixtures were read only.

## Exact formulas

For each active element, take up to k=8 nearest other active elements with
r_ij < radius=3; ties sort by current array index. After removals, array order
is surviving insertion order; persistent IDs are independent of array indices.
Cell width is radius, and the 3×3 stencil enumerates every active candidate.
Partial sort uses (hypot distance, index). Only the diagnostic neighbour API
scans distant elements when it needs the masked padding indices of the Python
reference. Integration never performs that fallback.

With n_i the active neighbour count, q_i=1/max(n_i,1), rbar=max(r,eps):

```
x_dot_i = geometry_rate * q_i * sum_j (x_j-x_i)
          * [A*(1+J*cos(theta_j-theta_i)) - B/rbar] / rbar
phase_dot_i = omega_i + q_i * sum_j K*w_C4(r)*sin(theta_j-theta_i)
w_C4(r) = exp(-r*r), or 1 if distance_weighted=False
```

The default A=1, B=1, J=.8, K=1, eps=1e-6, geometry_rate=1 reproduce the frozen
accepted law. Standard RK4 evaluates both position and unwrapped phase at four
stages, keeping the start-of-step neighbour set/mask/count through all stages.
No epsilon approximation is applied to C4 distance weights. Coincident positions
have zero displacement even though repulsion is regularized by eps.

Drive d adds `strength_d * exp(-r_id²/(2*width_d²)) * sin(psi_d-theta_i)`
when r_id < reach_d, without neighbour normalization. `strength_d` is the caller's
K_in times site strength. During RK4, psi_d(c)=psi_d(0)+c*rate_d at c=0,dt/2,dt.
For arbitrary psi(t), the caller sets phase/rate each step; piecewise linear psi
is the explicit local interpolation. Setting rate=0 holds the phase for the step.

Readout Z=sum_i a_i*exp(i*theta_i)/sum_i a_i, with the same Gaussian a_i and
strict reach. Return amplitude abs(Z) and phase arg(Z), ignoring silent elements.
Empty readout returns (0,0); cancellation at <=1e-15 of total weight returns
phase 0 because direction is undefined.

A sliding window retains W samples, one after each integration step plus any
explicit observe calls. At fixed dt its full span is (W-1)*dt. For the samples
where both persistent IDs are present:

```
PLV(i,j) = abs(sum_t exp(i*(theta_i(t)-theta_j(t)))) / sample_count
L(i) = max PLV(i,j) over current C4 neighbours and active input sites in reach
```

Values are unavailable (reported 0) before min_samples>=2 shared samples.
A zero partner set gives L=0. New IDs do not inherit parent history. A drive
identity change (position, band rate, strength, width, reach), disappearance or
reappearance invalidates its old PLV samples; phase-only updates preserve them.

For strain, each sample fits the **instantaneous** weighted partner target
phases, then S(i) is their mean over W samples containing i (requires min_samples).
The weights are abs(K)*w_C4(r)/max(n_i,1) for element partners and the drive
strength times its Gaussian for drives. Negative K targets theta_j+pi. Ignore
zero-weight partners. Sort targets on the circle and enumerate all contiguous
nonempty two-cluster partitions; maximize |z1|+|z2| (first partition wins ties),
where z_c=sum_{j in c} weight_j*exp(i*target_j), M_c=sum_{j in c} weight_j.
The cluster direction is phi_c=arg(z_c). For at least two positive-weight targets:

```
S_frame = clip[ 4*M1*M2/(M1+M2)^2
                * (|z1|/M1)*(|z2|/M2)
                * (1-cos(phi1-phi2))/2, 0, 1 ]
```

A missing/single target gives S_frame=0. Thus one direction gives 0; two equally
strong coherent opposite directions give 1; unequal weights reduce it. B2 uses
the latest fitted directions, not an average of absolute rotating phases.
PLV/strain within eight double machine epsilons of 1 snap to 1 to remove trig
roundoff at that mathematical boundary. This is numerical normalization, not a
growth threshold tolerance; growth comparisons otherwise use exact inequalities.

Lock groups are connected components over **all pairs**, with PLV>=threshold
and r < link_factor*median_i(min_{j!=i} r_ij), exactly the C4 spatial rule.
Silent elements get label -1; other components, including singletons, get stable
array-order labels. This is a lock graph, not full C4 resonator qualification.

Directed active element links plus active drive-to-element links are counted.
Cost is c_e*N + c_c*active_couplings; silent elements still cost an element.
Readouts do not add coupling cost. The count does not itself estimate runtime.

## Growth, structure and reward hooks

All thresholds/timescales/costs/cap are supplied explicitly in Growth; no
scientific growth defaults exist. dt and geometry_rate are supplied in the
integrator API. Growth never happens implicitly inside an integration step.
configure_growth starts fresh rule timers at the current clock and requires
L_on>L_off, valid ranges, nonnegative durations/costs, and current N<=N_max.
Timers are updated on every observation and at every growth check. A false
condition resets its timer. An interrupted novelty/strain/death episode does
not accumulate disjoint time. Growth checks earlier than growth_period since
the last check do nothing; a late caller makes one check, not retrospective
checks. A condition sustained from time t0 fires at t-t0>=T.

At a check: evaluate a measurement snapshot; D1, then D2, then repeated D3;
then B1 in input order, B2 in pre-existing array order, B3 in need-region order.
Birth competition at the cap is resolved by that stated order. A manual add or
split enforces N_max once growth is configured. Every successful add, remove or
split has a structural event; no-op rule checks produce no event.

- B1: positive-strength input with no in-range element having PLV>=L_on, for
  T_nov, creates one at its position/current phase, rate=band-centre drive rate.
  The timer restarts after a birth. There is no lock requirement before an
  empty medium can respond to an input.
- B2: qualified S>=S_split and L<L_on, for T_split, retires the parent and creates
  two new IDs at fitted phases. Children keep the parent's natural rate and
  sit at ±split_offset/2 along a seeded SplitMix64 direction. Net count +1.
- D1: qualified L<L_off for T_death. No estimate from a short window kills an
  element. Lock equal to L_off survives; lock equal to L_on blocks B1/B2.
- D3: while cost>C_max remove the lowest lock (stability) or lowest supplied
  utility (reward), tie by persistent ID. Repeat until budget holds or every
  eligible candidate is protected/unmeasured. Equality to budget survives.
- B3: reward only; externally accumulated region error>E_need for T_need,
  no birth at that region in the preceding T_need. Caller supplies the input
  phase and band centre; there is no engine-side learning or invented error.
- D2: reward only; abs(externally supplied U)<epsilon_U in utility_checks
  consecutive **fresh utility evaluations**. A value at epsilon_U resets the
  streak. Each supplied value is consumed once; a growth check without a new
  evaluation pauses the streak. Utility is permitted only for age>growth_period.

Automatic deaths require age>=T_protect; before that boundary, protection wins
against D1/D2/D3. Manual structural APIs are explicit owner/evaluator operations
and do not apply automatic protection. Protection can temporarily make C_max
unattainable. N_max is always enforced after configuration; refused cap births
leave their sustained timers ready for a later check. D3 in the reward arm skips
elements without an externally supplied utility, rather than assigning a fake
utility. Supplied values remain available for D3 after their D2 check consumes
them; the runner is responsible for their freshness. Growth is refused during
silenced evaluation, to prevent evaluator perturbations from killing structure.

Silencing freezes an element, removes both directions of its coupling and its
drive/readout contributions. The context manager restores its flag even after
exceptions. evaluation_without clones for a complete evaluation and leaves the
original trajectory/history/timers unchanged. U=score_full-score_silenced is the
wrapper convention; the task runner computes it. No training/reward updates are
implemented. Add/remove/split log exact time, rule, IDs, duration/lock/strain/
error/utility/cost as applicable. Split is one event with parent and child IDs.

Snapshots explicitly serialize configuration, clock, RNG, next ID, elements and
protection ages, drives/regions, all timers, utility streaks and freshness, the
full window and the full event log. Clone copies all fields and is isolated.
Snapshot v1 uses native-endian IEEE double/scalars without struct padding;
architecture migration is not claimed. C API errors never use global state.

## Choices and questions for Claude (drafter)

These are reviewable engine conventions, not frozen 0h experimental choices.

1. **Strain is unspecified in the proposal.** Confirm the weighted two-circular-
   cluster objective and balance×coherence×opposition formula above. It gives
   the requested 0/1 endpoints while resisting diffuse partner phases. Confirm
   that instantaneous strain averaged over W is intended; pooling absolute
   phases across time would mistake coherent rotation for conflicting pulls.
2. **Reach and kernel are unspecified.** Confirm Gaussian exp(-r²/(2σ²)), strict
   finite reach independent of σ, additive unnormalized drive, and locally linear
   drive phase. These keep widths/extent explicit and avoid infinite "in range".
3. **Window duration and warmup are unspecified.** Confirm sample-count W and
   min_samples, rather than a time-weighted irregular window, and no D1/B2
   decisions from insufficient history. The runner must declare constant dt or
   its sampling policy, and identify τ_a/τ_g/τ_l in the 0h design.
4. **Accepted law versus slower geometry:** geometry_rate=1 preserves parity;
   geometry_rate=τ_a/τ_g can impose the proposal's ≥10× geometry separation.
   The engine does not enforce that separation or silently alter the accepted
   law. Which setting belongs in the design and what measurement establishes it?
5. **Cost counting:** confirm directed links, including external drive links.
   C4 nearest neighbours are directed, so an undirected count would change the
   budget meaning. Readouts are measurements and therefore excluded.
6. **Rule interactions:** confirm the stated death/birth order within each
   category, protection over budget, restarting novelty after each birth, fresh
   children/protection/history on split, and seeded offset direction. Should B2
   preserve the parent ID or constrain split directions in a future design?
7. **Reward hooks:** confirm strict error>E_need and abs(U)<epsilon_U, utility
   streaks on fresh evaluations, and abstaining from reward budget deletion when
   utility is unknown. How should externally accumulated error/utility be timed
   and retired by the runner? No choices of task score or learning rule are made.
8. **Group labels do not certify a resonator.** Recovery, persistent membership,
   scientific recursion, library type identity and instance copying into another
   medium remain for later components/design. Whole-medium clone works here.

## Validation and speed

Final batch: **70 pytest contracts passed in 0.90 s** (1.465 s
including pytest process startup). The native C++ C API contract passed inside
that invocation. All five stored C4 cases × three variants matched neighbours,
masks/inverse counts, RHS and one RK4 step at absolute tolerance 1e-9. Grid tests
also compared against independent brute-force search over empty/single/dense/
sparse populations, exact radius boundaries and stable distance ties.

Other contracts checked Gaussian drive/RK4 input interpolation and readout,
window eviction, anti-phase PLV, lock groups and strict C4 spatial boundaries,
weighted circular strain (including extreme weight ratios), individual rule
thresholds/durations, hysteresis, interruption reset, protection, budget ranking,
reward-arm isolation, fresh utility checks, caps, clone and save/load isolation,
RNG continuation, stable IDs, malformed snapshots, silencing and error recovery.
The 2,000-step synthetic stress fixture had repeated B1 births and D1 deaths,
remained finite and N<=8, and reproduced its entire snapshot on a second
identical seeded execution inside the test. This fixture validates engine safety;
it is not a task-growth experiment or evidence for any G prediction.

| N | Steps | Seconds | Steps/s |
|---|---:|---:|---:|
| 50 | 300 | 0.043575 | 6884.7 |
| 200 | 300 | 0.226465 | 1324.7 |
| 500 | 300 | 0.672917 | 445.8 |

Speed uses dt=.01, fixed-density synthetic random initial states and 300
integration steps per size. It includes grid rebuild, RK4, window recording,
strain fit and ctypes overhead; it excludes growth checks and pairwise/group
queries. These are single-run throughput measurements, not a benchmark against
Python or a task-development result. The 500-element case has 4,000 active
directed element couplings at the end.

Compiler: `Apple clang version 21.0.0 (clang-2100.3.34.2)`. Platform: `macOS-26.6.2-arm64-arm-64bit`.
C++17 -O3, no fast math, FMA contraction disabled. Build took
5.912 s. Exact build/test commands, source/reference hashes,
validated implementation hashes, full pytest output and speed records are in
[verification.json](verification.json).

The first attempted pytest invocation never collected tests: resolving the
virtualenv executable symlink selected system Python without pytest. That error
is retained separately. The first completed implementation batch passed 67
contracts; final inspection then added B1's measured maximum-lock trigger to the
event log, protected strain fitting against extreme weight ratios, and added
isolated below-strain/interrupted-novelty contracts. After that complete change
batch, the focused suite ran once (70 PASS) and speed was refreshed for that
code. Both completed batch records are preserved; no experiment/panel/mutation
probe was run. No tests were run while editing code.
