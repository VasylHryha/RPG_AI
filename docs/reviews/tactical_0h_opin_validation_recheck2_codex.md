CHANGES_REQUIRED
Reviewer family: Codex
Reviewed commit: b5d89697d14ab6978b3843291f2c248e386b2b99
Reviewed scientific execution pin: e66c8969d434f475c4289b6d09b048940d148055567c7c1acfc8bd2652fde357 (revision 7.11)
Date: 2026-10-07

Owner request, verbatim:
> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Scope: round-2 review of the revision-2 O-pin validation report, provenance supplement, stored analysis and its analyzer, relabelled summary, research-memo correction, and proposed DESIGN_0H_REV7 §19.7. Supporting reads: round-1 review, pilot overlays, launch identities, raw-file manifests, registered inventory, and Harness.F5–F8 and their consumers. No simulations, pilots, fixtures, panels, project imports or tests ran. Only this review file was written.

The seven reviewed files still match the reviewed commit byte-for-byte, although another session advanced HEAD to `132b68ebc1a07a20a3cca4d6a7bff711af9cd60a` during review. Report SHA256: `f85016b15f6b2973412d8a9ea5f66647d4acf6974ce38f17182ea74a7e1357c8`. Stored analysis SHA256: `7b775b57dd4aa61ff25851b606f7aef2cf74aa1b869ace5a665121659904763e`. Proposed design SHA256: `268c4962bbedcd2a9b3704493a04ab7b134208a3d25947b4f43bf0c03b562979`.

Revision 2 substantially improves the claims and provenance. Its stored numbers reproduce. Remaining blockers are an incomplete downstream gate policy and new interpretations that the traces contradict or cannot establish. C2 can remain a candidate for owner-approved evaluation; neither this review nor the pilots authorize adoption or execution.

## Round-1 disposition

| Finding | Round-2 disposition |
|---|---|
| R1, operational multi-key gate | Partly fixed: five fresh configurations per start, all ten passing, unchanged within-run thresholds and no outcome-driven replacements are explicit. Downstream guards and F7 entropy mapping remain incomplete (R2-F1). Owner approval and registration remain pending. |
| R2, improvement/direction overclaims | Substantially fixed: exploratory paired improvement, shared worlds/assays, design-informing key 0, nominal calibration and unproved direction/offset hypotheses are disclosed. Retain the bounded wording in note N1. |
| R3, mechanism/literature | Fixed for the requested correction: the mechanism is a plausible explanation, missing geometry/controls are open, and the Lee et al. attraction/phase equations are correctly distinguished. The memo explicitly qualifies its retained historical reasoning. |
| R4, provenance | Fixed within the recoverable record: the two HEAD groups, overlay limitations, current/historical tracked hashes, actual world intervals, reused assays and unavailable execution bytes are disclosed. Seeded baseline naming is corrected. This disclosure does not recover missing launch-time source identities. |
| R5, per-site evidence | Partly fixed: full E vectors and stored training connectivity are supplied; causal response and checkpoint/pair records are correctly unavailable. The denominator and example need correction (R2-F4). |
| R6, seeded failures/margins | Partly fixed: the two failures and their distinct margins are retained; the scaffold is downgraded. Budget permanence, checkpoint attribution and key-4 structural-break claims remain wrong or unverified (R2-F2/F3). |

## Verified evidence and numerical checks

- Executed the authorized analyzer's read-only functions using `runpy.run_path(..., run_name='stored_review_only')`; did not invoke its writing entrypoint. Every one of its 34 rows equals the committed STORED_ANALYSIS row after normalizing JSON object keys. Independently checked log B and complete E as well as the analyzer's A binding. All 34 raw byte counts and SHA256 hashes match the relevant manifest entries: 30 in RAW_FILES.json and four earlier assay traces in RAW_FILES_OUTSIDE_GIT.json. No stored artifact was rewritten.
- Counts and calibration remain correct: baseline 2/5 empty and 1/5 seeded; toward-root C2 5/5 and 3/5; five paired gains, no losses, three shared passes, two shared failures; both-start success 0/5 versus 3/5. Direction and offset counts match SUMMARY. The nominal paired p-values and illustrative intervals are arithmetic descriptions, not registered inference.
- The seven baseline failures' final nearest distances, in `(start, key)` order, are `(i,0) 2.449`, `(ii,1) 2.082`, `(ii,2) 1.665`, `(i,3) 1.783`, `(ii,3) 2.290`, `(i,4) 2.179`, `(ii,4) 2.239`. Thus the displayed 1.67–2.45 range is supported. Three of these are empty-origin controls; four are the legacy seeded pin, not a centred O.
- The eight passing **toward-root, distance-1.0** C2 runs have final distances `0.382, 0.407, 0.391, 0.343, 0.591, 0.463, 0.415, 0.404`, supporting 0.34–0.59. This scope matters: passing direction controls include larger distances, such as opposite empty key 0 at 1.190.
- The per-site E table matches stored floats at its displayed precision. Its eight passing toward-root runs have three or four sites with nonzero late conditional connectivity. Empty key 3 site 0 is 0.875 and site 3 is 0.038; empty key 4 site 3 is 0.556. These support the displayed 88%, 4% and 56%, with the denominator correction below.
- The §5 table reproduces: seeded key 1 A/B `1.657483/1.491223`, max E `0.4666667`, longest any-path span `490.5–792.6`, late any-path `0.954`, final nearest `1.452`; key 3 A/B `0.427782/0.299360647`, E zero, longest span `197.8–260.4`, last path `362.4`, late any-path zero, final nearest `2.338`; key 4 A/B `1.626270/1.493404`, max E `0.7`, longest span `432.1–656.0`, last path `800`, late any-path `0.70`, final nearest `0.404`. First recorded paths are 20.1 s, displayed as 20 s.
- Seeded key 1's final positive training sample is 792.6 s; the first negative sample is 792.7 s despite all eight sites being active. Thus the transition is bracketed by those samples; 7.4 s is the interval from the last positive sample to 800 s. Its max E equals `0.7 × 2/3` arithmetically, but the missing individual assay records prevent verification of that checkpoint decomposition.
- Every run's first cost refusal is indeed between 280 and 480 s. This is not the time after which births necessarily cease (R2-F2).
- All 34 launch identities record the same scientific pin: four have HEAD `553369eef6caf3192624d7fec9d862837c2bbba4`, thirty `fd2182681ee8ed7b7b3a0772d69de898a8aa17c2`. The three scripts' hash prefixes/suffixes in PROVENANCE match git versions and current bytes. Alternative trace episode events are consistent with the 13.1–13.4-million schedules.
- The proposed five F5 growth pools contain 250 worlds and their assay pools 100 recipient/donor IDs. These 350 IDs are unique and disjoint from every registered world pool and the actual four 13-million pilot training pools. Appending `/gate{g}` to the seven F5 growth/recovery/medium recipes produces 35 distinct seed hashes with no collision to registered master values. These are proposed reservations, correctly pending approval; the missing M matching recipe remains a design issue.
- The [Lee, Yeo and Hong paper, equations 1–2](https://arxiv.org/html/2103.11584v1), confirms separation-proportional spatial attraction with a spatial cutoff and globally summed phase coupling. The memo's correction is accurate; those equations do not prove a limit for this driven growing system.

## Findings and concrete fixes

### R2-F1 — HIGH: §19.7 still leaves the downstream execution policy inconsistent and F7 entropy incomplete

DESIGN lines 1017–1020 choose F7 per key and F6/F8 on g=1, but require F6/F8 “whatever its F5 outcome.” `Harness.require` (rev7_fixtures.py lines 156–164) blocks F6/F7/F8/F9 unless aggregate F5 passes, and F8/F9 unless F7 passes. Naming a key before results fixes selection bias; it does not resolve this contradictory execution instruction. The amendment explicitly replaces the single-key verdict and its stop row; it does not specify whether the conflicting downstream Harness guards are retained or replaced.

F7's current `keys('i','M')` includes `matched/F5/i` in addition to growth/recovery and the intentionally shared `medium/F5/i`. §19.7's recipe reservation names only growth/recovery/medium. Current F7 also hardcodes worlds `12000000+e`; merely retaining that schedule would no longer match its proposed g-specific intact run. F6 needs both starts' three g=1 checkpoint clones; F8 needs g=1's empty-start live episode-50 clone with histories, timers, clock and RNG retained. These must survive all per-key processing, without substitution or regeneration.

**Fix, drafter before owner approval:** explicitly state amendment precedence and the permitted failure-path schedule. The simplest policy preserves existing guards: run the named descriptive fixtures only after the complete F5/F7 prerequisites pass, retaining g=1 as the fixed source. If diagnostic execution after a failed gate is intended, separately specify the approved exception and keep development blocked; do not bypass existing guards. Name M's growth, recovery and `matched/F5/i/gate{g}` keys, its shared per-g medium key, and the same per-g training worlds as its intact comparator. Specify g=1 checkpoint/live-state retention and aggregate F5/F7 guard semantics. Keeping existing F6/F8 worlds/keys is a possible explicit policy, not itself a freshness defect. Add yes/no stop handling for INVALID F7 runs and invalid downstream records, with one responsible role and no discretionary key replacement. This is a design correction, not authorization to implement it now.

### R2-F2 — MEDIUM: first cost refusal is incorrectly treated as permanent budget exhaustion

Report §5 line 138 says “After that no new elements can be added, so a path that breaks late cannot be rebuilt.” Sixteen of the 34 stored rows have an accepted birth strictly after the first cost refusal. Raw empty C2 key 3 records B1 cost refusals at 320 s and later B1 acceptance at 800 s; its later births also include B-path at 460 and 640 s. Seeded C2 key 0 has first refusal 280 s and last birth 400 s; seeded baseline key 4 has 480 s and 760 s respectively.

`Rev7Medium.feasible` recomputes candidate-dependent geometry/budget admission, and `growth` can remove elements. A refusal is not an absorbing state. Connectivity can also return without adding an element. The seeded key-3 record does show last birth 360 s and cost refusals from 380 s, but its last path already disappears between 362.4 and 362.5 s: the first refusal is later than that final loss.

**Fix, drafter:** retain the correct 280–480 s range and report first refusal separately from last accepted birth. Remove permanent exhaustion and inability-to-rebuild claims. State the seeded key-3 event order without making the first refusal the cause of collapse. Budget pressure remains an untested possible contributor. Correct the matching PLAN_CURRENT A6u wording “collapsed after the budget ran out at 380 s.”

### R2-F3 — MEDIUM: the seeded event interpretation confuses active-site coverage with structural loss, and infers missing assay records

Report §5 lines 132–137 treats key 4's 0.70 late any-path fraction as an unstable path that “broke at 656 s and re-formed.” In all 1,600 late training samples, there are 1,120 with any path and exactly 1,120 with any active site among 0, 1 and 7. Each of those three sites has a path in **every** late sample in which it is active. At 656.0 s active sites are `[0,2,3]`, path `[0]`; at 656.1 s active sites become `[2,3,4,5]`, paths empty; at 672.1 s site 1 becomes active and has a path. The intervening absence does not demonstrate a structural break. Key 4 differs from key 1, whose final loss occurs with all sites active.

For key 1, `0.7 × 2/3` reproduces max E, but asserting measured assay exposure at checkpoints 40/45 and none at 50 contradicts §4's disclosure that per-checkpoint records were not retained. The training sample at 720 s contains only path `[1]`; it cannot measure site 7's separate assay. Evaluator copies integrate new assay worlds, so training paths cannot substitute for those missing records. Site 0's aggregate E is `0.3333333`, not `0.4666667`; the stated product concerns max E/sites 1 and 7.

Finally, key 3's `197.8–260.4` interval is the longest uninterrupted hold, not its only hold: the raw trace contains 13 spans, including shorter holds afterward through 362.4 s.

**Fix, drafter:** describe key 4's no-path frames as the absence of active connected sites, with no demonstrated late connectivity failure conditional on those sites being active. Keep key 1's verified active-site loss and aggregate miss, but label the checkpoint explanation a hypothesis consistent with the arithmetic; the individual assay exposures are unavailable. State the sampling interval around the loss, and call the key-3 interval the longest hold. No new run is needed for these corrections.

### R2-F4 — MEDIUM: per-site connectivity's denominator and the coverage example are misstated

Report §4 line 106 calls the per-site metric the fraction of late steps “in which a site was active and had a path.” `analyze_stored.py::site_conn` instead divides by the number of steps **where that site is active**. Its JSON note is similarly ambiguous. This is conditional connectivity, not joint exposure over the full window. Key 4's three values of 1.0 coexist with late any-path 0.70 precisely because activation matters.

Line 118's chosen example, empty key 3 E `[.33,.7,.8,.2,0,0,0,0]`, has **four**, not five, zero sites. Its late training table likewise has four connected sites, including site 3's partial connection. Other passing runs do have five zero sites, so the underlying max-E scope warning is valid.

**Fix, drafter:** label whole-run/late per-site ratios “fraction of site-active samples with a path”; retain or report active sample counts alongside them, and distinguish this from joint/any-path exposure. Correct the JSON description as well. Use a true five-zero example (empty C2 key 1, or seeded key 0) or say four for the existing example. Do not equate max-E success with broad causal response; retain the correctly open per-site intervention condition.

## Nonblocking note

**N1 — LOW, remaining wording/plan consistency:** replace “a single-key F5 gate is not reliable” with the bounded observation that this battery shows seed-dependent outcomes and one key establishes only one configuration. The proposed engineering consistency gate is reasonable without a proved reliability claim. Scope the passing-distance sentence to toward-root distance-1.0 runs, and distinguish the legacy seeded controls from a centred origin. PLAN_CURRENT A6s still says direction “matters” and carries the revision-1 disposition; update it to the corrected hypothesis wording and this review's result. These editorial changes must not revise historical fixture verdicts or claim owner approval.

## Disposition and preservation

Claude, as drafter, should complete the above document/analysis-description corrections and the operational amendment before the owner approves §19.7. R2–R4's substantive round-1 corrections can stand. Missing historical overlay bytes and per-checkpoint causal data remain disclosed limitations, not recoverable facts. No new pilot, test or simulation is needed to fix these findings, and none is authorized here.

The owner's verbatim request was also sent to a separate Codex reviewer for adversarial scrutiny of this review's findings and completed draft. This supporting scrutiny is same-family; the present review remains cross-family against Claude. Its checks corroborated the gate, budget, denominator, coverage, checkpoint-record and key-4 activation gaps. Its one draft correction was applied: distinguish the explicit single-key verdict replacement from the still-undefined downstream guard policy. This is an owner recheck, not milestone acceptance.

The owner/drafter must record this review and dispositions in PLAN_CURRENT. Only the requested new review file was changed; committed receipts, raw traces, existing reports/designs, STATUS and unrelated concurrent work were preserved. `.git` and `.git/config` are not writable in this environment. The review is therefore left uncommitted as instructed; no alternate checkout, hook bypass or commit attempt was used.
