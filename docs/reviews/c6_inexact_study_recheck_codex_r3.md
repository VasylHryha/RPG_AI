APPROVE_WITH_NOTES
Reviewer family: Codex
Reviewed commit: 932e98f26d5e54f803a6b29eeee481e949920900 (932e98f)
Reviewer model: GPT-6
Review date: 2026-10-07

## Scope and conclusion

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Reviewed revision 3's report, analyzer, fixed identities, ten comparison receipts, summary and reconciliation against the round-2 findings, protocol and evaluators. Also checked the original tolerance, performance deep-dive, archived run/build receipts, surviving scratch binaries and selected raw worlds. This is a cross-family owner recheck of Claude's engineering diagnostic, not C6 acceptance, a numerical-contract change or authorization to adopt the inexact engine.

**R3 supports its narrowed headline: `NO_OBSERVED_CHANGE_WITHIN_ASSESSED_SCOPE`.** The observed numerical changes and approximately 25% lower compute CPU are reproduced by the stored evidence. Kernel identity and the exact baseline are substantiated. The unsafe extrapolation to future-panel risk remains withdrawn. The major round-2 corrections are implemented; no new blocking defect or observed outcome change was found.

**Coverage is still bounded.** Fine-grid pair decisions, recovery/causal trajectories, fine-grid candidate inventories and final-panel decisions remain explicitly unassessed. Two small stored-input preconditions remain outside the explicit ledger, and the analyzer does not substantiate its universal finite-value wording; see N3/N4. Neither makes the bounded observed-agreement headline false. `SAFE_UNDER_PROPOSED_TOLERANCE` should remain a superseded historical claim, including in the plan; see N5.

## Round-2 dispositions

| Item | R3 implementation and review result |
|---|---|
| **R2-F1 — decision ledger and validators** | **Substantially resolved, with low completeness notes N3/N4.** Continuous normalization/geometry/probe guards are separated from discrete decisions and panel statistics. Causal, recovery and persistence grid agreement are assessed from stored values. The unchanged `validate_world` and `publication_valid` are actually called on both engines' records, rather than inferred from `invalid is null`. Missing contexts and the grid-0-member geometry caveat are explicit. Counts reaggregate correctly; development-0 and smoke-1 scalar/guard receipts reproduce from raw data. |
| **R2-F2 — expected identities and reproduction** | **Resolved.** All 20 expected input hashes and sizes are fixed before analysis, including the three external exact references. Each is cross-checked with its own run receipt's `world_sha256`. Nine evaluator/protocol/helper files, NumPy version and protocol constants are checked before imports used for analysis. Expected and observed identities are separated. `--output-root` and a read-only `--verify-only` route are supplied. The latter passed in this review. It checks identities, not reproduction of every numerical receipt; that distinction is correctly documented. |
| **N1 — strings and semantic hashes** | **Resolved for these artifacts.** The opening says non-digest labels/strings. Physical digests are excluded by field context, while the 368 other candidate/member identity hashes are compared for equality. The 45,592 changed physical digests are disclosed. The total 46,050 hexadecimal strings reconciles with R2. |
| **N2 — reconstruction in both engines** | **Resolved.** Each engine's prefix mapping and its own grid-0 persistence statistics are validated. Window, member and frame inventories are checked before pairing. All 39 recorded cells validate with maximum statistic difference zero in both engines. Raw smoke-1 prefix endpoints and the closest persistence-lock window agree. This does not validate unstored fine-grid frames. |

## Nonblocking findings and concrete fixes

### N3 — Low: the remaining universal stored-guard claim omits two preconditions

`INEXACT_IMPACT_REPORT_R3.md:210` says, "Every guard whose inputs are stored is now evaluated." Two stored-input checks are still absent from the explicit assessment:

- `c6_r4_field_assay.py:155` checks the causal arrays' lengths and nonnegative values, in addition to finiteness. The floor/spread/ablation tests and causal-agreement composite do not separately assess these input-validity predicates; the ledger's finite-value row does not name nonnegativity or lengths.
- `select_accepted` rejects duplicate selection tokens at `c6_r4_field_assay.py:212`. R3 reimplements the ranking at `analyze_r3.py:398–403` without checking that precondition. Ranking equality alone does not verify it.

**Concrete fix:** in the next author addendum, explicitly label these guards ASSESSED with stored-data counts/results, or UNASSESSED with a reason, and qualify the universal sentence. Duplicate tokens and causal-array lengths are discrete guards; causal nonnegativity has the continuous `>= 0` predicate. No simulation is needed. The secondary reviewer found no such violation in either raw development-2 artifact; this is a completeness note, not an observed flip or invalid artifact.

### N4 — Low: the value walk does not establish that every stored value is finite

The ledger at `INEXACT_IMPACT_REPORT_R3.md:108` asserts every stored value is finite because the value walk found no nonfinite pair. At `analyze_r3.py:121–123`, identically nonfinite pairs return silently when their representations match. There is no nonfinite counter or unconditional failure. A small in-memory check of `{x: NaN}` against itself produces an empty discrete-difference list and one counted float. The same applies to matching infinities.

**Concrete fix:** add an explicit per-engine nonfinite count/assertion in a future analyzer revision, or narrow the report to the finite checks that actually ran and separately verified raw contexts. The secondary review scanned all 2,494,664 float leaves in each development-2 raw artifact and found zero nonfinite values. No current nonfinite input was demonstrated. This note concerns the proof claimed by the analyzer, not evidence of a changed outcome.

### N5 — Low: the current plan still presents the withdrawn safety headline

`docs/PLAN_CURRENT.md:91` still labels C5 DONE with **`SAFE_UNDER_PROPOSED_TOLERANCE`**, the R1 counts, and "Corrective revision R2 RUNNING." It records round-1 findings but has no R2/R3 disposition. That conflicts with R3's narrower report and the repository requirement to track rechecks in this plan. The unchanged R1 report may legitimately remain historical; an active plan should point to the current conclusion.

**Concrete fix:** the author/owner should update that row and record this review's dispositions, linking R3 and stating no observed change within assessed scope, panel risk unquantified, adoption undecided. Retain the historical report unchanged. This task expressly permits only a new review file, so the reviewer has not edited the plan.

## Evidence checked

### Identities, baseline and preservation

- HEAD was `932e98f` when inspected. Its study revision adds 15 new files. The original R1 files and the R2 report/analyzer/results are unchanged. Existing unrelated untracked work was preserved.
- Ran the permitted command with `nice -n 15` and `python -B`:

  ```sh
  nice -n 15 .venv/bin/python -B evidence/c6_option_b/inexact_study/scripts/analyze_r3.py \
      --repo-root . --study-root evidence/c6_option_b/inexact_study --verify-only
  ```

  It returned `identity_passed: true`, `errors: []`, exit 0. The sandbox refused `setpriority`; Python nevertheless completed the identity-only check in under a second. No full stored-data analysis was run.
- A fresh recursive type and binary-float equality comparison of exact smoke 1 against `reference_smoke_1/world.json.gz`, excluding only root cost/build metadata, found **zero mismatches**, covering **1,365,412 float leaves and 1,396 Booleans**.
- All study START records distinguish exact source `9ebe2acf7dd873d3437b5d645091e41bb9ed1a3e69a56a6fc36ebdfdfff96920`, binary `3e269f1464b328e660b5b37ee16a72ed7273c090ee00dd27370129f60ff38f90`, from inexact source `d27d46bb6053bed84acbed330e0c28fa2c174ae417ad80bd9e4d1f6c5338582d`, binary `e9c3a10fecb81d63558253d4e6eda35cf6b631f4659a05c0e75a4e3d6fd69ec1`. START/COSTS build identities agree. Both surviving scratch sources/binaries match their BUILD records. Static `otool -L` and `nm -u` confirm Accelerate linkage and `_vvexp`/`_vvsincos` imports in the inexact binary. The archived helper identity and loader guards support selection of that binary, including verification after use; this was not merely a changed source paired with the exact binary.

### Counts and raw arithmetic

- Reaggregating the ten R3 receipts using the analyzer's summarizer reproduces `SUMMARY_R3.json` **exactly**. All **34 reconciliation rows** are equal. Totals are **17,413,140 floats**, **8,907,030 changed**, **77,342 scalar decisions**, **10,741 guards/composites**, **1,142,364 lock tests** and **3,121,284 link tests**. All reported flips and discrete differences are zero. All recorded guard predicates pass in both engines. The validators record 203 successful publication calls per engine; both-engine reconstruction records all 39 cells valid.
- Re-evaluating scalar families, guard families and unchanged record validators from raw **development 0 and smoke 1** reproduces those receipt sections. This is not an exhaustive raw recomputation of every world's pair decisions.
- **Closest scalar, raw development 0, turn 2, intact window 29:** grid-0 frequency `0.010000007263912924 → 0.010000007263912841`; margins `-7.2639129242851874e-9 → -7.2639128410184606e-9`. Change `8.326672684688674e-17`. Grid-2 change is `4.163336342344337e-16`. All three grids fail in both engines. The observed distance/change ratio is not a future-panel probability bound.
- **Moving causal margins, raw development-0 initial source, m→g:** spread `0.10819288425894119 → 0.10819288425893314`; ablation `0.21638576975218882 → 0.21638576975219492`. Each side uses its own `min(intact)` threshold. Their changes are approximately `8.05e-15` and `6.11e-15`.
- **Closest qualification lock, raw smoke 1, first turn before-formation episode 4, pair (0,22):** the detector's vector-array reduction/clipping policy gives `0.1001632847400453 → 0.1001632847400464`. Signed margins are `-1.632847400452886e-4 → -1.632847400463988e-4`, both unlocked. **Closest persistence lock**, first-turn NO-R window 94, pair (7,18): `0.10000148720862774` in both engines, margin `-1.4872086277345486e-6`. Both prefix mappings hold.
- The secondary reviewer independently checked raw **development 2**, `/turns/0/episodes/intact/3`: radius `0.43268670141324295 → 0.4326867014134311`; spacing `0.21457384119198386 → 0.21457384119988873`. The latter reproduces the maximum geometry-guard change **7.904871202057961e-12**.
- The stored value extrema remain **3.3404761575145728e-9** on the development-2 position monitor and **2.3871038479228446e-10** on development-7 recovery pattern error. Reconciliation and receipt reaggregation reproduce those exact numbers. These two raw extrema were not independently re-read in this round.

### Tolerance, risk and speed

- R3 keeps the memo's **absolute difference <= 1e-8 on every comparable finite float**, including monitors, with decision identity required. Relative monitor changes remain descriptive. Stored receipts show zero exceedances; the largest absolute difference is only about three times inside this bound. This is measured agreement, not a guarantee of all internal or future decisions.
- R3/R2 correctly withdraw the old panel-risk estimate. No probability of a flip in a future 40-world panel is established. Only smoke 0 completes the chain in this sample. Final-panel contrasts, CI boundaries, quorums, hypothesis combination and readiness remain unassessed. The macOS build was read after the fact, not proven by run-time receipts.
- Recomputed paired **compute CPU** ratios from COSTS: six nontrivial-pair mean **0.7467061076503366**, range **0.7193794288053382–0.7679028382788675**; seven-pair mean **0.7553286775461542** including trivial development 6. Compute wall ratios range **0.6402407685601228–0.8328890465247973**. These support the approximately 25% CPU observation. Sequential pairs under changing v5/shared load do not establish quiet-machine speed or two-worker panel throughput. Serialization is outside these compute ratios. R2's retained **396.1-second** exact-engine failure under load about 85 correctly prevents an unconditional runtime-headroom claim.
- Both stored reference/equivariance batteries pass with the identified builds. Reference maxima are **9.46687173097871e-13** exact and **1.278033234797249e-12** inexact; scene equivariance **7.549516567451064e-15**, renaming zero. Batteries were read, not rerun. The withdrawn equal-mathematical-accuracy claim stays withdrawn.

## Reviewed R3 artifact SHA-256

Paths are relative to `evidence/c6_option_b/inexact_study/`.

| Artifact | SHA-256 |
|---|---|
| `INEXACT_IMPACT_REPORT_R3.md` | `6f7f5e3125cb53d48c83d8a96e0960cfd5744e91414894fc8ab46c256ee65f60` |
| `scripts/analyze_r3.py` | `3a9608c956d793fea106090e396dbab2f1e0b704880dd11cc6dbaa0e1ba0029d` |
| `r3/IDENTITY_R3.json` | `33aee80f28225026f1353b7d7447a7c68de05608bc0313b2f43ce23f5ae36cb1` |
| `r3/SUMMARY_R3.json` | `d867e363f76c0e63e2b2e7e7cce31b1235014f0feb3f23b0eec86ad486319e6e` |
| `r3/RECONCILIATION_R3.json` | `781653e0664705d7ca88dcebfe24ce57996cc4c74bdaf6c5c9cd6fea974b5b89` |

## Review and delivery boundaries

A separate Codex reviewer received the owner's request verbatim and independently checked the new ledger, reconstruction and raw development-2 guards. It corroborated N3/N4 and the supported measured conclusion. This supporting check is same-family; the main review is cross-family against Claude's R3.

Used read-only inspection, hashing, static binary inspection, receipt reaggregation and short Python reads/calculations on stored JSON. No C6 world, native load/build, test suite, battery, bootstrap, mutation probe or panel ran. No existing file was edited. Owner adoption, decision 0029's contract change, new references, registered execution and milestone acceptance remain separate gates. The author/owner should record this review and disposition in `docs/PLAN_CURRENT.md`.

Only this new review file was written. Existing files and unrelated work were preserved. The secondary reviewer also read this completed review and found no required corrections.
