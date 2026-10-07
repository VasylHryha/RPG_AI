NOT_ADOPTED: daytime compute projection exceeded one hour before the first reference world.

Decision 0032's implementation is present, but adoption verification is incomplete. The implemented default is the inexact engineering kernel; it is not qualified for recorded use by this delivery. C6 remains **BLOCKED / R006 STOP**. No final entropy, recorded panel, mutation, scientific change or milestone status change occurred.

The owner requested STOP whenever the daytime projection exceeds one hour. After builds, the test batch and diagnostic battery, the runner projected **3,606.5388 s (60 min 6.54 s)**: **306.5388 s elapsed + 10 remaining worlds × 300 s + 300 s analysis/IO reserve**. It stopped immediately, before launching any full world. This is a conservative planning estimate, not a measured duration of the remaining work: it counts both concurrently planned timing worlds sequentially and uses five minutes for every world. Actual elapsed time to the compute stop was about **306.54 s**; builds took 7.08 s, tests 184.02 s, diagnostics 99.26 s. Further simulation was not attempted after STOP. Budget receipts: [runs/BUDGET_00.json](adoption_0032/runs/BUDGET_00.json), [runs/BUDGET_01.json](adoption_0032/runs/BUDGET_01.json), [runs/STOP.json](adoption_0032/runs/STOP.json).

## Implemented and tested

- `native/c6_option_b/field.cpp` defaults to Accelerate `vvexp` / `vvsincos` and separable site Gaussians. `C6_OPTION_B_INEXACT=0` selects the original scalar evaluator. The site buffers are accessed only with `n <= 64 && ns <= 64`; larger valid inputs fall back to scalar site Gaussians. Pair/site dimension overflow is rejected before allocation/access.
- `tools/build_c6_option_b.py --kernel inexact|exact` builds isolated libraries, with inexact as default. `C6_OPTION_B_KERNEL=inexact|exact` selects the library; `tools/c6_option_b_check.py --kernel ...` declares it explicitly. Build receipts bind source SHA256, compiler/flags, binary SHA256, selected kernel and macOS build. Loading checks those identities and the compiled kernel marker. macOS drift refuses loading and requests re-verification/reference regeneration.
- The exact audit remains bit-sensitive. The inexact audit compares returned arrays within 1e-8 and requires native return-code identity; complete-world decision assessment is still pending.
- `tools/c6_option_b_adoption_analyze.py` derives from the preserved R3 analyzer. **N3 fixed:** causal intact/ablated lengths, finite nonnegative inputs, and duplicate selection priorities have named guard rows. **N4 fixed:** every nonfinite float leaf is counted independently per engine, and matching NaN/infinity fails the comparison. Negative tests exercise these guards. No new stored-world counts are claimed, because analysis did not run on the four worlds.
- `tools/c6_option_b_adopt.py` pins the four immutable old references before runs, checks both diagnostics, STOPs on any failed world contract, and permits fresh bit-exact reference generation only after all four comparisons pass. It also declares the simultaneous exact/inexact smoke-1 timing pair and captures load samples. Those world stages were not reached.

The option-B suite and added switch/guard/analyzer tests ran **once, after the complete implementation/review change batch**: **178 passed in 183.68 s** (184.02 s measured subprocess time), under `caffeinate -dims`. Existing scalar bit-equality contracts explicitly use the exact build; concurrent grid/fork tests exercise both kernels. New tests cover the default, selection, build/OS tampering, inexact full flow/cache repeatability, the 64/65 bounds and overflow rejection. [Test output](adoption_0032/TESTS.stdout.txt), [test receipt](adoption_0032/TESTS.json).

## Observed numerical diagnostics

These unchanged registered diagnostic functions were called only as authorized engineering fixtures, without the blocked development/panel gate. Both passed:

| Diagnostic | Required bound | Observed maximum | Result |
|---|---:|---:|---|
| `b_reference_equivalence` | 1e-10 | 1.278033234797249e-12 | PASS |
| `b_transform_equivariance` | 1e-9 | scene 7.549516567451064e-15; rename 0 | PASS |

[Diagnostic receipt](adoption_0032/runs/DIAGNOSTICS.json) records all fixtures, macOS and binary/build identity. Diagnostic battery time: 99.26 s. World-run receipts support separate awake and elapsed times; no world ran in this attempt. Tests record awake 184.02 s and elapsed 184.02 s. Raw execution log remains local.

## Remaining required gates

| Work | Status | Reason |
|---|---|---|
| Four stored exact-reference comparisons: smoke 0/1, development 0/1; decisions identical and floats <=1e-8 | NOT_RUN | one-hour projection STOP |
| Four newly generated inexact references and repeat-bit comparisons | NOT_RUN | four exact-reference contracts have not passed |
| CPU of smoke 1 under simultaneously launched exact/inexact kernels, with load | NOT_RUN | one-hour projection STOP |
| Adoption qualification | NOT_ADOPTED | required world/reference/timing evidence unavailable |

No claim of observed four-world equivalence, regenerated references or new speedup is made. The study's future-panel risk remains unquantified. Its limits remain: unstored fine-grid frames/candidates, recovery/causal trajectories, and final-panel statistics are unassessed. The adoption analyzer preserves those limits.

## Identity, preservation and delivery

macOS at this attempt: **26.6.2, build 25G83** (`sw_vers`; ProductName macOS). Both build receipts record that pin. Exact binary SHA256: `bb573e1e30441fd1146bdc17d97a4732f06388316acd7f4ef41004d0184bd6fa`. Inexact binary SHA256: `07ad3daa3939a376604074accc55affe55a726c1098af91382a535ba2048c289`. Libraries stay in ignored local `build/c6_option_b/` and `build/c6_option_b/exact/`. [Input identity](adoption_0032/runs/IDENTITY.json), [exact build](adoption_0032/EXACT_BUILD.json), [inexact build](adoption_0032/INEXACT_BUILD.json).

All four old reference files and their COSTS receipts, STATUS.json and docs/PLAN_CURRENT.md match their pre-run hashes: [preservation receipt](adoption_0032/PRESERVATION.json). Frozen C0–C5 and historical evidence were not edited. Other sessions' tactical/growing-shapes work is excluded from delivery. No new world raw file exists, so [local raw inventory](adoption_0032/runs/RAW_FILES_LOCAL.json) is empty. Existing large raw inputs remain local with their pinned SHA256 identities. No >45 MB file is included in the delivery.

Implementation owner recheck: the verbatim request went to separate Codex reviewer `adoption_code_recheck`, who found one loaded-library test-path issue; fixed before testing. No remaining blocking finding. Claude is installed but `claude auth status` returned `loggedIn=false`, so this is an explicitly disclosed same-family fallback, not cross-family acceptance. [Recheck/disposition](adoption_0032/IMPLEMENTATION_RECHECK.md). The conservative estimate retains a 300-second reserve; parent-side analysis/equivariance has no hard interruption, a disclosed bounded-task limit. This stop occurred before those world-analysis stages.

Final report/evidence owner recheck and verified transport are recorded in adjacent sidecars. The plan is deliberately untouched under the user's express instruction; this report records rechecks/dispositions for the owner to incorporate later. The delivery is a bounded implementation plus passing fixture diagnostics and a resource STOP, not completed adoption or C6 acceptance.
