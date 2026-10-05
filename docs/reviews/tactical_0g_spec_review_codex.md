CHANGES_REQUIRED
Reviewer family: Codex

Reviewed 2026-10-05, within the requested 20-minute cap. Registration commit: `5460380b82651c4dcd4e1d92ebbe2e47b7200e86`. HEAD at final source recheck: `5dea8c25201a68989487a4493ad87dac6669a3fb`. Another session committed the previously dirty amended S4 evidence during this review; the reviewed specification, design, planning, identity and Claude-review hashes remained unchanged.

This is a review of the registration draft, not approval to execute S6. The statistical comparisons are coherent, but the governing JSON still requires implementation choices that can change the experiment. Findings 1–6 require corrections; 7–8 are lower-severity clarifications.

References below are relative to `evidence/tactical_composition_demo/`, except where another root is named.

1. **High — The JSON does not fully define the panels, native requests or score.**

   **Evidence:** `SPEC_0G.json:14` delegates the world to the design and `astelia_cpp/s3_runner.py`; `SPEC_0G.json:107–121` names “19 doctrines” and “elite skills” without listing the doctrines or the actual skill map, and makes P3's panel/statistic prose aliases. The JSON uses S without defining it. Its P2/P3 panel also omits an explicit controlled side. S and ordinary-timeout treatment are present only in `SPECIFICATION_0G.md:37` and `DESIGN_0G.md:153–160`.

   The intended requests can currently be recovered from `astelia_cpp/s3_runner.py:9–16,53–77`: the ordered doctrine roster, the exact `ELITE_NO_ROLLOUT` dictionary, `lookahead=null`, controlled side 0 and the world options. However, that runner is not pinned by the registration. The binary hash does not freeze the Python request builder. Reconstructing the prose as an actual `level=elite` profile would change the brain/base formation as well as skills (`astelia_cpp/src/native/config_codec.cpp:228–255`). That would not reproduce S4's doctrine panel.

   **Fix:** put a structured native-request template, all 19 exact opponent configurations, orientations, controlled side, arm membership and equal doctrine weights in the JSON. Explicitly define S as the controlled team's survivor count minus its opponent's, including ordinary game-duration timeouts. Binary-default fields may be declared as defaults of the pinned binary; do not require an implementer to infer a profile from a level name. Use a structured shared-panel reference for P2/P3. Register the bound formula `mean ± t_(1-alpha,n-1) * sample_SD/sqrt(n)`, sample variance denominator `n-1`, strict comparisons, and zero-variance handling. Also pin the request-builder identity if it is reused. The current engine identity itself passes; see the checks below.

2. **High — Seed derivation does not uniquely determine the shared panel.**

   **Evidence:** `SPEC_0G.json:79–82` specifies `root || endpoint || index`, but does not define whether root means 16 decoded bytes or 32 textual hex bytes, the endpoint encoding, or whether indices start at zero. `SPEC_0G.json:108–121` describes one common P2/P3 panel, yet literal calls with endpoint `P2` and `P3` produce different panels. P1 also does not specify whether its two levels reuse indices/seeds or use distinct ranges/namespaces. Orientation sharing and within-block sharing across doctrines/arms are correctly stated, but do not resolve these choices.

   **Fix:** freeze byte encoding and index ranges, a single explicit P2/P3 seed namespace, and the P1 level-sharing rule. For example, declare decoded root bytes, ASCII namespace bytes, zero-based unsigned 8-byte big-endian indices, and one named shared pool panel used by both endpoints. Declare preflight handling of duplicate derived seeds and overlap with all development ledgers: reject/re-register before any fight, without inspecting outcomes. Emit the resulting complete keyed schedule in the run identity. Do not generate or inspect judging fight outcomes to resolve this. I did not derive judging seeds during this review.

3. **Medium — Failure scope and incomplete endpoint coverage are underdefined.**

   **Evidence:** `SPEC_0G.json:139` handles controller failure and prohibits dropping/replacing fights; `SPEC_0G.json:152` promises coverage, but neither defines native-process errors, host request timeouts, malformed/nonfinite summaries, duplicate/missing pairing keys, interrupted panels, or which arms' failures affect which endpoints. Descriptive arms share the panels (`SPEC_0G.json:140–145`), so “any fight of an endpoint” could silently make a nearest-controller failure veto a substantive contrast. Conversely, a missing orientation/block could silently become a smaller sample. The design requires failure records, not ordinary scores (`DESIGN_0G.md:108–109,157,258`).

   **Fix:** register the dependency sets: P1 requires its resonator fights at both levels; P2 requires pool resonator/morale; P3 requires pool resonator/pushpull. Declare whether descriptive-arm failures veto anything; the intended descriptive-only interpretation should be explicit. Recognize both `controllerStatus` and failure counts. Define technical-error/incomplete handling separately from an ordinary game timeout, retain every attempted record, and forbid partial-block averaging, zero-filling, replacement or reduced-n inference. Require exact scheduled key/count completeness before bounds. On interruption/error, write coverage for all P1/P2/P3, with explicit reasons when a statistic was not computed and an INDETERMINATE endpoint outcome as applicable. A negative P1 result must not gate away the registered P2/P3 panel.

4. **Medium — Final approval, root lifecycle and the one-shot latch need one governing rule.**

   **Evidence:** `SPEC_0G.json:3,136,138` makes owner approval of delta/n plus Codex review the prerequisites. `SPECIFICATION_0G.md:61` additionally requires owner approval to run S6 once with exactly this specification; that prerequisite is missing from the governing JSON. `SPEC_0G.json:152` requires a nonexistent output directory, a useful latch, but does not say when it is created or how attempted runs survive an interruption. The rule requiring a new root after a changed draft has been used appears only in `SPECIFICATION_0G.md:39–42`. Claude also requested freezing knob sources before judging seeds exist (`astelia_cpp_review_claude/S4_AMENDED_REVIEW.md:40`); the draft says the root was drawn “at drafting,” without identifying that ordering.

   **Fix:** require explicit owner authorization naming the final specification/hash and S6, in addition to delta/n approval and a passing review. Register an atomic exclusive creation of the fixed output directory before the first fight, saving specification/root/engine identity and authorization evidence there; refuse any existing attempt and preserve partial evidence. Put the fresh-root rule in JSON and prohibit retrying an attempted judging panel through another directory or deleting its latch. Record that the knob/panel choices preceded root creation. If that ordering cannot be evidenced, freeze the corrected draft and draw a fresh root before any judging use. Merely publishing an unused root is not evidence of outcome peeking.

5. **Medium — The P1 power-floor provenance belongs to C validation, not the registered B knobs.**

   **Evidence:** `SPEC_0G.json:17,138` chooses B knobs and calls 49 per level its S4 power floor; `SPECIFICATION_0G.md:60` offers those floors if the owner rejects the larger sample. However, `astelia_cpp/s4_amended_development/POWER_PLANNING.json:99–156` uses C-validation means/SDs, including novice −6.565 and regular −8.945. The amended report expressly requires a new declared calculation from retained B data when choosing B (`astelia_cpp/s4_amended_development/S4_DEVELOPMENT_REPORT_AMENDED.md:154,164`). B-validation SDs are 4.3343 and 0.7023 (`.../S4_DEVELOPMENT_REPORT_AMENDED.md:88–89`), substantially different from C's.

   **Fix:** add a prospective B-based planning calculation using retained development/validation data and the declared noise-uncertainty procedure, or explicitly justify 100 as a fixed conservative choice with correctly labelled inherited C-noise evidence. Remove the unsupported B-floor/fallback claim until its provenance is corrected. Do not rerun development fights or change recorded evidence. Keep the owner-approved final n fixed before judging and retain the original planning receipt.

   Raising n to 100/32 before judging is acceptable; it is not outcome-informed judging adaptation. Counts remain below the design's 2,000-configuration-cluster bound: 200 for P1 and 608 each for P2/P3. Standalone noncentral-t calculations using the S4 planning assumptions give support power approximately 0.99975/0.99999 for P2/P3 at 32 blocks. Even the inherited worst P1 C-noise allowance gives approximately 0.99835 per level at 100, versus 0.87019 at 49. These are hypothetical normal-model planning calculations, not predictions that the observed negative effects will become positive.

6. **Medium — Descriptive outputs are declared but their fixed selection is not.**

   **Evidence:** `SPEC_0G.json:140–145` asks for diagnostics on “3 fixed P2/P3 blocks” without selecting those indices, doctrines or orientations. It names damage difference D without specifying cross-team counters or friendly-fire separation, and timeout counts without their criterion. `DESIGN_0G.md:155–156,179–189` supplies the intended damage and group formulas, but does not select the judging diagnostic subset. “Fixed” alone still lets an implementer choose attractive examples after results exist.

   **Fix:** declare the diagnostic block indices and exact capture subset before execution, and reuse those scheduled fights rather than adding judging replays. Bind the existing design-section-7 diagnostic definitions, declare D from controlled-side cross-team dealt/taken totals including dead units, report friendly fire separately, and fix timeout classification. Fully enumerate descriptive arms on each panel and prohibit their use for endpoint selection, tie-breaking or stopping. Playing all four arms over both panels requires 6,464 fights before any extra captures; “about 6,000” is a reasonable approximation, not a count defect.

7. **Low — Alpha logic is valid, but rounded constants are not an exact equal endpoint split.**

   **Evidence:** `SPEC_0G.json:98–99,113–124,129–131` allocates support 0.0025, P1 refutation 0.000417 per level, and P2/P3 refutation 0.000833 each. P1 support correctly uses an intersection-union: under its union null, at least one true-null subtest must reject, so its size is at most 0.0025 without a further split. P1 refutation is a union and needs the shared two-test Bonferroni allocation. Independence between levels/endpoints is unnecessary for these arguments.

   Literal allocations give P1 0.003334 and each other endpoint 0.003333; the total is exactly `3*0.0025 + 2*0.000417 + 2*0.000833 = 0.01`. Thus this is **not** a familywise overspend, but contradicts an exact equal `0.01/3` allocation and a literal “share 0.000833” within P1.

   **Fix:** use one numerical/rational alpha definition: support `1/400`, endpoint refutation `1/1200`, P1 refutation per level `1/2400`. Derive all quantiles from it and reserve rounded percentages for display. Keep REFUTED as significant opposite effect below zero, not merely exclusion of delta; the current INDETERMINATE region is intentional.

8. **Low — Clustering is appropriate; t calibration should be labelled approximate.**

   **Evidence:** `SPEC_0G.json:93–96,108–111` correctly averages two orientations before P1 inference and takes 32 seed-block means, each averaging 38 matched differences, for P2/P3. This retains cross-doctrine and arm covariance, unlike counting 1,216 orientations or 608 configuration clusters as independent observations. Shared resonator results across P2/P3 induce endpoint correlation, which the familywise allocation already permits. The estimand is the equally weighted fixed doctrine pool, not a random population of doctrines.

   The amended validation supplies 100 shared blocks with SD 3.0226/2.0907 (`.../POWER_PLANNING.json:25–29,68–72`). Standalone reconstruction gives modest block skewness (−0.410/−0.322) and excess kurtosis (0.184/−0.180). These support a reasonable exploratory t approximation, but do not prove coverage at the very small refutation tails. Discrete survivor scores are not exactly normal; 32 blocks alone is not an exact finite-sample guarantee.

   **Fix:** declare the independent seed-block sampling assumption and approximate t calibration in the registration/claim limits. Keep the method and n fixed; do not select a different interval method after viewing judging results. No additional fights or blanket sample-size increase are required by this finding. Standard bounds use sample SD divided by sqrt(n), with one-sided t quantiles ([NIST mean confidence limits](https://www.itl.nist.gov/div898/handbook/eda/section3/eda352.htm), [NIST t quantiles](https://www.itl.nist.gov/div898/handbook/eda/section3/eda3672.htm)).

Verified points and authority reconciliation:

- All 22 copied knob values per panel match exactly: `SPEC_0G.json:18–45` equals amended `B_best.json:2–29`; `SPEC_0G.json:49–76` equals amended `C_best.json:2–29`. Panel-specific tuning is declared (`SPECIFICATION_0G.md:20–24`), recommended by both Claude reviews (`S4_AMENDED_REVIEW.md:40–41`, `S4_ORIGINAL_REVIEW.md:49–53`), and not prohibited by design section 5. Claims must remain about these separately tuned panels, not one universal parameter vector.
- Both registered engine hashes (`SPEC_0G.json:10–11`) equal amended `run_identity.json:5–6` and the current binary/build-manifest bytes. The design hash also matches. Engine identity is bound correctly; full JSON-only request identity is still blocked by finding 1.
- P1 still requires both novice and regular, and P2 remains registered despite its unfavorable development result (`SPEC_0G.json:86–102,147–150`). No judging-outcome-informed narrowing was found. Delta 4.0 matches the declared spread rule and S4 planning receipt. This review did not establish root-generation provenance or absence of every possible prior judging use.
- The original STOP is preserved. The amended optimizer supersedes design section 5's old racing rule (`astelia_cpp/S4_AMENDED_PROTOCOL.md:3–13`); the owner decision supersedes the conflicting full-budget gate in design section 10 (`astelia_cpp/s4_checks/AMENDED_GATE_OWNER_DECISION.json:4–11`). Claude explicitly reconciles that clarification (`S4_AMENDED_REVIEW.md:10–13`). Cite/pin these overrides in the final registration's authority chain; do not treat the unchanged design's old stop row as a newly failed gate. Design section 11's S3 authority is not S5/S6 authorization.

Reviewed identities (SHA-256):

| Artifact | SHA-256 |
|---|---|
| SPEC_0G.json | `abac4b3cb3e70d9959cefb803ac7ba6573bec1ebd482e82a35cdef588b69d06d` |
| SPECIFICATION_0G.md | `523e6e76648e306cca51ad31bb713e50c24763d9dd9116124ec6ca6050284e01` |
| DESIGN_0G.md | `fc6494b2bf3e2e8127a7f60a1e2a5b607dd910eeb52a65ccb4ca26c9ff6c262b` |
| amended B_best.json | `02ada71ef5f16c5de6ecd390464ecf75589d405b552f16b4ff5a37d202f2a3ea` |
| amended C_best.json | `cef27aa02f57dc3d8e2d6f9176b44e02e14a40a5fcf755a3cd74fab40f6e0325` |
| amended POWER_PLANNING.json | `b02dd244d657231a4a551fe30aec7fd0b78bf8b1d17b145c6ea6f74aa52109e8` |
| amended run_identity.json | `964fe6c0594050e18046e776a109538bc3afb9434af87f1e77ef2e44fa65f2b0` |

Scope: read documents/source and retained JSON data; compare hashes; perform standalone arithmetic, stored-score summaries and SciPy t/noncentral-t calculations; consult NIST statistical definitions. An initial standalone calculation could not import SciPy from the project venv; the available system package was used instead. No project tests, optimizer, game/simulation code, fights, judging-seed derivation or commit were run. Only this review file was written. The drafter owns the corrections and self-audit; owner approval of the corrected registration and its execution remains required.
