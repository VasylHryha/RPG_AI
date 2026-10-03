# Preparation validation

No pilot inputs, native build, development run, mutation probe or panel were
started by the harness validation. Existing project tests ran once before
synthetic harness checks. All final harness edits precede the final checks.

1. `.venv/bin/python -m pytest -q -x tests evidence/c6_dev_pilot/r4_sensitivity/test_harness.py`
   — 579 existing tests passed; the first synthetic supervisor test failed
   because the sandbox denied process supervision. Total: 302.24 s.
2. A targeted harness run with process supervision enabled passed five tests,
   then exposed macOS EPERM for a group whose worker had already exited.
   Total: 1.83 s. No scientific sampling.
3. After the final batch, `.venv/bin/python -m pytest -q -x evidence/c6_dev_pilot/r4_sensitivity/test_harness.py`
   with process supervision enabled — **13 passed in 7.52 s**.

Final checks exercise successful ordering/accounting, global wall, arm wall,
aggregate CPU and RSS cancellation, queue discard, failed-worker stop, atomic
JSON replacement, partial-pair missingness, refusal to load a missing native
artifact, all dependency identities, owned descendant termination with an
unrelated process surviving, asymmetric shutdown and refusal to reuse a run
directory. Only synthetic subprocesses are used. There is no rehearsal panel
or population trial. Existing project tests are not repeated after changes
confined to this scratch harness.

Repairs before commit: skip already-reaped workers during grace polling;
pre-reap exited workers; handle a vanished/zombie-only macOS process group
without suppressing failures on a live group; include supervisor subprocess
CPU via RUSAGE_CHILDREN; check paired material/probe equality; record setup
cost and set failed workers INCOMPLETE even after late guard failure.

The real execution requires the same OS process inspection/signaling access;
it will remain bounded by the committed supervisor caps.
