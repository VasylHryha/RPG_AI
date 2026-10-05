CHANGES_REQUIRED
Reviewer family: Codex
Reviewed SPEC_0G.json SHA256: 45ee45fabaa1fa0c65f8b05c14d3a8dc6fb83d33c3fe7c3eb0a56f0a305e2eef

Reviewed revision 2 on 2026-10-05, within the requested 20-minute cap. Reviewed HEAD: `dfaddcfc5c3498ec73538bdad8730430bd6a7e72`. The working tree was clean at entry. This is a registration review; it does not authorize S6 or accept experimental results.

At final scope verification, an unrelated untracked `evidence/tactical_composition_demo/astelia_cpp/s6_run.py` had appeared. I did not create, modify or review it. HEAD and both reviewed specification hashes remained unchanged. The only task-owned write is this report.

Unless prefixed with `docs/`, paths below are relative to `evidence/tactical_composition_demo/`. Findings 1 and 2 require correction. Finding 3 is a nonblocking evidence-retention note. The drafter owns the corrections and the proposal self-audit.

1. **High — The literal request template contains a field rejected by the pinned engine.**

   **Evidence:** `SPEC_0G.json:21–28` places `comment` inside `request_template`, calls this object “one native request per fight,” and says every field other than the placeholders is literal. `astelia_cpp/s3_runner.py:72–77` emits no `comment` field. The native codec permits only `mode`, `options`, `trace`, `opponent`, `debug`, `decisionTrace`, `diagnostics` and `s3` at this boundary (`astelia_cpp/src/native/config_codec.cpp:147`). Its `only` helper rejects any other key with `unsupported native combat field: <key>` (`:13–16`). The host catches that exception and returns an error object before world creation (`astelia_cpp/src/native/host.cpp:58–61,84`). Sending the registered object literally therefore rejects every request; silently stripping `comment` is an unregistered request-building rule.

   **Fix:** move this explanation outside `request_template`, leaving only native fields inside the template, or explicitly register a metadata exclusion rule. Moving it is the smallest repair. Keep the pinned engine unchanged. The combat fields themselves match S4; the field comparison below isolates this single discrepancy.

2. **Medium — Controller-failure invalidation is still not explicit for P2/P3.**

   **Evidence:** P1 requires its fights to complete “without controller or technical failure” (`SPEC_0G.json:265`). P2 and P3 require only that their respective 1,216-plus-1,216 fights be “completed” (`:276,287`). `failures.controller_failure` defines the detection predicate (`:301`), but `failures.rule` attaches INDETERMINATE only to required fights that are not all completed (`:303`); it does not expressly invalidate completed controller-failure fights.

   This distinction exists in the actual host. Invalid controller actions increment a failure count and fall back to hold (`astelia_cpp/src/native/controller_bridge.cpp:43`), while the fight continues to its ordinary terminal summary (`astelia_cpp/src/native/host.cpp:69–83`). That summary contains finite survivor counts together with `controllerStatus: "controller_failure"` and failure counts (`:18–25`). Thus a fully populated POOL panel containing one failed morale fight can satisfy P2's literal completion requirement, and an implementation can compute a normal P2 verdict from fallback behavior. Defining the failure flag alone does not uniquely specify that verdict.

   A standalone logical witness is a complete panel with every P2 block difference equal to 8 and one required morale summary carrying the failure flag. The registered zero-variance formula gives lower=8>delta=4, hence SUPPORTED if completion is interpreted literally. The missing rule must make that case INDETERMINATE instead; this is a hypothetical input, not a played fight.

   **Fix:** state once in `failures.rule` that a required fight is valid only if it completes with neither the registered controller-failure predicate nor a technical failure; any invalid or missing required fight makes that endpoint INDETERMINATE and prevents its inferential bounds from being computed. Apply this to P1/P2/P3, and retain the raw failed record. Keep the existing dependency isolation: a morale failure affects P2, a pushpull failure affects P3, a POOL resonator failure affects both, and nearest failures veto neither. Do not alter n, average partial blocks, or replace fights.

3. **Low — The interruption record should preserve the schedule and requests before dispatch.**

   **Evidence:** `SPEC_0G.json:303` promises every attempted fight is recorded, but `execution.order` appends fight lines only “as [a fight] completes” (`:306`); the listed pre-fight identity fields contain neither the complete keyed schedule nor an attempted-fight record. A host hang or interruption after dispatch can therefore leave no durable record of the in-flight request. The fixed directory latch still prevents a retry, so this does not reopen seed selection or invalidate the latch repair.

   **Fix:** save the complete keyed schedule before the first dispatch, and persist each attempted key/request before sending it to the native host. Attach its summary or error afterward. Treat an unmatched attempted record as incomplete in the eventual coverage report. This also finishes revision 1 finding 2's request for a retained complete schedule; no extra fights or resumption mechanism are needed.

Revision-1 finding reconciliation:

| Prior finding | Revision-2 assessment |
|---|---|
| 1 — JSON panels, requests, score and bounds | **Partially resolved.** Panels, opponents, all knobs, side, score, timeout treatment and bound mathematics are now defined. The new literal `comment` defect is finding 1 above. |
| 2 — Seed derivation | **Resolved for panel definition.** Decoded root bytes, ASCII namespaces, zero-based 8-byte big-endian indices, first four digest bytes and output endianness are explicit. HEAD levels have separate namespaces; P2/P3 share `POOL`. Duplicate/development-overlap rejection precedes fighting. Retaining the schedule is the low note above. |
| 3 — Failures and coverage | **Partially resolved.** Dependency sets, technical failures, exact required counts, no partial averaging/replacement, all-endpoint coverage and P1/POOL independence are explicit. Completed controller-failure invalidation remains finding 2 above. |
| 4 — Gates, root lifecycle and latch | **Resolved at registration level.** Three gates require this revision's passing review plus owner approval of delta/n and S6 authorization naming the exact hash. Atomic exclusive mkdir and identity precede fighting; existing attempts cannot be deleted, reused or retried elsewhere. Changed specifications after judging starts require a new root. Knob-source-before-root ordering and retirement of revision 1's root are recorded claims, not independently authenticated entropy history. |
| 5 — P1 planning provenance | **Resolved.** The false C-derived B-floor claim is removed. The JSON now uses retained B-validation noise and explicitly selects fixed conservative n=100. Its normal-planning arithmetic gives 24 and 1 from the displayed upper SDs; these are pre-floor approximations, not proposed t-test sample sizes. The floor is 32. |
| 6 — Descriptive subset | **Resolved.** Resonator POOL indices 0,1,2, every doctrine, orientation false: exactly 57 existing fights. D uses controlled-side fight-long cross-team counters, friendly fire is separate, and timeout classification is fixed. Arms and prohibitions on verdict/selection/stopping use are explicit. Design-section-7 formulas are bound by the registered design hash. |
| 7 — Alpha rounding | **Resolved.** Exact fractions replace the inconsistent rounded split. |
| 8 — t calibration | **Resolved.** Independent clusters/blocks and approximate calibration for discrete scores are declared; the method is fixed before outcomes. |

Field-by-field request comparison against `s3_runner.py:53–77`, using controlled side 0, `s4_full_head` for HEAD and `s4_p23` for POOL:

| Native field | Comparison |
|---|---|
| `comment` | **Mismatch:** present only in the registered template; rejected by the native codec. |
| `trace`, `debug` | Both false, matching requests with trace off. |
| `mode`, `s3` | `alone`, true; exact matches. |
| `diagnostics` | False except the fixed 57-fight subset; the runner accepts the same boolean. Native diagnostic processing is output-only. |
| `opponent` | HEAD `alone` with the level in `ai[1]`; POOL the doctrine name; exact matches. |
| `options.rules`, `scenario` | `game`, `mirror`; exact matches. |
| `options.sandboxAbilities`, `perception` | Both false; exact matches. |
| `options.duration`, `dt` | 150 and `0.03333333333333333`; the latter equals Python's `1/30` exactly as a binary64 value. |
| `options.army.melee`, `ranged`, `artillery` | 10, 30, 10 for both settings; exact matches. |
| `options.seed`, `swapSides` | Seed placeholder and false/true orientation; the same fields used by the runner. No real judging seed was derived. |
| `options.ai[0].controller`, `params` | Each registered arm and its HEAD/POOL knobs; exact schema matches. All 22 numeric knobs in each panel equal the corresponding B/C source file. Nearest has empty params. |
| `options.ai[1]` for HEAD | Exactly `{level: novice}` or `{level: regular}`, with no pool skill override. |
| `options.ai[1]` for POOL | Exactly the eight-key skill map (`artyFire`, `lockedDodge`, `dodgeShells`, `castDodge`, `weaponsFree`, `saveWounded`, `artyBattery`, `artyRollout`) and `lookahead: null`. Values and all 19 ordered doctrine names match the source. No `level: elite`, brain or formation field is added; doctrine behavior comes from the top-level name and the pinned codec. |

Standalone reconstruction of these source rules compared 336 request variants (21 opponents × 4 arms × 2 orientations × 2 diagnostic flags), using a fixed dummy seed. Every comparison had exactly the extra `comment` key; excluding that key gave identical request objects. This did not import, execute or call the project request builder. `swapSides` mirrors positions without swapping team identities (`astelia_cpp/src/native/world.cpp:178–185`), so side-0 scoring is correct in both orientations.

Computability and arithmetic checks:

- On complete, failure-free data, the JSON alone determines each substantive endpoint. P1 uses 100 two-orientation S means separately per level, with df=99; P2/P3 use 32 means of 38 matched differences, with df=31. Sample SD uses n−1, zero SD collapses bounds to the mean, and comparisons are strict. There is no need to infer a statistic or margin from the Markdown. Finding 2 concerns the invalid-data branch.
- P1 support is an intersection-union at 1/400, without an extra support split. Its two refutation tails each use 1/2400. P2/P3 each use 1/400 support and 1/1200 refutation. Exact arithmetic: `3/400 + 2/2400 + 2/1200 = 1/100`; each endpoint receives `1/300`. Endpoint correlation does not require independence for this allocation. Calibration remains approximate as declared.
- The fixed pool estimand equally weights 19 named doctrines. Shared-seed block averaging retains cross-doctrine and cross-arm covariance; it does not treat 1,216 fights as independent observations.
- HEAD has `2 × 100 × 2 × 4 = 1,600` fights. POOL has `32 × 19 × 2 × 4 = 4,864`. Total: **6,464 fights**, with **232 distinct scheduled seed slots** (`100 + 100 + 32`), subject to the registered collision preflight. Diagnostics add zero fights.
- Retained B validation has 100 clusters per level: mean/SD 5.92/4.33433555 novice and −8.685/0.70228703 regular. Normal planning from displayed upper SDs 4.73/0.77, support alpha 1/400, power .90 and hypothetical effect 4.0 gives ceilings 24/1. An independent 2,000-resample reconstruction with RNG 811005 gave upper SDs 4.71458086/0.76665020 and the same ceilings. Revision 2 does not freeze the exact bootstrap RNG/quantile convention, so I verified the sample-size conclusion, not exact reproduction of the displayed 4.73. This does not change the fixed n=100 or assert that an observed negative effect becomes positive.
- The authority chain now identifies the amended S4 protocol and A/B-only owner gate override. P1 still includes both novice and regular; P2 remains registered despite unfavorable development results. No unsupported elite, C5, universal-knob or oscillation-necessity claim was introduced.
- The S6 authorization file and fixed output directory were absent at review time. The draft's false owner-approved flags do not supply approval; the named owner authorization record remains required. No S6 runner implementation or runtime enforcement was accepted by this document review.

Identity checks (SHA256):

| Artifact | Verified hash |
|---|---|
| SPEC_0G.json | `45ee45fabaa1fa0c65f8b05c14d3a8dc6fb83d33c3fe7c3eb0a56f0a305e2eef` |
| SPECIFICATION_0G.md | `6b68d0e01fbd77d018569ae76640a9cd0f602c26ef8e100f998257eb5ead52a4` |
| DESIGN_0G.md | `fc6494b2bf3e2e8127a7f60a1e2a5b607dd910eeb52a65ccb4ca26c9ff6c262b` |
| astelia_cpp/s3_runner.py | `733df41a0e3db76af90efceec788edbc59507b11ee6e90032112b05b07e7104d` |
| Native binary | `a1a2d5288481a66f75ec2d151c58ba3b5378121b23bc59396a268815b552c74a` |
| Native build manifest | `d3c4d8f9bc35a6e3c6eeab180ba0f5a81b09f4d12f693b6991ee48bbdaecb1fd` |
| Amended B_best.json | `02ada71ef5f16c5de6ecd390464ecf75589d405b552f16b4ff5a37d202f2a3ea` |
| Amended C_best.json | `cef27aa02f57dc3d8e2d6f9176b44e02e14a40a5fcf755a3cd74fab40f6e0325` |

The current binary and manifest match the registration, and every source hash in that manifest matches current bytes, including the codec and host used for these findings.

Scope: read repository rules, documents, source and retained development JSON; inspect Git state; compare hashes and source literals; perform standalone request-object, count, rational-alpha and stored-data planning calculations. No real-root judging-seed derivation, fights, game code, project tests, optimizer, build, mutation probe, recorded panel or commit was run. Only this review file was written. S6 remains blocked by findings 1–2 and by its recorded review/owner-authorization gates.
