APPROVE_WITH_NOTES

Reviewer family: Claude (claude-opus-5-5)
Reviewed: the typed C++ simulator at commit `1f694d4` ("Complete typed tactical simulator and performance qualification"), `astelia_cpp/build.py --engine native`
Engineering receipt reviewed: `astelia_cpp/native_qualification_r1/qualification.json`, sha256 `9dc3d7bfbdcad31ccd2ad8a1f74fa3e1de3c964a56c2d5ad950871bb02710e4b`
Date: 2026-10-05

## Verdict

The typed simulator may be used as the engine for the 0g AI experiments, **as long as every comparison is made inside the C++ engine** (note 1). Mixing JS and C++
numbers in one comparison is not allowed. This review approves it as an experimental engine only. It is not a scientific acceptance of anything, and it does not certify every line of the 18,166
lines of native code.

## What I checked

1. **Same game in distribution (the main question, since the owner's revision-2 plan relaxed whole-fight equality).** `equiv.py` → `equiv_r1/`.
   - **Players:** novice, regular, veteran, elite-fast and run 4's confirmed best profile.
   - **Opponents:** two settings, the pool defaults and the bench's elite skills without `artyRollout`.
   - **Fights:** the same requests in both engines: 19 pool opponents × review seeds 701-704 (never used by any run) × both sides, so 152 fights per cell and 1,520 per engine.
   - **Errors:** none in either engine.

| setting | player | JS margin | C++ margin | C++ − JS | se | z | JS won | C++ won |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| pool defaults | elite-fast | 44.57 | 44.12 | −0.45 | 0.58 | −0.8 | 1.000 | 0.993 |
| pool defaults | run 4 best | 35.25 | 35.07 | −0.18 | 0.46 | −0.4 | 1.000 | 1.000 |
| pool defaults | veteran | 14.36 | 13.78 | −0.57 | 1.07 | −0.5 | 0.921 | 0.928 |
| pool defaults | regular | 12.11 | 12.54 | 0.43 | 0.78 | 0.6 | 0.888 | 0.928 |
| pool defaults | novice | −1.31 | −1.31 | 0.00 | 0.94 | 0.0 | 0.316 | 0.289 |
| elite, no rollout | elite-fast | 28.80 | 29.71 | 0.91 | 1.46 | 0.6 | 0.921 | 0.914 |
| elite, no rollout | run 4 best | 20.49 | 21.93 | 1.43 | 0.78 | 1.8 | 1.000 | 0.993 |
| elite, no rollout | regular | −2.99 | −0.82 | 2.17 | 0.98 | 2.2 | 0.375 | 0.388 |
| elite, no rollout | veteran | −3.62 | −2.97 | 0.64 | 1.12 | 0.6 | 0.342 | 0.349 |
| elite, no rollout | novice | −15.64 | −12.83 | 2.81 | 0.93 | 3.0 | 0.007 | 0.026 |

   - **The ladder order is identical in both engines in both settings.**
   - With pool-default opponents the engines agree: mean difference −0.15 (se 0.36).
   - **Against elite-skilled opponents, every player does better in C++:** mean +1.59 (se 0.48, z 3.3). That is a small but real systematic shift, about 3% of an army (note 2).

2. **Speed, reproduced independently.**
   - Before the rewrite, I timed the mechanical port on 5 fights: 4.9 s in JS against 17.3 s in C++, with identical outputs. That confirmed Codex's NOT_READY finding.
   - The typed engine in this review run: 1,520 fights in 198 s on 4 workers, against 1,589 s on 6 workers for JS. That is about 0.52 against 6.3 worker-seconds per fight, **about 12×** at load 100-119, consistent
     with Codex's 9.5-15×.

3. **Controller plug.**
   - `src/native/api.h` offers create / step / done / summary / fork and ability triggers.
   - There is **no hook yet for an outside controller to decide a unit's move and target** (note 3). That is session S2's work, as planned.

4. **Documents.**
   - The behaviour changes are listed in `PORT_REPORT.md`: deviations 1-6, the repaired inherited defects, and a first-tick commander choice that differs ("hunt" against "skirmish").
   - The approval trail is recorded in `PERFORMANCE_REWORK_PLAN.md` (owner: "lets do it").
   - The frozen JS snapshot hashes are unchanged.

**Not checked:**
- a line-by-line reading of the native code;
- the ASan/UBSan and 158-test claims, which I did not rerun;
- portability to other machines or compilers;
- profiles beyond the five above;
- the abilities-off and sandbox-rules settings.

## Notes

1. **Compare only within one engine** (binding for 0g). The opponent ladder, every controller arm, tuning and judging all run on the same admitted C++ build. Results from runs 1-5 (JS) stay JS
   results. A profile found there can be replayed in C++, but its C++ score must be measured again.
2. **Find the source of the elite-skill shift** (low; does not block experiments that follow note 1). Candidates are the skills present only in that setting: `artyFire: plan`,
   `artyBattery`, `lockedDodge`, `weaponsFree`, `saveWounded`, and the smart shell and cast dodges. The artillery repairs (null queue, radius padding) are the first suspects. A per-skill
   comparison (each skill alone on the opponent side, both engines, 152 fights each) would locate it cheaply. Record whether it is an intended repair or a defect.
3. **The S2 plug** must add the outside-controller hook in the typed decision path (`decisions.cpp`) and keep the game's own decision for the other side byte-identical (the S2 sanity check:
   an outside copy of the `alone` brain equals the built-in one). Prefer a typed `Observation` / `Decision` pair shaped like Astelia's lab `Policy`.
4. **Two caches now exist:** Codex's `result_cache.py` (build identity) and `astelia_compose/cache.js` (fight fingerprint, seed ledger, library). The 0g runner should use one of them,
   keyed on the admitted binary's identity, and keep the seed ledger.
5. Any later source change invalidates this review's equivalence table for the changed build. Rerun `equiv.py` (about 30 minutes, mostly JS) after behaviour-changing edits.
