# Geometric composition demo — specification (committed before any recorded sampling)

## Pieces (level 1)

A piece is a `GeoMap`: `M` prototype points in the unit-scaled input box, a Gaussian width equal to 1.2 times the mean
nearest-prototype distance (a fixed rule, never tuned per piece), and a readout that is linear in the Gaussian responses
plus the inputs plus a constant (ridge, relative strength 1e-8). Training places the points by k-means++ then 20 Lloyd
iterations on the training inputs (competitive learning), then fits the readout by ridge least squares. Inputs and the
output are scaled by the piece's declared box and by the training output range.

Each piece is taught on the domain its composites actually use, from 1,000 uniform random samples:

| Piece | Inputs (domain) | Target | Points M |
|---|---|---|---|
| ADD | a, b in [-2, 20] | a + b | 16 |
| MUL | a, b in [1, 5] | a * b | 32 |
| SQRT | x in [1, 40] | sqrt(x) | 16 |
| DIV | a in [0.3, 4], b in [0.3, 3] | a / b | 256 |

The sizes come from `dev_piece_sizes.py` (record: `dev_piece_sizes.json`), a development run on its own entropy, separate from
the recorded run and the smoke, with a rule fixed before it ran: for each piece the smallest size in {16, 32, 64, 128, 256} whose
median relative error over 10 seeds is at most 0.005 (half the P1 bar), else 256. Only pieces were evaluated there; no composite,
no big map and no comparison. DIV never reached 0.005 within the grid, so the rule gave 256. The recorded P1 check is therefore a
check of the frozen sizes on fresh data, not an independent measure of how easy the pieces are.

DIV is taught and scored and is used by MIX4 only. The domains are chosen to cover every intermediate value of the composites:
a, b, c, d in [1, 3] for DIAG4; distances in [1.41, 4.25]; squares up to 18.5 and their sums up to 37 for DISTANCE on [1, 4.3];
for MIX4 products up to 9, quotients up to 13.3 and sums up to 22.3. Intermediate values are never clipped. A taught piece can
still be asked about a value outside its domain (for example a quotient predicted slightly below zero); the number of such
inputs is counted and reported per composite.

## Composites

- DISTANCE(a, b), a and b in [1, 4.3]: SQRT(ADD(MUL(a, a), MUL(b, b))) with the taught pieces, no further training.
- DIAG4(a, b, c, d), all in [1, 3]: DISTANCE(DISTANCE(a, b), DISTANCE(c, d)); one DISTANCE reused three times.
- MIX4(a, b, c, d) = sqrt(a*b + c/d), a and b in [1, 3], c in [0.3, 4], d in [0.3, 3]: SQRT(ADD(MUL(a, b), DIV(c, d))). All four
  taught pieces wired once (sum, multiply, divide, square root), no further training. This is the target of the comparison with
  one big map.
- Promotion: sample the wired DISTANCE at 2,000 uniform points of [1, 4.3]^2 (no ground-truth labels) and teach one new GeoMap with
  64 points on those samples. `DISTANCE_P` is the promoted piece. `DIAG4_P` is DIAG4 built from it.

## Baselines

- Straight line: the best linear model (least squares) fitted on 3,000 samples, for DISTANCE, DIAG4 and MIX4. It is the floor a
  composition must clearly beat: these targets are only mildly nonlinear (a plain linear fit is within about 3% of DISTANCE and DIAG4
  and about 5% of MIX4 over their domains, measured on the tasks alone before the run).
- Monolith: one GeoMap on the MIX4 box taught directly on MIX4. Equal budget: 320 points (the points of the four taught pieces,
  16 + 32 + 16 + 256, counted once each) and 4,000 samples (4 x 1,000, the composite's total training samples). Scaled series:
  (1,280 points, 16,000 samples) and (5,120 points, 64,000 samples).
- MLP reference (ordinary matrix math, descriptive only): 4-64-64-1 tanh, Adam, full standardization, trained on MIX4 with 4,000 and
  with 64,000 samples (fixed epochs: 300 and 40, batch 256, learning rate 0.003).

## Measurements

Relative error = RMSE / (max - min of the true output over the test set). Test sets: 5,000 fresh uniform points per target,
independent of every training stream (checked: all random streams are keyed by purpose, seed and a distinct key). Seeds: 20
independent seeds for everything except the largest monolith (10 seeds). Reported per seed and as median and quartiles. Each
scaled-monolith comparison uses the composite's median over the same seeds.

## Predictions (stated before any recorded run; each can fail)

Verdict words: SUPPORTED if the bar is met by the median and by at least 75% of seeds; REFUTED if the median misses by the
stated factor; INDETERMINATE otherwise. Every composite bar also has a straight-line floor: the composite's median error must be at
most half the straight-line baseline's median (at least twice as good as a straight line). With a straight line near 3% (DISTANCE,
DIAG4) and 5% (MIX4) the effective bars are about 1.5% and 2.5%, tighter than the absolute bars below.

- P1 (pieces learn): relative error of ADD, MUL, SQRT and DIV on their own test domains <= 0.01. REFUTED if any piece has
  median > 0.02.
- P2 (wiring works): wired DISTANCE relative error <= 0.02 AND its median <= 0.5 times the straight-line baseline's median.
  REFUTED if median > 0.04.
- P3 (composition beats one big map at equal size and data): wired MIX4 relative error <= 0.03 (median and 75% of seeds) AND its
  median <= 0.5 times the straight-line baseline's median AND the equal-budget monolith's error is at least 3 times larger than the
  composite's (per seed ratio; median and 75% of seeds). REFUTED if the median ratio < 1.5 or the composite's median error > 0.06.
- P4 (data needed to match): compare each scaled monolith's median MIX4 error with the composite's median over the same seeds.
  REFUTED if the equal-budget monolith matches or beats the composite. Otherwise INDETERMINATE if the composite does not clear its P3
  bars (error bar and straight-line floor), or if only the 4x monolith matches; SUPPORTED if neither the equal-budget nor the 4x
  monolith matches and the composite clears its bars.
- P5 (promotion keeps it one piece): closure error (RMS of promoted minus wired DISTANCE over the test set, divided by the
  test range) <= 0.01 AND the median DIAG4_P error <= 1.5 times the median wired DIAG4 error AND the wired DIAG4 median is at most
  half the straight-line baseline's median. REFUTED if closure error > 0.02 or the ratio > 3.

Descriptive, no verdict: MLP errors at both sample counts, the straight-line baselines for all three composites, intermediate domain
violations for DISTANCE, DIAG4 and MIX4, runtime per seed.

Reading, as written: P2 and P3 and P5 SUPPORTED means small taught geometric pieces compose and promote in this setting, and
the data-to-match number says how much the one-sided supervision matters. P3 REFUTED means one big map of the same size does
as well and composition adds nothing here. Either result is reported as it is. No claim about oscillators, RRG physics or
general superiority over matrix methods follows from this demo.

## Supervision caveat

The composite is built from pieces that were each told their own answer; the monolith is told only the final answer. That
asymmetry is the idea being tested (teach small pieces different jobs, then combine them), not hidden. The 4x and 16x
monolith rows show how much extra data or size the monolith needs to catch up. The pieces are also taught only on the ranges
their composites use, while the monolith is taught on the MIX4 box; both are taught on the ranges of use.

## Rules of the run

Own entropy (SPEC.json, 96-bit, generated once by `--write-spec`, with a separate smoke entropy; the config copy in SPEC.json was
refreshed from `demo.py` before the specification commit and a test checks they agree). Single process, numpy only. The implementer
runs the mechanics tests before the commit; the run records the hashes of `demo.py`, `test_demo.py` and `SPEC.json`. The run refuses
to start unless README.md, SPECIFICATION.md, SPEC.json, demo.py and test_demo.py are committed and clean; creating the exclusive
`run/` directory is the one-shot latch; every post-latch failure is recorded in `run/SUMMARY.json`. Expected duration 10 to 20
minutes, dominated by the largest monolith (about 5,000 points, 64,000 samples, 10 seeds; estimated from arithmetic, unmeasured).
Soft cap 45 minutes, checked between seeds: stop starting new seeds and record INCOMPLETE. A hard kill or out-of-memory exit after the
latch leaves `RUN_STARTED.json` and the finished seed files but no summary; that case is INCOMPLETE and is not retried. Peak memory is
reported in bytes on macOS. No retry, no seed replacement, no threshold or piece-size change after seeing a recorded result.

## Normalization ledger

| Quantity | Normalization |
|---|---|
| Inputs | scaled to the unit box of each piece's declared domain |
| Output | scaled by the training output range |
| Error | RMSE divided by the true output range over the test set |
| Budget | points counted once per distinct taught piece; samples summed over taught pieces |
| Gaussian width | 1.2 x mean nearest-prototype distance, the same rule for every map |

## Stop conditions (yes/no, one action, one role)

| Condition | Action | Role |
|---|---|---|
| Specification or code not committed or not clean? | Refuse to run | Implementer |
| `run/` already exists? | Refuse; no resume, no retry | Implementer |
| A seed fails numerically (non-finite)? | Record it as missing, never replace it; INCOMPLETE takes precedence over any verdict | Implementer |
| Soft cap reached? | Stop, record INCOMPLETE | Implementer |
| Result tempts a retune or a rerun with new seeds? | Do not; return to the owner | Implementer |

## Drafter self-audit

| Issue found | Cause | Fix |
|---|---|---|
| The first design compared the composite with one big map on a 4-input diagonal; a plain straight line already fits it to 1.9%, under the 3% bar, so P3's bar would pass for a model that does no composition | Bars were set before measuring how nonlinear the task was; found by fitting a straight line to the task itself before any recorded run (the numbers of a toy-sized smoke prompted the question; they were not otherwise used) | New comparison target MIX4 using all four taught pieces; straight-line baselines for every composite; bars tied to them |
| Two calibrations of the MIX4 domain (denominators down to 0.5, then 0.3) | Same: difficulty was set by the straight-line check on the task only, never by any method's error | Design frozen after the second |
| The equal budget was stated for the old target | The target changed, the budget did not | Budget derived from the pieces actually used |
| Independent review: DIV (hyperbolic, wide denominator range) and MUL could not meet P1 at the original sizes, and pieces were taught on wider domains than the composites use while the monolith was taught on exactly the MIX4 box | Piece sizes and domains were guesses | Domains restricted to the composites' use; sizes set by a rule fixed in advance on a separate development entropy, pieces only (this section, `dev_piece_sizes`) |
| Independent review: the P3 floor (0.25 x straight line) was stricter than its stated bar and undocumented; P4 and P5 had no floor despite the claim; P4 compared unpaired seed sets | Written incrementally | Floor factor 0.5 stated with effective bars; P4 and P5 gated on the composite clearing its bars; P4 pairs seeds |
| Independent review: SPEC.json could drift from the code; spec text had wrong intermediate maxima and a claim that domains keep values inside by construction; README still framed the monolith on the diagonal; quartiles claimed but not reported; the distance violation counter was not written out | Edits not cross-checked | A test ties SPEC.json to the code; text corrected; quartiles and all three violation counters reported |
| A guard test raised on every path and so proved nothing | Written in a hurry | Replaced by a real check in a throwaway git repository |
