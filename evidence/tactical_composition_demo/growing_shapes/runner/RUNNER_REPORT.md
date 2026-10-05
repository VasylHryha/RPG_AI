READY

Engineering implementation of DESIGN_0H revision 5.1 (af3e7dd), under decision
0028 item 17. Implementer: Codex:GPT-6. This delivery is ready for Claude's
independent review. READY does not close that review or authorize section 10.
Only `growing_shapes/medium/` and this new `runner/` folder were changed.
Frozen geomind sources are read-only imports; unrelated workspace work is preserved.

Built:

- Sections 2–5: continuous integer world clock and carrier, no episode reset;
  five full driven RK4 substeps; task-specific logical slots, seeded physical-site
  permutations and legal actions; append-first indexed histories; rate/gain
  adaptation and the sole reward-arm gain term with carried baseline/eligibility;
  D1/D3/B1 timers, protection, strict reach, offset coverage, spiral placement,
  monotone IDs, undirected pair cost, rejections and event logs.
- Section 6: 601 endpoint frames including t=0; whole-window cohorts checked
  against immutable birth steps; missing/nonfinite histories are INVALID. The
  frozen C4 component, window, lock, kick, membership/pattern and criterion
  functions are imported, with the exact scaled thresholds. Full check-time
  native state, coefficients, clock, histories and adapter timers are preserved.
  Recovery replays 600 actual future drive bindings in two isolated full-population
  branches with adaptation, growth and reward off; entrants exert forces but are
  excluded from membership comparisons. All three Jaccards, pattern error,
  relaxation times/censor flags and admission/check times are logged. The wrapped
  increment alias warning blocks snapshots and does not certify absence of aliasing.
- Sections 7–9: templates store persistent-id-ordered members, phase relative to
  the continuous carrier, rates/gains and the binding rule/constants version.
  Canonical finite JSON uses sorted keys and float repr; SHA256 is the type id.
  Evaluation extracts an isolated identity-pose group, makes a fresh copy for
  each validation episode 0–127, applies that episode's seeded binding, and scores
  empty-readout abstention. Copy instance IDs are monotone. Reference/random
  validation episodes 0–255 are paired and frozen before training; all four tasks
  pass the specified mean/3-SE/positive-denominator usability rule. Competence is
  unclipped; only the episodic reward is clipped.
- Sections 10–11: dormant eight-seed/2000-episode arm orchestration, exact filtered
  20-episode rotation, bounded qualification schedule, largest-three snapshot cap,
  first-20 evaluator cap, per-group hash suppression, exposure/accounting ledgers,
  G0 random-control FIFO/retries/redraw/terminal drops, final whole-medium copies,
  G0/G0'/G1/G1c/G5 read-outs with INVALID-first ordering. Interrupted execution
  preserves partial reports, final templates and pending qualification state,
  yields INVALID and stops further seeds. No section-10 execution entry is exposed
  by the CLI; it permits only a capped engineering smoke.

Tests and smoke:

- 175 distinct contracts passed: 70 unchanged legacy engine tests, 45 medium
  follow-up tests, and 60 runner tests. C4 stored reference parity remains 1e-9.
- The first combined `-q -x` run stopped at one overly exact PLV assertion after
  89 passes (1 versus 0.9999999999999998). Its log/receipt are retained separately.
  After numerical assertion fixes, both new files passed: 102 tests in 5.59 s.
- Final audit tightened cohort corruption checks and preserved final/partial
  states. The affected runner file then passed 58 tests in 5.31 s; two additional
  interruption/pending-state contracts passed in 0.57 s. Passing unchanged legacy
  and medium checks were reused. Tests were run after each complete necessary
  correction batch, never while code was being edited.
- Exactly one integration smoke: dev medium seed 105051, eight episodes, 1280
  world steps and 128 s on the continuous clock. It completed without failure,
  with five births, six growth checks and one 601-frame qualification check.
  That check produced no qualifying candidate: recovery simulated time and
  evaluator episodes were both zero. Synthetic tests separately exercised the
  complete paired 60-second replay with an entrant and copy/evaluator paths.
  Under the fixed 20-episode rotation this short smoke exercises perceive only;
  the other bindings/actions have synthetic contracts.
- Measured smoke stages: training 35.176 s, qualification 0.533 s, recovery
  completion bookkeeping 0.00025 s, evaluation 0. All smoke data are explicitly
  engineering-only, not development evidence. These times are not a cost projection.
- The smoke preceded the final report/corruption-guard additions. Numerical
  integration/adaptation/growth/replay behavior did not change. Its saved cohort
  equals the tightened birth-step cohort and every required frame exists. The
  receipt distinguishes source hashes at smoke execution from final source hashes;
  the smoke was not repeated or relabelled as final-source development evidence.

Artifacts: `CHECKS.json` records final identities, test evidence and smoke source
identity/reuse bounds. `SMOKE.json` preserves frozen validation raw scores, all
smoke events, realized assignments, drives and qualification check-time state.
`TEST_ATTEMPT_1.txt`/`CHECKS_ATTEMPT_1.json` preserve the failed attempt;
`TEST_LOG.txt`, `TEST_RUNNER_FINAL.txt`, `TEST_INTERRUPTION_FINAL.txt` preserve
passing batches. `BUILD_LOG.txt` identifies the explicit native build.
Historical medium receipts were not edited.

Questions: none raised. No protocol constant, threshold or reset rule was chosen
in response to results. Claude must review the medium follow-up and the runner.
The owner's separate go-ahead is still required for the 200-episode projection
and section-10 development. No judging entropy, recorded run, development
read-out, efficiency claim, scientific acceptance or milestone status change
occurred. Driven snapshots do not establish autonomy/closure; G5 is a numerical
copy-covariance check. H-BG, H-PS and H-RBG remain NOT_TESTED.

Delivery: workspace .git is read-only. See `WORKSPACE_DELIVERY.md` for the scoped
commits, verified bundle and import command. Do not repeat valid unchanged checks;
Claude reviews and integrates the delivery, then the owner decides the next gate.
