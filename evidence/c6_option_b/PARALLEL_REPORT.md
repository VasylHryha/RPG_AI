NOT_READY

Official runtime readiness is pending a quiet-machine measurement scheduled by Claude.
This is decision-0029 engineering work. Exact-equivalence checks pass; this report
assigns no new scientific verdict, milestone acceptance or runtime readiness result.
The existing Claude APPROVE_WITH_NOTES review covers the preceding sequential port;
this parallel extension is supplied for subsequent review.

## Design and budget

`geomind/c6_option_b_parallel.py` selects a new GridSet implementation inside the
existing isolated-process native backend context. The original R4 files, native
law, build flags, thresholds, entropy definitions and sequential selection remain
unchanged. Select the extension with `tools/c6_option_b_check.py --backend native
--parallel`; omit --parallel for the sequential option-B path.

Declared k = 5 threads per world: one coordinator plus four ThreadPoolExecutor
compute workers. Two world processes × five threads = ten, on this ten-logical-CPU
Apple arm64 macOS 26.6.2 machine. BLAS/OpenMP helper teams are constrained to one
thread before importing NumPy in the CLI. The harness launches at most two cold
world processes together. Every complete world used all four compute workers.

Each ordinary scope runs its three independent full grids concurrently. Each
recovery schedules the control and kicked futures together (six grid jobs), and
each causal assay schedules all eight control/treated forks together (24 grid jobs).
Nested work is flattened into the same pool; no worker submits and waits for
another worker. Blocks retain the original ten-second streaming boundaries and
production-step integration/sampling. Each task returns a new full owner, its
full production-step flow and original outgoing-channel computation. The coordinator
merges grid results by k=0,1,2, accumulates powers/traces/maxima in the original
order and appends checks in the original control/kick and direction/label/fork order.
Original per-grid reductions, perturbations, normalization and measurements remain
unchanged. Candidate selection and the surrounding world protocol retain their
original sequencing. Actual-medium and all underlying material states continue evolving.

Tasks read private cloned owners. Python passive/emission caches retain their
existing complete physical/time/grid keys, lock-protected lookup/eviction and
immutable arrays. Duplicate simultaneous misses may recompute the same exact
value. Native drive/trajectory caches remain thread-local with exact byte keys;
cache admission/eviction and task scheduling affect costs only. Audit bookkeeping
is protected by a lock; native arithmetic runs outside that lock. Results resolve
by original job index, including exception propagation. Shutdown drains active
work and cancels queued work before restoring assay/backend functions. Both
contexts require one isolated orchestration process, as the prior backend did.

## Tests and exact comparisons

All implementation edits preceded testing and every long world run. The first
end-of-batch command ran the 378 existing/option-B checks successfully, then failed
in a new short fixture because its 0.1-second duration retained a one-second frame
interval: `ValueError: nonintegral time grid`. That fixture-only error was fixed.
The bounded retry passed the exact grid/recovery/causal comparisons and concurrency
check, then exposed an exception-test scheduling assumption: shutdown correctly
cancelled a queued task before it set the test's event. A barrier now ensures both
tasks have started, so the test checks active-work draining. No implementation
change followed either attempt. Failed logs/XML remain as TEST_ATTEMPT_1_LOG.txt /
contracts_attempt_1.xml and TEST_ATTEMPT_2_LOG.txt / contracts_attempt_2.xml.

Final affected parallel contracts: **4 passed in 1.15 s**, zero failures/skips,
TEST_PARALLEL_LOG.txt / contracts_parallel.xml. Unchanged earlier contracts: **378
passed** in the first 175.32-second run before its fixture failure. This is **382
distinct successful affected contracts** across retained valid evidence, with two
separate failed test-setup attempts; repeated new-test passes are not added.
The existing checks were not rerun after changes confined to the new test fixture.
Commands used `.venv/bin/python -m pytest -q -x` with the six C6/option-B test files
for attempt 1, then only tests/test_c6_option_b_parallel.py for bounded retries.

Forward and reverse task submission run the same complete inputs and merge order.
Both schedules compare directly against the stored sequential option-B artifact
and original reference for each world, at tolerance zero. The comparator also
rejects float-bit/type differences, including signed zero. Digests, inventories,
check order, all decisions, reached windows, publication/continuation and chain
outcomes must agree; only the established root cost/build metadata are excluded.
These are three existing worlds repeated for scheduling checks, not six independent
scientific worlds. Reserved descriptor inputs remain 882901/552.

| Input, in both schedules | Numerical leaves per comparison | Boolean leaves | Maximum error | Changed digests |
|---|---:|---:|---:|---:|
| Stored descriptor fixture | 254,920 | 51 | 0 | 0 |
| Smoke world 0 | 3,045,093 | 2,847 | 0 | 0 |
| Smoke world 1 | 1,460,200 | 1,396 | 0 | 0 |
| Development world 0 | 2,601,660 | 2,512 | 0 | 0 |

Each fixture schedule additionally audits all 159 kernel calls / 17,372,682
float64 values directly against the original kernel on identical inputs, bit for bit.
The forward development audit compares **4,900 calls / 1,017,108,092 float64 values**,
all bit-identical with maximum error zero, and checks every label in **59,007 detector
calls**. Its kernel-call count differs from sequential V3 because concurrent Python
cache misses can duplicate exact computations. This is a cost difference, and all
duplicated calls are audited too. New signed-zero and existing tiny-difference
negative controls pass. The native scalar kernels and binaries were not rebuilt.

Comparison JSON files under parallel/ bind both input artifact SHA-256s. References
are the stored post-stop descriptor, original reference_smoke_0/1, the original
profile_run/reference_world_000 and the final sequential V3 fixture/smoke/audited
artifacts. They remain unchanged. New source hashes are in parallel/SOURCE_HASHES.json;
the inherited C++/binary identities remain in OPTION_B_BUILD.json / REFERENCE_BUILD.json.

## Timing under observed load — informational only

No quiet-machine measurement was attempted. Observed load was high throughout
the comparison batch. Process enumeration is unavailable under this sandbox, so
no attribution is inferred from load. Ten-second samples live in parallel/MACHINE_LOAD.jsonl, and each case has
START.json, COSTS.json and the exact command/exit record. CPU below is process CPU
for computation, including backend/pool setup and teardown; wall is the original
complete-world timer. Serialization/write is separately measured in COSTS.json.
CPU sums execution across this process's threads. The audited development row also
executes the original reference and is diagnostic cost.

Observed load-average ranges (1 / 5 / 15 minutes), including samples and start/end observations: **34.44–86.66 / 43.61–66.13 / 43.34–56.77** on ten logical CPUs. Load variation prevents an isolated speedup claim.

| Case | World wall s | Process CPU s | Start/end 1-min load | Peak RSS bytes |
|---|---:|---:|---:|---:|
| smoke_0_forward | 608.837933 | 764.754579 | 60.87 / 43.88 | 2,188,935,168 |
| smoke_0_reverse | 558.162490 | 755.214469 | 44.37 / 37.35 | 2,198,290,432 |
| smoke_1_forward | 266.938126 | 325.586662 | 60.87 / 64.38 | 1,386,676,224 |
| smoke_1_reverse | 366.453516 | 339.060899 | 34.97 / 86.66 | 1,408,319,488 |
| development_0_forward (audit) | 643.365530 | 755.319273 | 44.37 / 34.44 | 1,956,741,120 |
| development_0_reverse | 437.205097 | 409.924076 | 34.97 / 66.77 | 1,817,804,800 |

Native payload/key bounds remain per compute thread: 256 MiB retired trajectories,
32 MiB repeated-control trajectories, 2 MiB probation and the original 32 MiB drive
cache. Four workers can each retain these caches; Python caches remain 64/16 MiB
shared per process. Container overhead, live integration buffers and retained
protocol evidence are additional. Worker-local counters and payload snapshots are
in COSTS.json; payload bytes are not RSS or peak-cache measurements. Scheduling can
change cache hits and CPU cost. The measured process RSS above captures the increased
memory footprint. No resource-rule amendment is made.

## Expected quiet-machine wall time — estimate only

For planning, use the mean normal-path CPU cost of the two smoke schedules and the
normal reverse-development CPU cost. An illustrative effective compute parallelism
of 2.5 yields CPU/2.5 seconds per world; a broad planning band uses CPU/4 to CPU/1.75.
A three-grid scope with ideal costs 1:2:4 has only 7/4 speedup, while independent
fork batches can fill four workers. Serial diagnostics/coordinator work, unequal
core speeds, cache misses, thermal state and scheduling can reduce those gains.
These assumptions have no quiet-machine calibration; the band is not a guaranteed
bound or a confidence interval. Serialization is outside this world-time estimate.

| World | Normal CPU basis s | Estimated quiet world wall s | Illustrative planning band s |
|---|---:|---:|---:|
| smoke_0 | 759.985 | 304 | 190–434 |
| smoke_1 | 332.324 | 133 | 83–190 |
| development_0 | 409.924 | 164 | 102–234 |

Claude will schedule the official quiet-machine measurement with the same source,
build and declared two-world budget and no concurrent heavy jobs. The registered
runtime gate has not been evaluated for this extension in this report. The estimate
and noisy observations confer no readiness or acceptance result.

## Preservation and delivery

New implementation/test files: geomind/c6_option_b_parallel.py and
tests/test_c6_option_b_parallel.py. Edits are confined to the prior option-B backend,
checker, comparator and test file. All other additions are this report and new
parallel evidence/delivery files under evidence/c6_option_b/. No C0–C5 frozen file,
original R4 source, committed receipt, STATUS.json, final entropy, R007 registration,
mutation probe, recorded panel or milestone status is changed. Every run verifies
the audited 25-file RRG source pin and both native build identities. Development
world 1 remains outside this comparison scope, as in the preceding port.

PRESERVATION_CHECKS.json records the baseline hash comparison and any independently
changed unrelated paths. Workspace .git is read-only; delivery uses a temporary
checkout, normal pre-commit/commit-msg hooks and Assisted-by: Codex:GPT-6 trailers.
The verified bundle and integration instructions are recorded in PARALLEL_DELIVERY.md.

| Yes/no stop condition | Action | Responsible role |
|---|---|---|
| Source/build identity mismatch? | Stop before loading. | Implementer |
| Exact array, digest, decision or whole-world comparison differs? | Fix the defect before delivery. | Implementer |
| More than two world processes or four compute workers per world? | Stop and correct the budget. | Implementer |
| Official quiet-machine measurement absent? | Leave runtime readiness pending. | Owner |
| Parallel extension independently reviewed? | Record the separate engineering review. | Reviewer |
