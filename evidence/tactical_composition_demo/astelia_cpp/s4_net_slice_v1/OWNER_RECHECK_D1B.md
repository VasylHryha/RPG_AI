CHANGES_REQUIRED
Reviewer family: Codex
Review type: quick same-family source recheck of the in-progress deliverable 1b; pre-final-test, no execution.
Date: 2026-10-08

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Reviewed the current slice sources against `frozen/network_slice_d1_recheck_claude.md`. No fights, collection, training, build or tests were run. This is an implementation recheck; it does not replace Claude's cross-family gate. The implementer must record the disposition after fixing the finding and running the final focused batch. `PLAN_CURRENT_APPEND.md` and `docs/PLAN_CURRENT.md` were left untouched.

## Finding B1 — collection-blocking regression in the moved act-entry aim gate

`build.py::generated` inserts `net_slice::actAimReach(w,i)` unconditionally at `actNovice` entry, before walking. `host.cpp::actAimReach` invokes `aimReach` immediately. When a unit belongs to a team controlled by Host, `aimReach` performs `h->cache.at(id)` and `h->casts.at(id)` without checking the unit role. Host only prepares caches/casts for artillery. Both drill requests contain two own infantry scaffolds. Their first native action therefore throws an out-of-range exception even though their decision is stationary/no-release. The new lifecycle integrations only use artillery and cannot catch this regression.

Required fix: guard this gun-specific seam by artillery role before any cache/cast lookup, retaining native action behavior for the stationary scaffolds. Add a bounded scripted native integration containing the actual non-gun scaffolds. It must exercise `coreStep`, without outcomes, collection or fights.

## Finding B2 — drill dispatch behavior still lacks integration coverage

M7's source implementation correctly differentiates `builtinDecision`/`prePrep` in D1 and D2, but `test_drill_geometry_and_record_caps` only checks request metadata/geometry, and the lifecycle integrations install a custom non-firing opponent controller. No fixture exercises the collection opponent's actual D1 hold versus D2 native firing dispatch. A bounded scripted coreStep fixture with infantry and the real built-in opponent path should assert stationary/no-prep/no-shell behavior in D1 and native preparation/launch in D2. This also provides the regression fixture for B1; do not read fight outcomes.

## Reviewed dispositions

| Original finding | Source-check result |
|---|---|
| H1 | Coherent decision-tick opportunity rule across decoder, teacher, masks and cached deployment, including this tick's prep increment; shared automatic ready+6 rule is declared. Cooldown/winding parity fixtures cover inactive cached permissions. |
| M1 | Paired whole-draw t intervals, two ordered primary axes, .005/.015/.030 discrete spending, unchanged .10 margin and reachable equal-student noninferiority fixtures are present. Approximation assumptions and exact-margin limits are disclosed. |
| M2 | Actual overlay coreStep fixture covers eight scripted lifecycle scenarios, first-ready arithmetic, pre-walk act aim, veto and consumed-without-launch. B1 must be corrected before collection. |
| M3 | Both live non-slow shell teams reach planner input; own shells have separate public wire kind/flag and damage, with tensor/encoder parity coverage. |
| M4 | Round 0 uses the teacher pool; later rounds retain each arm's whole trajectories; decision-row weights sum to one third per round and empty strata raise. |
| M5 | N1r now has separate mean8 plus unaliased per-target cosine12; slot 0/8 opposite-group fixture catches the former alias. |
| M6 | N1/N1r receive the same A/B/share phase-free drift as N2's baseline; N2 J modulation remains the declared mode channel. Full action/drift parity is covered. |
| M7 | D1 static versus D2 native gunfire and intended rear-infantry geometry are documented and implemented. Add B2 behavior fixture; B1 presently blocks both paths. |
| L1 | Pending aim uses current cached aim until lock. |
| L2 | Sequence parity compares every action field, drift, phases and persistent-ID pruning after death, including frozen topology remapping. |
| L3 | Launch-reset channel is ledgered; frozen_phase ignores resets; no_reset exists. |
| L4 | ES retains evaluated incumbent on ties/survival deterioration, enforces common panel IDs, and uses evaluated clipped perturbations. Matched-kick harness explicitly limits claims to the recorded-context channels. |
| L5 | Record cap is 1 MiB with checked raw unit/threat bounds and actual maximum-record diagnostics; resource projection uses the raised worst-case cap. |
| L6 | Native private energy/cost/skills/RNG mutations are compared for wire and policy invariance. |

The original D1 REPORT and other living delivery summaries still describe the old receipt/test inventory while this review occurs. The implementer's final D1b documentation must retain that inventory as frozen history and clearly state the current fixtures/results and collection gate.

## Implementer disposition before final verification

B1: fixed with artillery role guards in both actAimReach and aimReach; non-guns never access gun cache/cast. B2: added drillDispatch fixtures, each60 actual coreStep ticks including own infantry; D1 asserts no enemy prep/shell, D2 asserts native prep and shell launch, both assert stationary target-none/prep-zero scaffolds. Final verification receipt follows in REPORT.md. This disposition does not replace the reviewer's original snapshot verdict or constitute cross-family acceptance.
