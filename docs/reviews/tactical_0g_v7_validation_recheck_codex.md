APPROVE_WITH_NOTES
Reviewer family: Codex

Stored-data cross-family owner recheck. This verdict approves the stored development
measurement and the bounded §20.2 readings, with the interpretation notes below.
It is not scientific acceptance, an S5 registration approval or a population claim.

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Reviewed commits:

- `d6adafc54f4a831c38a2caad8be885e5b9bee2d3`: Claude's DESIGN_0G §20.3 write-up; §20.1–20.2 supply its contract.
- `796d0a8c43e5f81533b0b363d856d6a44e33413e`: committed v7b tuning authority.
- `e44b528799d50f5a00a82d1767fd26580da71ea8`: COMPLETE validation analysis and the subsequent render STOP.
- `c8241f2d1861bc012d42443da523f887e518a8ba`: recovery v1; `4147896779296f3b2c56f69c7580868a35c2b890`: boot evidence. Recovery v2 is bound by its supplemental manifest at the reviewed validation commit.

Reviewed `ANALYSIS.json` SHA256:
`f3160cf72e240d2fbfd493b4ba801e79ea4680daac8a4d46a2d0952bdec6bb52`.

## Findings and fixes

No blocking measurement or contract defect was found. The findings concern the
interpretation of §20.3, not new verdict rules or permission to tune on validation.
The requested design and plan documents remain unchanged. The new
`evidence/tactical_composition_demo/astelia_cpp/S4_V7_VALIDATION_REPORT.md`
carries the narrowed interpretations; the drafter should carry them into any
future authorized summary or registration draft.

1. **Medium — absence-of-effect wording (§20.3, “timing does not measurably improve”).**
   The declared reading is a descriptive band, not an equivalence test or a test
   proving no improvement. **Fix:** “v7 had one additional observed regular win;
   this falls in the predefined observed-match band. The descriptive paired
   interval includes both negative and positive differences.” Disposition:
   corrected in the new report; source prose is preserved per owner instruction.
2. **Medium — causal over-reading (§20.3, “the witnessed action map does the killing”).**
   forcedv6 had no elimination wins, but this is a contrast between complete
   interacting policies. It does not identify geometry as the sole cause, separate
   firing from movement, or remove the inherited oscillator from the P16 package.
   **Fix:** report v7 / forcedP16 / forcedv6 regular wins as 32 / 31 / 0 and limit
   the conclusion to these package outcomes. Disposition: corrected in the report.
3. **Low — broad ω0 shorthand (§20.3, “changes little”).**
   The regular win count changes from 32 to 30; other diagnostics change too.
   Regular gate-mode transitions are 951 versus 811, P16-selected unit-tick shares
   are approximately 0.840445 versus 0.825140, and own launches are 7377 versus
   7515. **Fix:** “ω0 had two fewer observed regular wins; the intervention changes
   the total inherited policy, including targeting, firing and gate diagnostics.”
   Disposition: corrected and quantified in the report. No isolated-timing or
   rotation-necessity inference is made.
4. **Low — historical priority (§20.3, “first resonator-based controller”).**
   A current validation panel cannot establish an unrestricted priority claim.
   P16 already contains inherited oscillator dynamics. **Fix:** “first explicit
   oscillator-gated witnessed-map candidate meeting the current elimination
   criterion in this documented series”; do not use priority as evidence for
   what the resonator adds. Disposition: omitted from the report.

## Contract and identity verification

The reviewer audit is reproducible with
`evidence/tactical_composition_demo/astelia_cpp/s4_checks/v7_validation_recheck/audit_stored.py`.
Its new `AUDIT.json` and stdout/stderr logs record the evidence. It never executes
the native engine, calls a fight runner, creates a sealed attempt, rewrites an
existing receipt, or renews an allowance. The raw hash pass precedes decompression.

- All 4,512 tuning/validation COMPLETE record chains were checked: committed
  completion identity → claim/request/gate/binary identity → compressed raw and
  stderr hashes. Both declarations' input hashes and local binary hashes match.
  Tuning authority byte-matches `796d0a8`; validation/analysis byte-match `e44b528`.
- Evaluation 0 is θ_v6. Exactly 16 generations × 16 additional candidates give
  257 evaluations and 8,224 tuning fights: eight clusters × two orientations ×
  both heads per candidate. All raw terminal summaries and candidate metrics were
  recomputed. Eligibility, regular wins, regular mean S, lower own losses and
  earlier ordinal form the same order for retention and CMA selection.
- The sealed CMA 4.5.0 search (seed 1052031267, normalized inherited ordering and
  bounds, σ = 0.25, population 16) was replayed using stored rankings only. Every
  generated vector at ordinals 1–256 matches exactly. The best is ordinal 161,
  regular 16/16, mean S 10.6875, mean own losses 39.3125, novice 16/16. No
  validation input enters that replay, candidate selection or incumbent retention.
- The preserved v7b tree (21,158 files, tree SHA256
  `d8131c06f66769c987c7e4f55751dedc59078ab68da8d4fbc449c7f81506cc58`)
  also binds its rejected validation attempt. `c03_o0` explicitly reports native
  executed_fights = 0 and executed_steps = 0. The interrupted `c02_o1` has empty
  raw output/stderr, so it supplies no independent native count; its zero-combat
  conclusion follows from the pinned codec rejecting the same invalid trace
  flags before world creation. Neither contains a validation outcome for selection.
- θ* is identical in tuning, origin, validation and actual stored requests.
  Validation has 20 unique fresh seeds, disjoint from the hash-verified 37 prior
  development inventories and v7b tuning/unused validation seeds. No judging
  ledger was read. Actual requests cover the exact 400-cell arm/head/cluster/
  orientation grid, with 150 s duration and the delivered templates.
- forcedP16 and forcedv6 force only the outer selected source; latent gate modes,
  v6 pair history, target publication and oscillator integration continue. Source
  inspection confirms one v6 preparation per tick and the delivered P16 overlay.
  The stored pre-fight fixture PASS covers four admissible knob vectors, complete
  commands/state, edge observations, mixed modes, clone isolation and integration
  identity. Stored per-tick telemetry checks the selected complete command against
  its P16 or v6 source. Historical P16 uses θ_v6 and is labelled separately.
  ω0 uses θ* with only its inherited artillery/ranged natural rate overridden.

## Recomputed measurements and readings

All 400 validation fights completed with completed controller status, zero
controller failures and zero numerical-failure ticks. Completed timeouts count as
outcomes, not execution failures: v7 regular has one; forcedv6 regular has 39.
All per-fight numerical fields, ten arm/head summaries, 40 paired-cluster rows,
orientation outcomes/discordance, sign counts and bootstrap endpoints were checked.

| Arm | Regular wins | Regular mean S | Novice wins | Novice mean S |
| --- | --- | --- | --- | --- |
| v7(θ*) | 32/40 | 4.675 | 40/40 | 26.450 |
| forcedP16(θ*) | 31/40 | 2.100 | 40/40 | 21.650 |
| forcedv6(θ*) | 0/40 | 1.575 | 0/40 | -7.075 |
| ω0(θ*) | 30/40 | 4.100 | 40/40 | 25.850 |
| historical P16(θ_v6) | 32/40 | 1.075 | 40/40 | 22.425 |

The displayed §20.3 values are these numbers rounded to two decimal places;
all win counts agree. Positive S does not imply elimination, as forcedv6 shows.

The full paired table, including both heads and all five arms, is in the generated
report and audit. On regular, v7−forcedP16 cluster differences are positive in
4 clusters, negative in 4, tied in 12. Orientation contingency counts are both
win 27, v7-only win 5, forcedP16-only win 4, neither win 4. Resampling the 20 paired
two-orientation clusters 10,000 times with seed 20261007 and linear percentile
interpolation reproduces mean win-rate difference +0.025 and interval
[-0.125, +0.200]. This is descriptive; no inferential verdict follows.

The §20.2 readings reproduce exactly: **OBSERVED MATCH** (+1 win, within ±3);
forcedP16 passes the 21/40 comparator floor; **OBSERVED OWNER CRITERION MET**
(32/40 regular, 40/40 novice, positive mean S on both heads, no failures).

Telemetry was recomputed for every fight from the hash-verified trace and compared
field for field, including counters, source combinations, pair modes, survival
curves, chosen-target values, arrival/band fractions, spacing summaries, shell
counts/multiplicity, firing targets and complex diagnostics. This part reuses the
reviewed sealed observation analyzer and inherited observation oracle: it proves
raw-to-receipt reproducibility, not an independently reimplemented telemetry
oracle. Outcome measurements, rankings, optimizer replay, paired aggregation,
discordance and bootstrap were implemented separately. Source inspection and the
independent terminal unit snapshot check supplement the shared telemetry code.

## The 32 genuine regular wins

Each row has enemy survivors **0**, own survivors **≥1**, and end time **<150 s**.
The audit checks both the raw terminal summary and the last raw observer snapshot
of living units, rather than relying on the score or a win flag. Cluster and
orientation are zero based. Tags are `validation_v7_regular_cNN_oO`.
Times below are display-rounded only; exact values are in `AUDIT.json`.

| Cluster | Orientation | Own survivors | Enemy survivors | End time (s) |
| --- | --- | --- | --- | --- |
| 0 | 0 | 15 | 0 | 40.766667 |
| 0 | 1 | 7 | 0 | 39.133333 |
| 1 | 0 | 14 | 0 | 37.000000 |
| 1 | 1 | 13 | 0 | 32.333333 |
| 2 | 0 | 9 | 0 | 34.400000 |
| 2 | 1 | 8 | 0 | 29.666667 |
| 3 | 1 | 7 | 0 | 45.100000 |
| 4 | 0 | 8 | 0 | 38.366667 |
| 4 | 1 | 2 | 0 | 75.500000 |
| 5 | 1 | 12 | 0 | 49.033333 |
| 6 | 0 | 8 | 0 | 39.266667 |
| 6 | 1 | 7 | 0 | 41.966667 |
| 7 | 0 | 13 | 0 | 43.066667 |
| 7 | 1 | 7 | 0 | 39.200000 |
| 8 | 0 | 9 | 0 | 42.900000 |
| 8 | 1 | 2 | 0 | 70.233333 |
| 9 | 0 | 13 | 0 | 40.433333 |
| 9 | 1 | 10 | 0 | 46.166667 |
| 10 | 0 | 6 | 0 | 38.300000 |
| 10 | 1 | 10 | 0 | 40.200000 |
| 11 | 0 | 10 | 0 | 39.000000 |
| 11 | 1 | 15 | 0 | 34.200000 |
| 12 | 0 | 8 | 0 | 36.733333 |
| 12 | 1 | 17 | 0 | 36.466667 |
| 13 | 0 | 7 | 0 | 36.433333 |
| 13 | 1 | 9 | 0 | 40.400000 |
| 15 | 0 | 4 | 0 | 58.366667 |
| 15 | 1 | 13 | 0 | 37.100000 |
| 16 | 0 | 12 | 0 | 38.366667 |
| 16 | 1 | 7 | 0 | 41.733333 |
| 17 | 0 | 12 | 0 | 30.833333 |
| 19 | 0 | 5 | 0 | 67.966667 |

## Recovery and delivery disposition

Recovery v1/v2 leave the measurement rules, combat declaration, θ*, requests,
entropy, raw data, validation receipt and observation analyzer unchanged. The
v1/v2 supplemental hashes match; their preservation snapshots retain all
2,186/2,207 original measurement artifacts with identical bytes, sizes and mtimes.
Later authorized commits changed the mutable design/plan documents; that is not
a recovery measurement change.

Boot epoch 1791399114.777526 minus the interrupted analysis start gives
2723.777526 s. Adding the completed validation's 227.16235725 s gives historical
2950.93988325 s. The original interruption record's conservative 3377.771384 s
charge is preserved; v2 supersedes its accounting only. Original combat retains
its 3600 s fence. The new allowance is stored-only, shared, and not date-renewable.

Night analysis PASS consumes 6569.993903167 s; render STOP consumes 630.00906 s
against the 630.006096833 s remaining allocation. Total 7200.002963167 s includes
0.002963167 s watchdog overhead; no charge is erased or clipped. The preserved
RUNNING historical receipt remains tied to its explicit interruption and boot
records. The render timeout affects presentation, not the completed measurement.
No sealed render was restarted for this review.

The new report generator reads committed JSON only, checks receipt linkage, and
writes a separate Markdown report. It summarizes pooled numerators/denominators
with explicit units and limitations. The owner recheck and its disposition are
tracked here because the owner explicitly forbids editing `docs/PLAN_CURRENT.md`.
An additional Codex reviewer checked the contract, new scripts and generated
report; preferred cross-family execution is not available in this environment.
Their concrete code findings (exact cell grid, singleton requests, candidate
allocation/metadata, latent gate wording and JSON-derived timings) were fixed
before the full audit. Focused final verification and delivery identity are
recorded in the new review evidence directory.

Final stored audit: **PASS**, 274.748605875 s; 400/400 exact telemetry reproductions,
4,512 verified record chains and all 32 genuine regular wins. The only stderr
message is the vendored CMA library's optional matplotlib plotting warning;
no plotting was requested. No combat test suite or native fixture was run under
this stored-data-only authorization.
