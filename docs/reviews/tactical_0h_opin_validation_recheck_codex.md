CHANGES_REQUIRED
Reviewer family: Codex
Reviewed commit: 47b578cf256105acc72cbabea86e2bfdb43e1034
Reviewed scientific execution pin: e66c8969d434f475c4289b6d09b048940d148055567c7c1acfc8bd2652fde357 (revision 7.11)
Date: 2026-10-07

Owner request, verbatim:
> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Scope: `OPIN_VALIDATION_REPORT.md`, `SUMMARY.md`, all 30 `batt*.log` files, the four earlier baseline/C2 `assay_pilot_*.log` files, `RAW_FILES.json`, `OPIN_RESEARCH_MEMO.md`, `pilot_common.py`, `pilot_c2_opin.py`, `pilot_baseline.py`, and `DESIGN_0H_REV7.md` §19 including the overriding §19.6. Read-only git/history, receipt, hash and stored-data checks; no project imports, simulations, fixtures, panels or tests executed. Six stored validation traces were inspected. Only this review file was created.

Report SHA256: `ac4d6142dc03aee007b3b2cf128bff9dbe421870607be45d7c75b7de7e4ddd6d`.
Summary SHA256: `4d1804eec54607e6e547f1cacd102ed29ff3959b3cd39127dfeb703c220f17c3`.

The counts are correct and C2 is a promising candidate. It is reasonable to recommend an owner-approved, preregistered evaluation of C2. The present evidence does not establish robust improvement, unique necessity of the root direction, or a proved bridging limit. The blocking work is correcting those claims and defining the replacement gate before anyone builds on this recommendation. These are pilot observations; historical fixture verdicts remain unchanged.

## Verified evidence

- All 34 detailed table rows agree with their logs at the displayed precision; the aggregate counts also agree. In particular, the rounded seeded key-3 B of 0.299 is below 0.3, not a pass. All 30 manifest-listed raw traces match both their byte counts and SHA256 hashes.
- Matched baseline versus C2, distance 1: empty start 2/5 versus 5/5; seeded start 1/5 versus 3/5. There are five fail→pass changes, no pass→fail changes, three shared passes and two shared failures. Both-start success on the same key set is 0/5 versus 3/5; this is a separate quantity from pooling the ten starts.
- Direction controls on keys 0–2: toward 5/6, opposite 3/6, perpendicular 3/6. Opposite and perpendicular each pass twice in the empty start and once in the seeded start. Distance 0.5 fails and 1.5 passes for empty key 0 only.
- The worktree currently has HEAD `fd2182681ee8ed7b7b3a0772d69de898a8aa17c2`. All 69 scientific files, including the copied native images and pre-§19 design, match its execution pin. The worktree's three modified pilot scripts currently equal the three scripts committed at the reviewed commit.
- The alternative training intervals actually used are 13,100,000–13,100,049, 13,200,000–13,200,049, 13,300,000–13,300,049 and 13,400,000–13,400,049. None overlaps any world pool in `REV7_SEED_INVENTORY.json`. Development slots occupy 11,000,000–11,151,999 with gaps; F5/F7 growth uses 12,000,000–12,000,049 and F8 uses 12,100,000–12,100,039. The range claim is supported for these registered schedules, not an assertion that arbitrary future IDs above 13 million are reserved for pilots.

## Findings and concrete fixes

### R1 — HIGH: the proposed multi-key gate is not yet an operational criterion

Report §5 recommends adoption and gives "five key sets" with an unspecified pass-rate criterion. Design §19.5 still blocks development when either start fails its existing F5. Pooling starts could conceal seeded-start failure; choosing a threshold after observing 3/5 would make the replacement gate accommodate this outcome. A multi-key gate also leaves downstream F6/F7/F8 unclear: the harness retains particular F5 checkpoints/live state for later fixtures.

**Fix, drafter/owner:** amend and review the design before implementation or formal execution. For a bounded engineering gate, my recommendation is **five newly reserved key sets, with a complete per-key F5 PASS in every key of each start separately**. Retain A ≥ 0.3, B ≥ 0.3 and max E ≥ 0.5 per run, plus the existing start-specific birth and validity requirements. Do not average A/B/E across keys to manufacture passes, pool the starts, drop failed keys, replace keys, or run until the target count is reached. INVALID blocks the gate; FAIL in either start blocks development and requires the drafter's failure report. Define the downstream checkpoint policy in advance: either all keys proceed where required or a named key is selected before results; never select a passing checkpoint afterward. Preserve F1–F4/N1 and M/U requirements.

This is an engineering consistency gate, not proof of a high population reliability. Five successes have an illustrative one-sided exact 95% binomial lower bound of only about 0.549, under independent, representative trials. If a population claim is wanted, the owner must first choose the minimum acceptable reliability and the drafter must preregister a suitable sample size and confidence criterion. A 3/5 or 4/5 rule is a deliberate relaxation, requiring an explicit rationale and owner approval; it is not justified merely by adding keys. None of these ten existing training configurations or their reused assays is fresh qualification evidence.

### R2 — MEDIUM: descriptive improvement and direction contrasts are over-read

The headline "VALIDATED AS AN IMPROVEMENT," §2's "real improvement," "merely moving O off-centre does not help," and §3's "other directions do not" exceed the evidence. Opposite/perpendicular do work in several configurations. Perpendicular even rescues seeded key 1 where toward-root fails. Equal aggregate counts to baseline do not establish equivalence or absence of benefit. There is no replicated isolation of first-root identity versus distance to eventual mass, task-driven site ordering, phase initialization or birth timing.

For calibration, nominal exact paired McNemar/binomial two-sided p-values are 0.0625 pooled, 0.25 empty and 0.50 seeded. Toward versus opposite has two gains and no losses (p = 0.50); toward versus perpendicular has three gains and one loss (p = 0.625). These are exploratory diagnostics, not registered verdicts. Treating ten starts as independent is questionable: each key shares training worlds across starts and all keys share the same assay panel. Key 0 also informed the design. Restricting the baseline/C2 comparison to alternative keys leaves four gains and no losses (nominal p = 0.125). Illustrative 95% Wilson intervals are wide: 8/10 about 0.49–0.94, 3/10 about 0.11–0.60; seeded C2 3/5 about 0.23–0.88. No significance threshold was registered and none is imposed retrospectively here.

**Fix, drafter:** say "observed paired improvement in this exploratory battery; toward-root had the highest observed pass count; direction dependence is a hypothesis requiring further controls." State shared worlds, reused assays and outcome-informed key 0. One run per fully specified deterministic seed/configuration is not inherently defective; repeating the identical seed would not supply independent robustness evidence. Broader independent configurations, rather than repetitions of the same deterministic trajectory, are needed. Replace "the threshold lies between 0.5 and 1.0" with the two observed outcomes: monotonicity and a single sharp threshold were not established by three offsets.

### R3 — MEDIUM: placement is a defensible claim boundary, but the mechanism is not identified

Report §3 converts the memo's inference into settled face placement and a universal inability to hold a long filament. Nearest-element distance is not a cluster-face measurement, hop count, force balance or equilibrium test. The stored recorder contains only O, four nearest distances, element count, active sites and path membership; it cannot determine which neighbor forms the last strong edge or whether O lies inside a cohesive cluster. Moving a pinned body can reshape the cluster itself. Removing the seeded literal O at (−0.5, 0), then inserting a new O at t = 20 with an inherited mean/random phase, changes timing/phase as well as position. The empty C2 O appears at t = 40. This is a policy package, not a pure fixed-state displacement experiment.

There is also a concrete literature mismatch. [O'Keeffe et al. (2017), equations 3–4](https://arxiv.org/html/1701.05670v2) supports the constant-magnitude spatial attraction analogy. But [Lee et al. (2021), equations 1–2](https://arxiv.org/html/2103.11584v1) uses spatial attraction proportional to separation, not the same constant-magnitude attraction with only a cutoff added; its phase coupling is globally summed. The memo must disclose those differences. Neither paper proves impossibility for this driven, pinned, capped-neighbor, growing system with its distinct phase law and sensor forces. "Curvature flow" is a heuristic analogy, not a derived dynamics theorem.

**Fix, drafter:** retain "C2 changes placement infrastructure; it does not demonstrate new fixed-gap bridging capability." Qualify face placement, geometric limits and disc cohesion as plausible explanations of the tested failures. Correct the finite-cutoff equation comparison. To distinguish mechanisms later, preregister the memo's closure/end geometry, last-edge identity/degree/coefficient, hop count, hold/break duration, contact/inside-cluster checks and matched initialization controls. A no-growth control and site-order permutations remain unperformed; do not say all memo conditions/tests were satisfied. No new run is required to correct the current wording.

### R4 — MEDIUM: scientific pin verified; per-batch pilot provenance remains incompletely bound

The statement "every pilot ran ... at fd21826" is false for the four earlier `assay_pilot_baseline_*`/`assay_pilot_c2_opin_*` receipts: their `START_IDENTITY.json` records HEAD `553369eef6caf3192624d7fec9d862837c2bbba4`. Their scientific pin is identical to fd21826, so this does not invalidate the metric comparison. The other 30 receipts record fd21826. These snapshots bind the scientific baseline, not the monkey-patched pilot functions.

Git history fd21826→47b578c records three script changes together: alternative keys/worlds and the 160-decision guard in `pilot_common.py`, key parsing in `pilot_baseline.py`, and distance/key/direction arguments in `pilot_c2_opin.py`. The earlier logs lack `keyset`; later logs contain it and the direction tags/O coordinates match the implemented rotations. This is consistent with the stated sequence, but a single later commit and result-only logs cannot independently prove the exact script bytes or the time of the direction edit. Earlier assays predate the new guard; §19.6 correctly limits their status to exact baseline metric reproduction, rather than full Harness equivalence.

The alternative receipts' `PRE_EXECUTION_SEED_INVENTORY.json` still lists the original registered inventory, not the `/altK` master keys or actual 13-million training worlds. Its DISJOINT status therefore does not certify the pilot entropy substitution. All assays remain `F5_PAIRS` 10,000,768–10,000,787. Sampled trace episode events confirm the alternative training intervals, but assay reuse must be explicit.

**Fix, drafter:** correct the two HEAD groups, disclose unpinned pilot overlays and distinguish current byte equality from historical execution proof. Add a separate provenance supplement with the three current script hashes, per-log mapping, arguments/environment, actual key recipes/world intervals and any contemporaneous command/source snapshots that exist; mark unavailable historical hashes as unavailable. Do not retrofit or edit committed start receipts. Future pilots should bind actual pilot sources and inventory before launch, including direction/distance and the phase/RNG branch. Relabel the seeded baseline in the summary as "legacy seeded pin (−0.5, 0)"; it is not an origin pin.

### R5 — MEDIUM: per-site response and checkpoint retention promised by §19.6 are missing

`pilot_common.py` adds the stream-length guard, but collapses A/B over all checkpoints/pairs and retains only averaged per-site E. Its gzip output does not retain own/donor/lesion decisions or per-pair/checkpoint A/B/E summaries. Thus §19.6 N3's retention requirement and the memo's per-site response condition remain open. E alone measures reachability, not site-specific causal response. For example, empty C2 key 3 has E = [0.3333, 0.7, 0.8, 0.2, 0, 0, 0, 0]; a max-E gate can pass while four sites never have a strong assay path. Seeded C2 key 4 passes with E = [0.5, 0.7, 0, 0, 0, 0, 0, 0.7]. This is allowed by the existing F5 claim, but does not establish broad sensor coverage or processing.

**Fix, drafter:** report the available complete E vectors and per-site training connectivity, with the selected-root/site bias and max-E scope. Mark missing causal response data unavailable, rather than claiming the check was completed. Future instrumentation should retain checkpoint × assay-pair summaries, active/connected site exposures and the per-site/input interventions needed to identify A/B contributions, plus the selected root, insertion pin and phase/RNG branch. Extra coverage gates would change the design and require prior owner approval; do not silently impose them on these pilots.

### R6 — MEDIUM: seeded fragility is supported, but a narrow miss and reference reliability need separation

Seeded C2 key 1 has max E = 0.4666667, late training connectivity 0.401 and no strong path at the final frame (nearest distance 1.452). Key 3 is a substantive collapse: E is zero, late connectivity is zero, final nearest distance is 2.338, and B = 0.2993606. Key 4 passes the averaged assay gate despite late connectivity only 0.222. Training connectivity, averaged assay exposure and end-state stability are distinct measurements. Neither changing the cutoff to rescue key 1 nor dismissing key 3 as unlucky would be justified.

**Fix, drafter:** keep both failures and their margins, and downgrade the seeded protocol from a reliable reference to a literal-scaffold condition with variable outcomes. Provide a stored-event diagnostic of root timing/site, budget/deletion history and loss of late connectivity where available; causal attribution awaits a preregistered matched-start study. Do not retrospectively change the six-element scaffold or recorded verdicts. State that the original 7.11 result is conditional on its key, rather than claiming it was "largely luck" or that its failure proved a general geometric limit.

## Disposition

Claude, as drafter, owns the report corrections and design self-audit. Before adoption/implementation, address R1 with an explicit owner-approved gate amendment and address R2–R6 with corrected claims, provenance and clearly open measurements. Further runs are not authorized by this review. The candidate can remain C2; the evidence does not require immediately replacing the element law. Mechanically supported alternatives remain hypotheses requiring their own design/review.

The repository requires the recheck and disposition to be tracked in `docs/PLAN_CURRENT.md`. The owner/drafter must add that entry; this task expressly prohibits editing existing files. `.git` is not writable in this environment, so this review is left uncommitted, as requested; no alternate checkout or hook bypass was attempted.
