# Exploratory two-body force-map pilot (Pilot A, revised) — NOT C6 EVIDENCE

Status: SPECIFICATION, committed before any sampling. C6 remains BLOCKED / R006 STOP.
Authority: owner instruction 2026-10-03 ("do it"), following the Claude research report in this session.
This is an owner-requested exploratory pilot under AGENTS.md: own pilot entropy, scratch code outside `geomind/`,
all scripts, raw results and this status committed to `evidence/c6_dev_pilot/a_twobody/`. No project/source/native
file, threshold, protocol, status or historical receipt is changed. No R007, final entropy, mutation probe or panel.

## Why this pilot replaces the placement-gap sweep

The first plan (sweep the level-3 placement gap) rests on a premise the element law does not support. From
`geomind/c4_model.py` (inference from the equations, not yet measured): each element's velocity is the mean over its
k=8 nearest neighbours within radius 3 of a force along the pair axis equal to `A(1 + J cos dtheta) - B/r`, and phases
couple through `K exp(-r^2) sin dtheta` with K=1. In phase the pull is stronger and the sine coupling has its stable
fixed point at dtheta=0, so coupled groups should phase-lock near zero offset and close up. Elements cannot literally
cross (the `B/r` repulsion diverges); the question is whether the groups' member hulls overlap, which is the existing
criterion-6 quantity (overlap above 0.2). Two cautions from the review: the 0.556 equilibrium applies to an isolated
in-phase element pair and ignores the averaging over up to eight neighbours, so the cross-group force is diluted; and
at offset pi the pair force is `0.2 - 1/r`, repulsive for every r < 5, so anti-phase pairs may be pushed out of range
before the phase can slip. The phase-coupling weight is `exp(-r^2)`: 0.70 at 0.6, 0.24 at 1.2, 0.018 at 2.0, 4e-4 at
2.8. Beyond the radius groups do not interact at all. A gap sweep would mostly separate "fused" from "apart". The
two-body map measures the group-group interaction directly, which is the RRG closure test (03 section 13, 04 section
25) reduced to the force law: does the law that binds elements into a unit bind units into distinct, phase-locked
composites at a preferred separation, or does it fuse them?

## Question

For pairs of level-2 groups (and, as the descriptive lower-level comparison, pairs of level-1 C4 units), as a
function of initial separation and initial phase relation: do they (a) phase-lock, (b) approach or repel, (c) end
as two distinct, internally valid, interacting parts, or (d) fuse or separate?

## Fixed apparatus

Unchanged: the C4 element law (`c4_model.INTACT`), native engine `build/c6/element_law.dylib`
(binary sha256 5ac55f17..., source 895d7883..., verified before loading and in every worker; no build path exists in
this import chain), the frozen C4 detector thresholds, and the existing level-generic modules
(`c6_experiment`, `c6_levels`, `c6_compose`, `c6_units`) used read-only.

Pilot-only entropy (SPEC.json, 96-bit, generated once by `--write-spec`, disjoint from every other namespace).
Set per worker through `c6_experiment.DEVELOPMENT_ENTROPY` before any sampling; no file in `geomind/` is edited.

Harvest (same label-free procedure as the R2 gate, own entropy): 3,200 C4 worlds (purpose 1) give level-1 units;
260 level-2 worlds of five source-isolated units each (purpose 11, C2=3.4 as measured in the R2 gate) are formed,
and each accepted group re-accepted alone becomes a level-2 template (`harvest_composites`). A second pool of 400
C4 worlds (purpose 2) supplies level-1 pair templates. At most one template per source world is used, so no pair
shares upstream randomness. Pairs are formed from consecutive picks in harvest order. Targets: 32 level-2 pairs, 40
level-1 pairs (about 2x supply margin from the smoke yields: 0.45 usable groups per level-2 world, 0.5 distinct sources per level-1 world); fewer complete pairs are reported as such (level 2 needs at least 8 for any verdict, otherwise INCOMPLETE).

Pair construction (identical across all conditions of a pair, derived from the entropy and the pair index): a random
rigid rotation per part, a random approach direction, one random phase offset, one rate per part from
`U[-.096/C_dest, +.096/C_dest]` (C_dest = 3.4 for level-1 pairs, 16.4 for level-2 pairs, the destination level's
factor as in `c6_compose.assemble`). Part 1 sits at the origin; part 2 is brought in along the direction until the
minimum element distance between parts equals the gap (the `contact_solve` bracketing and bisection with the gap as a
parameter; checked equal to the original function at gap 0.6).

Conditions per pair: 5 gaps x 4 cases.
- Gaps (minimum element distance, L0): 0.6, 1.2, 2.0, 2.8 (coupled, below the radius 3) and 4.5 (decoupled control).
  Gap 0.6 is the current level-3 assembly.
- Cases: `natural` (the registered fixture: the pair's random phase offset and random rates); `phase0`, `phase_halfpi`,
  `phase_pi` (offset 0, pi/2, pi; both parts' collective rates set to zero so only the interaction moves the phase).

Integration: native RK4, dt 0.02. Short runs T=200. Frames every 0.2 for t<=20, every 1.0 up to the last own-level
observation window, every 0.2 inside it (W = 30 C_part; C_part = 3.4 for level-2 parts, 1 for level-1 parts). Long runs
(level 2, `natural` case, gaps 0.6, 2.0, 2.8) run to the level-3 horizon T=1640 (100 x 16.4) and evaluate the real
criterion 6 (`levels.recursive_validity` for the pair as the parent, W=492).

Measured per run: published centroid separation R(t) and wrapped published phase difference dTheta(t); minimum
element distance d_min(t); radius of gyration of each part; own-level dynamic validity of each part (`dynamic_validity`);
hull overlap of each part with the other (`geometric_validity`) over the last window; 13 (short) or 21 (long) full
state snapshots; wall/CPU per run. Series are stored every 0.2 for t <= 20 and at integer times afterwards; the 0.2
frames inside the last window are used for validity and are kept only in the snapshots.

## Estimators (fixed before the run; the same for both levels, no per-level tuning)

- coupled gap: gap < 3.0 (0.6, 1.2, 2.0, 2.8). Effective-coupling gaps: 0.6 and 1.2, where the phase-coupling weight
  exp(-gap^2) is at least 0.1. Gaps 2.0 and 2.8 are tabulated but do not enter P1 or P3(b).
- coupled at end: d_min < 3 at every stored frame of the final 50 time units.
- end category (mutually exclusive): SEPARATED (not coupled at end); FUSED (coupled at end, hull overlap > 0.2);
  DISTINCT_COUPLED (coupled at end, overlap <= 0.2, both parts' own-level dynamic validity ok, no degenerate hull);
  PARTS_DAMAGED (coupled at end, overlap <= 0.2, a part fails its own-level validity).
- bound: coupled at end and |R(end) - R(end-50)| / mean(R over the span) <= 0.10.
- distinct-bound: DISTINCT_COUPLED and bound.
- early slope: least-squares slope of R(t) on t in [0, 3].
- in-phase locked: over t in [50, 100], circular mean of dTheta within 0.5 rad of 0 and circular std <= 0.3.
- informative offset: |dTheta(0)| >= 1.0 rad (outside the lock zone). The offset-0 case and natural-case runs with a
  smaller initial offset are never scored for locking.

## Predictions (stated before any run; each can fail)

- P1 (phase locking): among level-2 short runs at the effective gaps, cases natural, phase_halfpi and phase_pi, with an
  informative offset, the in-phase-locked fraction. The decoupled baseline (gap 4.5, same filter, same estimator) must be
  <= 0.10, otherwise P1 is INDETERMINATE. SUPPORTED if >= 0.80, REFUTED if < 0.50, INDETERMINATE otherwise or with fewer
  than 8 runs.
- P2 (no distinct bound pair): among level-2 short runs that are coupled at the end (gaps below 3), the distinct-bound
  fraction. SUPPORTED if <= 0.10, REFUTED if >= 0.25, INDETERMINATE otherwise or with fewer than 10 runs. The FUSED
  fraction among the same runs and the full category decomposition are reported with it. Separated pairs are outside the
  denominator and are reported as their own category.
- P3 (phase-dependent push, then slip): (a) at gaps 0.6, 1.2 and 2.0, the early slope at phase_pi exceeds the slope at
  phase0 for the same pair and gap by more than 0.01 L0/C0 in >= 75% of comparisons (floor: ten times the decoupled drift
  noise), with the gap-4.5 comparisons quiet (|difference| < 0.01 in >= 90% of them, otherwise INDETERMINATE); and
  (b) among phase_pi runs at the effective gaps that are still coupled at t=50 (d_min < 3), |dTheta(50)| <= 0.5 in >= 75%.
  The fraction that separated before t=50 is reported. SUPPORTED only if both hold, REFUTED if either is below 60%,
  INDETERMINATE otherwise or with fewer than 8 runs in (a) or (b).

Reading, applied as written: FUSION_REGIME requires P1 SUPPORTED, P2 SUPPORTED and a FUSED fraction >= 0.5; then this
element law fuses coupled groups, distinct level-3 composites are structurally disfavoured here, and the next step is a
law or architecture proposal (for example node-level formation with the same law on published states). P2 SUPPORTED
without the other two conditions means no distinct bound pair, but not shown to be by fusion: report the decomposition
and return to the owner. P2 REFUTED means a distinct bound regime exists; report its (gap, case) region as the placement
for any future level-3 design. Anything else returns to the owner. All of this is an exploratory decision aid. It assigns
no C6 hypothesis verdict, does not qualify the repaired implementation, and does not show that RRG or this model can
never form level 3 under another law.

Level 1 (units) is reported with the same estimators, descriptively and without a verdict, as the lower-level
comparison for the closure question. Long runs (level 2, criterion 6 over the real level-3 window) are reported by gap
and category separately; they decide no prediction.

## Missing data and stops

INCOMPLETE takes precedence over interpretation within its scope. The scope that decides P1 to P3 is the complete set of
short runs (all conditions, level 1 and level 2) with at least 8 level-2 pairs and unique source worlds per pair; a
missing, duplicated, errored or unreadable short run or a pairing/dependency failure gives INCOMPLETE and no verdict.
Long runs are scored separately: a lost long run makes the overall status INCOMPLETE and leaves the short-run verdicts
standing, reported with `long_complete: false`. Missing runs are missing values, never negative outcomes. There is no
retry, no replacement and no outcome-dependent scheduling. Fewer than 8 level-2 pairs gives status INCOMPLETE.

## Resource caps and supervision (fresh harness, not the earlier pilot harness)

8 worker processes. Soft stop at 2,700 s total wall: no new submissions, pending work cancelled, workers terminated
(SIGTERM, then SIGKILL after 5 s), partial results kept, INCOMPLETE recorded. An independent watchdog thread at
3,000 s kills any remaining children, writes `HARD_STOP.json` and a minimal INCOMPLETE `SUMMARY.json` if none exists, then
exits; it is cancelled only after the summary has been written, so finalisation is inside the cap. Short, decisive runs
are scheduled before long runs. Expected duration about 6 to 9 minutes of wall time (about 3,000 core-seconds on 8 workers, from the smoke timings: 0.75 s per
level-2 run, 3.6 s per 600-unit long run, 0.28 core-s per harvested C4 world, 1.9 core-s per level-2 formation; the
full workload itself is unmeasured). There is no `--worker` entry point. Preflight refusals (identity, uncommitted files) happen before the
latch and consume no attempt; creating the exclusive `run/` directory is the one-shot latch, and from then on every
failure is recorded inside the run (the whole post-latch path is guarded). The run refuses to start unless the
specification files, this harness and every dependency in SPEC.json match their committed identities. All writes are
atomic (write, fsync, replace). The final summary write is guarded with a minimal fallback. Native identity (binary and
source hash against BUILD.json and SPEC.json) is verified before the first import use and in every worker; the loader in
this import chain only opens the existing library and has no build path.

Smoke (own entropy, own directory, not evidence): a reduced harvest with full level-2 formation, two level-2 and three
level-1 pairs, a reduced condition grid, and one long run at a shortened horizon, to exercise the level-2 and criterion-6
paths. The first smoke covered level 1 only; it is kept as `smoke_level1_only/`.

## Normalization ledger

| Quantity | Level / units / normalization |
|---|---|
| Separation, gap, radius of gyration | L0; element-level distances at both levels; no level-specific rescaling |
| Time | C0; own-level windows 30 C_part (C_part 1 for units, 3.4 for groups); level-3 horizon 100 x 16.4 |
| Rates | `U[-.096/C_dest, +.096/C_dest]` per part, the registered assembly rule, C_dest the destination level |
| Phase | wrapped radians; lock 0.5 rad / 0.3 rad std in the estimators above |
| Thresholds | the frozen C4 detector thresholds through `levels.thresholds(base, C)`; overlap <= 0.2 |

Descendant reads (members, element states) are owner/evaluator-side only; no upper-level predictor exists in this pilot.

## Stop conditions (yes/no, one action, one role)

| Condition | Action | Role |
|---|---|---|
| Specification, harness or dependency identity differs from the committed value? | Refuse to run | Implementer |
| `run/` already exists? | Refuse; no resume, no retry | Implementer |
| Native artifact hash differs from BUILD.json or SPEC.json? | INCOMPLETE; no build | Implementer |
| Soft wall cap reached? | Stop submissions, terminate workers, keep partial results | Implementer |
| Hard wall cap reached? | Watchdog kills children, writes HARD_STOP.json | Implementer |
| Fewer than 8 complete level-2 pairs? | Level 2 INCOMPLETE; return to owner | Owner |
| Result tempts a retune or rerun with new seeds? | Do not; return to owner | Implementer |

## Drafter self-audit (independent review of this specification and harness, 2026-10-03)

| Finding | Cause | Fix |
|---|---|---|
| P1 and P3(b) averaged over gaps 2.0 and 2.8, where phase coupling is 0.018 and 4e-4 and anti-phase pairs are repelled; both could fail whatever the law does | Defined "coupled" by the neighbour radius, not by the phase-coupling range | P1 and P3(b) restricted to gaps 0.6 and 1.2 (weight >= 0.1, from the law, not from data); other gaps tabulated |
| "P2 supported" could not mean fusion: repelled pairs and internally damaged groups also fail "distinct-bound" | One boolean estimator for three different outcomes | Mutually exclusive end categories; P2 evaluated among pairs coupled at the end; fusion reading needs FUSED >= 0.5 |
| The lock estimator had no decoupled baseline (about a third of decoupled natural runs would count as locked) | Offsets small and rates tiny in the natural case | Lock scored only from an informative initial offset (>= 1.0 rad); baseline must be <= 0.10; P3(a) has an effect-size floor and a quiet control |
| Spec said series were stored at 0.2 spacing in the last window; code thinned them | Wording written before the storage decision | Spec now states the stored grid |
| P2 population "all coupled runs" was ambiguous about long runs | Wording | Short runs only; long runs reported separately |
| Fewer than 8 level-2 pairs still reported COMPLETE | Status not set on that branch | Status INCOMPLETE |
| Spec said elements "interpenetrate"; B/r repulsion diverges | Loose wording | Reworded as hull overlap (criterion 6); dilution caveat added |
| Several post-latch statements outside the guarded block; hard stop wrote no summary; final summary write unguarded; watchdog cancelled before finalisation | Supervision written incrementally | Whole post-latch path guarded; watchdog writes a minimal summary and is cancelled last; guarded summary write with fallback |
| A long-run error would erase short-run verdicts; long runs were scheduled first; the long path was never smoked | Scope not separated | Scoped interpretation; short runs first; smoke includes one long run |
| First smoke exercised level 1 only (level-2 formation used the short observation window) | Smoke flag shortened formation | Smoke uses full level-2 formation (cheap) and a long run |
