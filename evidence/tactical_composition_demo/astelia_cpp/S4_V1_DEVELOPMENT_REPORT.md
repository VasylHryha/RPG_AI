STOP

# S4 v1 development: unresolved damage-attribution timing

Implementer family: Codex (GPT-6). Date: 2026-10-05.
Inspected checkout: `fd7ea6f4127a351f7bec68f9cfad8876e3fd4e0c`.
Scope: owner-authorized exploratory controller improvement under decision 0028,
items 15–16, and DESIGN_0G.md section 12. This is a contract-ambiguity stop,
not an A/B performance-gate result or a controller failure.

## Question for the design drafter

Section 12 says damage is split by whether the unit "had a legal target at that
tick". **Which instant determines that status for each incoming-damage increment?**

1. The frozen controller snapshot at the start of the tick that produced the
   damage, retaining its legal-set nonemptiness until the next counter update.
2. The current snapshot at the next `prepare`, where that counter increment is
   consumed.
3. The instant each damage event occurs, after any movement or deaths within
   the tick, requiring event-time attribution in the engine/observation bridge.

These alternatives do not define the same controller. For example, a unit has
no enemy in reach at a tick's initial snapshot, moves into reach during that
tick, and takes projectile damage. At the next `prepare`, it has a legal target.
Alternative 1 calls the increment unanswered; alternative 2 calls it answered;
alternative 3 depends on the reach state when the hit occurred. With zero outgoing
damage, the first two alternatives give opposite signs for the new contribution
to own pressure and therefore opposite commitment responses.

Section 12 does not choose among these timings. Sections 1–4 establish the frozen
snapshot and cumulative-counter recurrence, but do not establish when to label
damage for the new split. No timing convention was chosen by the implementer.

## Caller-path evidence

- `src/native/combat.cpp:115`: `coreStep` calls `prepareControllers` before unit
  decisions and actions. Actions begin at line 126; melee hits, projectiles and
  shells are processed at lines 135–148. Units can move in `actNovice`
  (`src/native/combat.cpp:15`) before these hits.
- `src/native/controller_bridge.cpp:35`: observations copy cumulative
  `dealtToEnemy` and `takenFromEnemy` counters from unit state.
- `src/native/s3_controller.cpp:78`: new memories baseline current counters;
  line 81 consumes subsequent counter differences at `prepare`.
- `src/native/s3_controller.cpp:95`: target legality is evaluated using the
  current frozen positions, with the role-specific reach predicate at line 96.
- `src/native/world.cpp:227`: cross-team counters are incremented in
  `World::damage`; they currently carry no legal-target timing label.

Thus current counter differences cannot by themselves identify event-time
legality, and current-snapshot classification can relabel preceding-tick damage.

## Stop row and execution state

| Yes/no condition | Answer | One action | Responsible role |
|---|---|---|---|
| Is section 12's incoming-damage attribution timing ambiguous? | Yes | Specify the attribution instant in section 12. | Drafter |

The owner's instruction requires reporting an ambiguity and stopping instead
of silently choosing. Part 1 implementation, rebuild, tests and v0 fixture
comparisons were not started. Consequently there is no Part 1 implementation
commit and Part 2 is not eligible to start. No development seeds were allocated,
no fights ran, and `s4_v1_development/` was not created. A duration estimate is
not a started-run log; one must be logged before any future development run.

| Arm | Stage A validation | Stage B validation | Stage C validation | Regular head results | Timeouts | Mean enemy artillery alive |
|---|---|---|---|---|---|---|
| resonator | not_run | not_run | not_run | not_run | not_run | not_run |
| morale | not_run | not_run | not_run | not_run | not_run | not_run |
| pushpull | not_run | not_run | not_run | not_run | not_run | not_run |
| nearest | not_run | not_run | not_run | not_run | not_run | not_run |

Every `not_run` above has the same reason: unresolved section 12 timing, before
implementation. No fresh paired spreads, delta proposal or sample-size planning
are available. Historical amended S4 measurements remain historical v0 evidence.

Only this report was added. No registration, judging-root-derived seeds,
recorded run, SPEC_0G.json change, frozen GeoMind change, receipt edit or milestone
status change occurred. The pre-existing untracked
`../viz_0g/replays_0g.json` was left untouched. No independent review or acceptance
is claimed.
