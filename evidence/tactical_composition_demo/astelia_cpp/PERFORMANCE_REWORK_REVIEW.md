CHANGES_REQUIRED

# Native performance rework — adversarial self-review

Reviewer family: Codex (same author/implementer; **not independent acceptance**).
Reviewed on 2026-10-04 at HEAD `797ced26ff95caa5f84ea71e9bb247422068b5c5`,
with the uncommitted performance working tree. Scope: source, architecture,
tooling, existing measurements and proposed contract. No project code, tests,
benchmarks or simulations were run. Existing JSON evidence was read only.

The current engine is **NOT_READY**. The revised plan is a draft for owner
review; its corrections do not repair the working implementation or prove that
the chosen structure reaches the performance goal.

## Findings, in priority order

### 1. High — the timed workload omits the expensive branching AI

`checks_r2/speed_fights.jsonl` contains 50 mirror fights, all 20 seconds:
16 alone, 15 novice, 13 regular and 6 veteran. Opponents are fixed formations.
None configures elite, elite-fast, look-ahead or artillery rollout. The level
definitions at [formation_sim.js:304](../astelia_snapshot/formation_sim.js#L304)
confirm that these four timed profiles have no look-ahead; veteran artillery
planning does not enable `artyRollout`.

Consequently, even a large improvement on these 50 would leave the main
fork/network/rollout workload unqualified. The previous plan's instruction to
report elite cost could not be fulfilled by this input file.

**Plan correction:** retain the original 50 gate and add separately timed,
predeclared elite, elite-fast and game-rule artillery-rollout groups. Each
must actually invoke its intended search/inference paths and reach the 3x
minimum; a fast basic aggregate cannot hide a slow branching group.
**Implementation repair remains open:** workloads, internal counters and timing
group support do not exist yet.

### 2. High — grid assumptions can exclude genuine game collisions

Game melee bodies have radius 16 ([formation_sim.js:406](../astelia_snapshot/formation_sim.js#L406)).
Both blocker grids pad by 12, despite accepting perpendicular distances below
`u.r + 1.5` ([source:850](../astelia_snapshot/formation_sim.js#L850),
[source:894](../astelia_snapshot/formation_sim.js#L894)). Consider a horizontal
segment from (20,53) to (200,53), with an intermediate radius-16 blocker at
(100,39). The blocker passes the geometric hit threshold, but live-grid row
zero is omitted because floor((53−12)/40)=1.

Separation uses cells of 24 and a 3×3 neighborhood
([source:2844](../astelia_snapshot/formation_sim.js#L2844)). Two radius-16 bodies
at (23,100) and (48,100) overlap by 7 but lie in columns zero and two, so this
pair is omitted. The optimized generators retain both assumptions
([generate.cjs:223](generate.cjs#L223), [generate.cjs:250](generate.cjs#L250)).
These are inherited source defects, not evidence that the original exact port
failed its matching contract. `cx*4096+cy` also needs coordinate bounds to be
collision-free; it must not be generalized to arbitrary configured arenas.

**Plan correction:** derive query reach from actual radii and use independent
all-body/all-pair geometry oracles with boundary, movement and custom-radius
cases. Record the native-only repairs before timing; preserve frozen JS.
**Implementation repair remains open:** the current working generator still
retains these assumptions. Counterexamples above are analytical, not executed.

### 3. High — the timing tool does not enforce the requested performance gate

[benchmark.py:25](benchmark.py#L25) checks fight counts and the reported cache
count, but not output count, summary schema, errors or successful completion.
[Its return condition:60](benchmark.py#L60) checks optional equality and total
outer-step equality; it has no minimum-speed condition. Thus a successful exit
cannot mean the owner's 3x gate passed. The existing r9 rows were inspected:
all 50 rows exist and none is an error, so this finding does not invalidate
that historical measurement. It prevents trusting the tool as qualification.

[benchmark_host.cjs:7](benchmark_host.cjs#L7) counts exported steps only.
Internal playouts call the lexical `step` directly
([source:3170](../astelia_snapshot/formation_sim.js#L3170)), so their work escapes
the wrapper. `cache_hits:0` is a constant emitted by hosts whose caller paths
bypass the result cache; the constant alone does not prove execution coverage.

**Plan correction:** validate complete successful output and record internal
work, source/build identities and separately reported timing groups. Qualification
must explicitly fail below 3x. Preserve r9 as below-minimum historical evidence.
**Implementation repair remains open:** current tooling lacks these gates.

### 4. High — relaxed outcomes conflict with strict evaluation/work counting

[verify_cached.py:71](verify_cached.py#L71) aborts on the first difference, which
prevents classifying the remaining coverage cases after an allowed numerical
change or bug repair. It also counts matching historical errors separately
from completions; neither may become a successful native fight by relabeling.
The benchmark's total-tick equality requirement likewise rejects a legitimate
different elimination time. Conversely, merely dropping that condition could
credit faster completion or fewer active bodies as faster engine execution.

**Plan correction:** preserve strict tools for explicit equivalence claims;
add exhaustive relaxed diagnostics plus independent mechanics checks. Audit
configured budgets and actual work; use matched-state, fixed-operation probes
to support engine-cost claims while retaining end-to-end timing. Natural tick
differences alone neither fail correctness nor establish engine speed.
**Implementation repair remains open:** an exhaustive native evaluator and
the work audit must be implemented.

### 5. High — source/build/cache admission is incomplete

[result_cache.py:28](result_cache.py#L28) keys native results by executable and
network bytes, but does not verify that current sources produced that executable.
[verify_cached.py:37](verify_cached.py#L37) records current source hashes without
linking them to the binary. An edited source plus an old binary/cache can thus
be reported together. This is a provenance mismatch, even if the old binary's
cached result is internally consistent. [build.py:48](build.py#L48) records
commands and binary hash, but not a complete source-to-binary admission manifest.

[Cache.load:63](result_cache.py#L63) accepts any nonempty list of dictionaries
whose final dictionary lacks `step`, if its stored checksum matches. It does
not validate summary fields, trace ordering or operation-specific semantics.
For example, a checksum-valid `[{}]` meets this shape test. Checksums detect
accidental corruption; they do not authenticate a recomputed edited result.

**Plan correction:** complete build admission before cache lookup; validate
schemas, frame order and final result, and bind evaluator/codec versions. Keep
cache tests separate from fresh correctness/determinism. Historical imports
retain their pinned committed-evidence provenance.
**Implementation repair remains open:** current cache and build tools need work.

### 6. Medium — layout selection was premature

The r4b profile describes an older compatibility runtime, not a typed native
engine. It justifies investigating dynamic lookup/allocation overhead, but
cannot prove a particular record/column split is optimal. Energy, protection,
casting and dodge state appear in game ticks; classifying these fields as cold
without measuring their access pattern risks adding unnecessary indirection.

**Plan correction:** start with typed contiguous state, inventory accesses and
compare bounded layouts/copy costs at a core vertical-slice checkpoint. Keep
the full rewrite estimate provisional and revise before porting the rest.
**Validation remains open:** no typed layout has been implemented or measured.

### 7. Medium — branch and entity lifetimes needed explicit contracts

The source removes dead units from `w.units` each tick
([source:3011](../astelia_snapshot/formation_sim.js#L3011)); an append-only native
slot array can instead retain all historical spawns and copy them on every
branch. Reusable branch buffers also need a depth/lease rule: a nested rollout
must not overwrite its parent. A position-only copy or stale world-local ID
resolution would pass basic fights while corrupting complex skills.

**Plan correction:** a clone/reset ledger, world-local identity resolution,
branch leases, retained-reference/reclamation rules, memory measurements and
nested/repeated-reuse isolation checks. No silent capacity truncation.
**Validation remains open:** these are required typed-engine design checks,
not demonstrated bugs in an engine that has yet to be written.

### 8. Medium — current source cannot inherit previous receipts

The last complete optimized measurement is r9: **1.169x wall**, below the owner's
minimum. Later changes to lazy capture cells, field writes and geometry have
no complete validation receipt. Fourteen earlier focused passes do not cover
the current source. The reviewed dirty tree also includes unrelated composition
artifacts, which were left untouched.

**Plan correction:** preserve version-specific claims, admit the new build,
finish the approved change batch and run its appropriate checks once. Do not
promote a historical receipt, a local self-review or a compiler optimization
flag into engine acceptance.

## Disposition

The drafter repaired the plan in revision 2 and recorded the causes in its
self-audit. README/research guidance now states the missing branch qualification.
No implementation defect was repaired in this review: plan-first scope remains
in effect. The new engine, tool repairs, fresh checks, >=3x measurements and
independent Claude review are outstanding. There is no evidence yet that the
current design is the best achievable implementation.
