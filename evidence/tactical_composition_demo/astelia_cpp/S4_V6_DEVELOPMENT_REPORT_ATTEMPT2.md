READY_TO_DRAFT_S5

# S4 v6 development report: attempt 2

Implementer family: Codex (GPT-6). Owner-authorized second exploratory A/B attempt, once, under decision 0031, after the repaired-cache no-combat smoke. Attempt 1 remains unchanged. No C/P2/P3, S5 execution, judging, registration, status change or scientific acceptance.

Runner outcome **READY_TO_DRAFT_S5**; completed stages ['A', 'B']. Recorded 60,996 rows, 60,996 recorded fresh fights, 0 cache hits, 0 recorded numerical-failure rows. The process and cleanup completed successfully; all planned rows are present. All gates are strict; tuning novice eligibility includes equality. Historical -6.025 is an unmatched development comparison.

Planned CMA4.5.0: population16, generations16, fixed budgets; B regular-head selection with novice tuning mean>=0 eligibility. Both orientations averaged within seeds, then each head separately. No validation-based selection. The protocol allocates all four arms to a common fresh validation panel.

Outer elapsed/awake **45.597/45.596 min**, runner 45.591 min, exit 0. Expected about 65 minutes, 10 workers, absolute 360-minute allowance. Literal caffeinate command in LAUNCH.json. Launched immediately, no low-load wait. One-minute load min/mean/max 6.84/25.49/69.24.

Native implementation commit `83c0faf81b4dcc27d07e2dea653470d344663ffb`; cache repair at `fe5b5f2`; attempt-2 wrapper is pinned in this run identity. Binary `02b30cce7ebdfd47130b5e7e99329553eba09d2043a3363629672e05acef4837`. Source/binary/build, fresh entropy and 114 runtime hashes matched stored-only audit. Raw inventory is RAW_FILES_LOCAL.json (SHA256, sizes); files>45MB remain local.

## Pre-fight checks

The 10,763-case acceptance grid passed: max Re/Im errors0.000221341/0.000335573 <=0.001; max commitment error0.000220594 <=0.02; same-substep independent RK4 agreement3.553e-15 <=1e-9. Stage counts1–48; synthetic64/65, retry/exhaustion/nonfinite/pressure cases passed. Controller counter/status/clone isolation, unclipped state, hysteresis/group boundaries, diagnostic action identity, historical contracts and fake-record gates passed. Three previously captured independent-seed default engineering fixtures passed <0.02 commitment refinement. 37 distinct prerequisite/integration tests and 27 offline cache-repair tests had passed before this session. None were repeated. The required attempt-2 cache smoke replayed one stored summary through both the repaired worker write and hit paths with zero native processes or new fights (CACHE_SMOKE.json).

The initial integration wrapper failed an unsupported >15,000-byte assertion after the native contract had passed13,367 compared bytes; corrected the assertion without repeating the passed native contract. The next preservation wrapper detected concurrent Claude TrackA commits (plan/0hdesign); recorded their exact committed identities and completed the corrected preservation check. Neither was a numerical acceptance failure. All failed attempts remain separate; passed cases were not repeated.

## Validation

| Stage | Arm | Head | Clusters | Mean S | SD | SE | Own/enemy guns | Timeouts/fights |
|---|---|---|---:|---:|---:|---:|---|---|
| A | resonator | novice | 100 | +3.9350 | 1.4489 | 0.1449 | 0.000/0.000 | 28/200 |
| A | morale | novice | 100 | +2.1350 | 2.2075 | 0.2207 | 0.000/0.000 | 0/200 |
| A | pushpull | novice | 100 | -1.6650 | 2.3731 | 0.2373 | 0.000/0.000 | 0/200 |
| A | nearest | novice | 100 | +0.8750 | 2.1920 | 0.2192 | 0.000/0.000 | 0/200 |
| B | resonator | novice | 100 | +5.1900 | 7.3298 | 0.7330 | 2.980/1.295 | 0/200 |
| B | resonator | regular | 100 | +8.0250 | 5.4967 | 0.5497 | 7.515/9.470 | 198/200 |
| B | morale | novice | 100 | +24.2300 | 10.6454 | 1.0645 | 7.415/0.215 | 0/200 |
| B | morale | regular | 100 | +8.0350 | 7.0059 | 0.7006 | 6.575/9.110 | 191/200 |
| B | pushpull | novice | 100 | -6.5400 | 3.3991 | 0.3399 | 0.200/6.460 | 0/200 |
| B | pushpull | regular | 100 | -11.5100 | 2.2708 | 0.2271 | 0.000/9.995 | 0/200 |
| B | nearest | novice | 100 | -17.4000 | 3.7444 | 0.3744 | 0.000/9.920 | 0/200 |
| B | nearest | regular | 100 | -22.7500 | 6.6661 | 0.6666 | 0.000/9.995 | 0/200 |

A regular is not_run by design. S=own survivors−enemy survivors. Guns and timeouts are descriptive; means average the two orientations within100 seed clusters. The A/B roster change is not a projectile-observation intervention.

| Stage | Novice >0 | Regular >−6.025 | Beats regular (>0, novice pass, failure-free) | Gate |
|---|---|---|---|---|
| A | True | None | False | CONTINUE |
| B | True | True | True | READY_TO_DRAFT_S5 |

## Historical v5 B comparison

Unmatched development panels and different selected knobs; these differences are descriptive, with no paired or causal interpretation. The v5 source is S4_V5_DEVELOPMENT_REPORT.md.

| Arm | Head | v5 B mean S | v6 attempt 2 B mean S | Difference |
|---|---|---:|---:|---:|
| resonator | regular | -6.025 | +8.025 | +14.050 |
| resonator | novice | +5.600 | +5.190 | -0.410 |
| morale | regular | +9.530 | +8.035 | -1.495 |

On this common v6 validation panel, resonator regular +8.025 and morale regular +8.035 differ by -0.010 points. This result does not establish resonator superiority over morale.

The declared regular gate measures survivor balance at termination. Resonator regular validation has 198/200 timeouts and 9.470 living enemy guns per fight: the positive mean is a survivor-score advantage, not evidence of eliminating the regular army.

## Selected knobs

Stage A (nearest untuned):

```json
{
  "resonator": {
    "K": 3.351491590725461,
    "K_t": 2.144825135377789,
    "kappa": 27.732954895434474,
    "beta": 0.25816056039934665,
    "G": 2.0927492093409925,
    "w": 1.1240227427237368,
    "f_c": 0.5679566632451292,
    "m_k": 0.9892052470669199,
    "lambda_th": 0.7907347012032167,
    "mu": -0.24204562169087707,
    "omega_ranged": 1.9986721332208397
  },
  "morale": {
    "K": 4.984675041543643,
    "K_t": 3.0356104292510366,
    "kappa": 37.72783253325087,
    "beta": 1.3155715784460333,
    "G": 4.354966159381208,
    "w": 0.9766086154271163,
    "f_c": 0.3562975959939625,
    "m_k": 0.3335264309158854,
    "lambda_th": 2.286466391363611,
    "lambda_melee": 0.6169920011923503,
    "lambda_ranged": 1.3804729064168886
  },
  "pushpull": {
    "G": 4.898028157957082,
    "f_c": 0.46074958148639844,
    "m_k": 0.5245512616920971
  }
}
```

Stage B (nearest untuned):

```json
{
  "resonator": {
    "K": 3.566896608697073,
    "K_t": 3.727239438188206,
    "kappa": 28.18188378050727,
    "beta": 0.1344978184970619,
    "G": 4.529277505112292,
    "w": 1.8368755705836595,
    "f_c": 0.9115160242941771,
    "m_k": 0.20353322914295716,
    "lambda_th": 1.250917647665491,
    "mu": -1.8154310511852993,
    "omega_ranged": 1.3914459541507074
  },
  "morale": {
    "K": 4.0984459287845425,
    "K_t": 4.022371164102497,
    "kappa": 47.59886326835983,
    "beta": 0.09479963713395179,
    "G": 3.9724957154757137,
    "w": 0.9545406584010505,
    "f_c": 0.9451551858145626,
    "m_k": 0.4655273981159842,
    "lambda_th": 2.7509426095949028,
    "lambda_melee": 0.3763090027453029,
    "lambda_ranged": 0.04972710765624594
  },
  "pushpull": {
    "G": 4.99929374719847,
    "f_c": 0.9994393878151429,
    "m_k": 0.9955654949688779
  }
}
```

Omega_melee is fixed0; artillery inherits omega_ranged. Selected mu/omega are optimizer diagnostics; A is real-axis melee-only and does not exercise rotation. Cubic versus morale hard saturation, role damping and the product-similarity formation change make v6 a changed controller package. No oscillation-necessity, amplitude-causation, RRG source-recursion, C5 or unchanged-C4 claim.

Final retained knobs (including partial incumbents on stops; completeness is in the selection record):

```json
{
  "knobs": {
    "resonator": {
      "K": 3.566896608697073,
      "K_t": 3.727239438188206,
      "kappa": 28.18188378050727,
      "beta": 0.1344978184970619,
      "G": 4.529277505112292,
      "w": 1.8368755705836595,
      "f_c": 0.9115160242941771,
      "m_k": 0.20353322914295716,
      "lambda_th": 1.250917647665491,
      "mu": -1.8154310511852993,
      "omega_ranged": 1.3914459541507074
    },
    "morale": {
      "K": 4.0984459287845425,
      "K_t": 4.022371164102497,
      "kappa": 47.59886326835983,
      "beta": 0.09479963713395179,
      "G": 3.9724957154757137,
      "w": 0.9545406584010505,
      "f_c": 0.9451551858145626,
      "m_k": 0.4655273981159842,
      "lambda_th": 2.7509426095949028,
      "lambda_melee": 0.3763090027453029,
      "lambda_ranged": 0.04972710765624594
    },
    "pushpull": {
      "G": 4.99929374719847,
      "f_c": 0.9994393878151429,
      "m_k": 0.9955654949688779
    }
  },
  "selections": {
    "resonator": {
      "novice_mean": 4.95,
      "regular_mean": 12.61111111111111,
      "eligible": true,
      "rank": [
        1,
        12.61111111111111
      ],
      "objective": -12.61111111111111
    },
    "morale": {
      "novice_mean": 21.15,
      "regular_mean": 10.61111111111111,
      "eligible": true,
      "rank": [
        1,
        10.61111111111111
      ],
      "objective": -10.61111111111111
    },
    "pushpull": {
      "novice_mean": -6.4,
      "regular_mean": -10.5,
      "eligible": false,
      "rank": [
        0,
        -10.5
      ],
      "objective": 111.5
    }
  }
}
```

## Amplitude diagnostics (resonator validation rows only)

| Stage | Head | Unit-tick samples | Fraction amplitude<0.2 | Valid consecutive arg-rate samples | Mean absolute arg-rate rad/s | Retries | Numerical failure ticks |
|---|---|---:|---:|---:|---:|---:|---:|
| A | novice | 5371917 | 0.445573 | 2970025 | 0.000000 | 0 | 0 |
| B | novice | 9653022 | 0.824790 | 1665923 | 0.216666 | 0 | 0 |
| B | regular | 22749769 | 0.932542 | 1511942 | 0.197919 | 0 | 0 |

Host exports Re z, Im z and amplitude. Arg valid only for amplitude>=0.2; rates use both consecutive valid endpoints, unwrap within valid segments and reset across gaps. Zero is not phase0. The fraction uses accepted living prepare-unit tick records; rates are weighted by their valid endpoint counts. Scalar v5 coherence, target-phase and candidate diagnostics are explicitly not_run for v6.

## Owner recheck and delivery

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Launch recheck was APPROVE_WITH_NOTES; its low smoke-recipe note is retained in CACHE_SMOKE_RECIPE.md without repeating the smoke. Final report recheck is **APPROVE_WITH_NOTES**, recorded in `s4_v6_attempt2_checks/OWNER_RECHECK.md`; the independent stored-only recount is `REVIEW_STORED_AUDIT.json`. Current Claude auth status returned loggedIn:false, so the separate Codex reviewer is a disclosed same-family fallback. No numeric quality scores or independent scientific acceptance. The scoped delivery commit, normal-hook and independent fresh-fetch identities are recorded separately in `s4_v6_attempt2_checks/DELIVERY_TRANSPORT.json`; Claude maintains PLAN_CURRENT, which this task did not edit.
