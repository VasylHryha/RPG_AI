# Specification 0g, revision 2 (S5 registration DRAFT): the resonator AI against Astelia's scripted AI

**Status: DRAFT.** Revision 2 answers the Codex review of revision 1 (`docs/reviews/tactical_0g_spec_review_codex.md`, CHANGES_REQUIRED; the self-audit is below).
`SPEC_0G.json` governs, and the runner reads only that file. Execution needs three recorded gates (JSON `gates`):
1. a Codex review of **this** revision returning APPROVE or APPROVE_WITH_NOTES;
2. the owner's approval of δ and n;
3. the owner's authorization of S6, naming the specification's hash.

This is exploratory, under decision 0028, and changes no milestone status.

## What is tested

1. **P1, beat the code:** does our AI (the C4 element law driven by damage) beat the scripted novice **and** regular levels head-to-head with full armies?
2. **P2, does the beat matter:** does it beat plain morale, the same controller with a number instead of a circular phase, by more than δ?
3. **P3, beyond known swarm forces:** does it beat the specified push-pull baseline by more than δ?

## How

All of it is written structurally in `SPEC_0G.json`: no field is inferred from a runner script.
- **Engine:** binary sha256 `a1a2d528…552c74a` (the S4 build), using the literal native request template.
- **Opponents:**
  - head-to-head: the scripted levels `{level: novice}` and `{level: regular}`;
  - the pool: the 19 doctrines, listed in order, each with the exact elite skill map with `artyRollout: null` and `lookahead: null`, equally weighted.
- **Arms and knobs:**
  - the HEAD panel uses each arm's amended-S4 **stage-B** knobs (tuned head-to-head);
  - the POOL panel uses the **stage-C** knobs (tuned on the pool);
  - nearest has no knobs.

  The values and the source file hashes are copied into the JSON.
- **Seeds:** a 128-bit root, with byte-exact derivation and three namespaces:
  - P1_novice and P1_regular, 100 clusters each;
  - POOL, 32 blocks shared by P2, P3, every arm and every doctrine.

  A preflight rejects any duplicate seed or any overlap with a development seed, before any fight. The revision-1 root was retired unused.
- **Panels:**
  - **HEAD:** a cluster is one seed in both orientations; the value is the mean S.
  - **POOL:** a block is one seed × 19 doctrines × 2 orientations; arms are joined by (doctrine, seed, orientation); the value is the mean of the 38 paired differences.
- **Statistics:**
  - one-sided t bounds, mean ± t(1 − a, n − 1) · sd/√n, with sample SD (n − 1), strict comparisons, and sd = 0 giving bounds equal to the mean;
  - the t calibration is an approximation, declared as a limit.
- **Alpha** (exact fractions):
  - familywise 1/100;
  - support 1/400 per test (P1 is an intersection-union over its two levels);
  - refutation 1/1200 for P2 and P3, and 1/2400 per P1 level.
- **Verdicts:**
  - P1 SUPPORTED if both levels' lower bounds are above 0; REFUTED if either level's upper bound is below 0.
  - P2 and P3 SUPPORTED if the lower bound is above δ; REFUTED if the upper bound is below 0.
  - INDETERMINATE otherwise.
- **Score:**
  - S = survivors − enemy survivors for our side 0, timeouts included.
  - D = cross-team dealt − taken, fight-long, with friendly fire reported separately. D is descriptive only.
- **Failures:**
  - Every attempted fight is recorded. Nothing is dropped, replaced or partially averaged.
  - An endpoint missing any required fight is INDETERMINATE, with the reason.
  - Descriptive arms veto nothing, and P1 never stops the pool panel.
- **Execution:**
  - preflight;
  - an atomic, one-shot output directory with an identity file before the first fight;
  - HEAD, then POOL;
  - coverage for every endpoint.
- **Size:** 6,464 fights:
  - HEAD: 2 levels × 100 × 2 orientations × 4 arms;
  - POOL: 32 × 19 × 2 × 4.

  The diagnostics reuse 57 of the scheduled fights (resonator, blocks 0-2, orientation false).

## Disclosed development expectations (not evidence)

| Endpoint | S4 amended validation | Expectation |
|---|---|---|
| P1 | resonator (B knobs): novice +5.92, regular −8.69 | expected to fail on regular |
| P2 | resonator − morale: −1.09 [−1.69, −0.50] | not expected to be supported |
| P3 | resonator − push-pull: +7.32 [6.91, 7.73] | expected near or above δ |

Every endpoint is registered as designed, with nothing narrowed after seeing development data.

## Owner decisions needed

| Question | If yes | If no |
|---|---|---|
| Approve δ = 4.0 survivors? | keep | the owner names δ; the specification is revised and re-reviewed before any fight |
| Approve n = 100 clusters per level (P1) and 32 seed blocks (P2/P3)? These are fixed conservative choices above the floors of 32 and 16 | keep | the owner names n |
| After the Codex review of this revision, authorize S6 once with this exact file (its sha256)? | the runner may execute | stop |

## Self-audit: the revision-1 review findings

| # | Finding | Fix | Cause |
|---|---|---|---|
| 1 | Panels, requests and S not fully in the JSON | Literal request template, doctrine list, skill map, controlled side, S, timeout and the bound formula in JSON | I referred to the runner and the design instead of copying their definitions |
| 2 | Seed derivation not unique | Byte-exact derivation, named namespaces, a shared POOL panel, preflight against development ledgers | I wrote the derivation in prose |
| 3 | Failure scope and coverage underdefined | Required-fight sets per endpoint, technical failures defined, no partial averaging, independent endpoints | Not specified |
| 4 | Approval, root and latch lifecycle | Three recorded gates, an authorization file naming the hash, atomic mkdir before the first fight, the fresh-root rule and root provenance in JSON | Split between the Markdown and the JSON |
| 5 | The P1 floor came from C-knob data | B-based planning computed (24 and 1); 100 stated as a fixed conservative choice | I reused the S4 planning receipt without checking its knob source |
| 6 | The descriptive subset not fixed | Diagnostics fixed to blocks 0-2, orientation false, resonator; D and timeout defined; all descriptive arms listed | Left to the implementer |
| 7 | Rounded alpha constants | Exact fractions | Rounded decimals |
| 8 | t calibration | Independence and the approximation declared | Not stated |

## What is not claimed

- a C5 hierarchy;
- that a sustained oscillation is necessary;
- novelty over swarmalators or physicomimetics;
- results against elite;
- anything beyond this game, these panels and these separately tuned knobs.
