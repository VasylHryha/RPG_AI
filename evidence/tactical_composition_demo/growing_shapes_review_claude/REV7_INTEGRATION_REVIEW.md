CHANGES_REQUIRED
Reviewer family: Claude
Reviewed commit: 55a9f7a642a05bc1466e21c0333e12d3cdfe7863
Execution pin inspected (NOT approved by this review): 92a7cea19cc13d9074286a9a6ed6f9c32e57ef4198b3ff4585a9058d43af76fd
Design: DESIGN_0H_REV7.md revision 7.3 (sha256 d5545c92…, matches the pin and HEAD)
Owner recheck request (verbatim): "Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps."

Scope: I read the code, ran the existing synthetic suite once, and made small pure-Python formula checks. I ran no N1, F1–F9, training, development or panel. Synthetic suite: `pytest -q -x runner/test_rev7.py` gave 34 passed in 0.79 s (1.08 s wall). Its temp and cache files went to the scratchpad, and the repository tree stayed clean. The recomputed `rev7_inventory.construct()` is byte-identical to `REV7_SEED_INVENTORY.json`, and its status is DISJOINT.

## Findings

### 1. MEDIUM: the ω̂ estimator ignores the validity of the window-start endpoint (design deviation from 10.2)
- **Evidence:** `medium/rev7_design.py:185`. The code checks only `individual_valid(frames[-1], e.id)`. The estimate on line 186 uses both `frames[-1]` and `frames[0]`.
- **Design rule (10.2):** ω̂ "is suspended (ω unchanged) only if **an** endpoint sample is itself invalid". Both endpoints are samples, and either one can be invalid.
- **Test gap:** `test_individual_invalid_suspends_P_and_rate_only_at_endpoint` only flags k = 100, the last frame. A start-endpoint flag is never tested.
- **Failure scenario:** a cue onset with E_i > π/2 lands exactly 10 s before an adaptation step. ω is then updated from an endpoint that the design declares invalid.
  - This happens in every live run: F5(i), F5(ii), F7, F8 and all development trainings. N1 and F1–F4 are frozen and are not affected.
  - The fixture sequence runs N1 → F9 as one execution. Fixing this after N1–F4 results exist would be a protocol change after results were seen (stop row: new revision on fresh entropy). It must therefore be fixed before the first run.
- **Fix:**
  - Require `individual_valid(frames[0], e.id) and individual_valid(frames[-1], e.id)`.
  - Add a contract with `bounds=lambda k,id: 2. if k==0 else 0.` that asserts the rate is unchanged.
  - Re-pin the identity, rerun the synthetic suite once and refresh `REV7_SYNTHETIC_CHECKS.json`.

### 2. LOW: an undeclared extra validity screen on the recovery futures, wider than the criteria it protects
- **Evidence:** `runner/rev7_qualification.py:164` together with `:132-135`.
  - At every one of the 600 replay frames, every pair of the whole qualification cohort must be valid, in both the control and the kicked future.
  - Otherwise the candidate is skipped as `fast_transient_cohort`.
- **What the design says:** 10.2 defines the screen only for the qualification window ("the saved bounds … on the actual cohort's pairs"). Neither the design nor CONFIG (`excursion.qualification`) nor the integration report mentions screening the futures.
- **Why the scope is too wide:** the recovery criteria that read future phases (`recovery_pattern_error`, `tau_phase`) use only the candidate's members. Membership comparisons (`c4.components`, `best_match`) use future positions plus the window's `locked` matrix, not future phases. A transient in a non-member pair therefore cannot corrupt the candidate's criteria, yet it vetoes the candidate.
- **Failure scenario:** a cue onset in the next 60 s produces a transient in a driven non-member (see finding 4 for magnitudes). Valid candidates are then skipped, which biases G1 and the snapshot counts downward without any declared rule.
- **Fix:** either restrict the future screen to the candidate's members and pairs, or keep it and declare it. Declaring means a CONFIG entry, a report sentence and a contract test. The denominators are already recorded.

### 3. LOW: the fixture runner stops F2–F4 after an F1 FAIL, which is stricter than the stop table
- **Evidence:** `runner/rev7_fixtures.py:378`. The loop `break`s on an F1 FAIL. Only N1 blocks every later fixture (9.7); an F1–F4 FAIL blocks only F5 and development.
- **Failure scenario:** F1 fails, as F1b did in 6.5. The cheap, independent F2–F4 checks (mask, lesions, native/Python assay parity) are never measured. The receipt shows them only as `not_run`, so the failure report loses the evidence that separates an engine defect from a timescale failure.
- **Fix:** after an F1 FAIL, continue through F2–F4 and then stop before F5. Keep the break on N1 FAIL/INVALID and on any INVALID. `Harness.require` already enforces the F5+ gate.

### 4. MEDIUM (design risk for the drafter and owner; the implementation follows the design literally): λ = 8 combined with the whole-cohort window screen may leave most 60 s windows not-qualified
- **Evidence:** `runner/rev7_qualification.py:57-62` follows 9.1/10.2 as written: a single invalid pair of the whole cohort, in any of 601 frames, makes the window not-qualified.
- **Toy calculation:** first-frame E_i after a cue phase change Δ, for one driven element at r = 0.3 from the site, using the rev7 RK4 stage-max bound with h = 0.02.

| g | k | Δ = π/4 | Δ = π/2 | Δ = 2 | Δ = 2.8 |
|---|---|---|---|---|---|
| 1 | 1.6 | 0.60 | 1.05 | 1.18 | 0.79 |
| 1 | 2 | 0.69 | 1.23 | 1.42 | 1.10 |
| 2 | 1.6 | 0.88 | **1.60** | **1.92** | **2.07** |

- **What that means:**
  - Every new perceive cue moves the drive phase by an arbitrary angle. One driven member at E ≈ 1.1 plus any coupled neighbour at ≥ 0.47 already exceeds π/2 for that pair.
  - With about 4 episode boundaries per 60 s window, many or most windows that contain a driven element may be not-qualified.
  - That would make G1 or snapshot admission structurally scarce. This is not a code defect, and no fixture gate measures it.
- **Recommendation:**
  - Add a descriptive F5 summary row: the fraction of qualification windows that were not-qualified (`fast_transient_cohort`), plus individual and pair flag rates. The data are already in `events` and `validity`.
  - Have the owner and drafter look at it before development, rather than discovering it in a 48-training run.

### 5. LOW (informational): the "anchor-relative" displacement equals the absolute displacement by construction
- **Evidence:** `runner/rev7_qualification.py:138-144`.
- **Assessment:** this is correct, because every anchor is fixed in both futures. The 9.5 reporting row therefore carries no extra information. That is acceptable as disclosed (`anchor_policy`).
- **Suggestion:** state "identical by construction" in the report text, so a reader does not mistake it for an independent measurement.

## Verified against the design (no defect found)

**1. λ = 8.** It multiplies only the internal phase coupling and the site drive, at every RK4 stage, in both backends (`rev7_medium.cpp:122,131`; `rev7_rhs.py:47-52`).
- ω, motion and the wall are unscaled.
- The drive phase advances at stages 0, h/2, h/2 and h (`.cpp:142-145`, `rhs.py:61-63`).
- The serialized λ is restricted to 1 or 8.

**2. Neighbour lists.**
- **N^x:** elements plus active sites (strength > 0), strict r < 3, k ≤ 8. Ties go by distance, then type, then id. It has its own mean, is held over the 4 stages, and silent or lesioned elements keep their motion role.
- **N^θ:** elements only, ties by array index.
- **Uses:** N^θ drives the graph, lock and PLV (`offsets` uses `f.neighbors`), the B-path trials (`geometric_graph`) and the cost (`undirected_cost`, no site term).
- **Sites** are absent from N, the cap, templates and cohorts.

**3. Site-body law and pins.**
- The site-body law matches 9.4: `rr = max(r, .3)` in both appearances, and the vector is zero at r = 0.
- The output pin holds:
  - velocity is zeroed for the output;
  - `gm_set_element`, `reference_commit` and snapshot load reject a moved pin;
  - templates store and validate the pin coordinate.
- B-out tries (0, 0) only, and is refused with `placement` if an element lies within 0.05.

**4. Clearances (8.4).** One `clear_position` rule (0.05 from elements, 0.3 from all 8 SITES, an ULP allowance for roundoff only) is used by:
- B1 (spiral);
- B-out;
- the B-path trial (`clearance` check) and `feasible`;
- M (spiral plus feasible) and U (inherited queue through `feasible`);
- the kick admissibility test.

**5. Excursion bound and validity masks.**
- The bound is E_i = Σ over substeps of h · max over stages of |θ̇ − π|, summed over 5 (or 20) substeps.
- Pair rule: pair-only E_i + E_j. Site rule: E_i.
- Records stay consecutive, and invalid observations are dropped from both the numerator and the 80-of-100 count.
- P_i is undefined on own-invalid frames.
- The cohort screen runs before the circular criteria.
- The exception is ω̂; see finding 1.

**6. Recovery adapter.**
- Position kicks act on free members only, with the RMS over free members.
- Phase kicks act on all members, O included, and use the frozen-C4 order and mean removal.
- There are up to 8 draws in fixed order, no clipping, and an `inadmissible_kick` or `no_free_member` skip, all with denominators.
- Pins are fixed in both futures.

**7. Timers and start.**
- The B1 freeze, reset and retain recurrence is implemented, and a ready site requests a birth only while active (otherwise `queued_demand`).
- B-path is immediate.
- Intact, M and U start empty, with the first check at step 200 (20 s).

**8. Inventory and identity.**
- The id ranges are exactly those of 8.10 (training 11,000,000 + 10,000·slot; 10,000,512–639 and 640–767; 768–787; 788–807; 12,000,000+e; 12,100,000+e).
- All keys use the `0h-rev7/` prefix, and the donor ranks use `0h-rev7/donor_perm/j`.
- Disjointness is checked against all four earlier inventories and the 5.1 reuse ranges.
- The pin covers the three designs (also checked against `git show HEAD`), the rev7 sources, the native image and build manifest, the calibration, the inventory and the inherited dependencies.
- The legacy template loaders are delegated unchanged.

**9. Fixtures.**
- **N1:** the recipes match the 9.2 table exactly. The comparisons cover wrapped and unwrapped phase, free positions ≤ 0.01, entry (both / neither / one → FAIL), separate N^x and N^θ agreement ≥ 99%, pins and minimum distances.
- **Literal positions:** F1a (2.644), F1b (1.532), the new F1c layout (O at the origin, intermediates down to 0.42, no S→O edge), F4 at (3.7, 0), and the F5(ii) hexagon at (3.1, 0) with a clearance of 0.344 and an O distance of 3.044.
- **F1c gate:** all five 8.6 conditions, with an INVALID result on pin or record failure.
- **F1d:** λ ∈ {1, 8}, descriptive.
- **Execution:** denied by default without a grant and a Claude review that binds the pin.

**10. Site-body-off comparator.**
- It runs on fresh copies on the perceive panel 10,000,512–639, intact only, and recomputes N^x natively (`site_bodies = false`).
- Drives and the phase graph are kept.
- It is descriptive, with N^x count changes reported.

## Required before READY_FOR_FIXTURES

1. Fix finding 1 and add its contract.
2. Resolve finding 2: restrict the screen, or declare it in CONFIG, the report and a test.
3. Recommended: adopt finding 3 and the F5 qualification-rate summary from finding 4.
4. Regenerate `REV7_SOURCE_IDENTITY.json`, run the synthetic suite once, and refresh `REV7_SYNTHETIC_CHECKS.json` to the new pin.
5. Request a bounded Claude re-check that binds the new pin.
