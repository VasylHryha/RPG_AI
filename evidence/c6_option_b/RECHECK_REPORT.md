NOT_READY

C6 option B adversarial engineering recheck, 2026-10-05. Implementer/rechecker: Codex, GPT-6. Scope: decision 0029 and the owner's recheck request. This is a same-family self-audit and repair, not independent acceptance. The bounded checks pass, but the changed implementation still needs full-world zero-tolerance checks, quiet-machine timing, and Claude review. C6 remains BLOCKED / R006 STOP; STATUS.json is unchanged.

**Findings and repairs**

| ID | Severity | Finding | Repair / disposition |
|---|---|---|---|
| F1 | High | Native cache clearing left the hidden drive cache alive. Its numeric-equality key merged positive and negative zero. A supposedly cold run was not fully cold, and the key did not enforce bitwise identity. | Drive cache now has explicit thread-local storage, byte accounting, bitwise keys and clearing. Both coordinator and pool initializers reset all caches. Signed-zero and empty-after-clear contracts pass. No prior measured numerical failure is asserted from this latent key defect. |
| F2 | High | Oversized trajectory entries were allocated and copied before admission was rejected; drive admission evicted only after allocating. Retention limits were not transient allocation limits. Tiny entries could also accumulate unbounded list-node overhead. | Reject oversized trajectories before allocation/copy; evict retained payload before replacement allocation; cap each material-cache list at 128 entries. Reserve each complete key once and account vector capacities. Drive entries remain capped at four. Configurable, downward-only per-thread limits permit zero-cache and tiny-budget contracts. These are cache bounds, not an RSS ceiling. |
| F3 | High | Native RHS allocation exceptions could cross the C boundary. Dimension products/output offsets could overflow signed integers. Separately, material-cache accounting advanced before list insertion, so an allocation failure could corrupt it. | Catch native RHS exceptions, validate dimensions/clocks/null pointers, use size_t output offsets, guard detector dimensions/pointers, and update accounting only after successful insertion. A compiled synthetic contract injects an actual list-node allocation failure without exhausting RAM, then verifies clean accounting and successful subsequent admission. |
| F4 | High | Reference loading called a helper with an implicit rebuild path and did not bind compiler flags. Option-B build publication compiled mutable source paths and did not serialize builders. Loader reuse was not explicitly pinned against later rebuilds. | Explicit checked ctypes loading for both libraries; reference flags verified; loaded identities pinned for the process, with restart required on change. Builders serialize and compile immutable snapshots, reject source drift, and record compiler version, OS and architecture. Pre/post checks reject mixed identities. No reference rebuild occurred. Concurrent rebuilding of an active experiment remains prohibited. |
| F5 | Medium | Module selection depended on an unenforced isolated-context convention. Nested backend/parallel contexts could restore functions in the wrong order. | Non-reentrant selection guards; parallel selection requires an active native backend. Restoration and pool draining are protected by finally blocks. Invalid nesting and worker exceptions are covered. Direct unsupervised calls into the original modules during selection remain unsupported. |
| F6 | Medium | Concurrent equal Python cache misses repeated integrations/channels. Native material keys also included actual-medium state even though the cached OFF material/carrier path cannot read it. | One computation per in-flight Python key, with shared immutable result and exception propagation. Remove only actual-medium initial values from the OFF-only material key; recompute actual medium live on every hit. Changed-actual-medium inputs compare bit for bit against the original. No cohort, carrier, mask, clock, grid, law parameter or geometry input was removed. |
| F7 | Medium | All 24 causal grid jobs were submitted together and retained complete outgoing results until ordered collection. Submission favored cheap coarse grids; unequal work could leave workers idle near a batch's end. | At most four submitted jobs, costly jobs first in the forward schedule, reverse ordering as an adversarial control. Consume results as they complete, discard outgoing arrays after their per-grid reduction, and release full flows after each original three-grid diagnostic. Owners/sums remain independent by grid; checks and diagnostics retain their original order. Full-flow diagnostic buffers and sampled evidence still consume memory. |
| F8 | Medium | Build/helper/environment identities were not carried together in each execution record; ignored CLI combinations and failures could leave ambiguous output directories. | START/COSTS bind both builds, Python/NumPy, helper hashes, fixture entropy and cache limits. Reject incompatible audit/schedule selections; record runtime failures explicitly. An OS kill or inability to allocate failure metadata still needs an external supervisor. |
| F9 | Medium | Prior statements about an exhausted exact speed ceiling, full coldness, complete ten-core utilization, and the only remaining resource-rule option exceeded the evidence. The old world comparisons and planning estimate concern earlier code. | Corrected below; historical reports/review remain byte-for-byte unchanged. The new source/binary requires new world evidence. No optimality, universal memory bound, quiet-machine speedup, or acceptance claim is made. |

**Exactness and schedule argument**

The scalar evaluator text is identical to the preceding implementation. RK expressions and stage-time expressions are identical; only output pointer multiplication uses size_t. Detection arithmetic and traversal are unchanged. Flags remain `-O2 -fno-fast-math -ffp-contract=off`. See `recheck/UNCHANGED_ARITHMETIC.json`.

The OFF material key contains dimensions, start time, dt, steps, sample stride, complete material x/theta/carrier state, site q/omega/psi/adjacency, rates, masks, modes, origins and all nine parameters. It compares complete byte strings, without a digest collision path. Actual-medium initial state is intentionally absent: the cached outputs cannot read it; actual-medium outputs are recomputed from that state. The cache is entered only for one cohort with no positive emission marker. Active/multi-cohort paths remain live. Perturbations are represented by their resulting full physical inputs. Metadata IDs are not numerical kernel inputs. Drive keys contain ns/steps/start/dt/amplitude/psi and compare floating bytes, including signed zero. Different dt grids cannot share trajectories.

Each native cache belongs to one OS thread. Python caches are protected by the original cache lock; in-flight requests share one computation, results are immutable to supported callers, and a caller keeps its reference across eviction. No worker mutates another task's owner. Per-grid sums, hashes and sampled rows keep their original block order; three-grid error reductions keep coarse-to-fine order; final checks keep request order. Completion order changes independent-grid execution, never an arithmetic reduction. Exceptions are selected by lowest original job index after bounded work drains. This is the reason arbitrary supported scheduling cannot change successful results; finite schedule tests substantiate it rather than proving every possible schedule or hostile external mutation.

**Allowed-input evidence**

Final affected suite: **78 passed in 7.46 seconds**, command and actual wall time (7.75 s) in `recheck/TEST_COMMAND.json`, log/XML beside it. This covers all modes/grids, stored R006 detection windows, physical-key mutations, zero/tiny/default budgets, 100-iteration key churn, signed-zero/zero-field inputs, context restoration, single-computation success/failure/eviction, bounded submission and allocation-failure injection.

The first end-of-batch run passed 77 tests in 6.39 s. A subsequent static inspection found the allocation-accounting defect, triggering one concrete repair, its new regression contract and the final end-of-batch run. Earlier successful logs/builds/fixtures remain under `recheck/batch_1/`; their recorded original paths predate that archival move. They are not added to the final test count. No failed test attempts occurred in this recheck.

| Final execution | Full arrays audited directly against original | Stored comparison against each of two references |
|---|---|---|
| Sequential fixture | 159 calls / 17,372,682 float64 values, bit-identical | 254,920 numeric leaves, 51 Boolean leaves, zero changed digests |
| Forward parallel fixture | 159 calls / 17,372,682 float64 values, bit-identical | Same counts, zero changed digests |
| Reverse parallel fixture | 159 calls / 17,372,682 float64 values, bit-identical | Same counts, zero changed digests |

All six stored comparisons pass with tolerance zero and float-bit/type checking. References are the unchanged `evidence/c6_r006_post_stop_checks/optimized.json` and `evidence/c6_option_b/fixture_v3_native/world.json.gz`. Comparison JSONs bind both compressed/input hashes. The three executions reuse the same reserved 882901/552 fixture, not independent worlds.

The synthetic driver has no world/panel entrypoint. It compares **342 calls / 1,357,236 float64 values**, including four workers each churning 60 clock/drive keys with small budgets. All values match the original bit for bit; maximum error is zero. Synthetic peak RSS was 33,177,600 bytes. See `recheck/synthetic/CHECKS.json`. Fixture RSS was 196,149,248 / 267,550,720 / 266,600,448 bytes (sequential/forward/reverse), including serialization and reference auditing. None is a full-world memory measurement.

Only the two affected option-B test files were run. No full suite, full C6 world, final entropy, registered panel, mutation probe, C0 run or milestone update ran. Source-pin validation passed in the fixture and synthetic harnesses. A read-only RAM/CPU sysctl query was sandbox-refused; no physical-memory capacity or process attribution is inferred.

**Speed and memory limits**

Short unit measurements on 40 repeated six-member, 100-step integrations:

| Mode | Wall seconds | Process CPU seconds |
|---|---:|---:|
| Original reference | 0.033545 | 0.032307 |
| Option B, all caches deliberately disabled | 0.046347 | 0.046290 |
| Option B, warmed default caches | 0.008830 | 0.008831 |

Reference audit/comparison is outside these timing intervals; array creation/validation remains inside. All-cache-disabled also removes drive reuse, so its slowdown is not evidence of normal cold-world regression. Durations are very short and machine load was roughly 20–25; these are unit observations, not a hardware or whole-world speedup claim. Fixture times include reference audit and likewise do not establish performance readiness.

The remaining dominant work is the unchanged all-pairs material RHS and independent live forks. Exact improvements implemented here remove duplicate misses, unnecessary physical-key copies and delayed result retention, and improve scheduling. We did not delete forks or reuse integrations across different dt/start expressions. Fine-grid sampling is not coarse-grid arithmetic; even apparently common intermediate times can use differently rounded stage expressions. Only complete same-grid keys permit reuse. Recovery/causal treatment arms retain every original perturbation and measurement.

Remaining plausible work includes profiling fixed-origin Gaussian factors in the no-geometry-to-mode arm for exact scalar memoization, reducing owner validation/packing/copies at a new validated API boundary, and measuring whether cross-worker native-cache sharing would save more integrations than synchronization/key transfer costs. These are opportunities, not demonstrated speed defects or implemented gains. SHA-based inherited Python emission keys retain the existing collision assumption; native trajectory keys use full bytes. No evidence establishes that every exact saving is exhausted or that a resource-rule change is the sole next option.

Budget stays two world processes, each one coordinator plus four compute workers: ten declared threads. This permits eight simultaneous native compute workers, not ten continuously busy cores. Ordinary three-grid scopes expose only three compute tasks per world; fork batches expose more. GIL-held Python work, unequal grid costs, heterogeneous cores and load can reduce utilization. The CLI constrains numerical helper teams to one before NumPy import; direct embedding must honor the same environment contract.

Retired/control/probation/drive caps remain 256/32/2/32 MiB per native thread (322 MiB), plus 64/16 MiB shared Python caches per process. Four pool threads can retain 1,288 MiB native payload; the coordinator can retain another 322 MiB if it integrates. Container overhead, live buffers, pending three-grid diagnostics, sampled protocol evidence, Python/NumPy memory and serialization are additional. Limits describe cache storage, not process RSS. Counter snapshots are current payload, not peaks. Entry caps and pre-admission eviction improve bounded retention; no safe budget for arbitrary RAM limits or arbitrarily long retained evidence is claimed. On allocation failure the operation fails explicitly rather than emitting a successful scientific result. New stats include drive bytes; deploy the identified Python/native pair together.

The historical ~304-second quiet-machine estimate is uncalibrated and for earlier code; it is not a readiness result. Sequential CPU exceeding 360 seconds does not by itself disqualify a parallel wall-clock run. Conversely, passing short fixtures or one early-stopping world cannot establish the cost of every possible later panel workload.

**Exactly queued full-world checks — NOT EXECUTED**

Wait for the timed 0g run and other heavy jobs to finish, then have the owner scheduler confirm quiet conditions. Verify this delivery's helper/source inventory, source pin and both library/BUILD identities; use fresh processes/output directories. At most two world processes and four pool workers each. No final entropy. `recheck/QUEUED_CHECKS.json` enumerates every exact argv, reference hash and comparison argv: **13 equivalence computations plus 4 normal timing computations**, with a new reference needed only for development world 1. Existing original references for smoke 0/1 and development 0 are reused.

The following is the complete queued equivalence batch. It is listed for later execution; it was not launched here:

```sh
export PYTHONPYCACHEPREFIX=/private/tmp/c6_option_b_recheck_later_pycache
check() { .venv/bin/python tools/c6_option_b_check.py "$@"; }
compare() { .venv/bin/python tools/c6_option_b_compare.py "$@"; }
q=evidence/c6_option_b/recheck_later
check --backend reference --entropy development --world 1 --output "$q/reference_development_1" || exit 1
for entropy in smoke development; do
  for world in 0 1; do
    check --backend native --audit --entropy "$entropy" --world "$world" --output "$q/${entropy}_${world}_sequential" || exit 1
    check --backend native --audit --parallel --entropy "$entropy" --world "$world" --output "$q/${entropy}_${world}_forward" || exit 1
    check --backend native --audit --parallel --schedule reverse --entropy "$entropy" --world "$world" --output "$q/${entropy}_${world}_reverse" || exit 1
    case "$entropy/$world" in
      smoke/0) reference=evidence/c6_option_b/reference_smoke_0/world.json.gz ;;
      smoke/1) reference=evidence/c6_option_b/reference_smoke_1/world.json.gz ;;
      development/0) reference=evidence/c6_option_b/profile_run/reference_world_000.json.gz ;;
      development/1) reference="$q/reference_development_1/world.json.gz" ;;
    esac
    for mode in sequential forward reverse; do
      compare --reference "$reference" --native "$q/${entropy}_${world}_${mode}/world.json.gz" --exact --output "$q/${entropy}_${world}_${mode}_EXACT.json" || exit 1
    done
  done
done
```

Next, official quiet-machine normal timing, without audit, using the same pinned build and helpers. Launch the two smoke worlds together from cold processes; wait for both, then launch the two development worlds together. Record start/end and periodic load, CPU, wall, RSS, cache counters, and separate serialization. Use the identical reference mapping above and `--exact` comparisons for all four timing outputs.

```sh
for entropy in smoke development; do
  check --backend native --parallel --entropy "$entropy" --world 0 --output "$q/quiet_${entropy}_0" & p0=$!
  check --backend native --parallel --entropy "$entropy" --world 1 --output "$q/quiet_${entropy}_1" & p1=$!
  failed=0
  wait "$p0" || failed=1
  wait "$p1" || failed=1
  [ "$failed" = 0 ] || exit 1
done
```

Exact comparisons for those four normal timing outputs:

```sh
compare --reference evidence/c6_option_b/reference_smoke_0/world.json.gz --native "$q/quiet_smoke_0/world.json.gz" --exact --output "$q/quiet_smoke_0_EXACT.json" || exit 1
compare --reference evidence/c6_option_b/reference_smoke_1/world.json.gz --native "$q/quiet_smoke_1/world.json.gz" --exact --output "$q/quiet_smoke_1_EXACT.json" || exit 1
compare --reference evidence/c6_option_b/profile_run/reference_world_000.json.gz --native "$q/quiet_development_0/world.json.gz" --exact --output "$q/quiet_development_0_EXACT.json" || exit 1
compare --reference "$q/reference_development_1/world.json.gz" --native "$q/quiet_development_1/world.json.gz" --exact --output "$q/quiet_development_1_EXACT.json" || exit 1
```

Evaluate `max(normal quiet world seconds) * 40 / 2 * 1.5 <= 10800`, hence every measured world at most 360 seconds. An exceedance leaves engineering runtime NOT_READY. A pass establishes this bounded timing result, not scientific qualification, a full-chain/population claim, panel cost for unobserved paths, owner approval of R007 or milestone acceptance. The new source must receive one Claude engineering review of the committed delivery after the queued evidence is available; the old review is baseline evidence only.

**Preservation, delivery and remaining gates**

`recheck/PRESERVATION_CHECKS.json` compares 6,786 tracked-file baseline hashes. Only owned option-B tracked paths changed; all unrelated working edits are preserved. Original R4 sources, C0–C5 freezes, committed receipts, old reports/review, source archive, STATUS.json and gate stamps are unchanged. The native scalar build is archived with its new BUILD record; the reference pair is copied unchanged. All task additions are option-B sources/tests/tools and new evidence.

Workspace .git is read-only by the session filesystem policy. Delivery therefore uses scoped commits in a temporary checkout, normal pre-commit/commit-msg hooks and `Assisted-by: Codex:GPT-6`. See `RECHECK_DELIVERY.md` and external `RECHECK_BUNDLE_VERIFIED.json` for the bundle, commit IDs, byte inventory and verified import. No original index/ref is written.

| Yes/no condition | Action | Responsible role |
|---|---|---|
| Source, helper or build identity mismatch? | Stop before loading; explicitly build/identify or restore the matching pair. | Implementer |
| Any exact array/digest/decision mismatch? | Repair before readiness; preserve failed evidence. | Implementer |
| World computation requested before shared timed work ends? | Keep it queued. | Implementer |
| More than two world processes or four compute workers per world? | Stop and restore the declared budget. | Implementer |
| Full-world comparisons or quiet timing missing? | Keep NOT_READY. | Owner |
| Quiet world exceeds 360 seconds? | Keep NOT_READY and decide the next engineering/resource step. | Owner |
| New independent Claude review missing? | Leave this repaired implementation unaccepted. | Reviewer |
