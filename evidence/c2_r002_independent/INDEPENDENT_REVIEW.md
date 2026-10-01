Verdict: **ACCEPTED**.

# C2 R002 independent implementation review

Reviewer: separate Codex agent `/root/c2_independent_review`, with no authorship of the candidate, native kernel, evaluator, references, registration or original evidence. Date: 2026-10-01. Review instruction: approximately **15-minute cap**, focused on the committed C2 mechanism, evaluator, controls and evidence identities. The review completed within that cap. This accepts the implementation and faithful reporting of the registered experiment; it does not accept the primary learning hypothesis or authorize a later milestone.

Reviewed evidence commit: `c4400f7b95cb8df70d1dcf9ac328f7ac3feb37c1`. Numerical/tooling source commit: `63ae7ddc5d11f4c7b59972227c2c0ebf7fbc0cdf`. Experiment: `geomind-c2-r4-002`. All 43 registered source files match the current working files, archived source and actual `git show` contents of that source commit. No implementation edits were required.

## Exact identities

| Item | SHA256 |
|---|---|
| Recorded `results.json` | `34865a9783c2337afda0578ea46e1ac2954926b5485801c394cf2eb47fccd657` |
| Gate fingerprint | `7e9c156dc21824a9948fe1d794181408871018fac1e3e4c52c51cda1e159c9f9` |
| Manifest canonical digest | `1d3e2127da6027a96a9335cc73c5bc2de96c85486f9b09768502785e9af013e1` |
| Python candidate | `f455862a5f8d1e07d0bb58a30b32cfeca592c876b09fb7cdd40874fd1d22a319` |
| Native source | `f16fec19c44be698fb86455e0594c2f44b5df46221e8b5ba9b7bf0f8a1ea2146` |
| Actual native binary | `0a2377c1784117dc050e9b97a3db213aa963a359b7dcb20d3870a33314dc4080` |
| Fresh review `contracts.xml` | `d8d185a431b46bf2a984f7b3016929cc0e0cf4d55a6db7cfa31f0f7f8856f8a7` |
| `identity_check.py` | `f90e61f58243bd587cafdc616ad0742f4b1b4c47a071e03b2e81fc4593282d42` |
| `identity_check.out.json` | `326978c3fd0939ac2d8b9b7eed2ccaea104da06a95e2b529b93c7fb11a0e2a28` |
| `probe_numerics.py` | `490fbf47e8fd13d9cb94f0c7b9357d4192c89bb1e6576955dff9695de6878aa1` |
| `probe_numerics.out.json` | `2aa4aec356eca40f728f85832e0088a948667092a7bf1436c076137585edea55` |

## Focused checklist and findings

| Check | Finding |
|---|---|
| Synchronous Euler ordering | PASS. Every force uses the unchanged old activity vector. Nodes move only after the full edge-force scan and convergence test. The fresh one-sweep probe reconstructs force by a reviewer-owned matrix and verifies the exact timestep/state on eight disjoint development seeds. |
| Timestep bound and accounting | PASS. Current weighted degrees are scanned once per phase; `dt=0.25/(2*max_degree+lambda+beta)`. Bound edge scans, force edge/node reads and node updates are explicitly counted. The final force check after the cap is charged and does not add an extra update. |
| Convergence and same-old-g phases | PASS. Free activity starts at zero; nudged activity starts at converged free activity. Both phases receive the same conductance array, which stays unchanged until a complete proposal exists. Maximum force must be strictly below tolerance. Nonconvergence is visible and leaves persisted g unchanged. |
| Exact learning sign/factor | PASS. Native update is `g+eta/(2*beta)*(df^2-dn^2)`, with the prescribed bounds. Original direct-equilibrium controls and four detected mutants support this. Reviewer-owned incidence-matrix solves independently reproduce updates with maximum error `4.232220685018717e-10` across eight fresh seeds. |
| Transactional refusal | PASS. Fresh probes exercise free-phase refusal, nudged-phase-only refusal, and nonfinite proposal after both phases converged. All retain byte-identical exports and commit no update. NaN, infinity, booleans and extreme finite inputs also refuse without changing g. |
| Target-free inference and persistence | PASS. `query(x)` has no target argument and passes beta=0. Candidate does not import the generator or numerical references. Frozen queries preserve exported g; clone/restore/load tests pass. Recorded retention is the snapshot/query protocol, not continual-learning retention. |
| Independent references | PASS. Reference matrix assembly and adjoint differentiation do not import or call the candidate/kernel. Finite differences check the true half-squared output loss. Fresh probes use a separately assembled incidence-matrix Laplacian and direct finite differences; all eight small-nudge cosines exceed 0.999, minimum `0.9999934837807994`. Maximum equilibrium error is `6.620555048630905e-9`. |
| Generator, splits and controls | PASS. Reconstructed all initialization/dataset/teacher seeds and all 4,000 epoch orders from recorded registrations. Recomputed labels from affine coefficients or an independently assembled teacher system. Each task has 20 independent trial worlds; train/validation/test sizes are 100/50/200. Every method uses the same inputs/training order and permitted targets. Eta and epoch are fixed before fitting; validation does not select settings and test results do not alter training. Feedback removal equals frozen predictions in all 40 trials. |
| Evaluator and causal evidence | PASS. Candidate predictions are fixed before grading; no failed query is silently included in an unconditional MSE. Recomputed every recorded split/method MSE from predictions and targets. Both causal paths concern weighted conductance/activity: predicted edge intervention changes response, and changed feedback changes conductances. These do not establish resonator or hierarchy causality. The complete real caller's receipt serialization/durable-write check passes. |
| Uncertainty and costs | PASS within declared scope. Independently reconstructed the registered trial-level 2,000-resample bootstrap for candidate MSE, paired difference and paired relative reduction, matching means and intervals exactly. No example is counted as an independent world. Native workload counts are not FLOPs or joules. Four-worker wall times are contended measurements; process CPU times and separate generation/fitting/query/persistence/storage/compilation costs remain visible. No positive amortization saving over linear regression is established. |
| Pipeline/evidence identity | PASS. Existing genuine stamps correspond exactly to PIPELINE entries; all stage artifacts rehash and validate. Actual strict-float64 native source/binary match BUILD; archived BUILD matches the live build. Recorded 23 contracts have zero failures/errors/skips and the current fingerprint; the copied mutation artifact matches its real stage hash. Results, EVIDENCE_CONTRACT, JSONL and all 40 durable receipts agree. All 40 trial hashes and 80 initial/final snapshot bindings verify. |
| Prerequisites and historical failures | PASS. Read C1 R006 canonical ACCEPTED receipt and supplemental CONFIRMATION; accepted C1 source/result/receipt hashes remain exact. Its declared five-field Constraint domain limitation remains. C1 R004/R005 are not upgraded. R001 FAILURE and INTEGRITY remain unqualified, with 11 artifacts and an empty streamed result. All 58 R001 files plus the earlier failed-contract gzip are byte-identical to reviewed HEAD; INTEGRITY hashes verify. The initial report retains its one failure. R002 initialization/data/teacher/order seed families are disjoint from R001. |
| New-run guard | PASS. `geomind.run_c2.main` checks `gate.check('panel',milestone='c2')` itself before starting; C1 namespace stamps cannot authorize it. The review stage prerequisite check passed before this receipt was created. No gate stamp was edited or forged. |

No blocking findings or repair requests arose within this focused review. Acceptance covers the registered fixed-topology experiment and public snapshot/query/learning protocol; it is not exhaustive certification of arbitrary caller mutation, alternate settings or future tasks.

## Fresh executed checks

1. `.venv/bin/python tools/gate.py --milestone c2 check review` — PASS before creating the receipt.
2. `.venv/bin/python -m pytest -q -x -p no:cacheprovider tests/test_c2.py tests/test_c2_gate.py --junitxml=evidence/c2_r002_independent/contracts.xml` — **8 passed in 1.26 s**, zero failures/errors/skips. This meaningfully rechecks the affected numerical, persistence, serialization and gate paths; the original recorded pipeline's 23 checks are reused as original evidence.
3. `.venv/bin/python evidence/c2_r002_independent/identity_check.py` — PASS, output `identity_check.out.json`. Read-only audit of all source/build/stage/trial/history identities, splits, target generation, initializations, orders, scoring and uncertainty. The script was extended to include independently reconstructed labels and R001 INTEGRITY, then rerun; no numerical panel ran.
4. `.venv/bin/python evidence/c2_r002_independent/probe_numerics.py` — PASS, output `probe_numerics.out.json`. Eight disjoint development initialization seeds plus eight refusal cases; no training panel or final-test tuning.

Read AGENTS.md, R4 C2/C3, the recursive interface and C4 prerequisites, §§5–7, HANDOFF, results, EVIDENCE_CONTRACT, AUDIT, PIPELINE, contracts, MUTATION, BUILD, Python candidate, native kernel, generator, evaluator, independent references, tests and C2 verification/gate tooling. No C0/C1 experiment, full C2 panel, mutation suite, C3, hierarchy or hardware-energy evaluation was rerun. Recorded evidence was reused unchanged.

## Separate hypothesis verdict and next boundary

**Primary realizable endpoint: INCONCLUSIVE.** Independently recomputed candidate mean test MSE `0.0004149391585941494`, CI `[0.00021392073640519785, 0.000650805954005404]`; the error target passes. Mean paired relative reduction is `52.49198827478774%`, CI `[44.80292991425892%, 59.96338122546827%]`; its lower bound fails the registered >=50% requirement. The paired MSE difference is negative throughout its CI, so there is bounded evidence of actual learning against the frozen initialization, but the full meaningful-effect endpoint remains unqualified.

**Affine endpoint: NOT_SUPPORTED.** Mean test MSE `0.017576919005517194`; relative reduction `8.920474007224094%`, CI `[7.452492665375646%, 10.45594519539709%]`. Linear regression solves both tasks to numerical precision with much smaller reported fitting/query work. The native candidate and direct/gradient controls are passive linear models; the realizable teacher shares their topology. No additional task-quality or efficiency value, moving-coordinate necessity, resonance, recursive closure, novel AI or energy saving follows from implementation correctness.

C2 correctness and bounded actual learning evidence meet the literal C3 prerequisite; they do **not** constitute an instruction to start C3. R4 §7 additionally requires a bounded research decision because the matched simpler linear baseline dominates this supervised task branch. Stop progression pending that explicit decision. C3 and hierarchy remain **NOT_STARTED**; hierarchy cannot rescue the C2 result. The independent resonator lane needs its own registered contract, prerequisites and authorization.

Reviewer-authored files are this receipt, `contracts.xml`, `identity_check.py`/`.out.json` and `probe_numerics.py`/`.out.json` only. `RESEARCH_DECISION.md` and `RESEARCH_BASIS.json` in this directory are root-authored reconciliation material, not independent numerical-review artifacts. The reviewer made no implementation, original-evidence, status-document, gate-stamp, commit or push changes.
