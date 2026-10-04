# Typed core checkpoint, 2026-10-04

**CORE_CHECKPOINT_PASSED; FULL_ENGINE_NOT_READY.** Exploratory engineering under
decision 0028 and the owner-approved performance plan revision 2. No AI
experiment, scientific panel, ladder remeasurement or milestone acceptance.

Subsequent [adversarial recheck](../native_checkpoint_review_r1/RECHECK.md):
**CHANGES_REQUIRED**. The checks and measurements below remain historical facts,
but did not cover numeric extremes, live-grid spawning, hostile timing/cache
admission or enough active fork state. The layout decision remains provisional.
The original source/build inputs and compressed binary are retained by hash in
`source_archive/`. Repaired source requires fresh validation.

The typed engine supports sandbox mirror combat with two explicit novice
profiles, ordinary melee, direct/homing shots and artillery shells. Other
features return explicit errors. Immutable configuration is shared; mutable
world state uses typed vectors and generation-checked local handles. Native
simulation headers do not depend on the dynamic JS runtime; JSON decoding and
encoding remain at the host boundary.

## Checks

The announced blocking stage-B test checkpoint ran the four focused modules
`test_native_core.py`, `test_performance_admission.py`, `test_result_cache.py`
and `test_native_runtime.py`: **28 passed in 18.89 seconds**. This result was
captured from execution session 23992; it is not the repository-wide suite.
The legacy runtime checks do not establish complete legacy fight equivalence.

The native C++ contract executable checks 1,536 randomized blocker queries
against an independent long-double scan, 64 separation worlds against an
independent all-pair oracle, the two known radius-16 counterexamples, coordinate
alias prevention, moved/dead blockers, RNG conversion, stale handles, retained
projectile sources, 1,000 spawn/death cycles, deterministic replay, parent
isolation, nested branch leases and branch-buffer reuse. AddressSanitizer and
UndefinedBehaviorSanitizer execution passed without diagnostics; see
[sanitizer_receipt.json](sanitizer_receipt.json).

## Bounded profile and layout decision

Eight fresh full-army novice mirror fights, seeds 2026100400–2026100407, ran
with 20-second duration and default 100 total units. Their inputs were written
before timing. Fresh process order was JS/native/native/JS, with comparison
caching bypassed. Each engine reproduced its summaries across both fresh runs;
the two engines' summaries were identical for all eight inputs.

| Measure | JS | Native |
|---|---:|---:|
| Completed fights per process | 8 | 8 |
| Outer steps | 4,800 | 4,800 |
| Unit actions | 335,946 | 335,946 |
| Projectile updates | 49,655 | 49,655 |
| Branch steps / forks | 0 / 0 | 0 / 0 |
| Cache hits | 0 | 0 |

The ratio of summed JS wall times to summed native wall times was **15.6309x**.
This is diagnostic evidence for execution cost in this slice, not the original
50-fight or elite performance gate. The separately instrumented JS work audit
reproduced the unchanged host's outputs and exactly matched the native counters.
See [benchmark.json](core_slice_timing/benchmark.json), its raw summary files,
and [core_slice_work_receipt.json](core_slice_work_receipt.json).

The record/column comparison used identical geometry operations and observable
sums, 40,000 iterations per sample, and four cycles of records/columns/columns/
records. All 16 samples are retained. Summed record time divided by summed
column time was **1.03914**, a roughly 4% difference. Typed records are retained
as the current candidate: this kernel does not show a substantial column-layout
advantage, and contiguous records support complete branch copies. This does not
prove an optimal full-engine layout; revisit after the full mutable branch state
and matched-state probes exist. The copy probe includes rebuilding derived
indexes. See [layout_balanced_receipt.json](layout_balanced_receipt.json).

The earlier short ordered layout sample is retained as preliminary evidence in
`layout_receipt.json` and superseded for the decision by the balanced sample.
Both layout and combat runs were on a contended host, with load averages around
29–54. Neither can qualify final performance on this machine state.

## Remaining work

Stages C–E still require both rules, all abilities and effects, players/custom
kinds, every spawning mode, skills, formations, commanders, combos, network
inference, elite look-ahead and artillery rollouts. The full clone ledger and
branch-work telemetry are pending. The core lease tests are not execution of
elite search. Stage F requires complete fresh coverage, trace invariants,
matched-state cost probes and the original 50 plus all three supplemental groups
at least 3x faster, followed by independent Claude review before experiment use.

The original estimate remains provisional: 3–5 hours combat, 4–6 hours tactics,
3–5 hours branching AI, and 2–4 hours final validation plus independent review.
The core's speed does not reduce those feature and correctness obligations.
