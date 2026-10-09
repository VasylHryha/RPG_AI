# Stage B host execution

Run from the repository with the pinned ML environment. These are development runs. Stage A remains unchanged. All training, DAgger, parity and outcome commands stop on identity/cap/process/RAM/disk refusal; inspect the invocation receipt before resuming the identical command. Do not rebuild or edit code between measurement, fitting and later gates. No epochs or windows are silently reduced.

Claude must be authenticated on the host. The local attempt returned “Not logged in”; Stage B TRAIN_CAP was therefore not fabricated. The first command has Claude author the already-approved 10800-second cap and preserves any subsequent owner reduction. Actual ten-epoch fits, DAgger rounds, and new looks have not run in this implementation session.

```sh
cd /Users/new/RiderProjects/ai_RPG_test
set -e
export STAGEB=evidence/tactical_composition_demo/astelia_cpp/s4_army_slice_v1/stageb
export STAGEB_PYTHON=evidence/tactical_composition_demo/astelia_cpp/s4_net_slice_v1/_local/mlenv/bin/python
export PYTHONPYCACHEPREFIX="$STAGEB/_local/pycache"
"$STAGEB_PYTHON" "$STAGEB/claude_train_cap.py"
"$STAGEB_PYTHON" "$STAGEB/train.py" measure --round 0
"$STAGEB_PYTHON" "$STAGEB/train.py" run --round 0
"$STAGEB_PYTHON" "$STAGEB/parity_run.py" --round 0
"$STAGEB_PYTHON" "$STAGEB/dagger.py" prepare --round 1
"$STAGEB_PYTHON" "$STAGEB/dagger.py" run --round 1
"$STAGEB_PYTHON" "$STAGEB/train.py" measure --round 1
"$STAGEB_PYTHON" "$STAGEB/train.py" run --round 1
"$STAGEB_PYTHON" "$STAGEB/parity_run.py" --round 1
"$STAGEB_PYTHON" "$STAGEB/readout_run.py" prepare --round 1
"$STAGEB_PYTHON" "$STAGEB/readout_run.py" run --round 1 --look 20
"$STAGEB_PYTHON" "$STAGEB/readout_run.py" run --round 1 --look 50
```

| Command | Time and evidence |
|---|---|
| Claude cap | Expected under 60 s; authenticated Claude required |
| Round 0 measurement | Expected 3–15 min; includes role target counting, full-prefix replay, windows, validation and provenance hashing |
| Round 0 fit | Historical four-lane projection about 2 h 50 min; new loss and all overhead must be measured; hard maximum 3 h per invocation |
| Each full validation parity | Expected 10–25 min; first four sequences establish measured remaining cost |
| DAgger preparation | Expected seconds, sealed fresh entropy; no fights |
| DAgger round | 88 full fights (22 per arm); expected 20–60 min initially, eight real full-fight samples determine admission under live LAB_CAP |
| Round 1 measurement/refit | Measurement expected 3–20 min; ten epochs on aggregate must project within 3 h, or the command refuses. Added data can exceed the cap; no promise that 3 h admits it |
| Look preparation | Expected seconds; seals 50 regular and 50 C3 seeds paired across six policies |
| Look 20 | 240 fights; expected 20–60 min, twelve actual full-fight samples govern admission |
| Look 50 | 360 additional fights after completed look 20; expected 30–90 min, measured admission governs |

Expected times above are planning estimates, not new production measurements. Exact build/test/diagnosis measurements are in BUILD_STAGEB.json, TESTS_STAGEB.json and STAGEB_DIAGNOSIS_COUNTS.json. Training, DAgger collection and outcome run invocations record refused/stopped/completed runs with unique receipts. Admitted parity invocations record their completion or stop; setup/precheck failures may exit before a parity receipt. Preparation/cap commands seal configuration, and measurement writes a budget when it reaches a projection verdict. Completed epochs/fights/parity sequences resume without rerunning successful work.

Default is one DAgger round. If round-1 residual target/movement disagreement warrants a second round within measured cost, insert this block before outcome preparation and use `--round 2` for outcome preparation and both looks:

```sh
"$STAGEB_PYTHON" "$STAGEB/dagger.py" prepare --round 2
"$STAGEB_PYTHON" "$STAGEB/dagger.py" run --round 2
"$STAGEB_PYTHON" "$STAGEB/train.py" measure --round 2
"$STAGEB_PYTHON" "$STAGEB/train.py" run --round 2
"$STAGEB_PYTHON" "$STAGEB/parity_run.py" --round 2
"$STAGEB_PYTHON" "$STAGEB/readout_run.py" prepare --round 2
"$STAGEB_PYTHON" "$STAGEB/readout_run.py" run --round 2 --look 20
"$STAGEB_PYTHON" "$STAGEB/readout_run.py" run --round 2 --look 50
```
