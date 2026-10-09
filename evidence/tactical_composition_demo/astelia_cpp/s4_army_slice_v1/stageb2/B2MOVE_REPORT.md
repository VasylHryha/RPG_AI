# B2 ordinary movement repair

Development geometry repair under decision 0039. Full old-bank diagnosis reads
all 180 round 0 fights at the existing 38,077 hash-phase 5 Hz frames. It does not
change data, labels, splits, thresholds, O, StageA/B/rev2 or accepted receipts.
The changed-path inventory is UNCOMMITTED_B2MOVE.txt. Math is in B2MOVE_MATH.md.

## Diagnosis from recorded data

The supplied 36.8/55.7/81.2% movement figures are **training-only**. The following
counts cover **all splits**, including validation/test. Ordinary rows total
154,997 melee, 533,163 ranged, 306,368 artillery; uncovered rows 99,081/234,166/56,727.
Distances are Euclidean pixels to the nearest **old** candidate, at unchanged 20 px.

| Role and inferred component path | Misses | Median gap px | P90 px |
|---|---:|---:|---:|
| Melee: v6 history/steering → participation band | 79,299 | 32.06 | 34.34 |
| Melee: v6 history/approach waypoint | 19,586 | 30.33 | 47.01 |
| Melee: baseline → arena clamp | 196 | 31.14 | 52.59 |
| Ranged: escort → participation band | 191,341 | 26.14 | 31.50 |
| Ranged: escort | 38,157 | 25.37 | 34.55 |
| Ranged: baseline/history | 3,164 | 45.21 | 79.80 |
| Ranged: baseline → participation band | 1,267 | 30.71 | 85.36 |
| Ranged: baseline → arena clamp | 237 | 61.20 | 92.33 |
| Artillery: anchor + gun repulsion/spacing | 50,531 | 29.79 | 50.50 |
| Artillery: focus + gun spacing | 1,153 | 23.66 | 29.17 |
| Artillery: focus | 656 | 24.69 | 29.45 |
| Artillery: baseline/history | 3,530 | 74.89 | 105.11 |
| Artillery: baseline → participation band | 621 | 32.73 | 85.73 |
| Artillery: anchor + spacing → participation band | 121 | 23.24 | 29.21 |
| Artillery: focus + spacing → participation band | 25 | 23.42 | 28.06 |
| Artillery: focus → arena clamp | 10 | 41.07 | 67.75 |
| Artillery: baseline → arena clamp | 80 | 92.32 | 112.40 |

P16 escort and focus/anchor formulas, gun-spacing sums and the participation
transformation are reconstructed **only in the diagnostic script**. They match
the executed endpoint exactly for 229,498 ranged and 52,496 artillery misses.
The deployed bank does not invoke that diagnostic code or a controller.

The compact source recordings discarded raw/winner. Consequently these are
public-formula matches and qualified geometric inferences, not a causal replay
of every intermediate operation. In particular v6 baseline sums complex-mode
friend attraction/repulsion and enemy motion before its 200 px waypoint; its
individual vector contributions cannot be separated from stored endpoints.
The 79,299 melee participation classification matches the nearest enemy's outer
body-aware band, rather than a recorded arbitration winner. Baseline/history
is not silently relabeled as irreducible. The small fixture's additional
compatibility subclusters separate 200 px waypoints from unresolved steering.

There is no ordinary command-goal velocity smoothing in the engine bridge.
It clamps to the arena; participation first body-clamps its projected point.
The public one-second velocity is a possible continuation input, and is used
by aim. The full-diagnosis script snapshot and builder hashes are preserved in
B2MOVE_DIAGNOSIS.json; the updated script uses a verified HEAD baseline twin
for prospective repeatability, without rewriting that completed evidence.

## Toolbox and consistency

The old vocabulary remains a prefix. New pure geometry supplies body-aware
bands, each enemy's artillery anchor and spaced anchor, escort directions about
the nearest friendly gun, approach/repulsion/continuation points and fixed
direction/engagement rings. Raw points and unconditional band images are both
options. No splash-value target rank, P16 activation, participation chooser,
react winner, multiplier or fire rule is copied. The network chooses.

The mathematical maximum is 1,226 movement candidates, with 1,280 padded slots;
the fixture's maximum was 838. Native/Python descriptors are 26-wide, preserving
numeric fields 11:18. Compact cache records remain 11 values per candidate,
explicitly excluding new one-hot fields from the numerical tail. Scorer widths,
source pointers and flat-head slices derive from common constants. Aim geometry,
20 px tolerance, ±12 px aim/±24 px move residuals and admission floors are unchanged.

## Small test-mode estimate

B2MOVE_SAMPLE.json records 11.04 seconds, two metadata-selected largest training
fights (C3 train_0019 and regular train_0049), 96 evenly spread members of their
existing 5 Hz sample, and all 3,541 physical-prefix ticks for exact public velocity
and deterministic N2 state. No combat or optimizer was run.

| Ordinary movement | Rows | Old candidate coverage | New candidate coverage | New bounded residual coverage |
|---|---:|---:|---:|---:|
| Melee | 296 | 34.80% | 100% | 100% |
| Ranged | 1,304 | 55.06% | 100% | 100% |
| Artillery | 590 | 76.78% | 100% | 100% |

New values hold separately for N1, N1r and full-prefix drift-adjusted N2 targets.
Sampled aim and dodge availability also remain 100%. This is TEST_ONLY with
small denominators, no admission or whole-population guarantee. The completed
fixture binds its source snapshot before the subsequent cache storage repair;
candidate generation/scorer/N2 formulas did not change afterward.

Uncovered ordinary share in this fixture is 0% per role, and all sampled goals
fit the existing ±24 px residual. A private-input irreducible share is **not
established**, not measured as zero: rev2 O is deterministic from public
prefixes. If full coverage finds residual misses, keep their full distances
and public-history limitations. A follow-up may propose a history-conditioned
bounded residual extension with a prospective pixel envelope and native/Python
parity. Do not lower 90% admission or silently widen ±24 px in this delivery.

## Cache integration and validation

Whole-fight cache projections in the two samples were 2,504/2,448 MiB, above the
previous 512 MiB eager worker allocation. Schema 2 caches only the four registered
90-tick head windows, reads all public prefixes, and stores exact IEEE-754 bits
as XOR-chained 32 MiB chunks. Lazy frame handles keep one decoded chunk/frame
resident; `stored(list(frames))` retains metadata rather than every bank.
State-only prefixes never load candidate arrays. The 20 GiB compressed projection,
2 GiB disk reserve, 2 GiB training-worker RSS guard and live time cap remain active.
Whole-dataset compressed size and timing are still host measurements; a
projection refusal remains a refusal. No resource gate was bypassed.

One focused pass passed 31 tests in 6.75 seconds (7.37 seconds wall time).
Focused validation and separate review are recorded in TESTS_B2MOVE.json and
OWNER_RECHECK_B2MOVE.md. Full sampled coverage, complete production build,
measurement and training remain the following host sequence.

```sh
cd /Users/new/RiderProjects/ai_RPG_test
B2=evidence/tactical_composition_demo/astelia_cpp/s4_army_slice_v1/stageb2
ML=evidence/tactical_composition_demo/astelia_cpp/s4_net_slice_v1/_local/mlenv/bin/python
export B2_VARIANT=react_on PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
nice -n 15 "$ML" "$B2/build.py"
nice -n 15 "$ML" "$B2/coverage.py" --round 0 --preserve-stale
nice -n 15 "$ML" "$B2/train.py" measure --round 0
nice -n 15 "$ML" "$B2/train.py" run --round 0
```

Build: approximately 30–90 seconds based on the earlier build, new production
time unmeasured. Coverage: unchanged 1,800-second cap and first-fight projection;
the old sampled run took 958 seconds and the larger bank may cost more.
`--preserve-stale` archives the old local COVERAGE.json byte-for-byte under the
ordinary admitted lock before sealing its replacement; same-code repeats
refuse. The supplied COVERAGE_ROUND0_V1.json stays unchanged. Existing round 0
INDEX/data and owner/Claude cap remain in place. Measurement obtains actual
cache compression, optimizer costs and projection. Training runs only after
full sampled coverage passes and a new admitted budget fits the live cap.
The four commands are for Claude on the normal host; this fixture does not
replace them or authorize behavioral acceptance.
