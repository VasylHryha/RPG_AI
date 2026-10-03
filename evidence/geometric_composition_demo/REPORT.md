# Geometric composition demo — results (exploratory; NOT a milestone, NOT C6 evidence)

Status: COMPLETE. One execution after the specification commit `a0c4499`. 20 of 20 seeds, no errors, no retry, 267 s wall,
308 s CPU, peak memory 2.3 GB. No milestone status, accepted file or threshold was changed. Raw per-seed results and the final
accounting are in `run/` (`SUMMARY.json` is the record).

## Verdicts (the rules in SPECIFICATION.md, applied as written)

| Prediction | What was measured | Verdict |
|---|---|---|
| P1 pieces learn | medians: ADD 0.0000, SQRT 0.0003, MUL 0.0047, DIV 0.0092 (all under 0.01); DIV is within 1% in only 70% of seeds (needs 75%) | INDETERMINATE |
| P2 wiring works | wired DISTANCE median 0.0122 (90% of seeds under 0.02); straight line 0.0298 | SUPPORTED |
| P3 composition beats one big map | wired MIX4 0.0126 (straight line 0.0551); equal-budget big map 0.0109; ratio median 0.83, no seed at 3x | REFUTED |
| P4 data needed to match | big map: 0.0109 (1x), 0.0061 (4x), 0.0043 (16x); composite at the same seeds 0.0126, 0.0126, 0.0120 | REFUTED (the 1x map already matches) |
| P5 promotion keeps it one piece | closure error 0.0030 and promoted DISTANCE 0.0121 vs wired 0.0122, but wired DIAG4 0.0246 vs straight line 0.0208 | INDETERMINATE (the reuse chain does not clear the floor) |

Descriptive: an ordinary 4-64-64-1 neural network reached 0.0017 on 4,000 samples and 0.0012 on 64,000 samples, about 7 to 10
times lower than the composite and than the geometric big map at equal size. Intermediate values left a piece's domain in at most
0.3% of calls.

## Reading

- **One level of composition works.** Four separately taught pieces wired into DISTANCE, and the all-four-pieces MIX4, are 2 to 4
  times better than a straight line without any joint training. A wired piece can be promoted into one new map with a closure error of 0.3%
  and the same accuracy (1.21% against 1.22%), so it does act as one piece.
- **Composition gave no accuracy or data advantage here.** One big map of the same size and data matched or beat the composite
  (1.09% against 1.26%) and kept improving with more points and samples (0.43% at 16x), while the composite stays near 1.2% because
  its error is set by its pieces (DIV 0.9%, MUL 0.5%) and adds up. The composition claim "better than one big map" is not supported
  in this 4-input setting.
- **Errors accumulate with depth.** The three-call DIAG4 chain (a distance reused three times) is no better than a straight line
  (2.46% against 2.08%), and promoting it gives 2.06%. Closure at one level (0.3%) is not enough over a chain.
- **Not geometry over matrix math.** The small neural network is an order of magnitude more accurate than these geometric maps on this
  task. The demo does not support, and was not designed to show, that geometry beats matrix math; it tested composition only.

## What this does not show

It does not test oscillators, the C4 law, hierarchical resonators or RRG physics. The pieces are prototype maps with a radial
readout, the task is small (at most four inputs) and smooth, and arithmetic is a task where matrix methods are very strong. Whether
composition helps with many more inputs, deeper hierarchies, scarce data, or tasks natural to geometry (positions, ranges,
tactics) is untested. The composite also received extra supervision (each piece was taught its own job).

## Limits and defects

- Piece sizes were set by a rule fixed in advance on a separate development entropy (pieces only), so P1 checks frozen sizes on fresh
  data. DIV was at the edge (median 0.0092, 70% of seeds within 1%).
- Three pre-run corrections are recorded in the specification's self-audit (a vacuous bar against a straight line, a stale budget,
  piece capacity and domains), with an independent review of the first design.
- No post-hoc analysis was done on this run.
