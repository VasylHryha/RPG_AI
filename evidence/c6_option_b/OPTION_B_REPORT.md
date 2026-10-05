NOT_READY

Option B engineering implementation. Final arithmetic: scalar R4, with exact typed reuse and detection. Implementer: Codex:GPT-6.
Final V3 is equivalent exactly on the stored current fixture, both complete smoke
worlds and the complete development world. The worst cold smoke world is
952.884861 seconds against 360, so runtime readiness fails. No independent
Claude acceptance is claimed; C6 remains BLOCKED / R006 STOP.
Authority: decision 0029 and the owner's current instruction. Baseline HEAD:
`b547d7f8efab06ec83bc47fff45c4dc5ddcff58f`.

## Predeclared equivalence contract (before profiling or port measurement)

- The reference is the current Python orchestration with its existing native
  field kernel. The selectable optimized path must retain that reference.
- Identical arithmetic: exact equality, including full-state arrays, identity
  hashes, entropy inputs, inventories and all discrete outcomes.
- Necessarily reordered float64 arithmetic: absolute error <= 1e-10, relative
  tolerance zero, for state, statistics, response arrays and gains. This is the
  existing independent-reference tolerance, not a changed scientific threshold.
- Every qualification, structural/recovery/causal and detection decision,
  selected membership, persistence row, control result, witness and chain outcome
  must match exactly. Any decision flip fails equivalence; do not widen limits.
- Only measured timing, CPU/RSS and build metadata are excluded from numerical
  comparison. Byte digests of numerically changed arrays are compared separately
  through their underlying arrays, never treated as numerical measurements.
- Use existing R006 development entropy 46036001, worlds 0 and 1, and stored
  descriptor fixtures, plus smoke entropy 46036002 worlds 0 and 1 for complete
  reference/native comparison. No final entropy, new registration or population verdict.
- Runtime rule: max complete-world seconds * 40 / 2 * 1.5 <= 10800;
  each complete world must be <= 360 seconds. Record load and serialization cost.

## Profile

Completed before porting: development entropy 46036001, world 0, unchanged full
protocol. Raw profile: `profile_run/PROFILE.json`; Python profile:
`profile_run/reference.prof`; full world: `profile_run/reference_world_000.json.gz`.

| Cost | Wall seconds | Interpretation |
|---|---:|---|
| Complete world | 1176.761319 | 443.376656 process CPU seconds |
| Native element-law RHS | 823.267350 | 69.96% of world; timer surrounds material work |
| Native field/carrier RHS | 51.424522 | 4.37%; medium drift/diffusion/forcing addition |
| Advance self time | 971.396763 | 82.55%; includes native integration/RK/drive and small Python overhead |
| Outgoing diagnostics | 95.503927 | Inclusive; Gaussian/phasor channels and reductions |
| Detection statistics | 38.298873 | Inclusive, 1896 windows |
| Component matching | 24.871350 | Within detection; 59007 calls |
| Qualification | 357.893916 | Inclusive, 26 calls; overlaps integration/detection |
| Recovery futures | 212.635119 | Inclusive, 17 calls |
| Causal forks | 144.051442 | Inclusive, 17 calls |
| Descriptor forks | 54.491551 | Inclusive, eight descriptors |
| Owner cloning | 9.331034 | Inclusive, 18146 calls |
| Grid orchestration self time | 3.910929 | 604 calls; orchestration remains Python |
| Serialization/gzip/write | 13.464800 | 57461990 raw bytes / 23343855 compressed bytes |

Inclusive rows overlap and must not be summed. Native timers use monotonic wall
time and include preemption. The instrumented source adds timers around the exact
original equations; source and binary hashes are in START/PROFILE. Original native
source and binary are preserved. Instrumentation/cProfile overhead is included;
this profile is not the optimized runtime measurement. Load averages were
[67.3125,73.41455,60.81348] initially and [77.21289,112.65674,107.61914] at completion,
on ten logical CPUs, with intermediate load exceeding 150. Process enumeration
was denied by the sandbox; this is recorded rather than omitted silently.

The world was valid, qualified its initial source, had first witness
[true,false,true], and lost the turn-2 source at 315; no complete chain. These
outcomes guide no scientific change. R006 is not rescored.

Port selection: material RHS is the dominant hot path. Batch its Gaussian exp
and pair sin/cos operations in a new typed float64 C++ kernel using the platform
vector math implementation, preserving scalar expression and accumulation order.
Vector transcendental evaluation changes rounding and is covered by the already
declared 1e-10 absolute tolerance; decisions still require exact agreement.
Also port component matching to typed C++ with the same distance arithmetic,
strict edge threshold, median spacing, and ascending component discovery.
Leave recovery/causal/world orchestration and all protocol settings unchanged.

## V1/V2 port (archived; superseded by exact V3 below)

New files only: `native/c6_option_b/field.cpp` batches the dominant material
pair/site transcendental calculations using float64 Accelerate vForce. Scalar
arguments, pair/site accumulation order, field/carrier law, RK4 stages, analytic
drive, modes, mask normalizer and compute-before-mask work stay unchanged.
`native/c6_option_b/detection.cpp` ports the connected-component kernel. It
retains median nearest spacing, strict distance comparison, lock mask and
ascending discovery. Other statistics and all qualifications/futures stay Python.

`geomind/c6_option_b.py` selects these kernels inside an isolated process;
`tools/c6_option_b_check.py --backend reference|native` is the engineering caller.
There is no final-entropy argument or panel route. Original R4 files are untouched.
Build is explicit and atomic in its separate build directory, with source/flags/
binary identities verified before load and after each run. Reference mismatches
stop before its loader can rebuild. Cross-backend passive/emission caches are
cleared at selection boundaries because the original cache keys lack a kernel
identity; within a run their original bounds and sharing semantics are retained.

The new audit path compares every returned production-step full array with the
original kernel on identical inputs and every native graph decision with Python.
It requires bit-identical no-cohort field arithmetic. Whole-world comparison
compares all finite numerical leaves and discrete/qualification/chain outcomes,
with exact generator inputs, perturbations and clocks. Digest changes are counted
separately: snapshots have underlying arrays in the worlds, and source flow
digests additionally require streamed full-array audit. Cost/build fields are
separate metadata. Tolerance remains 1e-10; no widening is permitted.

## Equivalence and runtime

The initial tolerance declaration stays unchanged. The final scalar path strengthens
the requirement to exact equality; no comparison limit or scientific threshold was widened.
All results below are engineering observations on non-final inputs.

### V1 retained results and prospective V2 engineering batch

V1 passed all 374 C6/existing/new contracts once, in 99.86 seconds. Source and
binary snapshot: `v1_source/`. Its audited descriptor fixture matches the current
stored fixture (maximum 3.77e-17); 17,372,682 full-flow floats compared with the
reference kernel (maximum 7.99e-15). The historical descriptor validator passes
at 6.88e-14. The generic historical comparison's differing diagnostic text is
preserved in HISTORICAL_FIXTURE_COMPARISON.json; its failure is not a decision flip.

At two concurrent workers, V1 smoke world 1 took 352.579488 seconds (264.853964 CPU),
357.126236 including serialization. It reached one operation, witness
[false,true,true], and did not form a chain. V1 smoke world 0 took 1032.023923 seconds
(693.862501 CPU), 1044.018615 including serialization; it completed two operations,
both witnesses [true,true,true], a mechanical chain without exclusive enablement.
These are engineering comparison observations, not registered scientific evidence.
V1 is NOT_READY: worst projection 30960.717699 seconds. No result is overwritten.

Reference smoke world 1 finished in 629.685210 seconds. Its comparison has numerical
maximum 3.442035120100967e-11 and identical 1396 Boolean decisions. The comparator
incorrectly classified start_ids and operation_end_ids as discrete physical IDs;
these are array digests, with underlying before/operation/end states and declared
treatment metadata present. V2 corrects
only that digest classification, preserves the failed comparator output, and adds
regressions requiring underlying state/decision disagreement still to fail.

Before the V2 port: the original complete-world profile attributes 779.843663
inclusive seconds to 2111 passive compute_source misses; cached_array had 7212
calls in total, including 2718 emission lookups. This overlaps native material
time and motivates exact reuse instead of altered arithmetic. V2 will retain
full returned-grid retired-source material/carrier trajectories in a typed C++
cache, keyed by every kernel input, clock, dt, horizon and sampling. The actual
medium is still integrated live on each hit. No coarse replay or discarded
element state. Cap retired trajectories at 256 MiB and repeated unselected
control trajectories at 32 MiB per native thread; a bounded probation inventory
admits unselected trajectories only after an exact repeat. Original Python cache
bounds remain unchanged. This additional memory is an engineering resource choice,
not a scientific/protocol/worker-budget change. Measure hits, bytes and memory.
Keep V1 vector arithmetic unchanged, preserving its already validated rounding.

The measured V1 runtime failure justifies this second change batch and one affected
end-of-batch test run; unchanged unrelated C6 contracts reuse their V1 evidence.

### V2 measured results (archived source; numerical equivalence failed)

The affected end-of-batch contracts passed once: 112 tests in 77.92 seconds,
`contracts_v2.xml`. All V2 changes were complete before this run. The unchanged
broader C6 contracts retain their V1 evidence; 374 and 112 are overlapping counts,
not 486 distinct tests. V2 retains V1 numerical arithmetic and adds bounded exact
trajectory memoization only.

| Smoke world | Registered world seconds | Process CPU seconds | Serialization/write seconds | Total seconds | Peak RSS after serialization |
|---|---:|---:|---:|---:|---:|
| 0, full two-operation chain | 592.356790 | 491.360260 | 7.330237 | 599.692654 | 1,060,683,776 bytes |
| 1, one operation | 284.705885 | 219.608599 | 5.939522 | 290.648943 | 781,402,112 bytes |

Both started in separate cold processes together, with exactly two world workers.
All three grids within a world remain sequential. Worker count and the rule are
unchanged. Worst V2 world is world 0: 592.356790 seconds > 360; projected
592.356789791 * 40 / 2 * 1.5 = 17,770.703694 seconds > 10,800. Therefore NOT_READY.
No normalized, load-adjusted or predicted time substitutes for this observation.

Both complete V2 outputs match V1 exactly, including every array digest:
3,045,093 numerical leaves / 2,847 Boolean leaves for world 0;
1,460,200 numerical leaves / 1,396 Boolean leaves for world 1. Other discrete
strings, integers, memberships, inventories, checks and witness/chain outcomes
also match. Comparisons at absolute tolerance zero:
`SMOKE_0_V2_EXACT_COMPARISON.json`, `SMOKE_1_V2_EXACT_COMPARISON.json`.

World 0's cache avoided 9,215,000 material RK steps (2,021 retired hits, 18 control
hits, 3,447 eligible misses); world 1 avoided 2,401,000 steps (519 retired hits,
9 control hits, 1,590 misses). Retained payload/key bytes stayed below the declared
256 MiB retired, 32 MiB control and 2 MiB probation limits. These bounds exclude
container overhead, live integration buffers and the unchanged 32 MiB native
drive / 64 MiB Python passive / 16 MiB Python emission caches. Recorded process
RSS includes those and full protocol/evidence state. Retired means selected OFF
material in this cache policy; its name does not change a source's scientific
status or suppress current-source work. All-OFF unselected controls require a
second exact key lookup before admission. Actual-medium trajectories are never
replayed; they are integrated live on each cache hit.

Machine: Apple arm64 macOS 26.6.2, ten logical CPUs, Apple clang 21.0.0. V2 starts
with load averages [31.47,32.78,43.58]; world 1 ends [40.60,34.82,41.22], world 0
ends [9.53,22.47,33.99]. Machine load differs across batches, so the V1-to-V2
wall-time reduction is a bounded observation, not an isolated hardware speedup.
Start/end metadata live in each COSTS.json; intermediate samples in MACHINE_LOAD.jsonl.

The original smoke-world-0 reference completed in 1379.423954 seconds (934.809456 process CPU).
The V2 full-array audit and its whole-world failure are recorded below. V2 is superseded,
and its runtime measurements do not qualify V3.

### V2 equivalence failure and required V3 correction (declared before edits)

The complete streamed development audit passed locally: 4,829 kernel calls,
996,971,880 float64 outputs, maximum 2.1316282072803006e-14 on identical inputs,
and 59,007 exact component decisions. Its comparison against the complete
profiled world nevertheless FAILED: two normalized position diagnostics differ
by 3.6345093791471787e-10 and 3.682683074506324e-10, beyond the predeclared 1e-10.
All 2,512 Boolean leaves and other discrete outcomes agree. Neither successful
local comparisons nor unchanged decisions excuse this numerical failure.
`DEVELOPMENT_0_COMPARISON.json` and V2 outputs are retained unchanged.

Required V3 repair: restore the original scalar sin/cos/exp and the original
field/element evaluator arithmetic, preserving the typed exact trajectory cache
and typed detector. No new mathematical reformulation, tolerance widening or
threshold change. The final kernel will require exact equality on every audited
full array; final whole worlds will use the comparator's --exact mode. V2 source,
binary and report will be archived before changing code. Wait for the active
original reference world to finish, finish the full change/test batch, then run
one affected end-of-batch suite and fresh non-final output directories. This
additional batch addresses an observed equivalence failure, not a routine rerun.

## Final V3 implementation and completed contracts

The original `native/c6_r4/field.cpp` evaluator, drive law and RK4 are included
literally, with only field_run renamed to a private uncached function, followed
by the typed trajectory-cache extension. Pair/site sin/cos/exp use the original
scalar implementation and accumulation order. Accelerate is removed from the
final source and flags. Final build: OPTION_B_BUILD.json and option_b.dylib;
final seven source identities: FINAL_SOURCE_HASHES.json. Earlier root V2 build
snapshots have explicit V2 filenames and v2_source/ retains the full V2 source.

The final C++ hot paths are exact material/carrier trajectory keying, lookup,
admission, eviction and replay, plus component detection. Material/carrier paths
remain complete at every returned production-grid time; actual-medium integration
remains live. The dominant repeated material-law work is avoided on exact hits,
without changing any arithmetic or freezing descendants. The original Python
orchestration and original native kernel remain selectable with --backend reference.
Normal native selection uses --backend native; --audit additionally compares the
returned full arrays against the original kernel on identical inputs.

The final audit requires identical float64 bits on every successful kernel call,
including signed zero; its negative controls reject both a 1e-15 difference and
a signed-zero difference. Exact detector labels are checked separately. Final
world/fixture comparisons require --exact: zero numerical error and zero changed
array digests. Only root runtime/CPU/RSS/build metadata are excluded.

All planned V3 code/test edits finished before its one end-of-batch test run:
377 C6 contracts passed in 67.51 seconds, zero failures/errors/skips, contracts_v3.xml.
Command: `.venv/bin/python -m pytest -q -x tests/test_c6.py tests/test_c6_r3.py
 tests/test_c6_r4.py tests/test_c6_r4_field.py tests/test_c6_option_b.py`.
Earlier 374-test and 112-test receipts are retained as separate, overlapping batches;
they are not added to the final 377 count. Additional batches were required by
observed runtime and equivalence failures. No code was edited during a world run.

Final descriptor fixture: all 159 kernel calls / 17,372,682 float64 values matched
the original kernel bit-for-bit; maximum error zero. The current stored descriptor,
all 254,920 numerical leaves, 51 Boolean leaves, all other discrete values and all
array digests match exactly (FIXTURE_V3_EXACT_COMPARISON.json). Reserved fixture
inputs are 882901/552; the runner's unused default smoke selector is metadata for
this fixture mode and is not consumed by fixture(). Timing includes audit and is
not a normal-path or full-world speed claim.

Final smoke world 1 completed validly in 301.320498 seconds (270.596456 process CPU),
307.064657 including serialization, with 790,970,368 bytes lifetime peak RSS after
serialization. Its complete output matches the original reference exactly:
1,460,200 numerical leaves, 1,396 Boolean leaves, all other discrete values and
zero changed digests (SMOKE_1_V3_EXACT_COMPARISON.json). It has witness [false,true,true],
no chain and no exclusive enablement, unchanged from the reference. Its cache
avoided 2,401,000 material RK steps with the same bounded V2 hit/miss inventory.
Final smoke world 0 completed validly in 952.884861 seconds (661.628785 process CPU),
960.573062 including serialization, with 958,627,840 bytes lifetime peak RSS after
serialization. It matches the original reference exactly: 3,045,093 numerical
leaves, 2,847 Boolean leaves, all other discrete values and zero changed digests
(SMOKE_0_V3_EXACT_COMPARISON.json). Both operations have [true,true,true]; the
mechanical chain is complete, exclusive enablement false. The cache avoided
9,215,000 material RK steps (2,021 retired / 18 control hits, 3,447 misses).

| Final cold world | World seconds | CPU seconds | Serialization seconds | Total seconds | Peak RSS after serialization |
|---|---:|---:|---:|---:|---:|
| Smoke 0 | 952.884861 | 661.628785 | 7.681639 | 960.573062 | 958,627,840 bytes |
| Smoke 1 | 301.320498 | 270.596456 | 5.733314 | 307.064657 | 790,970,368 bytes |

Worst final world: smoke 0. Projection 952.884861041 * 40 / 2 * 1.5 =
28,586.545831 seconds > 10,800, and 952.884861 > 360. Therefore NOT_READY.
This is the final source's measured result; V1/V2 costs do not qualify V3.
Even the worst world's process CPU cost exceeds 360 seconds; machine contention
is not a basis to waive the observed rule. Cold native worlds started together
with two workers, with all grids sequential. Load starts [4.93,9.99,20.30];
world 1 ends [23.35,14.08,18.70], world 0 ends [27.60,42.15,34.10]; intermediate
load reached 55.31 on ten logical CPUs. Load differs from reference batches,
so do not treat the wall-time ratio as an isolated hardware speedup.

Final complete development audit: all 4,829 kernel calls and 996,971,880 returned
float64 values match the original kernel bit-for-bit, maximum error zero; every
label from all 59,007 component calls matches. Its complete stored world also
matches the profiled reference exactly: 2,601,660 numerical leaves, 2,512 Boolean
leaves, every other discrete value and every array digest, including both earlier
failing normalized position diagnostics (DEVELOPMENT_0_V3_EXACT_COMPARISON.json).
The original development outcome is retained: first witness [true,false,true],
turn-2 source loss at 315, no complete chain and no exclusive enablement.

Audit world seconds 1236.797730, process CPU 684.944660, serialization 9.809169,
total 1246.615983, peak RSS 1,000,521,728 bytes. It deliberately runs the original
kernel as well as the candidate; its cost is diagnostic and is not used as a
normal candidate runtime. Load starts [67.13,50.10,38.05], ends [36.31,56.63,53.57].
Detailed costs/audit counters and source pin are in audited_v3_development_0/COSTS.json.
No new science conclusion or population verdict is assigned.

Final engineering equivalence: PASS at zero tolerance. Final registered runtime
rule: FAIL, worst 952.884861 > 360 and projection 28,586.545831 > 10,800.
Independent Claude engineering review: pending. No READY or acceptance claim.

## Deviations, preservation and owner handoff

Two setup attempts ran no world: the sandbox refused process enumeration (`ps`),
and an explicit bytecode compile used a protected default cache prefix. Subsequent
Python commands use PYTHONPYCACHEPREFIX=/private/tmp/c6_option_b_pycache. Machine load
averages, logical CPU count, OS/architecture, elapsed/process CPU time, serialization
and peak RSS are recorded; process enumeration remains unavailable.

The generic historical fixture comparator fails only on pre/post-repair diagnostic
method text. HISTORICAL_FIXTURE_COMPARISON.json remains unchanged; the existing
historical validator passes all its numeric/scientific comparisons at 6.88e-14.
Its reported descriptor ratio includes audit, compares an older implementation,
and is not a world-speed claim. The failed smoke comparator misclassified two
array-digest keys; its failure and correction are both retained, with negative
controls for altered underlying arrays/decisions. The V2 whole-world numerical
failure is a real failure, retained and addressed by restoring scalar arithmetic.

The implementation is new files only. No C0-C5 frozen file, existing R4 source,
committed receipt, STATUS.json, final entropy, registration or gate stamp is changed.
The source pin verifies the existing audited release before every world/fixture.
This task runs no R007, mutation probe, recorded panel or C0 experiment. Existing
unrelated work and later commits from concurrent sessions are preserved. PRESERVATION_CHECKS.json binds the final preservation inventory. Normal-hook
delivery commits and a verified bundle are described in WORKSPACE_DELIVERY.md.

The owner still needs the independent Claude engineering review required by 0029.
This port supplies no population claim, exclusive-enablement evidence or source
qualification of a new experiment. C6 remains BLOCKED / R006 STOP. The native
selection requires one isolated orchestration process; all three grids stay
sequential and the runtime workers stay at two. The supplied build is macOS arm64;
other platforms require a separately identified explicit build and measurement.
Development world 0 was profiled and audited; stored R006 windows from both
worlds 0/1 were checked for exact detector equivalence. Development world 1 was
not rerun; complete reference/native comparisons cover smoke worlds 0/1 instead.
No unresolved scope/protocol interpretation question was encountered.

## Stops

| Yes/no condition | Action | Responsible role |
|---|---|---|
| Scope or protocol interpretation ambiguous? | Record the question and stop. | Implementer |
| Source/build identity mismatched? | Stop before loading. | Implementer |
| Equivalence or a discrete decision differs? | Fix the defect before readiness. | Implementer |
| Measured world exceeds 360 seconds? | Report NOT_READY with the actual cost. | Implementer |
| Independent Claude review absent? | Leave implementation unaccepted. | Owner |
