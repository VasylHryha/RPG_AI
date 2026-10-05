Declared before comparison or timing: engineering equivalence, DESIGN_0H revision 5.1.

Compare reference and native on dev medium seed 105051, eight episodes, using
the same frozen calibration and episode seeds. Compare every event in order,
IDs, rules, decisions, boolean eligibility, counters, clocks, D1/B1 timers,
birth ages, all retained frames and native serialized state (including internal
history), drive schedules, reward eligibility, and qualification check-time
state. Synthetic contracts cover all four bindings, hidden/inactive sites,
strict cutoffs, warmup, partner eligibility, adaptation, coverage, timer reset,
growth/protection/budget rules, qualification and episode/batch boundaries.

RK4-only continuation with the same supplied drives must be byte-identical,
including native snapshots and endpoint frames: the existing native integrator
and its operation order are reused. Bindings from identical observations,
clocks and timers are exact. When an adapted trajectory changes the next
movement observation by roundoff, its drive angles and strengths use the
same declared numeric tolerance.
For adapted floating-point measurements/state only, use abs(a-b) <=
1e-10 + 1e-10*abs(b). NumPy's complex exponential/reduction and C++ libm's
sin/cos/sequential reduction have different rounding orders; adaptation can
propagate those roundoff differences into later trajectories. This bound is
fixed before runs and much smaller than the existing 1e-9 C4 parity bound.
Every differing event rule, membership, eligibility, admission, rejection,
drop, selection or decision is a failure, regardless of numeric closeness.
Template digest strings are independently verified against their own exact
content; compare template content numerically and duplicate decisions exactly
(a rounded float changes a content hash without changing its underlying state).

Timing: one reference and one native eight-episode smoke in the same process
with the same calibration/library. Report training seconds / 1280, excluding
qualification/recovery time exactly as the runner already does. Retain total
wall time separately. Compare first, publish timings only after equivalence
passes. No section-10 run, projection or judging entropy.
