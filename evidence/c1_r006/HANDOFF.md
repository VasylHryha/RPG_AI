# C1 R006 independent review handoff

C1 R006 (`geomind-c1-r4-006`) is **REVIEW_READY**. It is the first revision produced end to end by the gated pipeline (`PIPELINE.json`, `MUTATION.json`). It repairs the independent R005 review (`../c1_r005_independent/INDEPENDENT_REVIEW.md`, CHANGES_REQUIRED). That review confirmed R004's findings F1–F7 as fixed and found one blocking defect, N1. The author (the same agent as R003–R005) did not review it; a different reviewer decides acceptance. Earlier receipts are unchanged, and the 12 accepted C0 inputs are byte-identical.

## Changes against the R005 review

| Finding | Repair | Verification |
|---|---|---|
| N1 (blocking): numpy `float32`/`int64` inputs committed PASS, then every `export()` raised `TypeError` | `_validate_delta` serializes the delta exactly as export will (as C0 checks before committing). Non-JSON numbers refuse with INVALID_STATE. numpy `float64` (a `float`) still commits and exports. Algorithm/schema v6, with an explicit R005 migration adapter | New focused check (both numpy types refuse, state unchanged; float64 exports). New mutant `delta_serialization_unchecked` is caught. Migration of a real R005 artifact gives identical answers |
| N2 (wording): re-anchoring tail not stated | See "Re-anchoring tail" below | Receipt `regauged_worlds_by_kind` |
| N3 (wording): baseline ratio is single-run; the stop signal is reported, not gated | See "Baseline comparison" below | — |
| N4: `next_action` said R004 | Now derived from the experiment ID | Receipt |
| F6 leftover: refused rows reported post-transaction accuracy | `post_transaction_total_accuracy` is `None` on refused rows; their state accuracy is `frozen_total_accuracy` | Receipt |

## Evidence from the gated pipeline

`.venv/bin/python tools/verify_milestone.py --output evidence/c1_r006` ran on committed code. Every stage is stamped against the source fingerprint with the hash of the artifact that proves it:

| Stage | Time | Result |
|---|---|---|
| preflight | 0.2 s | clean committed tree, C0 inputs unchanged, manifest valid |
| tests | 16.8 s | 19 C1 checks; C0, review-contract and gate-hook checks |
| smoke | 0.8 s | one 32-node world per intervention, on non-panel seeds |
| mutation | 60.2 s | 29/33 caught; survivors are the 4 documented backstops; no unexpected survivors or timeouts |
| panel | 107.1 s | 80 interventions (seeds from 12,000,000), all six gates PASS |

**Panel results:**
- **Queue arm:** 60/60 consistent-edge, new-node and bridge updates commit correctly, with zero relaxation steps. One contradiction at 32 nodes resolves by relaxation; 0/15 at ≥ 128 nodes, each explicitly refused with byte-identical rollback. Maximum error `4.85e-8`.
- **Fallback arm:** 80/80 correct.
- **Registered H-L verdicts:** consistent-edge and new-node in-memory updates: SUPPORTED_WITHIN_SCOPE (operation ratios 1.33 and 1.11; time ratios 1.75 and 1.42). Bridges: size independence NOT_TESTED. Contradiction resolution by the local queue: NOT_SUPPORTED. H-P INCONCLUSIVE.

## Re-anchoring tail (N2)

When an update raises a node above its component's anchor (the C0 rule: maximum weighted degree, then smallest ID), the whole component is re-stored relative to the new anchor and re-certified. That work is O(component), and it is charged and reported (`regauged_components`, `translated_nodes`).

The registered locality endpoint uses medians, so a minority of re-anchoring updates does not change its verdict. Individual updates still have this tail:
- **R006:** re-anchoring occurred in 1 consistent-edge world (128 nodes, 317 operations), 4 new-node, 2 contradiction and 3 bridge worlds.
- **R005 review, fresh seeds:** it occurred in 32.5% of consistent-edge updates at 32 nodes and 2.5% at 2,048, with single updates up to about 5,300 operations.

## Baseline comparison (N3)

The incremental compiled baseline gives identical answers faster than the candidate on the additive kinds: 7–13× in the R005 run, and 10–18× in this one (consistent edge 18.5×, new node 10.3×, bridge 15.9×). These are single-run wall-clock ratios. The baseline's timed path also skips input validation and the convergence certificate, which the candidate performs, so the ratio overstates the gap per unit of equivalent work.

The comparison is **reported, not a registered gate**. It is evidence for R4 §7's stop rule ("a matched simpler baseline dominates"), not a registered endpoint outcome. The additive locality that holds comes from compiled frame bookkeeping, not from residual dynamics.

## Smallest meaningful independent review batch (time cap: about 15 minutes)

1. `python3 tools/gate.py status`: all five stages verified for the current fingerprint.
2. `pytest -q tests/test_c1.py tests/test_gate.py` (about 20 s).
3. Read the N1 repair (`_validate_delta`) and its focused check. Try other non-JSON numeric types against `apply` → `export`.
4. Read-only identity: `results.json` `file_hashes` against the live files and `source/`; `PIPELINE.json` fingerprint against `tools/gate.py`.
5. Confirm the N2/N3 statements above against the receipt.
