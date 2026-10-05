NOT_READY

Option B engineering work in progress. Implementer: Codex:GPT-6.
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

## Port

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

Pending. Tests run once after the complete implementation/test batch. No READY
claim, independent acceptance, final entropy, mutation, panel or status change.

## Stops

| Yes/no condition | Action | Responsible role |
|---|---|---|
| Scope or protocol interpretation ambiguous? | Record the question and stop. | Implementer |
| Source/build identity mismatched? | Stop before loading. | Implementer |
| Equivalence or a discrete decision differs? | Fix the defect before readiness. | Implementer |
| Measured world exceeds 360 seconds? | Report NOT_READY with the actual cost. | Implementer |
| Independent Claude review absent? | Leave implementation unaccepted. | Owner |
