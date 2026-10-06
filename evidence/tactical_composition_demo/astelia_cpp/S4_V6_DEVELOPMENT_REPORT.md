STOPPED: the sole development attempt failed at cache admission (invalid combat summary schema).

# S4 v6 development report

Implementer family: Codex (GPT-6). Implementation follows DESIGN_0G.md §18.2 > §18.1 > §18 and the r3 N1 fixture note. The mandatory pre-fight checks passed. The single authorized A/B attempt then stopped because I missed the cache's strict summary schema: the unchanged historical validator rejected the new `complexDiagnostics` field. This is an implementation integration defect, not a failed no-combat integration-policy check.

No development stage, tuning incumbent or validation endpoint completed. The attempt recorded **0 scored rows**, 0 recorded fresh fights, 0 cache hits and 0 recorded numerical-failure rows. The failure occurred after a host response returned, before scored rows reached the recorder. Total unreturned or unrecorded native work is unknown. These zero recorded counts do not establish zero actual fights or failure-free execution. The consumed entropy ledger and original runner, binary, receipts and logs are preserved. **No second development attempt was run.**

The runner receipt says NOT_READY; this delivery is STOPPED because the process exited before any development result. All A/B numerical-performance verdicts remain unavailable. No C/P2/P3, S5, judging, registration, STATUS change or scientific acceptance.

## Attempt identity and timing

- Implementation commit: `83c0faf81b4dcc27d07e2dea653470d344663ffb`.
- Binary SHA256: `02b30cce7ebdfd47130b5e7e99329553eba09d2043a3363629672e05acef4837`.
- Output: `s4_v6_development_20261007_0233/`.
- Started 2026-10-07 02:33:33 Europe/Kiev (2026-10-06 23:33:33 UTC), under `/usr/bin/caffeinate -i -s`, configured for 10 workers. Literal invocation: `s4_v6_checks/LAUNCH.json`.
- Outer elapsed **0.448012 s**, awake **0.448017 s**; runner **0.225343 s**; exit 1. Expected duration had been about 65 minutes; maximum allowance 360 minutes.
- Initial and final 1/5/15-minute load: **5.8091 / 3.8374 / 3.7700**. There was one load sample; the attempt launched immediately without waiting for lower load, as authorized under decision 0031.

The stored-only audit passed its receipt/identity checks: 108 runtime hashes, binary/build, fresh development declaration, empty recorded rows and empty selections matched. That audit PASS certifies bookkeeping of the stopped attempt, not development readiness. `s4_v6_checks/REPORT_AUDIT.json` is unchanged. Raw logs, acceptance rows, fixtures and engineering captures are listed by size and SHA256 in `s4_v6_checks/RAW_FILES_LOCAL.json`; raw files stay local, including any over 45 MB.

## Pre-fight checks

The **10,763-case no-combat grid passed**: maximum real/imaginary errors 0.000221341 / 0.000335573 ≤ 0.001; maximum commitment error 0.000220594 ≤ 0.02; independent same-step RK4 agreement 3.553e-15 ≤ 1e-9. It includes the pinned signed real/imaginary/oblique states, drive/rotation signs, equal/opposing phases, asymmetric amplitudes and neighbor lists, empty/singleton/cancelling groups and Z(6000) cases. Native policy fixtures cover n=64/n>64, stage monitoring, retry/exhaustion, non-finite inputs and pressure failures.

Native/controller fixtures passed counters consumed once, clone/parent isolation, persisted unclipped components, similarity/alignment contracts, diagnostic action identity and fake-record gates. Historical paths/fixtures were byte-identical; unchanged-arm action comparisons covered 13,367 bytes. Three separately declared engineering captures passed the independent commitment refinement check (maximum 7.57657e-06 < 0.02). They are engineering fixtures, not development validation. **37 distinct prerequisite/integration tests passed**; none of those passed checks were repeated after the stopped attempt.

Failed harness attempts remain separate from PASS accounting: an initial compile initializer error was fixed before tests; an unsupported >15,000-byte wrapper assertion was corrected using the already passed 13,367-byte native record; a preservation wrapper attributed concurrent Claude Track A commits to PLAN_CURRENT/0h design. This task did not edit those files. No no-combat numerical acceptance check failed.

## A/B validation

The planned protocol uses CMA 4.5.0, population 16, 16 generations and fixed v5 budgets. Stage B selects regular-head S with novice tuning mean ≥ 0 eligibility. Validation never selects knobs. All four arms were allocated the common fresh panel; two orientations form each of 100 seed clusters. No planned validation executed to a recorded result.

| Stage | Arm | Head | Clusters | Mean S | SD / SE | Guns / timeouts |
|---|---|---|---:|---|---|---|
| A | resonator | novice | — | not_run | — | — |
| A | morale | novice | — | not_run | — | — |
| A | pushpull | novice | — | not_run | — | — |
| A | nearest | novice | — | not_run | — | — |
| B | resonator | novice | — | not_run | — | — |
| B | resonator | regular | — | not_run | — | — |
| B | morale | novice | — | not_run | — | — |
| B | morale | regular | — | not_run | — | — |
| B | pushpull | novice | — | not_run | — | — |
| B | pushpull | regular | — | not_run | — | — |
| B | nearest | novice | — | not_run | — | — |
| B | nearest | regular | — | not_run | — | — |

All 12 endpoints are not_run because cache admission stopped the initial evaluation. Stage A regular is not_run by design. S is own survivors minus enemy survivors. Gun survival and timeouts would be descriptive.

| Stage | Novice validation > 0 | Regular > −6.025 | Beats regular (>0, novice pass, failure-free) | Result |
|---|---|---|---|---|
| A | not_run | not_applicable | not_applicable | unavailable |
| B | not_run | not_run | not_run | unavailable |

The historical −6.025 threshold is an unmatched development comparison. No progress or beat-regular claim is made.

## Knobs

**No knobs were optimizer-selected**: the selection record is empty. The failure receipt retained only the starting resonator midpoint defaults:

```json
{"K":2.5,"K_t":2.5,"kappa":25.0,"beta":1.5,"G":2.5,"w":1.5,"f_c":0.65,"m_k":0.6,"lambda_th":1.5,"mu":0.0,"omega_ranged":0.0}
```

The ledger has 11 knobs; omega_melee is fixed 0, and artillery inherits omega_ranged. Mu and omega_ranged above are initial values, not findings. The attempted implementation and repaired cache use the same native controller; the repair does not establish tuned behavior.

## Amplitude diagnostics and failure accounting

| Stage | Head | Recorded unit-tick samples | Fraction amplitude <0.2 | Valid arg-rate samples | Mean absolute arg-rate rad/s | Retry / numerical-failure ticks |
|---|---|---:|---|---:|---|---|
| A | novice | 0 | not_run | 0 | not_run | unknown |
| B | novice | 0 | not_run | 0 | not_run | unknown |
| B | regular | 0 | not_run | 0 | not_run | unknown |

No recorded development amplitude denominator exists. Re z, Im z and amplitude are exported; arg is valid only at amplitude ≥0.2, and rotation rates require consecutive valid endpoints, with unwrapping reset across gaps. Scalar v5 coherence/target-phase/candidate diagnostics are explicitly not_run for v6. Zero is not assigned a phase. The 0 recorded failure rows do not bound failures in unreturned native work.

The changed package includes cubic saturation, role damping and amplitude-gated formation; it supports no oscillation-necessity, amplitude-causation, RRG source-recursion, C5 or unchanged-C4 claim.

## Cache repair after the stop

New versioned files `result_schema_v6.py`, `result_cache_v6.py` and `s4_v6_cache_repair.py` admit and preserve complex summaries without modifying the historical schema/cache or original attempted runner. The repair requires native status/failure fields, finite counters, amplitude/rate denominator consistency, diagnostic rates matching requested mu/omega, fixed melee omega and bounded retry/failure tick counts. Its cache identity includes the repair sources. Repair entropy and execution receipt paths are separate and intentionally absent: this delivery authorizes no rerun.

The complete repair batch passed **27 focused tests once**, 0.49 s pytest / 0.849784 s launcher. It replays three stored engineering summaries through the real worker cache-write and cache-hit paths, tests malformed summaries and digest-consistent cache tampering, null denominators and failed status, and preserves historical pass-through. **No native process or new combat fight ran.** An earlier launcher mistakenly resolved the venv symlink to system Python; pytest was absent, so zero tests collected. That launcher error is preserved separately and is not a failed test case. Source hashes and timing: `s4_v6_repair_checks/TEST_RESULT.json`; reviewer findings/dispositions: `SOURCE_RECHECK.md`.

## Owner recheck and delivery

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Implementation and cache-repair source rechecks resolved all required findings. Report recheck is **APPROVE_WITH_NOTES**, recorded in `s4_v6_checks/OWNER_RECHECK.md`. Both final editorial notes are fixed: complete review/final-hash bookkeeping and distinguish the returned host response from missing recorded rows. Claude CLI returned Not logged in; the separate Codex reviewer is a disclosed same-family fallback, not cross-family or scientific acceptance. No numeric quality scores were assigned.

Main .git is read-only. Final transport identities and the outcome of scoped normal-hook commit, bundle and independent fresh-fetch/blob verification are supplied separately in `s4_v6_checks/DELIVERY_TRANSPORT.json`. `DELIVERY_NOTE.md` supplies Track B B4d status and recheck dispositions for Claude, who maintains PLAN_CURRENT; this task did not edit it.
