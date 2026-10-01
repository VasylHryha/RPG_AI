# Independent C1 implementation acceptance

Verdict: **ACCEPTED**. Reviewer: separate `/root/c1_acceptance` agent, 1 October 2026. Scope: `geomind-c1-r4-002` against the C1 transaction, residual, budgeting, reference and evidence requirements in `GEOMIND_GEOMETRIC_AI_QUALITY_STANDARD_R4.md`. No blocking implementation defect found. This establishes the accepted-C1 prerequisite for the C2 lane; milestone status changes belong to the implementation owner.

This acceptance uses R4's explicit rule: updates may commit correctly or remain explicitly unresolved, with the prior snapshot retained and all work charged. It does not mean all updates are solved or that this is an optimal numerical method. Numerical code, tests, manifests, original results, original contracts and authoritative status documents were not edited. Only this separate receipt and `acceptance_contracts.xml` were written.

## Exact reviewed identity

- Canonical manifest SHA256: `3d2385e73bc23a0e45ac3e7e65675ecb654bafd228fb4661a4b335925901dd12`.
- Manifest file SHA256: `9d6cec1e0f226103d39779de8eaa09a8b425c5665ab5462ff1695e1c717ac705`.
- Original `results.json` SHA256 at review: `c4e901f390cf230a7b021bc729cb719792c7d0c69a4e3960ad652734ae357c01`.
- Original `instances.jsonl` SHA256: `054b27a3f286d1a28a0a098938eabfa54c3dbc881a8535d2f3208ccba29b5c01`.
- Original ten-case `contracts.xml` SHA256: `b171bd1744e0b53dc135a8dce54842ca647323e2e0fc63c4e6f1c0f7e55a6ad5`.
- Reviewer `acceptance_contracts.xml` SHA256: `c4959ca9ba7bedf503274d711eef9e44fca975a56d4b8e1d78b8a642d62fded8`.
- Accepted C0 receipt SHA256: `ce6ecce70f35bb4af918b80a1c54136649a1f515f4788a3f34de776d87b6c453`.
- Source commit: none. The following 19 registered input hashes matched the receipt, archived source and live input bytes at review. This is the accepted input subset; later added milestone files do not inherit acceptance.

| Registered input | SHA256 |
|---|---|
| `experiments/c0_manifest.json` | `e098d5f7aa79ada9de8f1ae3716da39fa245c305ed01d74e199071f3e75236a4` |
| `experiments/c0_r4_001_manifest.json` | `b9f3fdbc52d2c6c0688196517abcfe365e5f0036766cd7f19341ee2976bae995` |
| `experiments/c0_r4_002_manifest.json` | `4c707247b0b71ed35eb52facf95565a4ff8ccf6211e88c3d58257b46732ec05f` |
| `experiments/c1_manifest.json` | `9d6cec1e0f226103d39779de8eaa09a8b425c5665ab5462ff1695e1c717ac705` |
| `experiments/c1_r4_001_manifest.json` | `896cb372c4824f5b461a23612bec70633aa3bf0ad48d5c6f4b9b25c8e7fa57a3` |
| `geomind/__init__.py` | `c68e2354ec176b189254b853c52029546321c6fbe5b85ac554e38986adc43039` |
| `geomind/c1_cases.py` | `0cbd7efe8336847eb79bcd38bf831e2180106ae27579a0c4ef09803c684caa71` |
| `geomind/c1_reference.py` | `e4d9439a69e65152cf04605f7aa7de0d878c2f27a530d5dc02ef148cac59279f` |
| `geomind/dataset.py` | `003fa18f0519bdb177f4594b1565ca91006b8fad8c0b4ca3d1e450ac2927b48e` |
| `geomind/geometry.py` | `973740d321705d9c8633a6cd2da1696af91cec930e53bcb6b6b4831e280066f0` |
| `geomind/incremental.py` | `3e35ef264dde32c31d29363a839397031dde74ec533712ea03fb3c994fbef43f` |
| `geomind/references.py` | `771f9b355083240fa2bf1a5e713bb1f964f9fd493d7e485aa2d4ba1f5e5255f9` |
| `geomind/run_c0.py` | `75708d230390bac8297c8f3a9ebfbf910b37d5d9b688f13989e27b98ba84f0ea` |
| `geomind/run_c1.py` | `5aa6289ed2eca78a0b997339fae317aa4daf471f773a3bbc360b5d39a3858d63` |
| `pyproject.toml` | `b13af15c4b02a76b429da4d76965cddf66f73d59198bca80d01fab7b51c705e2` |
| `tests/test_c0.py` | `915d8e8fd05b140e775ca164705eb0304353de4d1307a30ff72edf8630763e99` |
| `tests/test_c1.py` | `ecd57c74784feab31a19cc534ea4bad4697b645576b8bd7533e47c828ed6694a` |
| `tests/test_review_contracts.py` | `6afd2fe61c2a1e54018e475443b1e373587ee61306501128de802b357767205e` |
| `uv.lock` | `284881c4c71c8282aca81e9053794d2b0333f9ab10b21d9e425cba13bec918c8` |

## Findings and actual checks

Read R4 C1, the handoff and repair record, candidate state/fork/load/update implementation, case construction, independent sparse and compiled/dense controls, evaluator and all ten focused checks. The candidate receives only typed public constraints and imports no evaluator truth or reference solver. A saved C0/C1 state is explicitly forked rather than thawed. Existing component frames and singleton new nodes are translated through a deterministic added-edge spanning tree; direction signs preserve the declared `x_target - x_source = offset` convention. Old internal differences are preserved by rigid translations. Cycles and conflicting offsets still use the C0 residual energy and gradient law, with declared asynchronous node-local execution in stable ID rounds. Gauge changes are evaluated through displacement answers.

Added-edge placement reads, queue incident reads and global convergence certificates share the strict 100,000 dynamic edge-visit cap. A budget exhaustion can occur after partial workspace changes, but commits are atomic and prior snapshots remain intact. Absolute force, degree-normalized force and implied step must satisfy the declared stopping tolerances; ten metered certificates prevent an empty queue from qualifying a bad equilibrium. Load validates schema, checksum, public constraints, connectivity, gauge and stationarity, including the C1 step bound. Historical migration is explicit and revalidated.

The sparse control uses its own union-find, gauges, matrix-free anchored normal equations and preconditioned conjugate gradients; it imports shared public answer/number validation types, not candidate preparation or gradient numerics. Small dense and hand-derived weighted controls independently qualify its signs, weighted solution and tiny-weight behavior. Candidate predictions are fixed before the fresh references are constructed. Typed finite answers, complete per-answer error qualification and independently measured committed residual energy prevent success traces, missing answers or nonfinite values from qualifying an incorrect commit.

Ran one affected reviewer command, preserving the original contract report:

```text
.venv/bin/python -m pytest -q tests/test_c1.py --junitxml=evidence/c1_review/acceptance_contracts.xml
```

Result: **10 PASS in 2.55 seconds** (JUnit suite duration 2.555 seconds), zero failures/errors/skips. These checks exercise correct updates, sparse/dense agreement, tiny weights, budget rollback, bridge admission, frozen parent/sibling isolation, gauge changes, additive update chains, duplicates/cycles, explicit migration, custom tolerances, overflow, wrong/missing/malformed evaluator answers and exact-source report/acceptance controls.

Also completed read-only independent receipt inspection without rerunning the world experiment or incremental relaxation panel. Hashed all 19 current and archived inputs; checked the registered manifest and all sixteen size/kind/seed identities; compared the complete streamed records exactly with the receipt; parsed both complete source-bound contract reports; verified accepted C0 identity and unchanged reviewed C0 inputs. Loaded all 48 saved original/fork/after artifacts, checked their hashes and serialized round trips, compared every saved candidate panel answer, reconstructed evaluator-owned public cases to verify additive observations, and checked every one of **2,704 disconnected retention queries**. Recomputed every committed residual energy from saved query answers, every available displacement error and all **159/159** excluded cross-component abstentions. Verified dynamic visit arithmetic, strict caps, zero fallbacks, before/after digest identities and refusal proofs; checked that R001 and C0 archived sources and streams still match their own receipts. The first inspection attempt stopped on Python 3.9's unsupported Counter comparison; the inspection expression was corrected, then the complete read-only inspection passed. No experiment input was changed.

All six original engineering gates are PASS. The original ten-check report remains unchanged. Reached numerical evidence is **13 correct commits**, maximum committed displacement error **5.597670464368681e-8**, maximum independently reconstructed energy gap **3.469446951953614e-15**, and all fresh reference statuses PASS. All consistent-edge, new-node and bridge interventions commit across 32/128/512/2048 nodes; the 32-node inconsistent edge commits. Original full panel duration remains **7.280474417 seconds**; it was not repeated for this review.

## Accepted limitations and next action

The inconsistent-edge updates at **128, 512 and 2048 nodes remain NOT_CONVERGED**. Each recorded transaction consumed exactly **100,000** dynamic visits, required one additional visit, and retained its fork-before bytes exactly. Their old answers are prior-state answers and must never be presented as updated solved answers. These explicit refusals satisfy R4's implementation acceptance rule. The reference converges on all three, so the candidate is not established as the best general update solver; changing language alone would not remove the operation cap.

H-P and H-L remain **INCONCLUSIVE**. No learning, hierarchy, superiority, computational locality, sublinear end-to-end behavior, out-of-family generalization or hardware-energy claim is accepted. The panel contains one structured world per size/intervention. Global preprocessing, translations and certificates remain real overhead; the recorded times include these operations. Numeric workspace bytes describe selected arrays, not peak process memory or all Python heap allocations. Compiled setup is explicitly a public-constraint initialization, not learner work, and its traversal counter is not a complete operation count. R001/R002 timing differences are diagnostic observations with different seeds/coverage, not a paired benchmark.

No C1 implementation repair or repeated full C0/C1 experiment is required for this verdict. Preserve the original R002 execution evidence as historical REVIEW_READY and use this separate acceptance receipt to establish the subsequent review outcome. Proceed to C2 under its own declared mechanism, controls, held-out evaluation and acceptance gate; do not imply that C2 or recursive hierarchy has already been implemented or accepted.
