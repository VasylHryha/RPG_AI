# C1 R005 independent review handoff

C1 R005 (`geomind-c1-r4-005`) is **REVIEW_READY**, not accepted. It repairs the independent review of R004 (`../c1_r004_independent/INDEPENDENT_REVIEW.md`, CHANGES_REQUIRED), and its author is the same agent who wrote R004. A **different reviewer** must decide R005 before C2. Earlier receipts (R001–R004) are unchanged, and all 12 accepted C0 inputs are byte-identical.

## What R005 changes, finding by finding

| R004 finding | R005 repair | Verification |
|---|---|---|
| F1 (High): uncharged Θ(R) relation-map copy in every `apply` | Delta validation reads only the delta and looks stored relations up by key | Focused check with a counting map: 0 scans. Reviewer's `probe_hidden_work.py`: apply 133 → 184 µs from 32 to 32,768 nodes (R004: 66 → 2,644 µs). A registered **wall-clock** locality endpoint (≤ 4×) now complements the operation meter |
| F2 (High): certificate not sound for the exported gauge | **Export-gauge invariant:** coordinates are stored exactly as exported, with every anchor at 0.0, so C0 recomputes identical residual bits. The merged anchor is chosen first (C0 rule), its frame stays fixed, and re-anchoring re-stores the frame (charged, `regauged_components`). Every written node is certified. The margin is a rigorous rounding bound `4(n+2)·eps·Σ\|w·r\| + 8·eps·\|f\|` | Reviewer probes P2, P4 and P5 at scale 1e3–1e6: 1,338/1,338 commits reload (R004: 11 rejected). New focused checks reproduce P2, P4, large-scale chains and a relaxation frontier, and assert that every node whose C0 force changed *at all* (exact comparison) was certified |
| F3 (Medium): degree overflow committed | Non-finite degree → INVALID_STATE and rollback. A running energy upper bound is added as a backstop; certification makes it unreachable | Probe P3: INVALID_STATE, matching C0 `learn`; focused check |
| F4 (wording): verdict scope too broad; no compiled baseline | Verdicts split into consistent edge + new node, bridges (size independence NOT_TESTED) and contradictions. An **incremental compiled baseline** is measured on every case | Receipt `endpoints.incremental_compiled_comparison`; baseline gated for correctness |
| F5 (wording): fallback/reference ratio mixed units | Ratio claim removed; raw numbers reported, with units noted | — |
| F6: refused rows in accuracy medians | `frozen_vs_adaptive` uses committed rows only, per arm | — |
| F7: invalid oversized delta returned NOT_CONVERGED | Validate before charging | Focused check |

## Reached evidence

```text
.venv/bin/python -m pytest -q tests/test_c1.py --junitxml=evidence/c1_r005/contracts.xml
.venv/bin/python -m geomind.run_c1 --output evidence/c1_r005 --contract-report evidence/c1_r005/contracts.xml
```

Nineteen focused checks PASS. The panel ran 80 interventions (4 sizes × 4 kinds × 5 worlds, seeds from 11,000,000) in 104.5 s, and all six gates PASS.

- **Queue arm:**
  - 60/60 consistent-edge, new-node and bridge updates commit correctly, all with zero relaxation steps.
  - 3/5 contradictions at **32 nodes** commit after real relaxation (68,584–98,106 operations).
  - Contradictions at 128 nodes and above: 0/15, all explicitly refused with byte-identical rollback.
  - Maximum error `6.06e-8`.
- **Fallback arm:** 80/80 correct, 17 through the metered CG.
- **Abstention and identity.** 790/790 excluded cross-component pairs abstain in both arms. All states hash to the receipt.
- **Scaling at 2,048 nodes (medians over 5 worlds; min–max in `cells`):**
  - Consistent edge: 39 operations, 0.16 ms, against a fresh recompute of 60.9 ms.
  - New node: 30 operations, 0.16 ms.
  - Bridge: 2,639 operations, 3.1 ms. It translates and certifies the 512-node smaller frame, or 1,024 nodes when the anchor lies in the other frame.
- **Re-anchoring.** It occurred in 3 consistent-edge, 4 new-node, 3 contradiction and 1 bridge worlds, and in none of the 2,048-node locality cells.
- **Registered H-L verdicts:**
  - consistent-edge and new-node in-memory updates: **SUPPORTED_WITHIN_SCOPE**. Operation ratios are 1.18 and 1.11 against the ≤ 2 limit; time ratios 1.73 and 0.95 against ≤ 4; every 2,048-node speed ratio is ≤ 0.006, against < 1.
  - bridges: size independence NOT_TESTED; the faster-than-recompute endpoint is met (ratios 0.034–0.27).
  - contradiction resolution by the local queue: **NOT_SUPPORTED** (0/15 at ≥ 128 nodes).
  - durable persistence: NOT_TESTED, global by design.
- **H-P:** INCONCLUSIVE.

## The result that matters most: a matched simpler baseline dominates

The incremental compiled baseline is union-by-size compiled frames with O(1) consistency checks. At 2,048 nodes it gives the same answers in:

| Kind | Baseline | Candidate |
|---|---|---|
| Consistent edge | 0.012 ms, 1 operation | 0.16 ms, 39 operations |
| New node | 0.016 ms, 3 operations | 0.16 ms, 30 operations |
| Bridge | 0.41 ms, 513 operations | 3.1 ms, 2,639 operations |

It cannot represent contradictions, which need a least-squares solve. There, the candidate's local residual queue fails at ≥ 128 nodes, and only the global CG fallback resolves them.

So on the registered quality/cost criteria, **a matched simpler baseline dominates the candidate's mechanism**. Under R4 §7 that is a stop signal for the claim that the residual dynamics add useful locality. The locality that does hold comes from compiled frame bookkeeping, not from relaxation. This bears on the hypothesis, not on implementation acceptance, and should inform how C2 frames its mechanism question.

## Mutation probe

`evidence/c1_claude_review/mutation_checks_r005.json` records 32 deliberate defects, including every reviewer finding; the suite catches **28**. The four survivors are documented backstops, each compensated:

- the energy bound, which certification makes unreachable;
- the forced certificate step, which affects only budget use;
- the local step-tolerance quiet check, behind the certificate plus forced step;
- the local force-norm guard, behind the residual-energy finiteness check.

## Smallest meaningful independent review batch

1. `pytest -q tests/test_c1.py --junitxml=<fresh dir>/contracts.xml`: 19 checks, about 15–20 s.
2. Read-only identity check of `evidence/c1_r005/` against the live files, `source/` and the gunzipped states.
3. Review the export-gauge invariant and certificate argument in the `incremental.py` docstring against `_apply_structure`, `_relax`, `_certify`, `export` and `query`.
4. Rerun the reviewer probes from `../c1_r005_fix_checks/` (about 3 minutes) and, optionally, the mutation probe (about 12 minutes).
