READY

Engineering performance pass for decision 0028 item 17 and Claude runner-review
note 1. DESIGN_0H revision 5.1 is unchanged (SHA256
`39a630c3f4d440a6634538121773253443dcb15e8166406f36cde3727c119925`).
No protocol constant, threshold, rule, entropy domain or update order changed.
No section-10 development run, 200-episode projection, judging seed, evaluator
panel or scientific verdict was run or assigned. Independent Claude review of
this performance pass remains outstanding.

On the same eight-episode engineering smoke (medium seed **105051**, dev world
episode seeds 0–7, **1,280 world steps**), with the identical already-frozen
validation calibration from `SMOKE.json`:

| Path | Training seconds | ms/world step | Total episode wall seconds |
|---|---:|---:|---:|
| Python reference | 26.305713 | **20.551338** | 26.545975 |
| Native batch | 2.193319 | **1.713530** | 2.456812 |

**Training speed-up: 11.993567× (12.0× rounded).** Both timings include audit
record production, drive logging, Python history transfer, growth bookkeeping
and episode work. Qualification/recovery time is excluded using the existing
runner timing rule. Compilation, constructor initialization, comparison and
gzip artifact writing are outside training timing. One paired measurement in
the same process; reference then native, without a repeat or statistical timing
interval. These are measurements of this smoke, with its small medium and
perceive-only rotation block; there is no development cost extrapolation.

The native C++ library now consumes the bound observation, builds all eight
drives, runs the same five driven RK4 substeps, appends the endpoint first,
adapts rates and gains, updates D1/B1 timers and coverage, decodes the action,
and steps the existing world. It links the existing world binary rather than
recompiling world arithmetic under different optimization flags. Python receives
complete records at batch boundaries. Batches stop at episode boundaries or
the next 200-step growth boundary; that also contains every 600-step
qualification/recovery boundary. At the growth boundary, the world action is
deferred until Python finishes growth, qualification and admissions in their
original order. Reward stays at the episode endpoint. The smoke used **13 batch
calls**, with the protocol cap of 200 steps per call.

Growth/qualification, frozen C4 criterion functions, control queue, reward
baseline and evaluator code retain their existing implementation. Python's
timer method returns its already-computed coverage decisions for auditing,
avoiding extra statistic evaluations during timing. It evaluates each statistic
in the same order as before. Native frames/timers are reconstructed from the
authoritative Python state at each batch, so births, deaths, clones and reward
updates are visible to the next native call.

Comparison was declared first in `PERF_COMPARISON.md`, before compilation/test
or timing. RK4-only synthetic continuations have byte-identical complete native
snapshots and endpoint histories. Adapted floating state uses the fixed bound
`abs(a-b) <= 1e-10 + 1e-10*abs(b)`; events, membership, discrete decisions,
booleans, clocks and timers require exact agreement. Numeric tolerance was not
increased after a failure.

The smoke comparison passed **863,859 numeric and 796,218 exact comparisons**,
covering every event, action, timer, coverage decision and endpoint, complete
final state, and qualification check-time state including the native internal
history. The largest absolute numeric difference was **1.1102230246251565e-16**
(6.0842e-7 of the permitted bound). **Final and qualification check-time native
serialized snapshots are byte-identical.** The reference's events and drive
schedule also match the prior committed smoke. Both paths produced five B1
births, six growth checks, one qualification check, one recovery-complete event
and no admitted snapshot. Original smoke and evidence receipts are unchanged.

Synthetic contracts cover all four bindings (including native action decoding
and changing move observations), hidden memory, 1/37/200-step batch limits,
exact RK4 continuation, 99/100/101-frame warmup, 79/80 sample eligibility,
offset and strict-reach boundaries, tied salience, timer resets, B1 cap/cost
rejection, D1 protection/death, a qualified triangle and newborn exclusion at
check time, reward at episode endpoints, and control FIFO/terminal behavior.
Existing medium/world/runner contracts also passed, including D3 and the frozen
C4 fixture parity. All five affected test files were run together after the
completed fix batch: **360 passed in 90.62 s** (90.80 s subprocess wall time).
No successful final test or smoke run was repeated.

Two failed test attempts are retained separately. Attempt 1 stopped during
collection on a test-only relative import (`attempted relative import with no
known parent package`); no tests ran. Attempt 2 stopped after 289 passes when
the inclusive 0.5 phase-offset boundary reset B1 in Python but advanced B1 in
native. The fix reproduces the complex pairwise reduction order used by the
installed NumPy 2.0.2, including its aligned split, lane sum and remainder,
without changing the comparison bound or threshold. Arithmetic-order reference:
[NumPy 2.0.2 reduction source](https://github.com/numpy/numpy/blob/v2.0.2/numpy/_core/src/umath/loops_utils.h.src).
Only the final complete PASS batch is reported as final test evidence.

Evidence: `PERF_CHECKS.json` pins the declaration, all runner Python sources,
the timer adapter, unchanged design and the complete native build identities.
`PERF_SMOKE.json.gz` retains both reports, every endpoint/action/timer decision
and final states. `PERF_TEST_CHECKS.json`, `PERF_TEST_LOG.txt`,
`PERF_COMPARE_LOG.txt`, `PERF_BUILD_LOG.txt` and the two attempt receipts retain
commands and outcomes. Compiler: Apple clang 21.0.0; platform: macOS 26.6.2 arm64;
native flags include `-O3 -fno-fast-math -ffp-contract=off`.

Selection is explicit: `Run(..., backend='native')` or `backend='reference'`
(the compatibility default). `batch_size=1..200` provides smaller native
batches without changing protocol clocks or schedules. The bounded smoke CLI
also accepts `--backend native`. Build explicitly:

```sh
.venv/bin/python -m evidence.tactical_composition_demo.growing_shapes.runner.build_perf
```

This report's READY means the engineering equivalence/performance checks pass.
It grants no development execution, acceptance, source-recursion claim or owner
go-ahead. The later development driver remains dormant; its default selects
the Python reference and native selection is available through `Run`.
