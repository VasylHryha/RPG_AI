READY

S3 is engineering-ready under the owner-authorized revision-3 contract. Independent Claude review is outstanding;
this report does not accept an experiment or claim a tactical advantage. No tuning or recorded experiment was run.

The initial contract review stopped at five questions. The owner then explicitly asked Codex to handle/fix them.
Codex took ownership, committed the corrections in `4960eb9`, and completed the build/checks.
The exact equations, diagnostic rules, defaults and correction causes are in [DESIGN_0G.md](../DESIGN_0G.md),
sections 2-4, 7-8 and 11. The original stop report is retained in commit `3a91e2f`.

## What is built

- Named `resonator`, `morale` and `pushpull` controllers, with 10/10/2 bounded parameters and untuned midpoint defaults.
  State, pressure, targets and actions are prepared jointly once per snapshot; decide calls only read cached decisions.
- Per-unit cross-team and friendly-fire damage counters, artillery minimum range in observations, and fight-long
  per-side totals that retain dead/reclaimed units' damage. Historical damage fields retain their original semantics.
- Internal-state and raw-action failure reporting at the bridge, with hold/no target and an explicit
  `controller_failure` summary status. Failure counts are per unit per decision tick, with no double count for a
  simultaneously flagged/non-finite action. Branch-only failure counts stay separate from the played parent fight.
- The fixed-world [s3_runner.py](s3_runner.py), which accepts only the specified arm/params/seed/orientation/side/opponent/
  diagnostics fields. It fixes game rules, full sight, 150 seconds, dt=1/30, the 10/30/10 army and game-default body skills.
  Passthrough is refused there and in the general host unless `--test-controllers` is explicitly supplied.
- Output-only one-second group diagnostics, with a three-second prepared-state window, stable member IDs, exact
  empty/undefined handling and null phase quantities for non-phase arms. No diagnostic is fed back into a controller.
- Shared ally algebra, frozen-position RK4 state integration, a test-only coupled C4 reference adapter, and a
  captured-observation half-step replay. Production morale clipping occurs once at the physical-tick boundary.

## Check results

Final bound evidence: [s3_controllers_r3/S3_RECEIPT.json](s3_controllers_r3/S3_RECEIPT.json).

| Requested check | Result |
|---|---|
| Existing suite plus S3 checks, at the end of the repair batch | **213 passed**, 43.85 s pytest / 44.10 s stage wall time |
| Address/undefined-behavior sanitizer contracts | PASS, empty stderr |
| All five stored C4 fixtures × three variants | PASS: RHS and full coupled RK4 outputs within 1e-9; production phase RHS also matches |
| Production frozen-position RK4, including nonzero rates, pressure and target coupling | PASS against independent arithmetic within 1e-12 |
| Enemy restoring sign, commitments -1, 0, 1 | PASS inside, at and outside preferred distance |
| Cross-team damage recurrence | PASS scripted step/constant-input/decay sequence; friendly-fire separation checked against World::damage |
| Decide-call ordering | PASS cached actions independent of call order |
| Empty reach, dead targets, coincident units, no enemies, zero resultant and empty-group alignment | PASS |
| Artillery minimum range and push-pull retain/switch hysteresis | PASS |
| Non-finite state and raw action | PASS hold/no target and failure counting |
| Clone memory, previous assignments, damage averages, phase initialization/RNG and parent isolation | PASS synthetic clones and actual World fork |
| Determinism and diagnostic non-feedback | PASS one fresh-process, diagnostics-off replay per arm matches its checked fight summary |
| Historical no-controller reference | **80/80 byte-identical** |
| Historical S2 passthrough full trace/summary fixtures | **228/228 byte-identical**; 310 historical archives verified before comparison |
| Default full fights | **38 per arm**, 152 total, zero controller failures |
| Step refinement on the same captured snapshots | PASS maximum absolute commitment difference: resonator **0.0091638672**, morale **0.0000902675**, both < **0.02** |
| Whole-fight cost against nearest, with actual planning counters | Measured; scope and results below |

The 38-fight grid is the 19 existing doctrines × both orientations, controlled side 0,
with development/engineering seeds `2026100500 + doctrine_index`. Defaults are unchanged across all attempts.
These checks establish bounded engineering behavior, not a population failure rate or game-playing superiority.

## Defaults used (no tuning)

| Arm | Parameters |
|---|---|
| resonator | K=2.5, K_t=2.5, kappa=25, beta=1.5, omega_melee=0, omega_ranged=0, G=2.5, w=1.5, f=0.75, gamma=1 |
| morale | K=2.5, K_t=2.5, kappa=25, beta=1.5, lambda_melee=1, lambda_ranged=1, G=2.5, w=1.5, f=0.75, gamma=1 |
| pushpull | G=2.5, f=0.75 |
| nearest | no parameters, original S2 behavior |

Zero natural rates are the requested resonator midpoint defaults; this grid does not demonstrate sustained rotation.
The independent ODE checks include nonzero rates.

## Cost and evidence limits

The fresh-process determinism replays also supplied one uncached timing sample per arm, against the line doctrine at
seed 2026100500. Capture and diagnostics were disabled. Elapsed time includes host startup and each arm's own fight length.

| Arm | Elapsed seconds | Ratio to nearest | Executed world steps |
|---|---:|---:|---:|
| resonator | 0.5535 | 9.98 | 1916 |
| morale | 0.5468 | 9.86 | 4501 |
| pushpull | 0.2089 | 3.77 | 709 |
| nearest | 0.0554 | 1.00 | 783 |

All four samples recorded zero forks, search calls and artillery rollouts. They cover an opponent without planning;
no elite performance claim is made. Different fight lengths/work mean these ratios are not isolated controller overhead,
and one sample per arm is not a general performance estimate. No S3 speed cap was registered. Exact metrics and summaries
are retained in [determinism_cost.json](s3_controllers_r3/determinism_cost.json).

All per-fight summaries, diagnostics and refinement maxima are retained. Complete tick-by-tick refinement inputs are
retained for one fight per stateful arm; the remaining replay inputs have hashes and deterministic requests but are not
stored in full. This limits independent re-evaluation from stored inputs alone. The current source/build identities and
all retained artifact hashes are in the final receipt. No qualification of C4/C5 groups, hierarchy or source recursion is claimed.

## Repairs, deviations and failed attempts

- Revision 2's coupled-C4 oracle conflicted with frozen-position production integration. Revision 3 separates reference
  algebra checks from production ODE/refinement checks and explicitly retains the intended epsilon=0.01 regularization.
- Push-pull uses negative centre distance in model units with eta=0.2; empty-group alignment is zero in both stateful arms;
  kappa is dimensionless and target pressure uses the fixed one-second normalization.
- Diagnostic formulas/window rules were specified before execution. Member IDs are stable; persistent cluster IDs are not required.
- Cost uses the four determinism replays instead of adding a timing grid; this is written in the execution contract before the final run.
- [r1](s3_controllers_r1/S3_RECEIPT.json) stopped after 193 existing tests passed because the new contract fixture used an
  ambiguous Observation name. The compiler error was fixed; no fight stage ran in r1.
- [r2](s3_controllers_r2/S3_RECEIPT.json) passed 212 tests, sanitizer and parity checks. It completed 38 resonator and
  five morale fights with zero controller failures before a refinement check exceeded 0.02 (0.0432893). The replay had
  incorrectly added a clipping operation after its first half step. The fix applies the same single end-of-tick clipping
  map in both integrations; it changes no production one-step clipping rule, knob or tolerance. An independent regression
  check now covers this boundary. The failed attempt is preserved; its replay input was not retained by the old harness,
  which was corrected to retain future failed inputs and successful per-case check records.
- Code changes invalidated earlier test/build identities, so verification was run after each complete repair batch.
  The final r3 suite and each final stage ran once; no successful final stage was repeated. Failed attempts are retained,
  and no historical reference, committed receipt, gate or frozen GeoMind file was edited.

The only pre-existing dirty path, `docs/reviews/tactical_0g_design_review_codex.md`, is preserved and excluded from these commits.
No milestone status was changed.

## Identities and next gate

Author family: Codex (GPT-6). This is the implementer's report, including its own recheck, not an independent review.
Final receipt SHA256: db56b3b9867e0ff70594291076c86c76c07bd8e9628b1a0f5d7df844b19562eb
Design revision-3 SHA256: fc6494b2bf3e2e8127a7f60a1e2a5b607dd910eeb52a65ccb4ca26c9ff6c262b
Native binary SHA256: a1a2d5288481a66f75ec2d151c58ba3b5378121b23bc59396a268815b552c74a
S3 contract binary SHA256: cb2049f507e8098cd08327e6835e78b1f7a27c0e246d00efa4c6aa6fc8042b16

Next gate: Claude independently reviews the committed revision-3 contract, implementation and final bound engineering evidence.
S4 tuning and S5 registration/execution remain outside this completed session.
