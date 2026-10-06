APPROVE_WITH_NOTES
Reviewer family: Codex
Reviewer model: GPT-6
Reviewed commit: ec82c435b4c22d2172071ada1d2ef4d94a06badd
Review date: 2026-10-06
Scope: decision-0029 engineering delta review of Claude's fixes to 8214f3905426195d5df6d2ba1694d740e0e631f4; no scientific acceptance, registration or milestone-status change.

## Disposition of F1–F4

| Round-1 finding | Disposition | Evidence and remaining limit |
|---|---|---|
| **F1 — Blocking: nested failures lost checks and changed the first error.** | **Resolved for the input-driven worker, numerical and diagnostic failures identified in round 1.** | `geomind/c6_option_b_parallel.py:237–284` buffers request outcomes, chooses grid errors coarse-to-fine, and captures diagnostics per request. `publish():172–180`, recovery `:443–446`, and causal `:481–490` publish in sequential request order, with causal measurements between forks. The three named counterexamples pass under forward/reverse submission; input-based fuzz also covers causal forks and nested operation tasks (`tests/test_c6_option_b_parallel.py:287–338`). Resource-exhaustion equivalence remains outside this closure: **N1**. |
| **F2 — Medium: optional trajectory allocations ignored retention limits and drive lost its streaming fallback.** | **Core fix resolved; small-allocation follow-up remains.** | `native/c6_option_b/field.cpp:180–197`, `:422–454`, `:478–514` bypass disabled/oversized payloads, stream drive values, integrate medium directly into strided caller frames, and recover from optional payload allocation failures. The counting/refusing-allocator contract passes for no cohort, OFF retired/control, ON, and two cohorts (`tests/test_c6_option_b.py:538–572`). Small optional key/flight allocations are not covered by that fallback: **N2**. Retention counters remain distinct from peak RSS. |
| **F3 — Low: flight deregistration preceded publication.** | **Resolved by code inspection.** | `Store::finish`, `native/c6_option_b/field.cpp:131–153`, publishes `done/value` before removing the registration, under store → flight locking, and notifies after unlocking. Both retained and in-flight lookups compare full bytes (`:95–103`); forced equal-index/different-key tests pass. Publication-test scheduling remains a coverage note: **N3**. |
| **F4 — Low: rounded rules and partial timing ranges.** | **Resolved.** | Raw receipts and `performance_deepdive/REPORT_VALUES.json` agree: 152.628009959 × 30 = **4578.84029877 s**, displayed as 4578.8. Stage ranges cover all measured new runs: stage 1 **8.4149–23.4643 s**, stage 2 **53.3528–182.7318 s**. The report now explicitly includes the final-code overloaded run and its failed runtime rule. A separate memory-description correction remains: **N4**. |

## New numbered findings and fixes

1. **N1 — Medium, nonblocking engineering note: resource exhaustion can still change check publication and exception precedence.** Evidence: `geomind/c6_option_b_parallel.py:223–234`, `:279–283`, `:172–180`; sequential `geomind/c6_r4_field_assay.py:54–61`.

   `_finish()` materializes `[np.array(c) for c in collected]` before `publish()` appends the check and raises its numerical verdict. Sequential `GridSet.run` appends the check, raises `NumericalFailure` when needed, and only then materializes the arrays. If that final allocation raises `MemoryError`, parallel execution omits a passing check, or masks an already determined numerical failure with `MemoryError`. Also, sequential per-grid sampling/trace/reduction happens before the next grid's worker call; parallel execution selects all worker errors before `_merge_block`. A merge allocation failure and a later worker error therefore need not have the same precedence. Causal fork setup is likewise not literally exception-free: clones/copies allocate, although its input-validation failure is identical across forks.

   These are static exception-order counterexamples, **not executed memory-pressure experiments**. They do not reopen the round-1 input-driven counterexamples or invalidate successful-world equivalence. Round 1 expressly did not certify memory-pressure equivalence; this review keeps that same boundary. The report's unqualified statement that every first failure/check prefix is identical should be narrowed accordingly.

   **Follow-up fix (implementer):** defer final array materialization until after check publication and numerical verdict, including capturing a subsequent allocation error without losing that published check. Avoid materializing results for a failed numerical verdict. If universal exception-order equivalence is required, also interleave each grid's buffered worker error with its merge statements and account for speculative fork setup. Add focused allocation-failure tests; do not infer that contract from numerical/worker fuzz.

2. **N2 — Medium, nonblocking continuation of F2: optional key/flight allocation failures still abort a run.** Evidence: `native/c6_option_b/field.cpp:188–192`, `:104–107`, `:434–438`, `:478–483`, `:516`; allocator test `tests/test_c6_option_b.py:560–567`.

   Key construction and `Store::acquire` allocations sit outside the optional-payload `bad_alloc` catches. Failure of a key reserve/copy, `Flight` allocation or in-flight map insertion can still reach the outer catch and return **−1**, even if the direct/streaming integrator could complete. Material also constructs its optional key before checking a zero retention limit. The new test refuses allocations **above 256 KiB**, so it proves large-payload fallback, not fallback for all optional allocations. The report's “an allocation failure in any optional path falls back” and “nothing optional is allocated when disabled” are too broad.

   **Follow-up fix (implementer):** move material admission sizing ahead of key construction; include optional key construction/acquisition in a scoped `bad_alloc` fallback to the appropriate direct path. Preserve lease cleanup and distinguish optional storage from mandatory integrator allocations. Inject failures specifically at key reserve, flight construction and map insertion. Until then, describe the tested fallback as applying to optional payload allocation/admission. No silent wrong result or stuck registered flight was found at these throw sites.

3. **N3 — Low: the new publication contract test uses elapsed time instead of a deterministic waiting barrier.** Evidence: `tests/test_c6_option_b.py:583–600`.

   The follower sets `waiting=true` **before** entering `acquire`; a 50 ms sleep then assumes it has registered its wait. Under delayed scheduling it can instead arrive after non-retained publication and become a new leader, failing `assert(seen)`. Conversely, ordinary execution of the old erase-before-publication implementation can pass this test; it does not force a third requester into the original publication gap. The lock-order fix itself is sound and the forced retained-key collision assertions are useful.

   **Follow-up fix (implementer):** synchronize on actual follower registration, with a bounded wait, and use a test-only publication latch to force the old gap and a competing requester. Keep this test independent of machine load and prove the old publication implementation fails it. Extend the forced-collision case to simultaneous in-flight keys when improving this coverage.

4. **N4 — Low: “at most one admissible value” is not a per-call optional-allocation bound.** Evidence: `evidence/c6_option_b/PERFORMANCE_DEEPDIVE_REPORT.md`, §4; `native/c6_option_b/field.cpp:440–444`, `:368–369`, `:193–196`.

   A medium miss holds its allocated trajectory while the nested uncached integrator constructs a drive trajectory on a drive miss. Those two optional payloads can coexist. Disabled/oversized payload bypass is real, but each store's admission limit does not imply one total optional value per active call. Retained limits also exclude map/list metadata, in-flight key copies, evicted values still held by readers, worker results and Python evidence/serialization buffers.

   **Follow-up fix (drafter):** say one admitted payload **per participating store**, with nested medium/drive overlap and reader lifetime included in the peak-memory explanation. Retain the measured RSS values and the explicit statement that the counters are not an RSS cap. No unbounded accumulation was found within the fixed, isolated-world protocol; this is not a proof of a process-wide RSS ceiling.

## Equivalence, concurrency and scientific scope

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Read AGENTS.md, decisions 0029/0031, `research/rrg/CURRENT.md`, the round-1 review, the revised report including §0/addendum, the original source/test change in 8214f39, the delta `8214f39..ec82c43`, sequential R4 callers, and committed measurements/profile/recheck artifacts. A supporting Codex reviewer received the request verbatim and independently inspected the native delta and residual exception seams. Its findings are incorporated above. This supporting recheck is same-family; the main review is cross-family against Claude's implementation. Per the owner's explicit scope, **PLAN_CURRENT.md was not edited**; disposition is recorded here for the plan owner to reference.

- **Native reuse:** the material key covers every material/carrier input; actual-medium initial state is excluded only because OFF material is independent of it and medium is separately evaluated with its own complete key. Drive keys include dimensions, start/dt, amplitude and all tone phases. Full byte equality, rather than the FNV index, decides reuse. Mutex-protected LRU/accounting and immutable `shared_ptr` values preserve readers across eviction. Flight failure cleanup releases followers. Publication uses store → flight locks; followers release the flight lock before reacquiring the store lock. Material → medium → drive dependencies introduce no reverse wait cycle.
- **Python reuse:** futures publish read-only array results or captured exceptions before their registration is removed; lookup, retention accounting and eviction share the cache lock. Existing R4 digest-based Python identities remain unchanged. Full-byte collision protection applies to the native stores; this change does not upgrade the pre-existing Python digest scheme into a full-byte key scheme.
- **Task determinism:** stage-1 conditions and stage-2 descriptor/before-episode/condition-episode order match `P.operation`. Owners/check lists are private during concurrent work and continuation branches are rebound to the shared journal. Seeds are explicit purpose seeds, with no shared mutable RNG stream. Block reductions and diagnostics retain coarse-to-fine order. Numerical results/checks are deterministic for the inspected input-driven paths; cache counts, LRU order and timings may vary with interleavings.
- **Coordinator:** `waiting()` releases/reacquires the compute token around scheduler waits. At most four grid workers plus one token holder compute per world; four task coordinators can submit up to sixteen grid jobs. Nested task batches are refused, and both pools drain before module/backend restoration. Job/result retention is structurally bounded for this protocol, separately from native/Python byte budgets.
- **Arithmetic:** original pair/site operands, scalar libm and accumulation order remain intact. J/K zero-term skips preserve nonfinite evaluation. Emission skipping requires finite output scale, and negative-zero accumulators replay the original terms. OFF-material misses integrate independent material and fill actual medium separately; material failure replays the inline path to decide the original error code. Direct-stride medium fallback changes destinations, not arithmetic. No new scientific discrepancy was found.
- **Frozen scope:** all **61 unique C1 R006/C2 R002 receipt-bound and STATUS C4/C5 frozen files** match their recorded SHA256s; none intersects the original or delta change. R4 laws/settings, audited RRG sources, comparator, build flags, STATUS, registration, final entropy and committed results receipts are unchanged. The independent world verifies the complete **25-file RRG pin** before execution.

## Credibility of the measured speedup

The speedup is credible as an engineering observation. All ten stored main/fix-pair world dumps exist and match their COSTS SHA256s. The nine stored main/final exact-comparison receipts pass; the overloaded old-control fix run has no separate exact receipt and is used only as its timing control. The fixed-code START identities match ec82c43's sources and the currently loaded binary.

Paired new/old CPU ratios independently recomputed from receipts are **0.661089**, **0.675061**, and **0.663976**. Wall ratios are **0.405132**, **0.441902**, and **0.597369**. Profile receipts support the explanation: CPU **688.672568 → 516.361988 s**, repeated-input native CPU **161.374105 → 8.301261 s** after shared caches. Timings from instrumentation are explanatory measurements, not interchangeable with the uninstrumented world pairs.

The historical “slowest world 152.6 s” means the slowest **unaudited new world in the original measurement set**, not every measured world or the final revision's maximum. Its raw rule is **4578.84029877 ≤ 10800**. Audited smoke 1 is **166.486144084 s**, rule **4994.58432252**. Final fixed code under the disclosed overload is **396.139820292 s**, rule **11884.19460876**, so that particular runtime gate **fails**. The revised report states this correctly. Its **493.8 / 360 ≈ 1.37 cores** calculation is a utilization estimate for that measured CPU demand, not a sufficient future-world guarantee. This review does not use wall time under concurrent heavy jobs to accept/reject equivalence or generalize readiness to unmeasured worlds.

## Independent validation

One suite and one smoke-world run only, under `caffeinate -i -s`, followed by the repository's exact comparator. No extra world, project diagnostic, mutation probe or panel was run. Raw logs, dumps, pytest temporary files and wrapper timing records remain locally under ignored `evidence/c6_option_b/perf_review_codex_r2_20261006/`; they are not staged.

```text
.venv/bin/python -m pytest -q -x tests/test_c6_option_b.py tests/test_c6_option_b_parallel.py --basetemp=evidence/c6_option_b/perf_review_codex_r2_20261006/pytest_tmp
.venv/bin/python tools/c6_option_b_check.py --backend native --parallel --entropy smoke --world 0 --schedule reverse --output evidence/c6_option_b/perf_review_codex_r2_20261006/world_smoke_0
.venv/bin/python tools/c6_option_b_compare.py --reference evidence/c6_option_b/reference_smoke_0/world.json.gz --native evidence/c6_option_b/perf_review_codex_r2_20261006/world_smoke_0/world.json.gz --exact --output evidence/c6_option_b/perf_review_codex_r2_20261006/EXACT.json
```

Suite: **128 passed**, pytest **76.69 s**; wrapper elapsed/awake **77.089628/77.089619 s**. Smoke world: **valid, chain complete**; wrapper elapsed/awake **244.222456/244.222422 s**. Exact comparator: **PASS**, tolerance 0, **3,045,093 numeric values**, **2,847 Boolean values**, **zero error**, **no changed digests**, **no failures**; wrapper elapsed/awake **24.340637/24.340549 s**. Root timing/build/resource fields are deliberately excluded by the repository comparator; scientific fields, checks and identities are compared. This loaded-session wall time is not a performance acceptance criterion. The supporting draft recheck found one wording error about exception immutability; it was corrected before delivery.

| Reviewed artifact | SHA256 |
|---|---|
| Performance report | `c8ff753952b83ac7ee8ecd77799a672553efc9c71b1c56e2a2e64370dfe7ff30` |
| Native field source | `9ebe2acf7dd873d3437b5d645091e41bb9ed1a3e69a56a6fc36ebdfdfff96920` |
| Parallel helper | `6bb6f55dea7b680b85892c3e80443299bfbc35aef7dc2490b110d76681096ad1` |
| Native binary | `b395c5902bb79a9747244665787a7d53f301bd8e6f6344844a3cee5f41099265` |
| Local test log | `fd951bea168c75b27ac85c19474d928c67c7dd0f9852abe09825e8cabd669881` |
| Independent smoke dump | `29d38d3e6710bf1e126f33efcae935ed00c8f75b731a3d6b6606a6eed1a029f4` |
| Local EXACT.json | `87e19191fc13a52eff6bd71a23b6a4875fabcc703963ad77c58fd4ac5f73428b` |
| Wrapper VALIDATION.json | `43bdad5332c4418f49b335dbb0bc2aacf2e583f1d27a44691c112c912f55d341` |

Engineering disposition: **APPROVE_WITH_NOTES** within the unchanged-science, successful-output and input-driven failure scope above. N1–N4 are retained follow-ups, not claims of memory-pressure certification. C6 remains **BLOCKED / R006 STOP**; only the owner can approve a new registered revision. No source or plan changes were made by this reviewer.
