# One-pass tooling recheck

Reviewer family: Codex (separate agent, same family). Claude was unavailable as
a spawned reviewer in this session. This is the lighter tooling review of
decision 0033, not a development-result review or independent scientific review.

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Scope: static inspection of new v4 `lab.py`, `build.py`, `requests.py`,
`metrics.py`, `report.py`, `replays.py` and `README.md`, with read-only comparison
to decision 0033, the admitted adapter request/host/observer seams and v2 request
constructors. No fights, fixture execution, project tests, or source changes.
The implementer was adding focused tests during this inspection; their results
are recorded separately by the implementer.

## Findings

1. **Selected replay rendering fails after the first outcome fights.**
   `replays.one()` reads `record['stats']['timeout']`, while `metrics.measure()`
   does not provide that field. The automatic report after a C3 stage therefore
   raises `KeyError` when rendering the selected C3 pairs. Derive timeout from
   the existing terminal time or provide the field, and cover selected replay
   rendering with the synthetic observer fixture.
2. **The lean observer must replace the actual inherited object.** The inspected
   build excludes `observer_v1.o`, but the admitted adapter's link names the
   object `observer_v1_observer_v1.o`. Leaving that object in the v4 link alongside
   `lean_observer.o` produces duplicate observer symbols and blocks preparation.
   The implementer had already identified this correction and was applying it
   during this review.

Both findings concern new tooling and require fixes before delivery; no fight
data needs rerunning because no v4 fights have been executed.

## Inspected behavior

The staged calibration and execution paths check the mechanism read gate before
C3; subsequent C3 looks check the preceding read; series calibration waits for
a completed/read C3 stopping look or look 200. Allocation is ten mechanism
pairs, at most 200 C3 pairs in total across twenty opponents, and ten paired
series of at most ten positions. Future map/tactic draws are persisted before
execution and independent of controller RNG. Series stopping/carryover is
arm-specific, with healed surviving cohort members and no resurrection.

Cap interruption archives unfinished native cells and reuses verified completed
receipts; other incomplete/unclosed attempts stop. Declarations seal inputs,
binaries, allocation and source identities. Reported shell ratios include
zero-hit landed shells and disclose unresolved/unassigned damage. Reports expose
sample denominators and survival conditioning, with streak primary for series.
Replay selection remains two C3 fights per arm and the first paired series;
decision/attribution streams are disabled and heavy observer geometry collectors
are removed in the new overlay. Elite remains an unpaired historical reference.

No further concrete defect was found in this bounded pass. This does not claim
runtime or fight-result validation; the focused synthetic tests and no-fight
build/preparation are the implementer's remaining checks. Fix dispositions are
recorded in `DISPOSITION.md`; no repeated review loop is requested.
