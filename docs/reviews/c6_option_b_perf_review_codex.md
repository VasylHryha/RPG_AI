CHANGES_REQUIRED
Reviewer family: Codex
Reviewer model: GPT-6
Reviewed commit: 8214f3905426195d5df6d2ba1694d740e0e631f4
Review date: 2026-10-06
Scope: decision-0029 engineering review of Claude's C6 option-B performance change; no scientific acceptance or registration.

The successful-world equivalence and measured speedup are credible. Approval is blocked by F1: the advertised sequential failure/check-prefix equivalence does not hold inside batched recovery/causal grid runs. The defect predates this commit, but the new ordered protocol wrapper inherits it. F2–F4 are engineering follow-up notes and do not invalidate the successful measurements.

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Read: AGENTS.md, decisions 0029/0031, research/rrg/CURRENT.md, the full performance report, committed measurement/profile/recheck artifacts, the seven changed source/test files, their parent versions, and the original R4 protocol/assay/field callers. A separate Codex reviewer received the request verbatim and independently checked the native seams and F1. That supporting recheck is same-family; this main review is cross-family against Claude's implementation.

## Numbered findings and fixes

1. **F1 — Blocking: batched inner failures lose sequential check prefixes and can change the first error.** Evidence: `geomind/c6_option_b_parallel.py:93–124`, `:183–215`, `:366–376`; sequential counterparts `geomind/c6_r4_field_assay.py:54–59`, `:110`, `:140–141`.

   A minimal static counterexample needs only one failing job. Recovery batches `[base/control, kick/kicked]`. Let all three control grids succeed and one kicked worker raise a native-flow error. Sequential recovery completes `base.run`, appends its passing control check, then raises from `kick.run`. Parallel `completed()` captures the worker error and raises at line 124 before `run_many()` reaches its check-publication loop at lines 203–214. The parallel private checks list therefore omits the successful control check. `ordered()` cannot restore a check its task never wrote.

   Error identity can differ too: let the control grids complete but exceed their numerical limits, while a kicked worker raises. Sequential recovery raises the control `NumericalFailure` and records its failed check. Parallel recovery raises the kicked worker error before evaluating the control verdict. In addition, `state_errors()` is invoked in completion order at line 198; an exception there can escape before an earlier request's saved worker error. Selecting `min(errors)` only orders worker exceptions, not numerical failures or coordinator diagnostics.

   This is a read-through control-flow proof, independently corroborated, **not an executed injected-failure experiment**. Successful-world comparisons do not exercise it. The existing operation tests (`tests/test_c6_option_b_parallel.py:120–173`) inject failures after qualification returns; they do not inject nested recovery/causal worker failures. The separate worker-exception tests check pool drainage/error indexing, not the sequential check prefix.

   **Required fix:** buffer terminal outcomes/errors per original request and publish checks/failures in the original sequential request/block/grid order. A later request's worker or diagnostic error must not bypass an earlier request's numerical verdict. Drain outstanding work before restoring the backend. Cover passing-control/failing-kick, earlier-numerical-failure/later-worker-failure, and earlier-worker-error/later-diagnostic-error under both submission orders. Keep the successful arithmetic/reductions unchanged. Implementer owns this fix; no source was edited in this review.

2. **F2 — Medium, follow-up: cache limits govern retained data, not peak allocation; the disabled drive path lost its streaming fallback.** Evidence: `native/c6_option_b/field.cpp:168–186`, `:401–418`, `:489–490`; parent `drive_path()` returned null before allocation when its payload exceeded the limit. The new drive path always allocates `3 * steps * ns` complex values, even at a zero limit. The medium miss allocates an additional complete trajectory even when retention is disabled. An allocation failure in these optional-cache paths propagates as `field_run == -1`, rather than falling back to the existing per-stage/direct computation. The material admission path alone catches optional allocation failures after frames are complete.

   These bytes are additional to retained values, in-flight key copies, list/hash metadata, arrays held by readers after eviction, task results and serialization buffers. Four task coordinators can each submit four jobs (the measured maximum is 16 queued/submitted jobs), although only four grid workers and one coordinator compute concurrently. Python byte accounting tracks array payloads, not keys/containers. No unbounded accumulation was found for the fixed protocol in its isolated process, but the budget counters are not an RSS cap. The measured peaks remain credible and disclosed; this review does not certify memory-pressure equivalence.

   **Suggested fix:** bypass full drive precomputation for disabled/oversized entries and fall back on optional allocation failure; make the medium path integrate directly into the caller's layout when optional storage is unavailable. Add allocation-failure/disabled-budget checks and peak-allocation evidence, beyond the current retained-counter tests. Preserve full-byte reuse and numerical order.

3. **F3 — Low, follow-up: native single-flight registration ends before publication.** Evidence: `native/c6_option_b/field.cpp:123–141`. `finish()` erases the in-flight entry and releases the store mutex before setting `flight.done/value`. With disabled/failed admission, an oversized value, or intervening eviction/clear, a new requester can become leader during this interval while existing followers still wait. The original arithmetic has already finished, so this creates duplicate work rather than a wrong value or dangling reference. The strict single-flight publication claim is nevertheless stronger than the implementation.

   **Suggested fix:** publish the flight state before removing its registration, with consistent mutex ordering, then notify outside the store lock. Add a deterministic non-retained publication test. Also add a forced same-index/different-full-key test; the inspected equality checks correctly reject collisions, but the current tests do not force that case. Retained and in-flight keys both use full byte comparisons; the FNV index itself cannot alias scientific results.

4. **F4 — Low, reporting: derive displayed rules and timing ranges consistently from raw receipts.** `ab2_new_smoke_0/COSTS.json` gives **152.628009959 s**, so the raw rule value is **4578.84029877 s**, still comfortably below 10800. The report's 4578 uses its rounded 152.6 input. Reverse smoke gives 4564.64370249, and development 1 gives 2815.75925127; the displayed 4566/2817 likewise use rounded times. The report's stage-2 “53–58 s per turn” range excludes pair-2 batches 67.7324/59.1942 s and reverse batches 71.2822/54.1838 s.

   **Suggested fix:** generate presentation values from the stored measurements, state rounding precision, and label the selected timing subset or give its full range. Preserve committed raw receipts. A/B CPU ratios 0.661/0.675 and wall ratios 0.405/0.442 match the receipts. Profile CPU 688.672568 → 516.361988 and repeated-input CPU 161.374105 → 8.301261 support the cache explanation. The 392 s historical run is a contextual comparison; the simultaneous old/new pairs provide the stronger evidence. Smoke/development timing is an engineering observation, not a registered readiness verdict or guarantee for every future world.

## Checks that passed

- The native material, medium and drive keys include the complete relevant input bytes. Actual-medium initial state is intentionally excluded only from the independent OFF-material key. Mutex-protected lookup/accounting, immutable `shared_ptr` values and full-key collision resolution preserve reader lifetime across eviction. Leader lease destruction releases followers on failure. No numerical race or lock-order cycle was found in normal isolated use.
- Python cache futures share immutable results and publish exceptions before removing their registration; accounting/lookup/eviction use the same cache lock. Existing Python identities/digests remain the R4 keys; this change introduces no new hash-only numerical shortcut there.
- Stage-1 condition order and stage-2 descriptor/before-episode/condition-episode order match `P.operation`. Each task owns cloned owners and a private check list. Rebinding branches and continuation grids restores the shared check list. RNGs are constructed from explicit purpose seeds, without a shared mutable stream. The new task-level ordering is sound; F1 is inside those tasks.
- The coordinator token is released around scheduler waits and reacquired before coordinator work; four grid workers plus one token holder bound compute concurrency to five per world. Nested task batches are refused; shutdown drains both pools before module restoration. Per-grid reductions remain coarse-to-fine. Queue size and thread count are separate limits.
- Pair/site restructuring retains arithmetic and accumulation order with the same scalar libm and build flags. Zero-term skipping retains nonfinite evaluation where needed; finite output scale gates emission skipping, with signed-zero replay protection. The OFF-material miss integrates independent material, fills actual medium separately, and replays original inline integration when material fails. Existing nonfinite/failure tests and the audited stored world support those branches. No new normal finite science discrepancy was found.
- All **61 unique frozen/receipt-bound files** from C1 R006, C2 R002 and STATUS's C4/C5 freezes match their recorded SHA256s; none intersects this commit's changes. The diff changes no R4 laws, protocol settings, STATUS.json, final entropy, accepted receipts, registration or milestone verdict. The independent smoke invocation also validates the 25-file RRG pin.
- All eight stored measured world dumps exist and match `COSTS.json.world_sha256`; their committed exact comparisons pass, including the audited smoke-1 run (796,159,608 full-array values). The native source/binary identities match the current build. Removing only the disclosed nested-task guard from the final parallel helper reproduces the measured helper SHA256 `6da954ada7d768f9b9d48f81d84ad29ef12d18885bc2eb8a40a17acca95570e8`; this explains its difference from the reviewed helper without conflating identities.

## Independent validation in this session

No source changes. One option-B suite and **one** full smoke world only, under `caffeinate -i -s`; no further world, mutation probe, panel or registration. Commands and raw logs stay local under ignored `evidence/c6_option_b/perf_review_codex_20261006/`. All evidence files are below 50 MB; logs/world dumps are not staged.

```text
.venv/bin/python -m pytest -q -x tests/test_c6_option_b.py tests/test_c6_option_b_parallel.py --basetemp=evidence/c6_option_b/perf_review_codex_20261006/pytest_tmp
.venv/bin/python tools/c6_option_b_check.py --backend native --parallel --entropy smoke --world 0 --schedule reverse --output evidence/c6_option_b/perf_review_codex_20261006/world_smoke_0
.venv/bin/python tools/c6_option_b_compare.py --reference evidence/c6_option_b/reference_smoke_0/world.json.gz --native evidence/c6_option_b/perf_review_codex_20261006/world_smoke_0/world.json.gz --exact --output evidence/c6_option_b/perf_review_codex_20261006/EXACT.json
```

Suite: **110 passed**, pytest 25.68 s; wrapper elapsed/awake 25.977182/25.977203 s. Smoke: valid, chain complete; wrapper elapsed/awake 154.524060/154.524185 s. Comparator elapsed/awake 6.404233/6.404238 s. Wall time in this loaded session is not a performance acceptance criterion. Exact comparison: **PASS**, tolerance 0, 3,045,093 numeric values, 2,847 Boolean values, no digest changes and no failures. Root timing/build/resource fields are deliberately excluded by the repository comparator; scientific fields/checks/identities are compared.

| Evidence | SHA256 |
|---|---|
| Reviewed performance report | `e0da5ad9564263e3921bed030f281e213943b50ce608c64432d957fffa23ded2` |
| Current native binary | `a90ba07284a3d99dd4cdbe92c08fca13e5e69c814fe2d2f9f34f9fa69d0ddff4` |
| Independent smoke dump | `ba0c295bb8e2241f8f76e7ee1834059c050d8247ba35dcf43efa4019616df043` |
| Stored smoke reference dump | `aeea74a98f3ffc1dec799633269382fa9b111d8a947e50bf3b4f2a79f290e0aa` |
| Local EXACT.json | `fb2aaf06ba87d1bea6a46898cfc19aa3311506ad652c3687a81f4e0b3be09043` |
| Local tests.log | `31f8e1f5d99bd68afdf4edd6268385911e62a35d4911716478a032f8a68f2750` |
| Local smoke_0.log | `8eb263df36b6a91b0409ddd29c89b0b9db36c825cef12e116089c355a7b66a7c` |

Disposition: **F1 remains open and blocks engineering approval of the exact failure/check-order contract.** F2–F4 are retained follow-up notes. Claude should repair the implementation and report the focused failure-prefix evidence; this reviewer intentionally leaves source and historical evidence unchanged. C6 remains **BLOCKED / R006 STOP**; the owner retains the new-revision approval gate.
