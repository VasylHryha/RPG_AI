Coverage pilot build-only delivery (Amendment 1), exploratory keys 0–4 only.

Run from /Users/new/RiderProjects/ai_RPG_test:

```sh
MV=evidence/tactical_composition_demo/growing_shapes_review_claude/rev711_diag/medium_variants
```

COVA and COVB are already built in kernel_builder/_worktrees/ at detached
fd2182681ee8ed7b7b3a0772d69de898a8aa17c2. Build receipts pin Python variants,
helpers, native/world source and binaries, harness, and Amendment 1. The native
screening image is the original b0b35a16… image in both arms. No project gate was
weakened: scratch stubs remain confined to the copied exploratory harness.
The new builder uses a project-local shared clone under _local/coverage_builder_repo
for worktree registration, so it never needs to write the primary checkout's .git.

If rebuilding on a clean checkout without these worktrees, run each command once:

```sh
.venv/bin/python "$MV/kernel_builder/build_coverage_kernels.py" COVA
.venv/bin/python "$MV/kernel_builder/build_coverage_kernels.py" COVB
```

Do not repatch/reset an existing worktree. Verify existing builds instead:

```sh
.venv/bin/python -c "import sys; sys.path.insert(0, '$MV'); from execute_coverage_plan import validate_build; validate_build('COVA'); validate_build('COVB'); print('Build identity PASS')"
```

The focused synthetic tests inspect actual scratch methods using fake graphs;
no native step, medium trajectory, F5 assay or real process listing executes:

```sh
.venv/bin/python -m pytest -q -x "$MV/test_coverage_pipeline.py" "$MV/test_service_telemetry.py"
```

Claude executes the scheduler, followed by the report writer, with no code edits:

```sh
.venv/bin/python "$MV/execute_coverage_plan.py"
.venv/bin/python "$MV/write_coverage_report.py"
```

The scheduler must independently see the process list. Permission errors stop
before any job. Its anchored alternatives use this absolute repository path:
Python executing absolute astelia_cpp/s4_*_v1 script paths, and astelia_native*
executables under this repository. It cannot match pgrep commands. Use absolute
script paths when launching concurrent 0g Python jobs; a process's relative
script path alone cannot establish its repository identity from pgrep output.

Exactly 20 on jobs and two off controls form one main phase (both empty/key-0
pairs are dispatched first). Max workers is min(10, reported logical CPUs).
The cap is 3600 seconds. It projects all remaining jobs, including controls,
using the maximum measured elapsed/CPU duration from the ten relevant historical
RD3 workers and any completed coverage workers, rounding waves by available
workers. Waiting for combat has a separate one-hour maximum. Execution uses
caffeinate and a common absolute deadline; each worker timeout uses that deadline.

**Current evidence projects above the cap.** The historical RD3 maximum is
1329.3264 seconds; 22 remaining jobs at 10 workers require three conservative
waves, or 3987.9791 seconds. Fewer CPUs increase this estimate. A fresh complete
schedule therefore stops before launching under the fixed 3600-second cap.
This is the spec's projection stop, not permission to increase the cap or reduce
the plan. Claude should report the stop to the owner/drafter. This delivery
implements the requested safeguards; it does not claim the earlier 45-minute
estimate is verified or that this complete plan currently fits the cap.

Resume is the same scheduler command. Identity-verified completed slots reuse
raw size/hash, code/build hashes and successful clone-isolation records. Any
started/incomplete slot is a stop, never rerun; report the preserved slot. Each
attempt keeps a unique RUN_TICKET_*.json. The exclusive SCHEDULER.lock prevents
two schedulers. An abnormal exit retains it; inspect the original process before
any manual lock disposition. Never launch run_coverage_pilot.py directly or edit
a ticket, marker, completion or build receipt to obtain a grant.

Raw files, markers and logs remain under _local/coverage/. Scheduler outputs are
new COVERAGE_PREFLIGHT.json and COVERAGE_RUN_SUMMARIES.json; report outputs are
new COVERAGE_COMPACT_SUMMARIES.json and COVERAGE_PILOT_REPORT.md. The report works
without pilots and renders NOT_RUN; a PARTIAL run retains valid completed metrics
and explicitly excludes bad/incomplete slots. Both integrity pairs must pass
before positive/regression readings can be issued. Missing runs never count as
failures. Prospective A7 candidacy does not authorize A7 or combining the arms.

Clock boundary: COVA initializes all eight clocks to zero, including seeded
roots. Once per completed integrate (.1 s) it reads physical-site service before
adapt/timers/growth. Idle service resets; inactive-unserved pauses; active-unserved
accumulates. No birth/removal updates the clocks. Clones copy them independently.
COVB inherits RD3's cap/cost-only resource-stop predicate: recycle_failed permits
later sites to try the changed graph; no eligible donor still returns cost.
B1 retries its existing admission, without a new B-path progress law.

Only B labels change in the observer. The restoring terminal and post-birth
restoring gap sample are excluded from non-repair B evidence and retained as
zero-duration restoration evidence. Initial candidate cost refusals are separate
from terminal-C evidence; a successful retry does not manufacture C. RD3's
historical B remains legacy_B because every intermediate birth boundary cannot
be reconstructed from retained world/growth samples. Historical coverage/assay
values and birth comparisons from COVERAGE_DIAGNOSTIC.json are reused unchanged.

No pilots or process listing were executed by Codex. Implementation review and
validation are in docs/reviews/tactical_0h_coverage_implementation_recheck_codex.md
and COVERAGE_DELIVERY_VERIFICATION.json. Existing A6w/A6x scripts, designs, plan,
receipts, summaries, and unrelated dirty work remain untouched.

Git delivery: the primary .git sandbox denied index.lock creation. The fallback
bundle is COVERAGE_PILOT_IMPLEMENTATION.bundle, based on the current delivery
HEAD recorded in COVERAGE_DELIVERY_VERIFICATION.json. It contains only the 15
explicit coverage-delivery paths. The isolated packaging checkout uses the
repository's .githooks for its commit; no hook bypass. To inspect/fetch it:

```sh
git bundle verify "$MV/COVERAGE_PILOT_IMPLEMENTATION.bundle"
git fetch "$MV/COVERAGE_PILOT_IMPLEMENTATION.bundle" coverage-pilot-codex-delivery
```

The owner can integrate the fetched commit after reviewing. Local scratch
worktrees and binaries already remain available in this shared workspace;
other machines rebuild them from the pinned inputs. The bundle itself contains
source, build identities, reviews, preservation and focused-test receipts, not
local raw/build products.
