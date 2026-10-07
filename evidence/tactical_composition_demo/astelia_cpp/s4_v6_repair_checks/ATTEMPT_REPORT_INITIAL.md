STOPPED: ValueError('invalid combat summary schema')

# S4 v6 development report

Implementer family: Codex (GPT-6). Owner-authorized single exploratory A/B run under decision0031. No C/P2/P3, S5 execution, judging, registration, status change or scientific acceptance.

Runner outcome **NOT_READY**; completed stages []. Recorded 0 rows, 0 fresh fights, 0 cache hits, 0 numerical-failure rows. All gates are strict; tuning novice eligibility includes equality. Historical -6.025 is an unmatched development comparison.

CMA4.5.0: population16, generations16, fixed budgets; B regular-head selection with novice tuning mean>=0 eligibility. Both orientations averaged within seeds, then each head separately. No validation-based selection. All four arms validate on the common fresh panel.

Outer elapsed/awake **0.007/0.007 min**, runner 0.004 min, exit 1. Expected about65min, 10workers, absolute360min allowance. Literal caffeinate command in LAUNCH.json. Launched immediately, no low-load wait. One-minute load min/mean/max 5.81/5.81/5.81.

Implementation commit `83c0faf81b4dcc27d07e2dea653470d344663ffb`; binary `02b30cce7ebdfd47130b5e7e99329553eba09d2043a3363629672e05acef4837`. Source/binary/build, fresh entropy and 108 runtime hashes matched stored-only audit. Raw inventory is RAW_FILES_LOCAL.json (SHA256, sizes); files>45MB remain local.

## Pre-fight checks

The 10,763-case acceptance grid passed: max Re/Im errors0.000221341/0.000335573 <=0.001; max commitment error0.000220594 <=0.02; same-substep independent RK4 agreement3.553e-15 <=1e-9. Stage counts1–48; synthetic64/65, retry/exhaustion/nonfinite/pressure cases passed. Controller counter/status/clone isolation, unclipped state, hysteresis/group boundaries, diagnostic action identity, historical contracts and fake-record gates passed. Three independent-seed default engineering captures passed <0.02 commitment refinement.37 distinct tests passed across the required prerequisite and final batch.

The initial integration wrapper failed an unsupported >15,000-byte assertion after the native contract had passed13,367 compared bytes; corrected the assertion without repeating the passed native contract. The next preservation wrapper detected concurrent Claude TrackA commits (plan/0hdesign); recorded their exact committed identities and completed the corrected preservation check. Neither was a numerical acceptance failure. All failed attempts remain separate; passed cases were not repeated.

## Validation

| Stage | Arm | Head | Clusters | Mean S | SD | SE | Own/enemy guns | Timeouts/fights |
|---|---|---|---:|---:|---:|---:|---|---|
| A | resonator | all planned heads | — | not_run | — | — | — | — |
| A | morale | all planned heads | — | not_run | — | — | — | — |
| A | pushpull | all planned heads | — | not_run | — | — | — | — |
| A | nearest | all planned heads | — | not_run | — | — | — | — |
| B | resonator | all planned heads | — | not_run | — | — | — | — |
| B | morale | all planned heads | — | not_run | — | — | — | — |
| B | pushpull | all planned heads | — | not_run | — | — | — | — |
| B | nearest | all planned heads | — | not_run | — | — | — | — |

A regular is not_run by design. S=own survivors−enemy survivors. Guns and timeouts are descriptive; means average the two orientations within100 seed clusters. The A/B roster change is not a projectile-observation intervention.

| Stage | Novice >0 | Regular >−6.025 | Beats regular (>0, novice pass, failure-free) | Gate |
|---|---|---|---|---|

## Selected knobs

Omega_melee is fixed0; artillery inherits omega_ranged. Selected mu/omega are optimizer diagnostics; A is real-axis melee-only and does not exercise rotation. Cubic versus morale hard saturation, role damping and the product-similarity formation change make v6 a changed controller package. No oscillation-necessity, amplitude-causation, RRG source-recursion, C5 or unchanged-C4 claim.

Final retained knobs (including partial incumbents on stops; completeness is in the selection record):

```json
{
  "knobs": {
    "resonator": {
      "K": 2.5,
      "K_t": 2.5,
      "kappa": 25.0,
      "beta": 1.5,
      "G": 2.5,
      "w": 1.5,
      "f_c": 0.65,
      "m_k": 0.6,
      "lambda_th": 1.5,
      "mu": 0.0,
      "omega_ranged": 0.0
    },
    "morale": {
      "K": 2.5,
      "K_t": 2.5,
      "kappa": 25.0,
      "beta": 1.5,
      "G": 2.5,
      "w": 1.5,
      "f_c": 0.65,
      "m_k": 0.6,
      "lambda_th": 1.5,
      "lambda_melee": 1.0,
      "lambda_ranged": 1.0
    },
    "pushpull": {
      "G": 2.5,
      "f_c": 0.65,
      "m_k": 0.6
    }
  },
  "selections": {}
}
```

## Amplitude diagnostics

| Stage | Head | Unit-tick samples | Fraction amplitude<0.2 | Valid consecutive arg-rate samples | Mean absolute arg-rate rad/s | Retries | Numerical failure ticks |
|---|---|---:|---:|---:|---:|---:|---:|

Host exports Re z, Im z and amplitude. Arg valid only for amplitude>=0.2; rates use both consecutive valid endpoints, unwrap within valid segments and reset across gaps. Zero is not phase0. The fraction uses accepted living prepare-unit tick records; rates are weighted by their valid endpoint counts. Scalar v5 coherence, target-phase and candidate diagnostics are explicitly not_run for v6.

## Owner recheck and delivery

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Report recheck is pending; implementation review was APPROVE_WITH_NOTES after fixes. Claude CLI was not logged in, so the separate Codex reviewer is a disclosed same-family fallback. No numeric quality scores or independent scientific acceptance. Final disposition and normal-hook bundle/fresh-fetch transport go in the delivery note; Claude maintains PLAN_CURRENT, which this task did not edit.
