NO_OBSERVED_CHANGE_WITHIN_ASSESSED_SCOPE (10 stored worlds; panel risk not quantified; adoption not assessed)

# C6 option B inexact math: impact study, revision 3

**Date:** 2026-10-07. **Author:** Claude (claude-opus-5-5).
**Answers:** Codex's round-2 recheck `docs/reviews/c6_inexact_study_recheck_codex_r2.md` (CHANGES_REQUIRED on `ea34db4`, committed `3c92fc8`): R2-F1, R2-F2, N1 and N2.
**Method:** stored data only. No C6 world, build or battery ran.
**Unchanged:** the revision-1 and revision-2 files. This report supersedes revision 2's ledger and reproduction claims; revision 2's measured values still stand, and are reproduced here (section 4).
**Status:** an engineering diagnostic, not an adoption decision. Using the inexact engine would end the zero-tolerance contract of decision 0029, item 3. That needs the owner's decision and a decision record.

## What the evidence supports, in plain words

**Outcomes:** in the 10 stored worlds (smoke 0–1, development 0–7), every recorded outcome and discrete value is identical between the exact and inexact engines. That covers:
- 17,278 Booleans;
- 992,981 integers;
- 159,356 non-digest labels and strings;
- **368 semantic candidate and member identity hashes.**

**What does change:**
- **45,592 physical-state digests.** These are snapshot, trace and state identities, which must change once any last bit changes.
- **Numbers:** the largest change is 3.3 × 10⁻⁹, on a grid-error monitor. Outside the monitors it is 2.4 × 10⁻¹⁰. None exceeds 10⁻⁸.

**Margins:** every decision family the ledger marks ASSESSED was evaluated separately for each engine, with the evaluator's own operator. There are **0 flips** across:
- 77,342 scalar statistic decisions;
- 10,741 guard and composite decisions;
- 1,142,364 pair lock tests;
- 3,121,284 pair link tests.

The stored-record validator `validate_world` passes on all 20 stored worlds, 10 per engine. It made 203 `publication_valid` calls per engine, all true.

**Not established:**
- the contexts the ledger marks UNASSESSED (section 2);
- the final-panel statistics;
- any future-panel outcome risk.

**Speed:** about 25% less compute CPU, an observation on this machine. Wall time is indicative only, and panel readiness is unassessed (revision 2, section 5, unchanged).

## 1. What changed from revision 2

| Item | Revision 2 | Revision 3 |
|---|---|---|
| **R2-F1: ledger** | Guards grouped as "discrete branches with no margin". No stored-record validation row. Causal grid agreement left implicit. §7 claimed every family with a stored value was assessed. | **Split into seven groups** (section 2): statistic decisions, pair decisions, continuous positivity and normalization guards, discrete guards, grid-agreement composites, stored-record validation, final-panel statistics. Each row gives operator, units, context, count and status. **Newly assessed on stored data:** <br>• GridSet normalization (7,317); <br>• candidate geometry: radius of gyration and median spacing on every grid's final state (717 each); <br>• recovery kick spacing (519); <br>• recovery position and phase probe norms (147 each); <br>• causal probe norm (145); <br>• minimum size (239); <br>• **selection, recomputed from stored rows and tokens** (239); <br>• **causal (342), recovery (173) and persistence (39) grid-agreement composites**; <br>• **`validate_world` and `publication_valid` run on every stored world of both engines.** <br>The §7 claim is corrected (section 6). |
| **R2-F2: identities** | Hashes checked only for inputs inside the study folder. Detector and protocol not pinned. No separate output. | `scripts/analyze_r3.py` holds a **fixed expected inventory of all 20 inputs**, the 3 external references included. Before any analysis it checks each input's bytes and SHA-256, **and** the `world_sha256` in that input's own run receipt. It pins the SHA-256 of the detector (`c4_detect.py`), its helpers (`c4_model.py`), the validators (`c6_r4_field_analysis.py`, `c6_r4_integrity.py`), the modules they import (`c6_r4_field_protocol.py`, `c6_r4_field_assay.py`, `c6_r4_field.py`, `tools/build_c6_r4.py`), the protocol file and the NumPy version (2.0.2). The protocol constants must equal the analyzer's constants. Expected and observed identities are recorded separately (`r3/IDENTITY_R3.json`). A separate `--output-root` refuses to overwrite, and `--verify-only` writes nothing. **Negative checks:** a wrong expected hash for development 1 and a wrong detector hash were both refused. |
| **N1: strings** | "Every string identical"; every 64-hex string treated as a permitted digest | **Field-aware:** a 64-hex string is a permitted physical digest only under one of the compare tool's `HASH_KEYS` fields (45,682, of which 45,592 changed). Every other one is a semantic identity, such as `selected_identity` or publication `candidate`, and must be equal: 368 are, with 0 changes. The opening now says "every non-digest label". |
| **N2: reconstruction** | Validated on the exact engine only; `zip` could truncate | Both engines validated: prefix mapping, and reproduction of **each engine's own** stored grid-0 persistence statistics in all 39 cells (max difference 0 in both). Window, frame, member and decision inventories must match exactly before pairing, or the script stops. |

## 2. Decision-coverage ledger

Operators, thresholds and units are those of `c6_r4_field_assay.py`, `c6_r4_field_protocol.py`, `c4_detect.py` and `c6_r4_field_analysis.py`, at the pinned hashes. "Closest" is the smallest distance of the exact engine's value from its threshold. "Change" is the largest change of that margin between the engines.

### A. Scalar statistic decisions: ASSESSED

These rows are unchanged from revision 2 and reproduced exactly (section 4).

| Family | Operator | Units | Instances | Flips | Closest | Change |
|---|---|---|---:|---:|---:|---:|
| membership Jaccard | `>= 0.95` | ratio | 12,069 | 0 | 6.5e-3 | 0 |
| shape CV | `<= 0.05` | ratio | 12,069 | 0 | 2.4e-2 | 9.3e-14 |
| group lock std | `<= 0.1` | rad | 12,069 | 0 | 3.6e-3 | 5.5e-12 |
| freq change | `<= 0.01` | rad/C0 | 12,069 | 0 | **7.3e-9** | 4.1e-14 |
| pattern change | `<= 0.1` | rad | 12,069 | 0 | 1.8e-4 | 7.3e-12 |
| recovery Jaccard / pattern error | `>= 0.9` / `<= 0.1` | ratio / rad | 558 each | 0 | 5.8e-2 / 9.1e-3 | 0 / 2.4e-10 |
| causal floor (per grid, strict) | `> 1e-8` | effect | 1,104 | 0 | 8.8e-3 | 1.9e-11 |
| causal spread / ablation (moving thresholds) | `<= 0.1·min` / `<= max(1e-12, 0.2·min)` | effect | 368 each | 0 | 8.8e-4 / 1.8e-3 | 1.5e-11 / 9.8e-13 |
| descriptor / paired gain refinement | `<= 0.001` | gain | 53 / 20 | 0 | 1.0e-3 | 2.8e-15 / 1.0e-15 |
| grid error: position / phase / field | `<= 0.05` | normalized | 4,656 each | 0 | 0.048 / 0.050 / 0.050 | 3.3e-9 / 3.2e-10 / 3.4e-12 |

**Contexts:**
- **Structural rows:**
  - rolling persistence, all 3 grids;
  - qualification and endpoint candidates, grid 0, since only `all_rows[0]` is stored;
  - source copies.
- **Recovery and causal rows:** all 3 grids for each stored candidate.

### B. Pair-level detector decisions: ASSESSED at grid dt; UNASSESSED at dt/2 and dt/4

| Context | Operator | Tests | Flips | Closest | Change at the closest | Status |
|---|---|---:|---:|---:|---:|---|
| lock, stored qualification windows | circular std `<= 0.1`, the detector's own clipping | 55,200 in 200 windows | 0 | 1.63e-4 (smoke 1, `/turns/0/before_formation/3`, pair 0–22) | 1.1e-15 | ASSESSED |
| link, stored qualification frames | `d < 1.5·median(nn)`, strict; a NumPy recomputation, not the native arithmetic | 1,711,200 | 0 | 6.3e-7, relative | 4.3e-15 | ASSESSED |
| lock, rolling persistence and endpoint windows | as above | 1,087,164 in 3,939 windows | 0 | 1.5e-6 | 0 | ASSESSED: reconstructed and validated **in both engines** |
| link, rolling persistence and endpoint frames | as above | 1,410,084 | 0 | 4.3e-6, relative | 4.7e-15 | ASSESSED |
| lock and link at dt/2 and dt/4, in every context | — | — | — | — | — | **UNASSESSED:** fine-grid frames are not stored |
| inside recovery control and kicked endpoints, and causal control and treated runs | — | — | — | — | — | **UNASSESSED:** those trajectories are not stored. Their resulting statistics are assessed in A. |

### C. Continuous positivity and normalization guards

| Guard | Evaluator | Operator | Units | Context | Count | Flips | Closest | Status |
|---|---|---|---|---|---:|---:|---:|---|
| GridSet normalization | `GridSet.run` | radius of gyration `> 0` and finite, per cohort at run start | L0 | every stored check (`normalization_sizes`) | 7,317 | 0 | 0.42 | ASSESSED |
| candidate geometry: radius of gyration | `qualification` | `> 0` (raises if `<= 0`) | L0 | final state of every grid, using **grid-0** members on grids 1–2 (grid-1/2 members are not stored) | 717 | 0 | 0.41 | ASSESSED, with that member caveat |
| candidate geometry: median nearest spacing | `qualification` | `> 0` | L0 | as above | 717 | 0 | 0.21 | ASSESSED, same caveat |
| recovery kick spacing | `recovery` | finite and `> 0` | L0 | each grid, every recovered candidate, endpoints included | 519 | 0 | 0.21 | ASSESSED |
| recovery position-probe norm | `recovery` | `> 0` | L0 | candidates with stored perturbations | 147 | 0 | 1.11 | ASSESSED |
| recovery phase-probe norm | `normalize_phase` | `> 0` | rad | as above | 147 | 0 | 0.58 | ASSESSED |
| causal phase-probe norm | `normalize_phase` | `> 0` | rad | selected sources with stored perturbations | 145 | 0 | 0.55 | ASSESSED |
| **endpoint-qualification** probe norms for recovery and causal runs | `recovery`, `causal` | `> 0` | — | 52 contexts | — | — | — | **UNASSESSED:** the operation's perturbations (`rng(entropy, world, 30, turn)`) are not stored. They could be regenerated from the seed without simulating, but this revision does not. |

The probe norms depend only on the stored perturbations and memberships, so they are identical in both engines; a change of 0 is expected. The geometry guards change by at most 7.9e-12.

### D. Discrete guards

| Guard | Evaluator | Operator | Context | Count | Result | Status |
|---|---|---|---|---:|---|---|
| candidate minimum size | `qualification` | members `>= 3` (integer) | every stored candidate | 239 | identical; smallest has 21 members | ASSESSED |
| selection and ties | `select_accepted` | max size, then lexicographic tokens | every qualification and endpoint record | 239 | the recomputed choice equals the stored `selected_members` in **both** engines | ASSESSED |
| sham source preservation, zero sham output, NO-R must not qualify, clean controls | `operation`, and again in `validate_world` | equality / Boolean | every turn | — | pass in both engines (inside `validate_world`, row F) | ASSESSED as validation; no margin exists |
| finite-value checks (statistics, causal grids, full-scope state) | assay, protocol | `isfinite` | — | — | every stored value is finite in both engines (the value walk found no nonfinite pair); the in-run checks on unstored arrays are not observable | partly ASSESSED |

### E. Grid-agreement composites

| Composite | Evaluator | Rule | Count | Flips | Nearest underlying decision | Status |
|---|---|---|---:|---:|---:|---|
| **causal grid agreement** | `closure_valid` (`grid-dependent causal qualification`) | the three per-grid `> 1e-8` decisions are identical | 342 | 0 | 8.8e-3 | ASSESSED |
| recovery grid agreement | `qualification` (`grid-dependent recovery`) | the per-grid recovered decisions are identical | 173 | 0 | 9.1e-3 | ASSESSED |
| persistence grid agreement | `operation` (`grid-dependent persistence`) | the three grids' window masks are identical (the stored `passed` flags were also checked against their statistics) | 39 | 0 | 7.3e-9: the freq-change case, failing on all grids in both engines | ASSESSED |
| structural candidate inventory agreement | `qualification` (`grid-dependent structural candidates`) | identical structural inventories on 3 grids | — | — | — | **UNASSESSED:** grid-1/2 candidate rows are not stored. Indirectly, neither engine raised (`invalid` is null). |
| descriptor and paired gain refinement | `descriptor`, `operation` | see A | 73 | 0 | — | ASSESSED in A |

### F. Stored-record validation: ASSESSED

`c6_r4_field_analysis.validate_world` was run, unchanged, on each stored world of each engine. It only reads records; it simulates nothing. Its checks:
- chain flags and the witness;
- for the complete chain (smoke 0): chain provenance, **clock within 1e-7**, and continuity of background, carrier and previous source;
- **`publication_valid`** for every source, before-formation and episode publication: required fields, finite values, positive size, a two-element centroid, a candidate identity equal to the member hash, `S` equal to the selected candidate's statistics, units, and id count;
- episode inventories;
- **inputs and perturbations matched across controls;**
- witness-tuple consistency;
- clean controls, the sham, and NO-R.

| Worlds | `validate_world`, exact / inexact | `publication_valid` calls (true) per engine | Chain checks |
|---|---|---:|---|
| all 10 | **PASS / PASS** | 203 (203) | smoke 0 (the only complete chain) |

`run_world` does not call these validators, so revision 2's "no invalid run" did not cover them; this run does.

### G. Final-panel statistics: UNASSESSED

The `c6_r4_field_analysis.evaluate` primary decisions remain unassessed:
- the 16 response and later-formation contrasts;
- the CI bounds ±0.01 and ±0.1;
- the bootstrap and empty-draw policy;
- the eligibility and chain masks;
- the quorums;
- grid-verdict agreement;
- hypothesis combination.

So do the development readiness gate and Arm A. They need the registered 40-world panel on final entropy, or development worlds 8–9 and the gate's schedule, none of which is authorized here.

## 3. Values

Unchanged from revision 2, and reproduced exactly:

| Class | Floats | Changed | > 1e-10 | > 1e-8 | Max absolute | Max relative |
|---|---:|---:|---:|---:|---:|---:|
| grid-error monitors | 14,085 | 10,765 | 28 | 0 | 3.34e-9 (development 2, `/checks/323`) | 5.06% (smoke 0, `/checks/809`, a value of about 9.9e-11) |
| all other floats | 17,399,055 | 8,896,265 | 1 (a recovery pattern error) | 0 | 2.39e-10 | near-zero values only |

**Tolerance:** unchanged from revision 2. Every comparable float must be within 1e-8 absolute, monitors included, and every decision must be identical. Relative monitor changes are reported, not gated. The platform note is unchanged: macOS 26.6.2, build 25G83, read after the fact.

## 4. Reconciliation

`r3/RECONCILIATION_R3.json` compares revision 3's output with `SUMMARY_R2.json`. **All 34 rows are equal:**
- value counts and maxima for monitors and other floats;
- Booleans, integers, digests changed, and the total 64-hex count;
- the 15 statistic families' counts and flips;
- both pair contexts' window, test and flip counts.

The new 64-hex split is 45,682 physical digests plus 368 semantic identities, which equals revision 2's 46,050 digests.

## 5. Reproduction

From the repository root:

```
# Identity check only (writes nothing): 20 inputs, run receipts, 9 pinned files, NumPy, protocol constants
.venv/bin/python evidence/c6_option_b/inexact_study/scripts/analyze_r3.py --repo-root . \
    --study-root evidence/c6_option_b/inexact_study --verify-only
# Full stored-data analysis into a NEW directory (about 2 minutes, one process)
.venv/bin/python evidence/c6_option_b/inexact_study/scripts/analyze_r3.py --repo-root . \
    --study-root evidence/c6_option_b/inexact_study --output-root /tmp/inexact_r3_check
```

**Where the inputs live:**
- The raw inexact worlds and the study's exact worlds are local and gitignored (`raw_worlds/`, listed in `RAW_FILES_OUTSIDE_GIT.json`).
- The 3 external exact references are under `evidence/c6_option_b/`.

On a clone without these files, the script stops with "missing input"; it never analyzes a partial set.

## 6. Owner recheck applied to this revision

The owner's prompt, applied verbatim: "Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps." No numeric score is assigned.

**Found and fixed while rechecking:**
1. **Gap: two grid-agreement composites.** Recovery and persistence agreement are also derivable from stored per-grid values, not only causal. Both were added: 173 and 39 instances, 0 flips. The persistence composite also cross-checks every stored `passed` flag against its five statistics; the script stops on a disagreement, and none occurred.
2. **Conflict: double counting by context.** Guards are evaluated on qualification records only, not on the `/source/` copies. That is why causal agreement shows 342 instances while the causal floor in A shows 1,104 = 3 grids × 368 records, 26 of which are source copies (368 − 26 = 342). This is stated rather than hidden.
3. **Issue: the identity guard was untested.** A wrong expected hash (development 1) and a wrong detector hash were each refused with a named error.
4. **Issue: the selection guard's margin column was meaningless.** It is an equality check, so it reports the result, not a fake margin.

**The corrected §7 claim from revision 2:** not every family with a stored value was assessed in revision 2. Revision 3 assesses the stored guards, composites and record validators listed in sections C–F. What remains UNASSESSED is listed with reasons. Only the fine-grid frames, the recovery and causal trajectories, and the grid-1/2 candidate rows need new instrumented runs. The endpoint perturbations could be regenerated from their seeds without simulation. The final-panel statistics need an authorized panel.

**Remaining, disclosed:**
- 10 worlds;
- the UNASSESSED rows above;
- grid-0 members used on grids 1–2 for the geometry guards;
- a NumPy recomputation of link tests;
- wall timing indicative only;
- the OS build read after the fact.

**Is this the best we can do?** On stored data, I believe so. Every guard whose inputs are stored is now evaluated, and the inputs and evaluators are pinned and checked before use. Closing the remaining rows needs authorized new evidence: instrumented worlds, or regenerating the perturbations.

## Files (new in revision 3)

- `INEXACT_IMPACT_REPORT_R3.md`: this report.
- `scripts/analyze_r3.py`: the analyzer.
- `r3/IDENTITY_R3.json`: expected and observed identities of the 20 inputs, their run receipts, the 9 pinned files, NumPy and the protocol constants.
- `r3/results_r3/<world>.json`: per world:
  - value classes;
  - statistic families and guard families, with contexts, flips, closest and change;
  - pair contexts, with validation for both engines;
  - stored-record validation;
  - outcomes;
  - input identities.
- `r3/SUMMARY_R3.json`: the aggregates.
- `r3/RECONCILIATION_R3.json`: the 34-row comparison with revision 2.
