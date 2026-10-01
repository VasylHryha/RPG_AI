Verdict: **ACCEPTED**.

# C1 R006 independent review (`geomind-c1-r4-006`, commit 721249b)

This verdict covers implementation acceptance only. Hypothesis support is a separate question; the registered H-L and H-P verdicts are reproduced below as stated and not re-argued.

## Reviewed identities (SHA256)

| File | SHA256 |
|---|---|
| `evidence/c1_r006/results.json` | `7026b5b59d438395801c81cb8b58a00bf30e01544cd9536a2d8239dfbd82342f` |
| `geomind/incremental.py` | `fcbb18a41f151da3d93c47f9779af0ae46adc3e45fe2f61581f825ab66118b23` |
| `geomind/run_c1.py` | `c561625056311ecee9ff795844b67775567db49a7b40f1697b4e6a9c74cbdeb5` |
| `tests/test_c1.py` | `31ff88acd1c7b7df479153063283d891fde2dd855e9bc9a9ebbf38eee343dd5e` |
| Gate fingerprint (`PIPELINE.json` = `gate.fingerprint()` = `gate.py status`) | `1f4b04b171030ca9509319f5d1e187e8e40fbe9909e1c073085eaf119e907978` |
| This review's `contracts.xml` (34 tests, 0 failures, 0 errors) | `39f44d0dd4e4f90d2f55703c1e4d8c922957708302502eca90c28c53524b6474` |

## R005 findings

| Finding | Status | Evidence |
|---|---|---|
| N1 (blocking): non-JSON numbers commit, then export fails | **Fixed** | `_validate_delta` (`incremental.py:453-458`) runs `canonical(...)` on the delta's nodes, edges and relations before any mutation. A `TypeError` becomes INVALID_STATE through the existing handler. `probe_n1.py` (`probe_n1.out`) ran 24 value kinds × 3 positions (offset, weight, relation vector), giving 72 applies. Every numpy non-`float64` scalar refuses with INVALID_STATE, and the export is byte-identical. The numpy types tried were float16, float32, longdouble, int8, int32, uint8, int64, uint64 and bool_. Python `bool`, `Decimal`, `Fraction` and ints ≥ 2**64 also refuse with an unchanged export. Valid inputs still commit, export, reload and re-export byte-identically: Python `int`/`float`, `np.float64`, `IntEnum`, int/float subclasses with overridden `__repr__`, `-0.0`, `5e-324`, and ints of 2**63 and 2**64−1 as weights. **0 values commit and then fail export or reload.** The `update()` compatibility path delegates to `apply`, so it is covered. Mutant `delta_serialization_unchecked` is caught (`MUTATION.json`) |
| N2 (wording): re-anchoring tail | **Fixed in the HANDOFF; residual Low item R1 below** | The HANDOFF section "Re-anchoring tail" matches the receipt. `regauged_worlds_by_kind` = {consistent_edge 1, inconsistent_edge 2, new_node 4, bridge 3}. I recomputed from `instances.jsonl`: the one consistent-edge re-gauge is at 128 nodes, costing 317 operations, as stated. The receipt also records `regauged_worlds_large: 0` per locality kind |
| N3 (wording): baseline ratio single-run; reported, not gated | **Fixed** | The HANDOFF now says "single-run wall-clock ratios" and "reported, not a registered gate", and notes the unmatched duties. The ratios recompute from the receipt medians: consistent edge 2.155e-4 / 1.1625e-5 = 18.5×, new node 10.3×, bridge 15.9×. `endpoint_rules` says the comparison "is reported and claims no advantage". The phrase "registered quality/cost criteria" now appears only in the standard's general stop rule (§7, line 434), not as a claim about this comparison |
| N4: `next_action` said R004 | **Fixed** | `next_action` = "Independent C1 review of geomind-c1-r4-006 before C2" |
| F6 leftover | **Fixed** | 19 refused arm-rows, all with `post_transaction_total_accuracy` = None. No committed row has None |

## New findings, ranked by severity

### R1 — Low (non-blocking): a `Constraint` subclass with extra dataclass fields commits and exports, but `load()` rejects it. The same latent behavior exists in accepted C0

**Evidence.** `probe_roundtrip.py` (`probe_roundtrip.out`) and `probe_c0_subclass.out`:
- `@dataclass(frozen=True) class ExtraConstraint(Constraint): note: str = "x"` passes `isinstance(edge, Constraint)`.
- `asdict` adds a `note` key, and `canonical` serializes it.
- `apply` returns PASS, and `export()` succeeds.
- `IncrementalGeometry.load` then raises "Invalid serialized edge", because `geometry.py:281` requires exactly the 5 fields. The `update()` path behaves the same way.
- Accepted C0 `GeometryState.learn` has the same behavior: PASS, then reload fails.

**Why this does not block.** It needs a caller to extend the typed public record class with new fields. That is API misuse, not a plausible data value like the numpy scalars of N1. C1 matches the accepted C0 contract exactly, and C0's acceptance would have to be reopened for the same reason.

It is still the same failure class as N1: a committed state that does not round-trip. The owner may prefer to fold it into a future revision.

**Fix.** In `_validate_delta`, replace `isinstance(edge, Constraint)` with `type(edge) is Constraint`. Alternatively, serialize only the five declared fields. Add a focused check: a subclass with an extra field gives INVALID_STATE and leaves the export byte-identical. Record the C0 counterpart as a known latent issue for the next C0 touch. Do not edit C0 under this milestone.

### R2 — Low (non-blocking, wording): the re-anchoring caveat appears only in the HANDOFF

The O(component) re-anchoring cost is stated in `evidence/c1_r006/HANDOFF.md`. It is absent from the receipt's `hypothesis_limits`, from `evidence/c1_r006/README.md` and from the root README's summary sentence, which is where the SUPPORTED_WITHIN_SCOPE verdict appears. R4 line 490 says the tail "is now stated".

Readers who see only the verdict sentence miss the caveat. It is not misleading about the registered endpoint, which uses medians and is applied correctly.

**Fix.** Next time `hypothesis_limits` is regenerated, add one clause: "updates that move a component's max-degree anchor cost O(component) (charged; see `regauged_worlds_by_kind`)".

No defect was found that makes a committed result wrong or unpersistable for a plausible input. None was found that leaves a refusal unsafe, a cost charge missing, or a stated claim misleading.

## Claims checked against the receipt (recomputed from `instances.jsonl`)

- **Queue arm.** 60/60 consistent-edge, new-node and bridge worlds commit and are correct, all with 0 relaxation node updates.
- **Contradictions.** 1/5 resolves at 32 nodes. 0/15 resolve at ≥ 128 nodes, all explicit rejections with an unchanged state. The summary reports queue 61 committed and 19 unresolved, all of kind `inconsistent_edge`.
- **Fallback arm.** 80/80 commits, 80/80 correct.
- **Maximum committed displacement error.** `4.85244e-8`.
- **H-L locality.**
  - Operation ratios: consistent edge 36/27 = 1.333 and new node 30/27 = 1.111, both ≤ 2.
  - Time ratios: 1.749 and 1.419, both ≤ 4.
  - Every world commits at 32 and 2,048 nodes.
  - All 2,048-node speed ratios are < 1: consistent edge ≤ 0.0040, new node ≤ 0.0169, bridge ≤ 0.280.
  - Under `endpoint_rules`, this gives **SUPPORTED_WITHIN_SCOPE**, which matches the receipt.
- **Contradiction rule.** The queue resolution rate at ≥ 128 nodes is 0.0, below 0.5, so the verdict is **NOT_SUPPORTED**, which matches.
- **Other verdicts.** Bridges are NOT_TESTED for size independence, and durable persistence is NOT_TESTED. Both match the rule text.
- **Root README.** It says "7–18×" across runs. This is consistent with R005's 7.6–13.1× and R006's 10.3–18.5×.

## Checks performed

| # | Check | Result | Time |
|---|---|---|---|
| 1 | Read `_validate_delta` and the focused N1 check (`test_c1.py:462-473`) | Fix is pre-mutation and delta-sized; the test covers both R005 types and the float64 control | — |
| 1 | `probe_n1.py`: 72 applies, then export, load and re-export | 0 blocking | ~3 s |
| 2 | `python3 tools/gate.py status` | revision r006; all 5 stages verified; no tree problems | <1 s |
| 2 | `.venv/bin/python -m pytest -q tests/test_c1.py tests/test_gate.py --junitxml=evidence/c1_r006_independent/contracts.xml` | 34 passed | 12.6 s |
| 2 | `results.json` `file_hashes` (24 files) against the live files and `evidence/c1_r006/source/` | 24/24 equal | <1 s |
| 2 | `PIPELINE.json` fingerprint against `gate.fingerprint()` | equal | <1 s |
| 2 | Accepted C0 inputs (`evidence/c0_review/results.json` `file_hashes`, `final_file_hashes`, `source_snapshot_hashes`, 12 each) | 0 mismatches | <1 s |
| 3 | HANDOFF N2/N3 statements and summary numbers, H-L/H-P against `endpoint_rules` | all consistent (see above) | — |
| 3 | `MUTATION.json`: `delta_serialization_unchecked` | detected; 29/33 caught overall | — |
| 4 | `probe_roundtrip.py`: Constraint subclass, namedtuple offset, lone-surrogate and str-subclass node names, chained applies | R1 found; the others round-trip with identical answers | ~2 s |
| 4 | `probe_c0_subclass.out`: the same subclass through C0 `learn` and the C1 `update()` path | C0 shares R1; `update()` shares R1 | ~1 s |

Total wall time was about 10 minutes, within the cap.

**NOT_RUN** (by instruction or outside the cap):
- `geomind.run_c0`, the mutation probe, `tools/verify_milestone.py` and a panel rerun. The R005 review already showed the panel is byte-reproducible, and this review did not repeat that for R006.
- A deep-compare of internal structures after refusal (the R005 `probe_rollback.py`). Rollback after refusal was checked only through byte-identical exports.
- The adversarial re-anchoring stream (alternating hubs).
- Timing reproducibility of the 18.5× / 10.3× / 15.9× ratios.

## Files written (only in `evidence/c1_r006_independent/`)

`INDEPENDENT_REVIEW.md`, `contracts.xml`, `probe_n1.py`, `probe_n1.out`, `probe_roundtrip.py`, `probe_roundtrip.out`, `probe_c0_subclass.out`.

## Independence statement

The reviewer is the same model family as the author (Claude) but shares no conversation context with the author's sessions. Every claim above was re-derived from the live code, a fresh test run, probes written for this review, and recomputation from `instances.jsonl` and `results.json`. No source, test, manifest, standard, README, AGENTS.md or existing evidence was modified. No git commit or push was run.

## Note on directory contents

During this review, another process wrote `identity_check.py`, `identity_check.out.json`, `probe_compatibility.py` and `probe_compatibility.out.json` into this directory. They are timestamped 16:38–16:39. This review did not write them and relied on none of them. The files this review wrote are the seven listed above.
