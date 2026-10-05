APPROVE_WITH_NOTES

Reviewer family: Claude (claude-opus-5-5)
Reviewed: the S2 outside-controller plug at commit `b143ed4` ("Fix S2 controller boundaries and evidence validation"), with the reports `astelia_cpp/S2_PLUG_REPORT.md` and `S2_RECHECK_REPORT.md`
Receipt reviewed: `astelia_cpp/s2_plug_recheck_r1/S2_RECEIPT.json`, sha256 `12b0322d2e4709fe6ec3c1f456c8a75c028d5296ba97f77d03c4a415403c0a09`
Date: 2026-10-05

## Verdict

The plug meets the S2 request (`astelia_cpp/S2_PLUG_REQUEST_CODEX.md`) and may be used to build the S3 controllers. Approved as engineering, not as an experiment.

## What I checked

**Code** (`src/native/controller.h`, `controller.cpp`, `controller_bridge.cpp`, and the call sites in `combat.cpp:115-116` and `world.cpp:57,131-141,183,274-276`):
- **The fence:** `controller.h` includes neither `world.h` nor `types.h`. A controller receives only `Observation` (t, dt, width, height, and the living units with exactly the requested fields, including cumulative `damageDealt` and `damageTaken`). Only the test-only `TestPassthrough` touches `World`, and its world pointer is rebound per call and cleared after.
- **The game's own planning is off for a controlled side:** `world.cpp:183` disables the pack, and `world.cpp:133` sets abilities to `Auto` (owner decision 1).
- **Decisions are made per unit in the game's shuffled order** (`combat.cpp:116`). The observation is built once per tick before them (`prepareControllers`).
- **Validation:**
  - a non-finite decision becomes hold with no target;
  - the goal is clipped to the field, the multiplier to [0, 1], and the stop distance to at least 0;
  - the target must be living and on the other team, else none;
  - the guard reflex still holds the unit;
  - the release kind comes from the role, with reach computed as the game does (gap for melee and direct, centre distance and minimum range for artillery).
- **Artillery under outside control:** it fires through the game rule "a gun the planner did not use releases on its own" (`formation_sim.js` `act`, case `'art'`). My run below confirms it deals damage.
- **Unknown controller names and non-empty parameters are rejected** (`makeController`).

**My own fights** (fresh build of `b143ed4`, seeds 811-813, never used before):

| Check | Result |
|---|---|
| passthrough against built-in, novice, 6 opponents × 2 sides | 12/12 identical summaries |
| passthrough against built-in, elite-fast, the same | 12/12 identical |
| `nearest` run twice, 19 opponents × 2 sides | identical |
| `nearest` against pool defaults (38 fights) | mean margin −9.53, 0 won. Artillery damage 5,440, so outside-controlled guns fire |
| `hold` (38 fights) | mean margin −24.08, 0 won, 0 damage of every kind (as expected) |
| built-in novice, same fights | mean margin −0.87; artillery damage 5,675 |
| unknown controller | rejected with "unknown controller: nope" |

**Not rerun:** the 193 tests, ASan/UBSan, the 228 full-trace passthrough pairs and the cost measurement. I read their receipts but did not reproduce them.

## Notes (none blocks S3)

1. **A small timing asymmetry, declared rather than fixed.**
   - A controlled side sees one snapshot taken at the start of the tick.
   - A built-in side decides unit by unit and can see targets that other units set earlier in the same tick (both sides are interleaved in one shuffled order).
   - This is minor and the same for every controller arm. Record it in `DESIGN_0G.md` section 1.
2. **The observation shows every unit's current target, the enemy's included.** This follows the request I wrote (it said every living unit). It is information a player can see on screen (who attacks whom). Declare it in `DESIGN_0G.md` section 1, so that no arm's advantage comes from it unannounced.
3. **The special player body is not controllable** (S2 recheck). The mirror scenario used by 0g has no player body, so this does not matter for 0g. Keep the rejection.
4. **`passthrough` is test-only and privileged.** It must never be an arm in a tuning or judging run. The 0g runner should refuse it outside tests.
5. **A floor reading for development, not a result:** `nearest` scores −9.5 against pool defaults, while the game's own novice scores −0.9. The floor arm is clearly beatable. S4 measures this properly.
6. **The two caches are still separate** (the C++ review's note 4). Decide on one before S4.
