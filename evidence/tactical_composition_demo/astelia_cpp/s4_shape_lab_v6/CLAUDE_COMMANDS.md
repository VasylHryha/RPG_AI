# Claude execution handoff — v6 already prepared, zero fights

From `/Users/new/RiderProjects/ai_RPG_test`. Finish/read the existing V1 batch
first; do not change v5. Default v6 timing remains fire-when-ready. Optionally
choose the V1 winner once before ANY v6 fight claim; use actual V1 evidence and
oscillator grid values if chosen. No rebuild or code edit after preparation.

```sh
LAB=evidence/tactical_composition_demo/astelia_cpp/s4_shape_lab_v6/lab.py
# Optional common timing selection. Omit to seal default base automatically:
.venv/bin/python -B "$LAB" configure-timing --mode base --note "<actual V1 reading>"
# Alternatives, exactly one, only if selected by V1:
# .venv/bin/python -B "$LAB" configure-timing --mode central_sync --note "<actual V1 reading>"
# .venv/bin/python -B "$LAB" configure-timing --mode battery_oscillator --k 1 --radius 400 --note "<actual V1 reading and selected grid values>"
```

Run mechanisms in the adopted order V2 → E1 → R1 → E1+R1. Each line below
uses allocated paired cells; calibration is retained and reused. Process gate
waits for repository heavy jobs; discovery unavailable means no fights. Missing
cap defaults to3600s; shared owner LAB_CAP.json remains the resource authority.

```sh
.venv/bin/python -B "$LAB" calibrate --arm V2 --stage mechanism
.venv/bin/python -B "$LAB" run --arm V2 --stage mechanism
.venv/bin/python -B "$LAB" report --arm V2
```

Read `MECHANISM_V2_SUMMARY.json`. Record continue only if geometry activates
AND damage/coverage improves without an erasing fire-rate/survival tradeoff.
Use stop to park an inert/ineffective candidate.

```sh
.venv/bin/python -B "$LAB" review --arm V2 --stage mechanism --decision continue --note "<actual mechanism and both-axis reading>"
.venv/bin/python -B "$LAB" calibrate --arm E1 --stage mechanism
.venv/bin/python -B "$LAB" run --arm E1 --stage mechanism
.venv/bin/python -B "$LAB" report --arm E1
.venv/bin/python -B "$LAB" review --arm E1 --stage mechanism --decision continue --note "<actual activation, utilization, shots and ranged-death reading>"
```

Only after E1 is activated/read/frozen; otherwise rotation is blocked:

```sh
.venv/bin/python -B "$LAB" calibrate --arm R1 --stage mechanism
.venv/bin/python -B "$LAB" run --arm R1 --stage mechanism
.venv/bin/python -B "$LAB" report --arm R1
.venv/bin/python -B "$LAB" review --arm R1 --stage mechanism --decision continue --note "<actual diagnostic rotation activation/counterfactual/survival/firepower reading>"
.venv/bin/python -B "$LAB" calibrate --arm 'E1+R1' --stage mechanism
.venv/bin/python -B "$LAB" run --arm 'E1+R1' --stage mechanism
.venv/bin/python -B "$LAB" report --arm 'E1+R1'
.venv/bin/python -B "$LAB" review --arm 'E1+R1' --stage mechanism --decision continue --note "<actual primary E1+R1 minus active E1 reading>"
```

Use `--decision stop` instead of continue if inactive/ineffective. The numeric
false-extraction causal endpoint remains explicitly `not_evaluated`; contract
violations and triggered survival are separate. Do not call predicted deaths
observed deaths prevented. Native gates enforce activation; Claude must read
metric movement, survivorship and tactic guards honestly.

For EACH activated arm, set ARM to `V2`, `E1`, `R1` or `E1+R1`. Shared base and
E1 receipts reuse the exact same draws. Inspect all20 tactic cells at each look.
R1 versus base is diagnostic; E1+R1 versus E1 is the primary rotation contrast.
Deaths over all paired fights/exchange are decision numbers; wins descriptive.

```sh
ARM=V2
.venv/bin/python -B "$LAB" calibrate --arm "$ARM" --stage outcome --look 50
.venv/bin/python -B "$LAB" run --arm "$ARM" --stage outcome --look 50
.venv/bin/python -B "$LAB" report --arm "$ARM"
```

Read `OUTCOME_<ARM>_LOOK_50.json`; choose exactly one:

```sh
# Still unclear:
.venv/bin/python -B "$LAB" review --arm "$ARM" --stage outcome --look 50 --decision continue --note "<actual paired axes and tactic guards; unclear>"
# Clear survivor; omit all later C3 looks:
# .venv/bin/python -B "$LAB" review --arm "$ARM" --stage outcome --look 50 --decision stop --survivor --note "<actual clearly positive guarded reading>"
# Negative/parked; omit later C3 and series:
# .venv/bin/python -B "$LAB" review --arm "$ARM" --stage outcome --look 50 --decision stop --note "<actual negative/ineffective reading>"
```

Only when the preceding look says continue:

```sh
.venv/bin/python -B "$LAB" run --arm "$ARM" --stage outcome --look 100
.venv/bin/python -B "$LAB" report --arm "$ARM"
# Choose continue only if still unclear, otherwise stop with/without --survivor:
.venv/bin/python -B "$LAB" review --arm "$ARM" --stage outcome --look 100 --decision continue --note "<actual paired axes and tactic guards; unclear>"
.venv/bin/python -B "$LAB" run --arm "$ARM" --stage outcome --look 200
.venv/bin/python -B "$LAB" report --arm "$ARM"
# Stop at200. Use --survivor ONLY if clearly positive; otherwise omit it:
.venv/bin/python -B "$LAB" review --arm "$ARM" --stage outcome --look 200 --decision stop --survivor --note "<actual final paired reading and survival decision>"
```

For a stopped C3 arm explicitly marked survivor, at whichever completed look:

```sh
.venv/bin/python -B "$LAB" calibrate --arm "$ARM" --stage series
.venv/bin/python -B "$LAB" run --arm "$ARM" --stage series
.venv/bin/python -B "$LAB" report --arm "$ARM"
```

Streak primary, reach/roster/failure tactic and both axes secondary. If projection
exceeds cap, stop and obtain the owner resource decision. PAUSED_CAP may repeat
the same compute command to reuse verified completions; never run native fights
directly, rerun passing cells, edit sealed sources, or extend beyond200 pairs.
