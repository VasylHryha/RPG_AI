# v5b: tooling continuation of the recorded V1 lab

Development only. Same admitted v5 binary, byte-identical declaration, seed
ledger, 220 completed mechanism fights, mechanism summary, K=2/R_c=infinity
pick, and Claude mechanism read. No new pick, entropy, mechanism run, controller
change, or acceptance. The living spec's Amendment 8 does not apply to this
continuation: the exact v5-declared spec and decision 0033 are frozen locally.
All other v5-declared source/native identities remain enforced.

The bounded v5 profile reached 503 completion verifications and 1,472,008 JSON
decodes in 120 seconds before execution. `plan()` called `selected_knobs()` for
every arm/draw; every call re-aggregated 220 mechanism streams, each decoded
twice and re-measured. v5b resolves the pick once per plan. Receipt hashes bind
the already measured statistics/survivors to compressed raw hashes; admission
never decodes completed streams again. Stat-invalidated per-process hash caches
avoid repeatedly hashing unchanged native/source/raw files. New fights are
measured once and get a `_VERIFIED.json` measurement seal. Changed bytes fail
admission; missing seals require investigation and never authorize replay.

`CONTINUATION.json` pins the copied tooling, frozen documents, inherited
receipt bytes and original receipt order. Mechanism compressed streams remain
read-only at `../s4_shape_lab_v5/raw/`; their existing hashes are checked.
The original abandoned RUNNING outcome attempt is retained unchanged under
`inherited_audit/`. It is not a v5b compute attempt or calibrated timing. At
migration no C3/S10X files existed. Mechanism calibration/run attempt bytes and
their measured timing remain unchanged. Future cap accounting and stage/read
gates use the original policy. Execution takes both the v5 lock and the v5b
lock and retains the repository process gate, caffeinate, six workers and v1
owner cap. v5b never rebuilds the binary.

Preparation/migration is already complete. Do not rerun `migrate_v5.py`,
mechanism calibration/run, or `pick`. No outcome fights were run by Codex.
Mechanism calibration/run/review commands are explicitly blocked in v5b so
they cannot overwrite inherited receipts; `prepare` only verifies identity.
The regression invokes the real admission/planning path against all recorded
mechanism receipts with a hard subprocess deadline; full calibration/control
flow is also checked with synthetic outcome records in project-local scratch.
Synthetic timings are not outcome evidence. `--preflight-only` returns before
process discovery, attempts or native execution; actual calibration still runs
the 60 allocated outcome samples and measures their cost for Claude.

Claude commands, from repository root:

```sh
LAB=evidence/tactical_composition_demo/astelia_cpp/s4_shape_lab_v5b/lab.py
.venv/bin/python -B "$LAB" calibrate --stage outcome --look 50 --preflight-only
.venv/bin/python -B "$LAB" calibrate --stage outcome --look 50
.venv/bin/python -B "$LAB" run --stage outcome --look 50
# Read OUTCOME_LOOK_50.json. Stop if clear; continue only if unclear:
.venv/bin/python -B "$LAB" review --stage outcome --look 50 --decision continue --note "<actual reading at 50>"
.venv/bin/python -B "$LAB" run --stage outcome --look 100
.venv/bin/python -B "$LAB" review --stage outcome --look 100 --decision continue --note "<actual reading at 100>"
.venv/bin/python -B "$LAB" run --stage outcome --look 200
.venv/bin/python -B "$LAB" review --stage outcome --look 200 --decision stop --note "<actual reading at 200; script / RRG earns job / park>"
.venv/bin/python -B "$LAB" calibrate --stage series
.venv/bin/python -B "$LAB" run --stage series
.venv/bin/python -B "$LAB" report
```

For an earlier clear look, record its review with `--decision stop` and omit
later C3 looks. Series runs only after a read/finished C3 look. Same declared
strict elimination, losses, streak, replay selection and descriptive mechanism
metrics as v5; the original declaration is the authority. Projection above
the owner cap requires an owner resource decision. Paused-cap execution may
resume the same command, reusing completed cells. A successful stage is not
rerun. A RUNNING attempt, partial non-cap cell, process discovery failure or
identity drift blocks execution and requires investigation.

| Stop question | Action | Role |
|---|---|---|
| Did any inherited/sealed identity change? Yes | Stop and investigate | implementer |
| Is mechanism read/pick invalid or stopped? Yes | Block later stages | implementer |
| Is previous C3 look unread or stopped? Yes | Block next look | implementer |
| Is the result clear at a look? Yes | Record stop | reviewer |
| Are 200 pairs inconclusive? Yes | Park | reviewer |
| Is C3 unfinished/unread? Yes | Block series | implementer |
| Does projection exceed the cap? Yes | Decide resources | owner |
| Is discovery unavailable or a compute attempt unclosed? Yes | Stop and investigate | implementer |
