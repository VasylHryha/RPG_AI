PASS_WITH_NOTES
Reviewer family: Codex
Reviewer: separate Codex agent, GPT-6
Scope: static controller/tooling review for prepare-only shape lab v5. No tests, fights, coreStep, tuning, or outcomes were run by this reviewer.

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Reviewed against AGENTS.md, decision 0033, SHAPE_LAB_SPEC sections 11–14, the unchanged adapter v1, v4 structure, and original native artillery/combat rules. Findings were sent during implementation and repaired before this final static disposition.

Findings and disposition:

- F1, build blocker: extracting artillery.cpp::fireGate omitted its enclosing anonymous-namespace pi constant. The generated gate now declares pi=tau/2; reviewed the final generation seam.
- F2, measurement defect: dodge success excluded launch-exposed enemies which died before landing from its denominator. The final ratio uses all launch-exposed units of resolved shells; deaths remain disclosed as non-escapes. README/report now state the same definition.
- F3, receipt/resume defect: low-gun diagnostic maps used integer keys, which JSON serialization changed to strings and broke remeasurement equality. Final metrics return string keys, with synthetic stream round-trip coverage.
- F4, summary/resume defect: integer streak-distribution keys likewise broke unchanged SERIES_SUMMARY comparison after JSON round-trip. Final summaries return string keys, with synthetic-series round-trip coverage.
- F5, fixture defect: the missing-cap test changed CAP_PATH before establishing its synthetic CPP root. The final fixture establishes both before calling local_cap.

No remaining blocking static findings. The native fixture covers synchronous normalized local coupling, catalog-cycle omega, radius and infinity normalization, live-set removal and single-gun decoupling, ready versus unready crossing, legality veto, one-cycle bound, real-fire reset and independent clone state. Persisted synthetic CENTRAL_STATES cover ready/cooldown/windup states, the sync-window boundary and cached gate, waves timeout and one/two guns against the original engine gate and the original waves predicate. The unchanged adapter fixture is rebuilt against the derived v5 controller layout; this avoids mixing the old class layout with the added Battery member. Request fixtures construct each native arm/scenario at time zero without a fight.

The runtime seam evaluates central rules before gamePrep and evaluates oscillator release after gamePrep. Central holds are computed for the complete decision state before applying hold commands, preserving the engine waves count. Oscillator release requires a prepared cast and legal unblocked P16 target; unready crossings are not queued; phase resets only at actual normal-shell launch. Local coupling uses living own artillery within R_c, synchronous old phases and K_i=k/T_i. Re-submitted commands retain P16 target/aim and cannot override adapter REACT/body/failure precedence.

The declared nine-point grid uses twenty paired mechanism draws per point, sharing the two script baselines (220 fights total), including one/two-gun draws and dodging-dummy drills. No mechanism abilities run. Pick/read receipts are immutable and linked to complete mechanism/declaration identities; outcome cannot open without the one-time mechanism pick and continue reading. C3 retains 50/100/200 total paired looks; series has paired schedules, arm-specific healed survivors and streak as primary. Heavy collectors are removed, selected replays and the same cap/process gate/resume paths remain.

Notes for Claude's eventual development reading: exact-tick volley grouping can produce singleton-only data; null spread cannot support positive synchrony. Central idle starts at preparation readiness while oscillator idle starts at full preparation, as disclosed; interpret them with fired shells per living gun-minute. Dodge escape is descriptive launch/landing exposure, not causal attribution. Hits/shell and shells/kill use resolved landed shells and report unresolved shells. Grid selection uses mechanism measurements only. This review does not establish outcomes, source recursion, scientific acceptance, or authorization to run fights. The implementer must finish the focused test/build checks and zero-fight preparation.

Reviewed source SHA256 identities:

- `timing.h`: `985ffab8edbcc2c50e838adbd099212e90037bc8f8183fc476ba03040507eaf4`
- `timing.cpp`: `4d7fe035b7965e7f6d67ab14246f9e91fb612402c4b3f9e23ff32ad57cf025ca`
- `build.py`: `7b9b7fd886ac88c2b58be6e6f8ef88892c34f7da1b6c48a1914042ec319004da`
- `lab.py`: `7da25c8dd550e3651d946a27771dcd62bfb16d3ba6044dce9b5fd67c3d51ba93`
- `requests.py`: `0b32d169d720d8d3b5bb1a17a24b220beff8152cf621c792034a24cd69d26dcc`
- `metrics.py`: `d30a591cfa2bcd421ddbbe53419ff839cebfd7e6a26e26a740f857411980ba90`
- `report.py`: `c41523d797a6c3cbb20ca1c1001bdedfecb29da25de2f868b87bd3689527234a`
- `replays.py`: `5ff222a07bec888aded30bceab0dbec817c6264508f51c2bf4c529f04d42495d`
- `fixture.cpp`: `24eb8a40838a9220980a98ab1d6510ace4d3d49810cdde8159aa59c3c604c131`
- `test_lab.py`: `d65c2220bf44662622131fcdcb95c1fd1cb27938d4c8ca6d4895e965e1d27769`
- `CENTRAL_STATES.json`: `1437d753d8dad25d1be43e7b8afec4aebe44b77467010db8d64eb6077218d671`
- `README.md`: `42855166394cc78f2fca70280841554ea87777fe96d8c9082bb1b051a2f69ef0`

Addendum: collection syntax repair

The implementer first focused invocation stopped during collection at an unmatched closing parenthesis in lab.py declaration construction; no fixtures or fights executed in that invocation. The original static review missed this syntax defect. Inspected the final correction removing exactly one extra closing parenthesis after the reading list. Reconstructing the prior text by adding that parenthesis reproduces the historical reviewed lab.py hash above, proving this is the only lab.py text change. Historical reviewed hashes are preserved. No tests or fights were run by this reviewer; implementer final focused execution remains pending. Static disposition remains PASS_WITH_NOTES.

Updated reviewed lab.py SHA256: `1a021e901144d005583131ed3233340160854e4020a65bb2b84316f071845baf`.

Final prepare-only evidence review

Status: PASS_WITH_NOTES for delivery of the prepared V1 test; no final delivery blocker found. This is a read-only evidence recheck, not a fixture/fight rerun or an outcome reading.

Verified final BUILD.json reports PASS, 21.275289667 s and zero fights. Checked actual binaries against manifest binary hashes, all manifest source hashes and reused-object hashes, and all declaration source links against current files. Reviewed source files retain the historical reviewed hashes except the explicitly reviewed single-character lab.py syntax correction.

The collection failure is preserved separately. TEST_SETUP_ATTEMPT_02 output records seven passes before a missing basetemp-parent setup error. TESTS output records thirteen remaining passes and seven deselections, agreeing with the final twenty-check accounting and no repeated successful native fixture execution. NATIVE_FIXTURES and native stdout agree on 143 battery/controller/request assertions and 469 unchanged-adapter assertions, zero fights. These are implementer receipts; this reviewer ran no tests, fixtures, fights or coreStep.

Verified PREPARE ledger/declaration hashes, all 320 seeds unique and absent from the preserved prior development inventories, twenty paired draws for each of nine oscillator grid points with shared script baselines (220 declared future mechanism fights). The raw directory has no completed-fight receipts; there is no pick or calibration. OBSERVATIONS shows every stage incomplete and no pick, as required for zero-fight preparation.

PROCESS_GATE records UNAVAILABLE with the actual sandbox process-discovery failure. Execution remains blocked until the existing gate passes CLEAR on Claude's host; that environmental limit is disclosed in DISPOSITION and is not bypassed. Owner cap is unchanged at 10800 s. DISPOSITION accurately separates interrupted test attempts, passing focused coverage, preparation, controller review and future mechanism/outcome readings. PLAN_CURRENT tracks the recheck and remains excluded from the delivery staging scope. Git is read-only under this session's explicit filesystem permissions; no commit/staging is claimed.

Current delivery completes preparation only. Claude must still run the gated staged development comparison, make the mechanism-only one-time grid pick, and provide actual sequential outcome/series readings. No measured controller benefit, source recursion, experimental acceptance or release is established.

Final evidence SHA256 identities:

- `BUILD.json`: `09fa50167b227a2591cd1952f0606b1d8b795222f4cd06894a9227b303e58ce1`
- `TEST_COLLECTION_ATTEMPT_01.json`: `26cc015cce71f79b917348a477da6703d7b268d16cc4f0dd5ccffa4a60341461`
- `TEST_SETUP_ATTEMPT_02.json`: `4c0496fedd10b3d11e8e6a6e376321b86a7658d386ef5389969e0e17d98c9ef8`
- `TESTS.json`: `71e4c0464d9ec875bb6e2fb4affc377592280a4548024c3de9de2a32ef3f7074`
- `NATIVE_FIXTURES.json`: `607614e5f31c30bc5e268ac46cc962d33015c29fd64fc307e621ef7c17e66f9e`
- `DECLARATION.json`: `cbb32aec7034c02107d8f797245434c9dc759ce1b3b0e05e89b1265eff8fbb7a`
- `PREPARE.json`: `76afbe59a7d0c39353c86f47a6c21f551bbeb298245d2cb012b0ad060949da6e`
- `PREPARE_VERIFICATION.json`: `9105446e4608d6a4bcd27239b646f4288d947becedb4be6ddf1ec12172c2305c`
- `OBSERVATIONS.json`: `ca64ca6b36f36782b56e89a4509ea60aa257d280982c6e310f9d76c0d7823c19`
- `PROCESS_GATE.json`: `f2294f66073bf300b62b9b96aa0e15c9595512c7ac0d13ca7e9fd04737e2f2d0`
- `DISPOSITION.md`: `20b53db229f993944dcf230dccd7b77b5e645cca47bbcccf311f6fa8d58cb7db`
