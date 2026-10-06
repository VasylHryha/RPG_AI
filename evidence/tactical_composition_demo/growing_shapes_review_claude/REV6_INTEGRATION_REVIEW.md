CHANGES_REQUIRED

Reviewer family: Claude
Reviewed commit: 437e36a (Codex revision-6 integration import; Codex input HEAD 2bd6965)
Reviewer: Claude (claude-opus-5-5), 2026-10-06, about 25 minutes. Implementation review only. No numeric scores.

Governing design: `DESIGN_0H_REV6.md` as of the reviewed commit (revision 6.5, SHA256 `837d35f35af8b3a642376f8de8900cc47000c023d045c95fa603899e97f37d3d`). Precedence: 19 > 18 > 16 > 14 > 12 > 1–11 > base 5.1.

What was executed: the existing synthetic suite, once, with the command from `REV6_DELIVERY.md` (basetemp and cache moved to the reviewer scratchpad so that nothing in the tree changed). The result was **1 failed, 23 passed, 5 not run** (`-x` stopped the run). The failure is `test_no_execution_grant_and_all_stop_rows`: `ValueError: INVALID: source identity DESIGN_0H_REV6.md` (finding 1). I also ran one plain-Python micro-benchmark of `deepcopy` on a synthetic structure, with no project code (finding 2), and recomputed the seed inventory and donor permutation with plain `hashlib`. No fixture, training, development or evaluation was run, and no source file was edited. `git status` for `growing_shapes/` is unchanged.

## Findings

### 1. HIGH: revision 6.5 (section 19) is not implemented, and the identity pin blocks every run at this commit

**Evidence.**
- `runner/rev6_identity.py:8` pins `DESIGN_SHA256='2abda7e2…'`, which is revision 6.4 (`git show 2bd6965:…DESIGN_0H_REV6.md | shasum` gives `2abda7e2…`).
- The file in the reviewed commit is 6.5 (`837d35f3…`). It was committed in f7f6796, before the import 437e36a.
- `REV6_SEED_INVENTORY.json` `source_sha256` carries the same stale hash.
- `assert_inputs()` therefore raises in `Run.__init__` (`rev6_run.py:24`), `Evaluator.__init__` (`rev6_evaluator.py:24`) and `construct_only()`. The suite fails at HEAD. The report's "29 passed" was measured against 6.4 and does not hold at the reviewed commit.
- Content missing relative to section 19:
  - **19.2, fixture F9** (move: zero-demand, approach, retreat inside range and stop, with the decoded action recorded). It is absent from `rev6_fixtures.py`, from `run_all` and from the stop/receipt plumbing.
  - **19.3, memory-row baselines.** Neither the lawful single-oscillator baseline (one driven oscillator at a fixed site, ω = π, the same decoder) nor the explicit sample-and-hold reference (the last visible angle, held) exists. `Evaluator.panel` has only the 6.4 modes.
  - **19.3, separate reporting** of encoding (the visible 4 s) and retention (the hidden 12 s) is absent.
  - **19.1 and 19.6 labels.** The receipts and evaluator records carry no labels for the choose information ceiling, for move's inability to stop, or for "terminal readout dependence" on the output-channel lesion. Only `G2_sel_label` exists.

**Failure scenario.** Nothing can run as committed. If someone simply re-pins the hash to unblock, fixtures and development would proceed without F9 and without the memory baselines that 19.3 makes mandatory for interpreting the memory row.

**Fix.**
- Implement F9 as a descriptive fixture under `rev6_fixture` entropy, with its own seed/world-id inventory entries added before results.
- Add `single_oscillator` and `sample_and_hold` modes to the memory row, with encoding and retention split. Add the 19.1 and 19.6 labels to the receipts.
- Re-pin `DESIGN_SHA256` and the inventory `source_sha256` to 6.5. Then run the suite once.

### 2. HIGH (cost and feasibility, not validity): each B-path trial deep-copies the full medium, including its 601-frame history

**Evidence.**
- `medium/rev6_design.py:163`: `branch=self.clone(events=False)`. `frames=True` is the default, so `clone` deep-copies every attribute except `native` (`rev6_design.py:69-75`), including the `deque` of 601 `Frame` objects.
- A plain-Python `deepcopy` of a synthetic 601-frame deque with 48 elements and 8 neighbours per frame took **0.75 s**.
- `b_path` runs up to 8 pairs × 13 directions = 104 trials per site and up to 8 sites per check (`rev6_design.py:192-223`). That is up to 832 copies per check, roughly 10 minutes in the worst case. Every unconnected active site whose search is `exhausted` costs about 78 s.
- `feasible()` adds a native clone per candidate. `add()` recomputes `influence()` with no consumer (`rev6_design.py:85`).

**Failure scenario.**
- F5 has 40 growth checks per start, and F7 and F8 add more. Development has 1,600 checks per training × 48 trainings.
- Neither the 2.14-minute fixture proxy nor the 15.74-hour development projection includes this term. The report says that B-path trial cost is "unmeasured". The true cost can be orders of magnitude higher, past the 24-hour reporting line, and it would be discovered only mid-run.
- Results stay correct; the time budget and feasibility do not.

**Fix.**
- The trial needs only positions, gains, roles and the drives, and it consumes no randomness (16.1). Compute the post-trial graph geometrically: the current positions plus the candidate, k ≤ 8 nearest with strict r < 3, using the same tie order as `Medium::neighbors`.
- Alternatively, at minimum use `clone(events=False, frames=False)` together with a native clone.
- Keep the R3-2 test unchanged. Add a parity test (geometric trial = clone trial on random synthetic states) and a timing contract for one 104-trial exhausted site.

### 3. MEDIUM-HIGH: the native assay that produces every G2, F5 and F6 decision has no test and no native-versus-reference parity check

**Evidence.**
- With the default `backend='native'`, `Evaluator.episode` routes every intact, donor, output_channel, receiver, site0 and oracle episode through `gp_assay` (`rev6_evaluator.py:83-85`; `runner/rev6_perf.cpp` `gp_assay`). That covers all G2 contrasts and all F5 A/B/E and F6 β records.
- `test_rev6.py` never calls `bridge.assay`. The `grep` for `assay` finds no test.
- The relay that F4 checks is the **Python** `relay()` (`rev6_fixtures.py:171-173`). The panel uses the **native** relay branch inside `gp_assay`: it computes β as `phase + dt·rate − π·index·dt`, with its own strength/id tie rule.
- The donor-schedule substitution, lesion carry-over and `has_output` in the native path are likewise covered only by reading.

I found no defect in `gp_assay` by reading. It is logically consistent with the reference path:
- carrier `π·index·dt` at the start of the step, with the action decoded after `++index`;
- donor rows from `replay_on_clock(row, offset/π + 0.1j)`, which match the recipient carrier;
- relay β reducing to the site angle, and inactive → 0.

**Failure scenario.** A future edit, or an unnoticed off-by-one-step error in donor indexing or relay β, would bias G2's donor/lesion contrasts or F5's A/B. No gate would catch it, because F4 tests a different code path.

**Fix.**
- Extend F4, which is owner-gated and the right place, to run `gp_assay` with `relay=1` and `relay=2` on a fixture-namespace episode and compare against the Python relay decoded on the same drives.
- Add a reference-versus-native parity record for one perceive episode in the intact, donor and output_channel modes, comparing decisions, angles and paths.
- Report any mismatch as INVALID under the 14.9 measurement row.

### 4. MEDIUM: the F1 PASS rule accepts one transient sample

**Evidence.** `rev6_fixtures.py:128-130`: `reached` is the set of samples with 8 < t ≤ 16 and |β − π/2| ≤ 0.3, and PASS requires only that `reached` is non-empty (plus persistence).

**Failure scenario.** An output that swings through π/2 once and settles elsewhere, or oscillates, passes F1. F1 then unblocks F5 and development on evidence that the scaffold does not carry the step response.

**Fix.** Freeze the reading of "within 0.3 rad … by t = 16 s" before the fixture run. Require β within tolerance at t = 16 s and continuously from the first entry through 16 s, and report the first-entry delay. Record the rule in the fixture receipt; this is a drafter/owner clarification, not a re-analysis.

### 5. LOW-MEDIUM: the run-time identity guard pins process documents and is re-checked for every Run and Evaluator

**Evidence.** `REV6_SEED_INVENTORY.json` `source_sha256` includes `AGENTS.md` and `docs/reviews/…_r6.md`. `assert_inputs()` re-verifies them in every `Run(...)` and `Evaluator(...)` (`rev6_identity.py:15-17`). `run_development` constructs new Runs for each seed over a run of 16 hours or more (`rev6_development.py:33`).

**Failure scenario.** An unrelated `AGENTS.md` edit by another session in the middle of a campaign makes the next seed raise. The whole development returns INVALID, even though no scientific input changed.

**Fix.** Verify the full identity set once at campaign or fixture start and record it in the receipt. Inside the loop, re-check only the scientific inputs (design, base, calibration, frozen C4 code, native images), or check against the recorded campaign-start snapshot.

### 6. LOW: required descriptive reports exist only as raw events

**Evidence.** `late_count` pools outcomes over roles (`rev6_protocol.py:157-172`). `Run.report` has no summary of the following:
- per-role cap/cost with opportunity, attempt and acceptance denominators (12.9);
- cost-limited and cap-limited flags, turnover, count range, uncovered-sensor exposure and path exposure (section 7, G0');
- the wall's maximum radius, penetration time and loss of sensor access (12.10).

**Failure scenario.** None for fixtures. At development, the registered descriptive rows would be missing or improvised after results were seen.

**Fix.** Add a deterministic summarizer over the event and diagnostic ledgers before any development run, with a synthetic-ledger test.

### 7. LOW: the F3 scaffold makes two elements coincide

**Evidence.** `scaffold('F3')` puts S at (4, 0) (`rev6_fixtures.py:30`). F3 then moves O to (4, 0) (`rev6_fixtures.py:155`), so r = 0. The C4 radial term is finite only because of the `eps` clamp and `dx = 0`.

**Failure scenario.** No current invalidity, but the fixture exercises a degenerate pair that the design never needs.

**Fix.** Keep S at 4 − r* (or anywhere not coincident) and O at the sensor.

### 8. LOW: the suite rewrites a tracked evidence file

**Evidence.** `test_construct_only_dry_check_never_integrates` writes `runner/REV6_CONSTRUCT_ONLY.json` on every run (`test_rev6.py:401`). The file is tracked.

**Fix.** Write to `tmp_path` and compare against the committed receipt.

### 9. LOW: native and Python root definitions differ for silent elements

**Evidence.** The Python `graph()` excludes `silent` elements from roots (`rev6_design.py:48`). Native `diagnostics()` does not (`rev6_perf.cpp`, the roots loop). Silence is unused in revision 6, so there is no current effect.

**Fix.** Either forbid `gm_silence` in the rev6 bridge, or add `!e.v.silent` to the native root rule.

### 10. LOW: the execution grant is self-asserted

**Evidence.** `Execution` is a plain dataclass whose `approval_reference` is any non-empty string (`rev6_execution.py`).

**Fix.** Require `approval_reference` to name a committed owner-decision file and verify that file's hash at grant time. This is a guardrail improvement, not a blocker.

## Checked and found consistent with the design (no finding)

1. **Output mask (12.3).**
   - The drive term is skipped for `output` at all four RK4 stages (`rev6_medium.cpp` rhs, used by step/live/assay/future). Python has no separate RHS.
   - Outputs are excluded from sensor offsets, lock sensor partners, `gain_signal`/P_i, coverage and roots, in both Python (`rev6_design.py:91-108,48`) and native (`rev6_perf.cpp` offsets/signal/covered/diagnostics; `rev6_medium.cpp` plv/measure).
   - e_i = 0 through the absence of signals. Effective roots require g > 0, `k_s > 0` and strict `r < reach`.
2. **Fresh graph (14.1).** It is rebuilt from endpoint positions through `gm_neighbors` (strict r < 3, k ≤ 8) on every call. j → i holds when j is in i's list. It is recomputed per site in B-path and after births. D4 uses the forward(R_t) ∪ backward(O) rule, including O's zero-length path, with Python/native parity tested.
3. **B-path (12.1, 14.2, 18.3).**
   - The fair pointer advances every check.
   - Search is 8 pairs × 13 directions at r* = 0.556, ordered 0, +15, −15, … ±90.
   - All six named conditions are evaluated on the post-trial graph, with post-trial roots.
   - Clearance is measured against the pre-trial elements. Cap and cost are checked only after the geometry passes. The live state is untouched because the trial runs on a clone.
   - Codex's R3-2 configuration (u (−2.9, 0), a (0, 0), output b (3.1, 0), seven distractors near (1, 2.72), nine padding elements near (1, 2.85), sensor at (−4, 0)) is a test. It asserts REJECT, with `edge_a_to_new`, `paths_kept`, `deficit_or_connect` and `clearance` true and `new_reached` and `a_reached` false, and it checks byte-identical native state, RNG and Python state.
4. **Growth order and schema.** The order is D1 → D4 → D3 → B-out → B-path → B1, with quotas 1 + 2 + 2 and 200-step protection. The terminal set is accepted/cap/cost/placement/exhausted/no_output/no_root/quota, one terminal per request.
5. **Output and templates.** There is a singleton O (cap enforced at add, load and template). `rev6_template_v1` includes the role and version ids in the hash, roles survive clone/save/load/copy, and 5.1 templates route to the legacy loader unchanged.
6. **Controls.** Control M mirrors only the intact run's accepted B1 count at the same step index, with a random site spiral and phase from `matched/<arm>/<k>`, the same cap/cost/blocked rule, and unmatched slots logged and never repaired. Control U enqueues accepted B1 with the base FIFO and a PCG64 `control_u` key.
7. **Evaluator and statistics.**
   - The donor permutation is the full-SHA-256 rank. I recomputed it: all 128 entries match. Donor drives are replayed on the recipient carrier, and scoring uses the recipient's world.
   - The output-channel lesion zeroes the phase coupling into O at every stage.
   - The paired t uses `ddof=1`, 127 df, α = .05 for perceive and α/3 for the secondary tasks. A positive, negative or zero constant gives above, below or neither; any non-finite value gives INVALID.
   - G2 is the conjunction of the four lower bounds with ≥ 6 / ≤ 2 cuts. G0 requires matching, lower bound > 0 and higher coverage; it FAILs at an upper bound < 0 in ≥ 6. G0' uses the inclusive 25,600–32,000 s window, an OLS slope per 100 episodes, and placement/exhausted/protected-over-budget.
   - All 17 stop rows are present.
8. **Seeds.** I recomputed all 2,842 inventory seeds: big-endian, `0h-rev6/` prefix, 0 mismatches. Recovery uses `default_rng(entropy(master, "kick:<index>"))` with the inherited little-endian `entropy`, identical to `runner/run.py:122`. The F5, F7 and F8 keys match 18.1 and 18.6.
9. **Fixtures.**
   - The F1a/b/c and F2b coordinates, gains, step time and horizons match 14.3, 14.4 and 16.1. F5(ii) is the literal seven-member start with ids 0–6, protection and the counter at 7.
   - The F5 checkpoints are 40/45/50, with 10 recipient episodes (768–777) and their paired donors (778–787), A/B/E pooled over 30, and the missing-O → 0 rule.
   - F6 uses six checkpoints, pairs 788 + j ↔ 798 + j, the hidden window 40–159, R < .05 as undefined, and at least 5 defined pairs. F7 uses its own growth key and a regenerated F5(i) state. F8 is the live F5(i) clone with r̄ = .5, 20 move then 20 memory episodes, and its named keys.
   - All execution paths require an explicit grant; the default `Execution()` is denied.
10. **Native/Python equivalence.** It is tested for the live endpoint step (`contract`), the frozen future and C4 parity. The assay gap is finding 3.

## Verdict rationale

Finding 1 blocks execution at the reviewed commit and leaves the 6.5 obligations unimplemented. Finding 2 invalidates the cost projection that the owner's fixture and development approvals depend on. Finding 3 leaves the code path that produces every G2/F5 decision unverified by any gate. Fix 1–3, and preferably 4, then run the suite once and request a single re-review of the delta.

---

## Delta re-review (bba9348)

READY_FOR_FIXTURES

Reviewer family: Claude
Reviewed commit: bba9348 (Codex's revision-6.5 repair). The delta reviewed is `git diff 915dc32..bba9348 -- evidence/tactical_composition_demo/growing_shapes`.
Governing design: `DESIGN_0H_REV6.md` at SHA256 `0f62e13246bbfc02ee79d785dff1659d7ea7d0b021e47f57d5ec46bea926794b` (6.5 with 19.7 and 19.8), which equals the pinned `DESIGN_SHA256`.
Reviewer: Claude (claude-opus-5-5), 2026-10-06, about 15 minutes. No numeric scores.

**What was executed.**
- I ran the synthetic suite once, `pytest -q -x runner/test_rev6.py`, with the temp directory in the reviewer scratchpad and the cache disabled. The result was **47 passed in 1.17 s**.
- `git status` for `growing_shapes/` was identical before and after the run.
- I recomputed every hash in `REV65_SOURCE_IDENTITY.json` with plain `hashlib`; all match.
- No fixture, training or panel was run, and no source file was edited.

The verdict means the code is ready for the owner's separate F1–F9 fixture decision. It is not an acceptance and not an owner approval. Notes D1–D3 below should be fixed before **development**; none of them blocks the fixtures.

### Status of findings 1–10

1. **Resolved.**
   - The design pin is now 6.5 (`rev6_identity.py`), and the suite passes.
   - F9 exists as a descriptive, decoder-only fixture (`rev6_fixtures.py` `F9`, `F9_CASES`, world ids 808–811 reserved, four new seed keys). The inventory now has 2,846 keys.
   - The memory row gains `single_oscillator` and `sample_and_hold` modes (`rev6_evaluator.py`), the `memory_windows` encoding/retention split and the `INTERPRETATION` labels for 19.1 and 19.6 (`rev6_reporting.py`).
   - The single oscillator matches 19.8. It is an ordinary element, so its drive is not masked. It sits at `SITES[permutation(episode)[0]]`, which is the cue's permuted physical site, so K_d = 1. Motion is off (`geometry_rate=0`). g = 1, ω = π, and the initial phase equals the carrier offset, so the relative phase is 0. Decoding is direct with C = 1. It is a fresh frozen copy per episode, evaluated on the same panel with the same estimator.
   - Sample-and-hold holds `phase − π·t_start` of the last active drive, which is the last visible angle.
2. **Resolved.**
   - B-path trials and admission are position-only (`geometry`, `geometric_graph`, `geometric_trial`, `Rev6Medium.feasible`). No medium or native clone happens on a rejected trial; a test monkeypatches both `clone` methods to fail.
   - Neighbour selection is identical to `Medium::neighbors`. Python sorts all non-silent candidates by (r, array index) and takes k, then applies strict r < 3. Native first filters to r < 3, then partially sorts by (r, index) and takes k. The two give the same set, because every r < 3 candidate sorts ahead of every r ≥ 3 one.
   - `hypot` is sign-symmetric, so the distances are bitwise equal. Ties fall back to array index in both, and a newborn is appended at the last index in both.
   - The admission cost, `N + 1 + 0.1·undirected pairs`, is the same expression as `gm_cost` with `undirected_cost`.
   - Tests:
     - random states with a deletion and a silenced element, comparing the graph against `influence()` and all six checks against a native clone;
     - an exact equal-distance tie case at the strict r = 3 boundary;
     - admission cost against a native clone;
     - the unchanged R3-2 REJECT case.
   - The static timing gives 0.03–0.12 s per exhausted 104-trial site (`REV65_BPATH_TIMING.json`), down from about 78 s.
3. **Resolved.**
   - `gp_assay` and the new bounded `gp_assay_synthetic` share one templated `assay_run` loop.
   - Seven three-observation contracts on a nonzero carrier (t₀ = 1 s) compare the native result against the Python reference on angle, magnitude, choice, paths, has_output, drives, final state and index. The modes are intact, donor replay, output-channel lesion, receiver lesion, site0, oracle and empty.
   - F4 now also runs native-versus-reference parity on fixture episode 768 (donor 778) for intact, donor, output_channel, site0 and oracle. A mismatch raises INVALID and blocks F5.
   - `has_output` for the relays was aligned between native and Python. Decisions now record magnitude and choice.
4. **Resolved.** `step_response` needs all 80 samples in (8, 16] with t = 16 present, and every sample from the first entry through 16 s must be within 0.3 rad. The first entry and the delay are reported. Tests reject a later excursion, a miss at the deadline and a missing deadline sample. This matches 19.7.
5. **Resolved as specified by 19.7.** `AGENTS.md` and review files are out of scope. `Execution.start` checks the identity once, and the snapshot is reused by `Run`, `Evaluator` and `Harness` and recorded in every seed and fixture receipt. A test checks that an `AGENTS.md` edit is ignored and a design edit is caught. A scope gap remains; see D1.
6. **Resolved.** `rev6_reporting.descriptive` gives, for the whole run and the inclusive late window:
   - per-role opportunities, attempts and acceptances;
   - cap/cost rates with explicit denominators;
   - trial-failure counts;
   - cap-limited and cost-limited flags;
   - turnover;
   - count range;
   - uncovered-sensor exposure with warm-up undefined;
   - path exposure;
   - the wall's maximum radius, penetration time and sensor-access loss.

   The "flat count with unmet demand" label is applied in `Run.report`. The `sensor_access` and `covered_sites` fields were added to both the native and the Python diagnostics.
7. **Resolved.** F3 now places S at 4 − r* and O at the sensor (4, 0).
8. **Resolved.** The construct-only test writes to `tmp_path`. The tracked receipt stays byte-identical; it is compared except for F3 and F6 and is now stale for F3, F6 and F9 (see D3).
9. **Resolved.** Native roots require `!silent`. A contract test of a silenced root passes in both native and Python.
10. **Resolved as a guardrail.** `approval_reference` must be a repository-relative `docs/decisions/*.md` file whose bytes equal the HEAD blob; its hash and commit are captured. Any existing decision record satisfies the format, so this binds identity, not authority, and the authority booleans remain the actual gate. That is acceptable for a guardrail.

### New notes from the delta (none blocks fixtures)

**D1. MEDIUM-LOW: the execution-start identity omits executed inherited inputs and the reused calibration.**
- *Evidence.* `REV65_SOURCE_IDENTITY.json` covers the rev6 sources, native images, `medium_c.h`, `perf.h`, the world dylib, the design and the seed inventory. It does **not** cover:
  - `runner/development_20261006/CALIBRATION.json`, which normalizes every panel score;
  - the base `DESIGN_0H.md`, which governs every unchanged rule;
  - the inherited 5.1 Python modules that execute live: `medium/design_0h.py` (lock, timers, adapt, coverage), `medium/medium.py`, `runner/protocol.py` (entropy, permutation, bindings, oriented, Calibration), `runner/control.py` (the U queue) and `world/world.py`.

  Before the repair, the inventory pinned `CALIBRATION.json` and `DESIGN_0H.md` at run time; the repair dropped both. The 202-file baseline is enforced only by a unit test, which does not cover `DESIGN_0H.md`, not at execution start.
- *Failure scenario.* A changed calibration or inherited module between the suite run and a development execution would alter scores or rules with no INVALID.
- *Fix.* Add these files to `REV65_SOURCE_IDENTITY.json`. They are frozen 5.1 inputs, so pinning them causes no churn. This is required before development; it is harmless to do now.

**D2. LOW: the F6 memory baselines are evaluated six times on identical inputs.**
- *Evidence.* The baselines do not depend on the checkpoint, yet F6 runs them for each of the six checkpoints. That gives 60 records per baseline from 10 unique episodes, which are then pooled (`rev6_fixtures.py` `F6`).
- *Failure scenario.* The JS correlation value is unchanged by replication. The "at least 5 defined pairs" rule, however, counts duplicates, so a single defined unique episode becomes 6 pairs and clears the threshold. The rule is descriptive only.
- *Fix.* Evaluate each baseline once per recipient episode (10 episodes), or report the unique-episode count and apply the minimum to it.

**D3. LOW: the committed `REV6_CONSTRUCT_ONLY.json` receipt predates the F3, F6 and F9 recipe changes.**
- *Fix.* Regenerate it once as a new, labelled receipt (for example `REV65_CONSTRUCT_ONLY.json`) rather than editing the historical file.

### Verified with no new defect

- **Geometric trial semantics.** The post-trial roots include the newborn (g = 1, element), `paths_kept` iterates all drives' roots, the deficit uses post-trial forward and backward sets, and clearance is measured against pre-trial positions.
- **Order of checks.** Cap/cost is checked only after all geometry passes, and only an accepted placement mutates the medium.
- **Sample-and-hold and the encoding cue.** They use the same carrier arithmetic as `memory_windows`.
- **Native diagnostics.** `covered_sites` reports null during warm-up (fewer than 101 frames), matching Python.
- **Reporting with chunked ledgers.** `descriptive` accepts the string keys produced when chunked JSON ledgers are reloaded.
