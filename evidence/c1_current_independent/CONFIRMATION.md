# Independent confirmation of the C1 review decisions

Confirmed decisions: **R004 CHANGES_REQUIRED; R005 CHANGES_REQUIRED**. Date: 2026-10-01. Reviewer: separate Codex `/root/independent_c1_review` agent, which authored none of R003–R005 or their repairs. Review time cap: approximately 20 minutes. This supplement confirms the existing canonical receipts in `evidence/c1_r004_independent/INDEPENDENT_REVIEW.md` and `evidence/c1_r005_independent/INDEPENDENT_REVIEW.md`; it does not replace either receipt or establish acceptance. C2 remains gated on a separately accepted repaired revision.

The requested handoff named initial commit 8432be0. At review start HEAD was 5f1047a, containing R005 repairs. While this review was running, another session committed the already existing R005 reviewer material and tooling as 43ef4b3. The candidate hash remained the R005 hash during every executed check below. No numerical source was edited by this reviewer. All outputs are confined to this new directory; existing evidence, including the reconciliation and initially untracked R005 material, was preserved.

## Historical R004 decision

Read the R4 C1/C2 and review requirements; R004 HANDOFF and results; R002 acceptance conflict and reconciliation; Claude's repair/recheck and focused-check history; and the independent R004 receipt. R004 must remain CHANGES_REQUIRED. The independently documented uncharged relation-map copy, export-gauge certificate failures and weighted-degree overflow violate the C1 charged-work and persistence requirements even though its panel passes. Fourteen passing checks and correct panel answers cannot override those counterexamples.

The 80-world R004 evidence is historical: 60 queue commits, all with zero relaxation steps; 20 queue contradiction refusals; all 80 fallback commits, including 20 via separately metered CG. Its rigid frame placement is compiled bookkeeping, not learned computation; fallback commits are not queue success. The earlier R002 acceptance cannot bypass either rejected revision.

## Current R005 decision and blocking finding

Reading the repaired candidate, generator, evaluator, independent references and tests confirms the R004 repair design: delta-only relation lookups; coordinates stored directly in export gauge; certification of translated/re-gauged nodes and relaxation neighbors; finite degrees; journaled structural/coordinate rollback; distinct queue/fallback meters; candidate answers fixed before reference construction; stale refused-state answers excluded from update coverage; and independent sparse/dense reference qualification.

The new directed check nevertheless independently reproduces R005 finding N1. NumPy float32 offsets, int64 weights, and int64 new-node offsets pass `finite_number`, commit PASS through both `apply` and compatibility `update`, then make `export()` throw TypeError. Original Constraint objects keep the non-JSON scalar values; relation vectors have the same validation gap. The accepted C0 learner returns INVALID_STATE on the same observations. The float64 control commits, exports and reloads. See `probe_numeric_types.out.jsonl` and its copied, auditable probe source. The output's `state_unchanged_if_refused` field is vacuously true for these PASS cases; it does not claim atomic refusal occurred.

This is a persistence blocker, independent of panel correctness. The narrow repair is delta-sized canonical serialization validation before mutation, covering **both edges and relations**, with INVALID_STATE and byte-identical retained state for nonserializable input. Preserve JSON-compatible float64 behavior. Register the repaired source as a new revision and use fresh varied worlds; never overwrite R005 results or reinterpret R005 as accepted.

## Fresh checks and evidence identity

- `.venv/bin/python -m pytest -q tests/test_c1.py --junitxml=evidence/c1_current_independent/contracts.xml`: **19 PASS in 12.46 seconds**. The suite does not cover N1, so this is compatible with rejection.
- `probe_numeric_types.py`: three PASS commits that cannot export; float64 control exports/reloads; C0 refuses the three failing inputs; compatibility update reproduces the three failures.
- `identity_check.py`: all 22 R005 registered input hashes match live source and archived source at check time; all 223 before/committed-state hash bindings pass across 160 gzip files; original 19-case JUnit source binding and report SHA256 match; instances.jsonl equals receipt instances; all 12 accepted C0 inputs remain unchanged and C0 acceptance remains bound.
- `history_identity.py`: both historical source sets match their archived receipt hashes. Fingerprint below means SHA256 of compact, key-sorted JSON of the complete registered `file_hashes` mapping; it is not a gate stamp.

| Identity | Historical R004 | Reviewed R005 |
|---|---|---|
| Source set fingerprint | `3ad4b86bcbe3a93a15e655ffdd14dbbecfc15c88b822a78e9247ff35ef1c5e35` | `11845a73e47e2de30c9ad153015635329a31a5e6d1f9abc9cdce1393a7a88692` |
| Candidate SHA256 | `093159523e7abdbd8c6a1be64039bc20241a9a447adfd6c41a2452516cb2b06b` | `84ad79a62ec6b0b9831615bc7f5ad6eefd2ef00fd1313d8073f9172cca36a23a` |
| Original results SHA256 | `d769208dabe696f3f7e0ef9e4d17edcf652b12a33bc42a816239254b4ea44361` | `fb13bed3dfc9b7a7a2ae205c1f16fe6f656ed4e0aeb6b00ad9f4a845be90635a` |
| Canonical manifest hash | `80b987dea7e6955542a9104939504468048b5ebb4e2bd597549c96cc616ee40b` | `2f0f1d59de649eb349884d28fc68ecf4f4e41a82f38cdc9a3c372b7f8713bcf4` |

Read and reused, without rerunning, the prior R005 independent certificate, randomized-chain, rollback, degree, hidden-work and deterministic panel-comparison reports after confirming they identify the same source. Their searches support the repaired certificate and bookkeeping within the tested ranges; they are not proofs of all possible floating-point inputs. The prior reviewer reports 1,338 large-coordinate PASS reloads without rejection, 1,250 refusals without structural rollback differences, and flat Python work for non-reanchoring updates to 32,768 nodes. These are **reused prior evidence**, not newly executed searches in this supplement. The prior rollback probe omits `_energy_bound`; reading confirms assignment only after successful convergence, before final commit, so ordinary rejected paths leave it unchanged.

No C0 world experiment, registered panel, mutation suite, or costly scale search was rerun here. No gate stamps were forged or changed. No commit or status-document edits were performed by this reviewer.

## Scope and hypothesis limitations

R005 recorded 63 queue commits (60 without relaxation), 17 queue refusals, and 80 fallback commits (17 through CG). Three small 32-node contradictions were resolved by the queue; all 15 contradictions at 128–2,048 nodes remained unresolved there. Correct/unresolved engineering results do not establish learning or broad theory.

The registered median locality endpoints for consistent edges/new nodes are supported within the panel, with the necessary qualification that any anchor change can re-store the whole component at charged O(component) cost; adversarial streams can incur this every update. Bridges are not qualified for size independence. The incremental compiled baseline is faster on the reported additive cost measures; it has fewer validation/persistence duties, so exact timing ratios are not a universal efficiency result. Fallback and reference visit counts differ in units, scope and tolerances and must not be divided into an efficiency claim. H-L queue contradiction resolution remains NOT_SUPPORTED; durable persistence locality is NOT_TESTED and N1 reveals a real invalid-input failure; H-P is INCONCLUSIVE with no downstream task-learning evidence.

Implementation acceptance is withheld. A repaired revision may proceed to separate acceptance only after its required fresh evidence and focused regression checks. C2, C3 and hierarchy do not inherit acceptance from this supplement.
