# S1 wrapper diagnosis and prospective repair

Authority: owner S1FIX request, design rev 3 (`cac370a`), decision 0037 addendum and the lighter development process in 0035/0036. The initial pilot (`3945d7d`) remains unchanged and admits no cell. This analysis reads all 80 initial raw fights, verifies their SHA256 against their receipts and verifies request/inventory identity. It executes **zero fights**. Reproducible counters: `s1fix_diagnose.py` → `S1_WRAPPER_DIAGNOSIS_COUNTS.json`; `s1fix_trace.py` → `S1_WRAPPER_LIFECYCLE_COUNTS.json`. Per-fight receipt/raw hashes are in the first file. Those scripts refuse existing outputs. Analysis measured 67.14 s for the first pass; the lifecycle pass separately reverified raw bytes.

The leading integrity failure is a **raw-intent dead-target representation defect**, not a command overriding a live focus lock. The native lifecycle successfully retains the start-time target. The other main defects are release refresh four physical ticks late and lossy polar quantization of the copied planner's gun-bound points. Moving cells additionally request impossible autonomous leads. Existing evidence establishes these mechanisms, but cannot apportion the observed kill deficit causally without a new host pilot.

## What the reported lock violations actually count

`s1_metrics.measure` calls **any projection raw/effective target difference** a `native_target_lock_correction`; `summarize` adds both arms. It is a tick count, not a distinct-command or distinct-cast count. It does not inspect aim, body or reaction locks.

| Cell/arm | corrected ticks | winding | blocked | at six-tick decision | between decisions |
|---|---:|---:|---:|---:|---:|
| D2-10 unit | 1,471 | 862 | 609 | 295 | 1,176 |
| D2-10 wrapper | 1,211 | 661 | 550 | 247 | 964 |
| M2-10 unit | 4,496 | 2,455 | 2,041 | 915 | 3,581 |
| M2-10 wrapper | 3,726 | 2,028 | 1,698 | 758 | 2,968 |

Totals are exactly **2,682 D2-10** and **8,222 M2-10**. Every corrected tick has a dead/missing locked focus, snapshot target `0`, raw target `0` and a nonzero effective cast target. Every raw row has an empty command (`volley=0`). There are **zero live-focus retarget corrections** and zero command-present target corrections. Even two-gun arms with no command have corrections: 108/108 in D2-2 and 225/225 in M2-2.

Cause: `schema.cpp::snapshot` serializes only living native targets. `unit()` consults that snapshot target while prep is positive, finds no living enemy, and leaves its raw target at zero. `Host::decide` then reinstates `Cast.lockedTarget`. Native safety works; the raw command layer violates its own identity contract. Example: `s1_D2-10_00_wrapper`, tick 193, gun 10, cast start 169: raw/snapshot target 0, effective target 18, blocked `target_absent`. The fix resolves pending target identity from the authoritative `Cast` before oracle construction and raw logging, including a dead reference. It does not retarget or revive that enemy; native missing-target cancellation remains.

## Focus, shape, aim, body and reaction phases

The old wrapper creates commands only for unlocked, startable guns; its plan map retains those commands during winding. Existing raw data records **zero pending command-plan replacements** and **zero refresh/start focus disagreements**. Thus the evidence does not show a later leader replacing focus or shape during windup. Body/reach/energy remain native gates.

| Wrapper lifecycle | D2-10 | M2-10 |
|---|---:|---:|
| commanded starts | 188 | 130 |
| commanded first physical release opportunities | 171 | 110 |
| release refresh events | 161 | 106 |
| refreshed casts with comparable first-opportunity tick | 160 | 106 |
| refresh lag for those casts | always 4 ticks (0.1333 s) | always 4 ticks (0.1333 s) |
| commanded launches | 164 | 104 |
| commanded launches after first physical opportunity | 162 | 104 |
| commanded launches with no refresh | 3 | 0 |
| refresh occurs while reaction declines release | 14 | 10 |

`Host::prepare` exits between six-tick decisions. The .7 s windup becomes physically ready four ticks before the next readout; `Cast::project` already sees readiness. The old wrapper waits until that readout to refresh. When actual aim is locked later, `prepare` still resnaps the cached absolute request against the moving focus. `Host::decide` restores the original locked aim, so raw aim can disagree without being counted by the original target-only integrity endpoint. The lifecycle counters retain those differences under `aim_lock_correction_ticks`/`command_aim_lock_correction_ticks` if observed; absent keys mean zero. This is an implementation hazard even where this pilot did not exercise it.

A separate **reaction-priority defect is exercised**: native automatic release after its six-tick hold overrides the oracle's reaction suppression. Native release permission with a same-tick public reaction active: D2-10 **47 unit / 52 wrapper**, M2-10 **109 unit / 128 wrapper**; all occur through `hold_expired_auto_release`. The lifecycle JSON calls these `actual_release_reaction_active`, but counts projected release permissions, not confirmed shell launches; later act veto/no-launch can still intervene. This affects both arms and is not evidence of a leader-specific retarget. The revised native bridge includes the public reaction in its physical body/safety gate, so bounded automatic release cannot override it; legal release or bounded cancellation still terminates a held cast. Both script arms share this repair.

## Why moving snaps fail

| Cell/arm | release-support rows | bad snaps (>10 px) | bad snaps with command | bad snaps without command | bad request physically illegal |
|---|---:|---:|---:|---:|---:|
| D2-10 unit | 929 | 3 | 0 | 3 | 0 |
| D2-10 wrapper | 821 | 17 | 16 | 1 | 6 |
| M2-10 unit | 1,920 | 337 | 0 | 337 | 303 |
| M2-10 wrapper | 1,783 | 320 | 23 | 297 | 284 |

M2-10 has **634/657 bad snaps without a command** and **587/657 physically illegal desired points**. It is largely an autonomous lead/reach problem, not continuous leader drift. Moving enemy guns retreat beyond a gun's 320 px reach; the focus may be barely reachable while the velocity intercept is outside it. Quantization cannot make an impossible lead accurate. The remaining 70 legal-request failures diagnose the grid itself: centre plus half/full polar rings around the current focus has neither the exact lead nor the exact commanded point. Most bad moving rows use a 40 px radius; the half-ring radii cannot represent an arbitrary small lead, and the nearest full-ring point may be illegal. Bad-snap error means: 20.41 px unit / 20.43 px wrapper, maxima 38.77 / 46.68 px.

Prospective S1FIX support explicitly changes the public script oracle: autonomous raw velocity lead is first projected into arena/range, with raw lead and projection distance logged separately. Categorical support then includes that exact feasible single-shot centre. Commands require their actual cached point to be physically legal; illegal refreshed commands are explicitly rejected and use locked-target autonomous fallback. There are 33 candidates: desired centre, 31 local half/full splash-ring points, and the current living focus fallback. This removes accidental polar snapping while preserving finite, reconstructible categorical support. **Snap error measures requested-to-supported distance after the declared autonomous physical bound**; raw bound distance and >splash/4 counts remain explicit. This is a prospective support/oracle revision, not a retroactive improvement of the initial pilot. The moving conservative raw-command miss veto remains unchanged; intentional shape is not exempted.

## Why the wrapper loses kills, and what this evidence rules out

| Initial ten-pair totals | D2-10 unit | D2-10 wrapper | M2-10 unit | M2-10 wrapper |
|---|---:|---:|---:|---:|
| kills | 67 | 43 | 77 | 69 |
| own deaths | 106 | 120 | 86 | 82 |
| strict wins | 3 | 0 | 1 | 1 |
| enemy damage | 18,017 | 15,199 | 17,761 | 16,647 |
| cast starts | 1,098 | 991 | 2,611 | 2,441 |
| own launches | 929 | 823 | 1,957 | 1,818 |
| target-range blocked projection ticks | 292 | 518 | 51,593 | 62,506 |
| aim-range blocked projection ticks | 0 | 18 | 139 | 183 |
| cancellations | 94 | 94 | 582 | 548 |
| consumed without launch | 0 | 0 | 16 | 21 |

Every original decision was compared against the autonomous public oracle on **that same wrapper-arm snapshot**, with native-libm geometry. D2-10 wrapper: 6,282 decisions, 991 autonomous starts versus 991 wrapper starts, 760 autonomous releases versus 760 wrapper releases. M2-10 wrapper: 25,158 decisions, 2,441 starts on each, 1,630 releases on each. **Zero start or release permissions removed/added on the same state.** No delayed planner entries were rejected in these pilots, no expiry rejection was recorded, and no gun waits for a group command: the empty arm is autonomous. Dead-command fallback occurred 27/19 times; focus-infeasible candidate rejection 12/12 times. Fewer total starts are therefore not a command-veto counter; trajectory divergence, earlier deaths and longer range-blocked residence change available opportunities.

Spatial corruption is measured directly:

- D2-10: 180/188 accepted initial gun assignments **do not equal their copied planner point**; mean error 6.86 px, max 18.27 px. M2-10: 130/130 differ; mean 7.03 px, max 17.62 px. This is before any release refresh or target motion.
- Initial per-gun recentering differs from the planner's led centre on 48/190 D2 candidates and 122/136 M2 candidates; maxima 7.16/8.94 px. It is smaller than the worst snapping but changes the joint plan before winding.
- Commanded decision aim differs from the same-state autonomous snapped aim by >10 px on 801/885 D2 rows and 531/611 M2 rows. The command changes target on 160/885 and 107/611 rows. Mean aim displacement 37.00/43.30 px; maxima 232.40/210.05 px. A distant group focus can change engagement and movement; it is not intrinsically an error, but explains why old full-army utility cannot simply transfer to this drill.
- Raw wrapper miss exceeds the same-focus autonomous raw shadow by mean 11.16 px D2 (126 measured launches) / 7.12 px M2 (90). Shape-subtracted diagnostics are retained. Raw requested, snapped, native landing and their separate flight times are in the initial receipt; missing/dead/late-launch rows are not imputed.

The copied planner scores a bound set of exact points, but the old wrapper executes recentered and quantized points four ticks after physical readiness. Native range vetoes and automatic reaction releases further change execution. These are demonstrated adapter defects. The observed lost kills cannot be attributed uniquely to quantization, timing, focus selection or shorter gun survival: paired arms diverge after commands. Full-army lab v6 V2 (`d533e26`) differs in roster/scaffolds, opponent and ready-only scheduling; its +18% damage/shell and −2.75 deaths/fight are not a promised S1 effect. S1FIX preserves exact **assignment-time** planner points and retains only the designed single public release refresh. It remains a startable-projected, immediate-only adaptation, not full-army planner parity.

## Repair and fresh-seed rerun

All repair code is in new `s1fix_*` files. Original `s1_*`, committed evidence, raw bytes and `docs/PLAN_CURRENT.md` are untouched.

- Use authoritative pending target/aim identity before raw logging, retain focus/shape during windup, and never resnap locked aim.
- Refresh once at the first **physical** release opportunity, including a reaction-declined row; preserve the resulting absolute point until native lock or explicit expiry/death/illegal-point fallback.
- Preserve `q.point` exactly at assignment. Select the copied planner's immediate-only candidate slate before scoring; reject an infeasible group as a whole rather than cherry-picking its guns. Singles/leftovers remain empty/autonomous.
- Share reaction gating and legal autonomous aim support across both arms. Record a same-state autonomous shadow on every decision and strengthen integrity counts to include raw/effective aim differences. Physical bound errors, unsupported command points and missing launches remain reported.
- Drop D2-2/M2-2: both have exactly zero multi-gun opportunity. Keep D2-10/M2-10 unchanged, including .0/.12/.24 s readiness staggering, geometry variation, mirrored pairs and native opponent. They have 262/609 initial eligible multi-gun decisions and command rates 26.34%/7.39%.
- Use new S1FIX entropy/inventory, exclude **all** old pilot seeds (including the reserved unrun extension), prior collection/mechanism/DAgger/fixture/partial seeds and fresh S1FIX seeds from later training/validation/outcomes. Five pairs/cell (20 arm-fights) form the timing sample and are reused within the initial ten pairs/cell (40 total); twenty pairs/cell is the maximum (80 total). Failed attempts count, are retained and are never automatically retried.
- Preserve process ownership/common locks, live owner cap, 512 MiB/process and measured maximum-extent/disk admission. New manifests pin code, binary, immutable inventories and approved design commit identity; living docs and mutable cap bytes are not execution hash pins.

Recheck/disposition and focused verification are in `S1FIX_RECHECK.md` and `S1FIX_TESTS.json`. Native fixture RPC uses deployed wrapper/planner/bridge code without `coreStep` or fight collection; `fixtures/S1FIX_REPLAY.json` retains original raw-derived states. `S1FIX_HOST.md` contains exact host commands and timings. No outcome improvement, fresh-pilot snap rate or cell admission is claimed before that host run.

## Completed local verification

Final focused batch: **23 passed in 16.27 s** (16.47 s including coordinator), zero physical fights. Two earlier fixture failures are retained as `S1FIX_TESTS_ATTEMPT001/002.*`: initialize public scratch-world observations before native participation; give the synthetic shell enough time for the native escape search to find a safe endpoint. No fight or tuning outcome was used to fix them.

The native stored-state autonomous support regression evaluated all 1,750 D2-10 and 3,703 M2-10 initial release rows: **zero bad snaps** in each. The legal projection remains visible: raw lead bound exceeds 10 px on **4 D2 / 285 M2** rows. This does not claim that an impossible raw intercept became accurate or that the new command miss gate passes. It establishes categorical coverage of the revised feasible autonomous request on old states. Native multi-gun replay separately checks exact gun-bound planner points before refresh; lifecycle fixtures exercise reaction-declined first physical refresh, cache preservation after focus movement, dead/native aim locks and expiry, and body/resource/range/cooldown stops. New trajectories, throughput, command coverage, damage and kills require the fresh host pilot.

Separate same-family reviewer `/root/s1fix_reviewer` received the owner's request verbatim and found M1, stale resource admission. M1 is fixed: each new non-sample attempt checks current charged time, remaining maximum extent, live cap/disk reserve/RSS and sample receipt hashes; full raw sample identity is checked at invocation admission. Checks preserve the initial projection and append admission/refusal records. The final admission-only batch passed **8 tests in 0.20 s**; native sources/build remained identical to the earlier 23-test batch, so native replay was not repeated. The reviewer reread the corrected source and closed M1 with PASS; original finding/hashes remain in `S1FIX_RECHECK.md`.
