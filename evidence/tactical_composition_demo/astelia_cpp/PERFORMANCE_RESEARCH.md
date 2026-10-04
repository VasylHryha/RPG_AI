# C++ performance compared with this port

Owner requirement: at least **3x** the throughput of freshly executed JavaScript;
**5x** is the target. Caching is a separate convenience and cannot satisfy this
requirement. This is exploratory port work under decision 0028, not a scientific
panel or a milestone acceptance.

## Findings from primary sources

The [C++ Core Guidelines performance rules](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#S-performance)
recommend using static types, moving work to compile time, reducing indirection
and allocations, compact data structures, and predictable memory access.
Their rationale connects simple adjacent memory access to CPU cache behavior.
These recommendations support representation changes; they do not promise a
particular speed ratio.

[V8's property documentation](https://v8.dev/blog/fast-properties) explains shared
HiddenClasses, property offsets and inline caches. V8 can optimize access to
objects with compatible shapes. Therefore, replacing JS property operations
with a C++ string lookup is not inherently an improvement: both the generated
code and its native state representation need examination.

[Clang's ThinLTO documentation](https://clang.llvm.org/docs/ThinLTO.html) describes
whole-program analysis and cross-module optimization. [Clang's PGO manual](https://clang.llvm.org/docs/UsersManual.html#profile-guided-optimization)
describes instrumenting an executable, collecting representative usage profiles,
and rebuilding with those profiles. These are possible later steps, not measured
benefits of the present port. Stronger compiler flags cannot replace fixing a
costly representation. Fast math is excluded to retain combat arithmetic.

## What the code and profile actually show

The native executable runs C++; it does not invoke a JS engine. However, the
initial mechanical translation retained a generic JS-like runtime. That made
the language comparison a comparison of two runtime designs, rather than typed
C++ combat data against JS combat data.

The 10-second sample in `perf_profile_r4b/sample.txt` contains 8,300 main-thread
samples. Selected **leaf** counts below describe that sampled version; they are
not exclusive categories, exact CPU costs, or measurements of the next revision.

| Area | Actual implementation / evidence | Change justified by this evidence |
|---|---|---|
| Arithmetic | `V` tags and `num` surround generated arithmetic. `distanceXY` has 654 leaf samples. | Emit numeric expression trees and direct distance/length operations; preserve conversion fallbacks and operation order. |
| Named properties | Ordered values coexist with string indexes. Property-index hash lookup has 599 leaf samples; `prop` has 182. | Share shapes; cache offsets by shape and field; construct fixed-layout literals without repeated hash lookups. |
| Allocation | Objects and captured cells use individual allocations. `_xzm_free` has 423 samples and `_xzm_xzone_malloc` 209. | Reuse unreachable objects/cells after collection and retain backing-buffer capacities. |
| Spatial maps | Original map operations scanned an ordered entry vector. After hashing, map lookup still has 390 samples. | Maintain an ordered vector plus a hash index, preserving key identity and iteration order. Consider a typed numeric grid if later profiles justify it. |
| Combat loops | `lineBlocker` has 466 samples; `separate` has 208. | Translate measured hot loops into direct numeric code without changing neighbor traversal, ties or collision rules. |
| Closure calls | Sorting/predicates use captured cells and `std::function`. Numerous closure frames appear in the sample. | Prefer direct call sites and typed captures where lifetime semantics permit; escaping functions must remain valid across collection. |
| Memory access | Generic heap objects have separate property, array and map storage. | A subsequent typed unit/world representation can remove more pointer chasing. It is a larger change than compiler flags. |

These conclusions combine code inspection with sampling. A sampled function
name alone does not prove the cause or achievable gain. Every retained repair
must pass behavioral comparisons and uncached timing.

## JavaScript caching question

The original 50-fight timing in `checks_r2` ran fresh JS and fresh C++ processes.
`verify_port.py` called `timed` through `compare.invoke`; `js_host.cjs` created
each world and stepped it to completion. It did not read stored combat outcomes.
V8 optimization and simulation-local caches are different from reusing a saved
fight result; both implementations retain the source's simulation-local caches.

New `benchmark.py` also executes every fight. Both hosts report executed fight
and step counts with zero result-cache hits. The comparison cache in
`result_cache.py` is accessed only by comparison tools and has independent engine,
network and request identities. It invalidates native results when the executable
changes. Old JS results may be reused only after validating pinned sources,
runtime versions, the host and committed evidence.

## Qualification boundary

Five-fight probes diagnose changes; they do not establish the owner's 3x minimum.
The final gate is the unchanged 50 full-army requests, complete behavioral checks,
and explicit zero-cache execution counts. Report wall and CPU time and machine
load. A result below 3x remains below the requirement, regardless of improvement
over the original slow C++ implementation.

The [subsequent self-review](PERFORMANCE_REWORK_REVIEW.md) found that those 50
requests contain no elite, elite-fast or artillery rollout. The revised
[qualification plan](PERFORMANCE_REWORK_PLAN.md) retains that gate and adds
separate branching workloads, internal-work audits, independent geometry
checks and build/cache admission. Current timing wrappers count outer steps
only and do not enforce the minimum speed ratio. Neither these sources nor
the old sample prove that one particular typed layout is optimal; the plan
now checks that choice at an early native-core checkpoint.
