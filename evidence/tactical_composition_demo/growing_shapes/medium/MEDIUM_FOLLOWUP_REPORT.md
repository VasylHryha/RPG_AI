READY

Engineering follow-up for DESIGN_0H revision 5.1, R4-2/R5-3, under decision 0028
item 17. Claude review of this follow-up remains required before section 10.
The historical medium report, verification receipt and 70-test file are unchanged.

The native engine adds gain (default 1) inside each stage of the full driven RK4
RHS. `Medium.set_gain`/`gain` validate [0,2]. Sampling, carried-site histories and
undirected internal-pair cost are selectable; legacy defaults retain automatic
substep sampling, strength-change invalidation, directed/internal-plus-drive cost,
and the existing growth implementation. New native snapshots preserve the
options and gain, with backward reading of v1. Native source/binary identities
are checked against the explicit build manifest before loading.

`design_0h.py:DesignMedium` selects world-step sampling after exactly five
substeps, retains indexed positions/phases/site strengths and actual directed
neighbour lists, and provides 100/101-sample statistics. Lock uses partners
active/reachable in at least 80 samples; undefined warm-up resets D1. Coverage
also needs 101 element samples, PLV >=0.8 and absolute circular offset <=0.5.
Every reach test is strict: drive/partner/coverage radius 3 and readout radius 2.
The adapter implements D1, D3, B1 in that order, recomputes undirected union cost
without drive links after every structural change, and logs rejections and
protected over-budget states. Births use the exact 50-point spiral, separation
0.05, g=1, empty histories and 200-step protection. IDs start at zero and never
reuse; integer birth steps avoid accumulated native-clock drift at boundaries.

Verification:

- Original 70 engine contracts passed, including all five C4 fixtures x three
  variants at 1e-9. The file and engine law stayed unchanged thereafter.
- 45 follow-up contracts passed in the 102-test new-contract batch (5.59 s,
  including the runner contracts at that stage).
- Synthetic checks include exact drive/readout/eligibility/coverage boundaries,
  carried strength changes, historical reach and neighbour membership, offset
  coverage, warm-up, undefined/no-drive gain, Euler clipping, timers/protection,
  D3 ordering and cost, B1 cap/site order/rejections, spiral exhaustion, monotone
  identity, and native v1/v2 snapshot continuation.
- The first combined run stopped after 89 passes at an exact floating-point PLV
  assertion (1 versus 0.9999999999999998). Numerical assertions were corrected;
  that failed attempt is preserved separately. Legacy tests were not repeated.

Evidence and source identities: `../runner/CHECKS.json`, the original-attempt
log and final contract logs there. The eight-episode engineering smoke is
reported in `../runner/RUNNER_REPORT.md`. No development/projection/judging or
recorded run occurred. No open protocol question was raised.
