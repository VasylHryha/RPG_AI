READY

Local engineering recheck of the 0h pass merged at bc00869, against unchanged
DESIGN_0H revision 5.1 (SHA256
39a630c3f4d440a6634538121773253443dcb15e8166406f36cde3727c119925).
This is readiness of the verified implementation on this build, not section-10
cost acceptance, scientific qualification, cross-machine certification or owner
execution approval. No section-10 run, 200-episode projection execution,
judging seed, recorded run or real evaluator/validation panel was performed.
The cost projection below is algebra applied to dev-only measured rates.
Independent Claude review of these changes remains pending; its prior reviews
cover the earlier implementation, not this revision.

## Findings and fixes

| Severity | Finding | Resolution |
|---|---|---|
| High | A birth occurs after the appended endpoint. At a later qualification check, the age-only cohort rule could select a newborn absent from the first of its 601 frames, incorrectly invalidating a valid run. | Exclude that specific left-boundary entrant. Initialized members recorded at t=0 remain eligible. Any unexplained missing frame for an older cohort member still causes INVALID. Test both inclusion and exclusion at the exact boundary. This implements the complete endpoint-window interpretation of sections 4/6; the drafter should make that ordering explicit in future design prose. |
| High | The loader checked source text and the orchestration binary but not the exact linked dependency binaries or a resident image after an in-process rebuild. | Link the existing medium and world libraries directly, pin their binary identities and Python ABI wrappers, check orchestration ABI 3/structure sizes and NumPy 2.0.2, and reserve image digests across all supported loaders. Changed resident images require a fresh process. A failed performance build removes its ready manifest before dependency builds. |
| High | ctypes releases the GIL. Batch-only locks did not protect ordinary reads, mutations, saves or close calls in either acquisition order. | Cooperating leases cover public medium/world/policy ABI operations. Overlapping shared-handle operations fail before an unsafe native call; distinct handles remain independent. Same-thread packing inside a batch uses reentrant leases. Thread tests cover both acquisition orders, close/read refusal and byte-identical independent-thread continuations. Private raw pointers/CDLL calls are outside this ownership API. |
| High | Accumulated adaptation/drive logs, repeated complete check-state events and copies of all Python events caused horizon-dependent RAM growth. births_at scanned the entire event log at every control growth check. | Add lossless ordered JSONL audit storage with exclusive file creation and SHA256 receipts; require audit_root before the dormant section-10 driver constructs runs. Cache births by the integer growth index. Save qualification clones without Python events; frozen recovery clones retain only the last external frame while preserving the complete native state. Reports scan flags without materializing all late events. |
| Medium | Recovery remained in Python. A first native attempt that returned complete JSON frames was slower than the reference (N=4: 0.087 -> 0.411 s in that trial). | Replace recovery transfer with a numeric [step, element, x/y/phase] buffer: two 600-step native futures per candidate, no Python RK4 calls. Batch the unchanged NumPy centering/RMS estimators; preserve the first strict 1/e crossing, censor flags, frozen C4 membership criteria and exposure ledger. Complete endpoint/internal-state parity and 3/12/64-member estimator contracts pass. |
| Medium | Evaluator copies integrated and decoded 160 steps through Python. | Execute each disposable frozen copy's whole episode in one native call. Preserve five substeps and internal endpoint observations, fresh-copy construction, both carrier offsets, scoring, instance order and panel identity. The 128-copy panel loop and copy construction still belong to Python; no actual panel was run. |
| Medium | Unnamed doubles in decoded snapshots let the generic numeric tolerance cover opaque clocks, birth times and native track metadata. | Add exact comparison of native configuration, clocks, IDs, lifetime/track metadata, fixed drive geometry/rates and event times. Negative contracts reject changes of 1e-12. Recheck the existing raw trajectories with this stricter comparator; no simulation repeated. |
| Medium | The original eight-episode timing and the Claude review's roughly five-hour figure describe training at a small perceive-only medium; neither includes full recovery/evaluation or density effects. | Report all task cases, per-stage profiles and conditional costs. Also correct the estimator's population cap: at N=24 there can be at most 8 disjoint candidates of minimum size 3, not the global N=64 cap of 21. |

The endpoint sensor-statistic cache uses fixed storage for the same immutable
window. It reduces repeated sensor reductions without changing arithmetic,
thresholds or sampling. Its measured task timings are mixed; it is not evidence
of a uniform speedup. No fast-math, reduced integration, threshold tuning or
alternative scientific estimator was introduced.

## Equivalence evidence

The original fixed bound was retained and declared before measuring in
PERF_RECHECK_COMPARISON.md: adapted floating state uses
abs(a-b) <= 1e-10 + 1e-10*abs(b). Decisions, clocks, timers, cohort/membership,
birth/death/protection/budget outcomes, action choices, criteria, taus and
censor flags are exact. Supplied-drive integration-only continuations require
byte-identical internal snapshots and endpoint values. Digests are verified
against their own canonical template content.

Six fixture cases use engineering medium seeds 105061-105066 and dev episode
seeds 0-7: all four task bindings with reward, plus perceive/choose G0 controls.
There are 36 episodes / 5,760 steps per path (reference, exact old batch source,
new native). A one-task usable-list fixture selects each task; this is not new
calibration. Existing frozen validation data is reused. Every endpoint, drive,
action, adaptation event, timer, coverage decision, final state, reward baseline,
qualification check state and admission event is compared. The 800-step
coincidence of episode/growth boundaries and the 600/1,200 check/replay boundaries
are included. Existing contracts also cover 1/37/200-step batches, hidden/inactive
sites, 79/80 eligibility, 99/100/101 warmup, reach and offset boundaries, cap/cost
vetoes, D1/protection, D3, newborns through the next batch, and control terminal
behavior. Different site bindings and episode drive histories remain carried.

PERF_RECHECK_STRICT_CHECKS.json records 5,066,034 numeric and 5,563,494 exact
comparisons of the full raw artifact. Maximum absolute difference:
2.220446049250313e-16; maximum permitted-bound fraction: 1.2896637333867704e-6.
The separate recovery/evaluator/density comparison also passed (maximum
1.1102230246251565e-16). Recovery integration and individual evaluator internal
snapshots/scores are byte-identical to their reference where required.

Long synthetic evidence is explicitly bounded: a continuous 32,000-step adapted
one-element driven trajectory (3,200 s), a 1,000-step driven trajectory starting
at the synthetic 31,900 s clock, and a full 320,000-step unforced one-element
continuation (32,000 s). All measured differences were zero. The final driven
checks repeat after the cache/future change; the unchanged full unforced check
is reused. This does not certify a full-horizon driven many-body trajectory.

Test accounting is not summed as if repeated checks were independent tests:
initial complete affected suite 387 passed / 124.37 s; cohort correction batch
192 passed / 62.90 s; completed numeric implementation batch 243 passed,
1 unchanged unforced test deselected / 216.25 s. Later narrow changes passed
21 ownership/loader/copy checks, 7 stricter-metadata/recovery checks, 2 storage
entry-point checks and 1 estimator-cap check. Commands, reasons and actual
subprocess timings are in the corresponding *_TEST_CHECKS.json and logs.
No unchanged long run was repeated routinely. The first timing attempt stopped
on the synthetic harness error "clock requires pristine medium"; its log is
retained separately. Clock setup was moved before insertion. Trial rates are
excluded from final PASS timing and not mixed with final rates.

## Measured speed and remaining Python work

One paired measurement per final fixture; no repetitions, timing interval or
isolated-host control. Initialization is outside Run training timing, and
qualification/recovery are subtracted by the existing rule. The old batch is
compiled from the pinned bc00869 source against the same current dependency
binaries/flags. Both native timings use the repaired common Python bookkeeping
and ownership guards. Absolute values should not be compared to the earlier
1.71 ms smoke as a controlled regression experiment.

| Task / control | Reference ms/step | Old batch ms/step | New native ms/step |
|---|---:|---:|---:|
| perceive | 58.866 | 5.480 | 5.349 |
| move | 37.398 | 3.115 | 2.037 |
| remember_static | 32.275 | 2.688 | 4.152 |
| choose | 53.877 | 5.535 | 4.941 |
| perceive G0 | 57.565 | 4.029 | 5.060 |
| choose G0 | 57.903 | 5.860 | 3.505 |

Aggregate: reference 292.425 s, old batch 26.654 s, new native 24.974 s for
5,760 steps: 50.768 -> 4.627 -> 4.336 ms/step. New versus old is about 6.3%
less training wall time in this sample. remember_static and perceive G0 were
slower; there is no universal task-level improvement claim.

| Stage / size | Reference seconds | Native seconds | Unit |
|---|---:|---:|---|
| recovery N=4 | 0.286531 | 0.021196 | one candidate, two full 60 s futures |
| recovery N=24 | 0.558434 | 0.091114 | same |
| recovery N=64 | 1.840724 | 0.402393 | same |
| evaluator N=3 | 0.034817 | 0.004152 | one fresh dev episode, mean of four tasks/two offsets |
| evaluator N=24 | 0.159853 | 0.077943 | same |
| evaluator N=64 | 0.355698 | 0.223381 | same |
| adapted supplied-drive N=24 | 8.904906 | 0.664721 | 200 steps; 3.324 native ms/step |
| adapted supplied-drive N=50 | 22.874263 | 2.379432 | 200 steps; 11.897 native ms/step |

Recovery's reference measurement also uses compact compute clones, so this table
does not inflate the backend gain by charging only the reference for discarded
audit copies. Qualification plus full-N input construction, compact-event
check-state clone and serialization/materialization took 0.103 / 0.334 / 0.718 s
at N=4/24/64 (the exact N=4 value is 0.103348 s).

Native-call wall share in the task cases is 68-79%; the remainder includes
Python history packing, JSON decoding/reconstruction, drive/signal accounting,
growth/qualification/admission handling and audit collection. Packing costs
0.097-0.554 s per case, decoding 0.152-0.693 s and history reconstruction
0.024-0.619 s; full breakdowns are retained in PERF_RECHECK_CHECKS.json.
These shares include scheduling and ctypes transfer; native-call time also
includes native record production/serialization, not just physics CPU time.
At N=24/50 in the supplied-drive fixtures, 91-92% is inside the native call.
Recovery's native-call share is 62/92/84% at N=4/24/64. Batched NumPy estimators,
kicks, clone/setup and frozen C4 criteria remain Python. Evaluator native-call
share is 37/87/91% at N=3/24/64; small copies are dominated by Python construction
and bookkeeping. Whole 128-copy panels are not one native call.

## Algebraic section-10 cost, never executed

There are 32 training runs x 2,000 x 160 = 10,240,000 world steps; only the
16 intact runs have 532 checks each = 8,512 checks. Evaluation at the cap is
16 x (20 x 2 + 1) x 4 x 128 plus 16 x 4 x 128 = 344,064 fresh episodes.
Recovery work depends on candidate count, not the three-admission cap: all
candidate groups are tested before ranking. Its maximum is floor(N/3).

Use T = 10,240,000*r_train + 8,512*q_N + 8,512*c*r_recovery,N + E*r_eval,N.
With the observed small-medium mix, r_train = 0.004335797 s/step, giving
12.333 training hours. The following independent component envelope uses the
maximum evaluation count, even where actual snapshot/candidate counts would
make it smaller; it is not a prediction of a mutually consistent realized run.

| Component / conditional fixture | N=24 hours | N=64 hours |
|---|---:|---:|
| qualification/check-state bookkeeping | 0.789 | 1.699 |
| recovery per mean candidate/check | 0.215 | 0.951 |
| evaluation at the cap | 7.449 | 21.349 |
| total with c=1, small-mix training | 20.787 | 36.332 |
| total with c=3, small-mix training | 21.218 | 38.235 |
| total at population candidate cap (8 / 21) | 22.295 | 55.361 |

Training at the supplied-drive N=24 rate would be 9.454 hours; at N=50 it is
33.841 hours before any qualification, recovery or evaluation. Thus the earlier
rough five-hour training estimate is not a full-cost guarantee, and the 24-hour
reporting line is a real risk. PERF_RECHECK_PROJECTION.json is the authoritative
corrected algebra; it supersedes only the N=24 candidate-cap part of the
initial measurement receipt's projection field. Measured rates are unchanged.

These are conditional serial compute estimates, not runtime bounds. Synthetic
geometry/cohort sizes, group sizes, candidate count, retained native diagnostic
history, disk throughput, duplicate snapshots and host load differ in real runs.
N=64 fixtures stress the cap; they do not establish a typical legal budgeted
population. No 200-episode projection was used. Parallel seed execution was
not implemented or timed: the dormant driver preserves sequential paired-seed
and arm/stop behavior. Distinct-handle concurrency is tested, but no linear
wall-time scaling or new wall-clock guarantee is asserted.

## Memory, delivery and remaining risks

External frame history remains bounded at 601 endpoints and internal history
at 101. One maximum ABI history pack is 21,549,456 bytes (about 20.6 MiB);
a future trajectory is at most 921,600 bytes per branch. Frozen compute clones
avoid the 601-frame Python history copy and all Python audit events. Python
training events, drives and repeated check-state records stream to disk for the
dormant full-run entry point; reports carry content-addressed file receipts.
All ledger files must accompany a transported report. The small Run/smoke API
can still select an in-memory audit. Model-state scalar accounting in report()
is not total RAM accounting. Templates, instance metadata, bounded pending
futures and birth indices remain in RAM. Native ADD/REMOVE diagnostic events
still grow with turnover (at most 6,448 under the protocol birth bounds per run);
clone/serialization cost late in a run was not measured at that event count.
Disk volume/throughput and process RSS over a complete driven horizon remain
unmeasured. JSONL flushes preserve completed boundaries, not power-loss durability
or an authorized resume path. Reusing an existing ledger path is refused.

Runtime failures after a native step are not transactional across medium/world
and Python audit reconstruction. They invalidate the run and prohibit native
retry; raw native state can still be inspected. The full driver reports INVALID
and retains partial receipts. No fallback silently resumes on different code.
Fresh processes are required after library replacement. All build products are
local, ignored and rebuilt explicitly; dependency paths make copied binaries
unsuitable as portable delivery artifacts. Compiler/OS/libm/NumPy dispatch can
change boundary rounding across machines. Rebuild and requalify with the same
fixed numeric bound and exact discrete rules on any new platform; this pass
certifies only Apple clang 21.0.0, macOS 26.6.2 arm64, NumPy 2.0.2 and the pinned
binaries. A driven many-body 32,000 s equivalence claim is still unsupported.

Clear follow-up performance candidates are binary training-record transfer,
persistent native history with explicit growth/synthetic-edit invalidation,
copy construction, native RHS/neighbour costs at N=50, and measured isolated
seed workers. They need separate equivalence/profiling; none is presented as a
proven additional gain here. The current improvement is substantial recovery
and evaluator acceleration plus bounded audit storage, not a claim of a globally
optimal implementation.

Authoritative artifacts: PERF_RECHECK_CHECKS.json (timings and build identities),
PERF_RECHECK_EQUIVALENCE.json.gz (all three full trajectories),
PERF_RECHECK_STRICT_CHECKS.json, PERF_RECHECK_PROJECTION.json,
PERF_RECHECK_LONG_INITIAL.json / PERF_RECHECK_LONG_FINAL.json, and the test,
build and attempt logs. The measurement source closure and later comparator,
storage and algebra corrections are identified separately in their receipts.
Only growing_shapes files are delivered. Workspace .git is read-only; a scoped,
hook-verified commit and transport bundle are provided in the delivery note.
