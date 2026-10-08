CHANGES_REQUIRED

Reviewer family: Codex

Owner request, verbatim:
> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Static review of the new adapter against AGENTS.md, SHAPE_LAB_SPEC §§1–13,
research note §§3.2/5.4 and research recheck F2, including the native observation,
bridge, dodge, decision, artillery, combat and world-copy paths. No builds,
tests, fights, drills, series or calibration were run by the reviewer.

## Findings

1. **High: explicit artillery aim can bypass the gun's range.**
   `Controller::submit` checks arena bounds only. Native bridge and combat reach
   checks still use the selected target position, while the derived launch call
   uses `aimPoint`. An in-range target can therefore authorize an arbitrarily
   distant or inside-minimum-range aim point. Gate preparation/release on the
   actual explicit aim's gun reach; derive readiness from that same point. Add
   no-fight checks with an in-range target and illegal near/far aim points.

2. **Medium: submitted command readiness is stale.**
   Initial readiness refers to the v7 target. `submit(Hold)` forces false,
   but `submit(Release)` does not restore readiness, and changes of target/aim
   do not recalculate it. Use a shared readiness function for the current
   executed intent, including react/body/failure winners and target validity.
   Existing docs say ready includes eligibility to start preparation, but native
   `laneClear` and `attackerCap` can veto that eligibility. Include those checks
   or explicitly label the flag a narrower prerequisite rather than eligibility.

3. **Medium: executed target can disagree with the bridge.**
   `submit` permits missing, dead or friendly target IDs. The native bridge
   correctly clears them, but `Controller::executed` only updates movement
   fields, leaving an unreal executed target in telemetry. Validate submitted
   target IDs and/or reconcile the executed target to the actual resolved
   unit target. Add missing/friendly/dead target fixtures.

4. **Low: membership persistence wording exceeds the implementation.**
   `snapshot` clears records and `prepare` creates commands with volley=0 each
   tick. Membership remains on a reaction winner within the submitted tick, but
   does not survive to a later eligible tick. Document per-tick re-submission
   explicitly, or implement persistence with a clear cancellation rule.

## Reviewed behavior and limits

- The copied smart-shell/field/cast and dodgeShots calculations match the native
  stateless algorithms by static inspection. Excluding a cast aimed directly
  at self and retaining resolved dead projectile sources reproduce the engine.
- Shell.pos is the native landing footprint; using it for both position and
  landing is accurately disclosed rather than claiming a nonexistent trajectory.
- Guard, engaged-melee handling, temporary react precedence and ordinary attack
  pause match the declared unformed primitive source. Participation is separately
  disclosed as an endpoint correction in both new arms; it does not prove all
  body motion or later moving-enemy geometry stays in range.
- Teacher world, derived indexes, work counters and controller clones are
  separate; REACT draws no RNG. The eight-tick fixture's limited serialized
  movement/decision identity is accurately distinguished from full-fight identity.
- Both new arms dispatch through the original v7 selector and request builders
  retain lab v2 placement semantics. This is a new selectable host plus pure
  request constructors, not modification/admission of the sealed v2 executor.
- Full T-elite teacher control, search, V1/V2 execution, impact ranking and live
  effectiveness remain later work. No source-qualification or acceptance claim
  follows from this review.

## Source SHA256 at initial review

```
react.h       56ad1fff584e30f530d7ae217cb7a3c9386fc8947a839d6842f363e41314ede4
react.cpp     107151c1050c5e14a6129794d9247b473f514e81af2a487c13f038bb18f4057e
build.py      3e1a8a1e393cb5f2bd656d3150b61088e09b860d70dc1ad22b6e8c06f984675f
fixture.cpp   bed9bf856d5ab3c74fc279726d012003ff59c5ce8cd9a9c9e6dac27f17a29357
requests.py   9696146c8f0b515426d3a38245073361c1ec525cd4288fa3bc64105c383ffe34
test_adapter.py 4b88213cdf291250e7b953e659ea7e818fbfa767e9e2ef26ec0c00156a3763b2
dispatch.cpp  7087de38c74a301097830532c5f15bb6cca64b22ecd8f42ef3d0811287247a8c
```

Implementer disposition and final validation must be recorded separately after
the correction batch. This verdict refers to the source identities above.
