# NS1 deliverable 1b

Read CONTRACT.md and REPORT.md. This is the corrected pre-data slice; frozen/deliverable1_* retains D1 history and frozen/network_slice_d1_recheck_claude.md is the review input. OWNER_RECHECK_D1B.md records the separate same-family source check and fix dispositions. PLAN_CURRENT_APPEND.md is unchanged for Claude; docs/PLAN_CURRENT.md is untouched.

No fights, teacher collection, training, optimizer fitting or ES evaluation ran. Fixtures contain isolated seams and ten bounded scripted60-tick coreStep scenarios, with no fight outcome reads. Exports remain untrained fixture weights. The next execution gate is cross-family re-review plus a sealed collection/resource/timing inventory.

Rebuild and focused verification (already performed for this delivery; do not routinely repeat):

```sh
SLICE=evidence/tactical_composition_demo/astelia_cpp/s4_net_slice_v1
python3 "$SLICE/build.py"
"$SLICE/_local/mlenv/bin/python" "$SLICE/verify_focused.py"
python3 "$SLICE/project.py" --output "$SLICE/TEACHER_DATA_PROJECTION.json"
```

The isolated environment is described in ENVIRONMENT.json and requirements.lock; setup_env.py recreates it with the pinned offline distributions or online package sources. Ancestor sources/objects are read-only; generated overlays and binaries stay under _local/build. BUILD.json pins slice source and frozen document bytes, not living external documents. Historical build/test attempts are retained separately.

After Claude re-review and the authorized collection executor supplies a fresh sealed SEED/FIGHT/CELL/GUNS/ORIENTATION (reporting identities excluded), the exact one-request teacher collection commands are:

```sh
SLICE=evidence/tactical_composition_demo/astelia_cpp/s4_net_slice_v1
: "${SEED:?sealed collection seed required}" "${FIGHT:?sealed collection fight ID required}" "${CELL:?D1-static or D2-shellfire required}" "${GUNS:?1, 2 or 10 required}" "${ORIENTATION:?0 or 1 required}"
"$SLICE/_local/mlenv/bin/python" "$SLICE/requests.py" --cell "$CELL" --guns "$GUNS" --seed "$SEED" --fight "$FIGHT" --orientation "$ORIENTATION" > "$SLICE/_local/teacher_request.json"
"$SLICE/_local/build/net_host" --collect < "$SLICE/_local/teacher_request.json" > "$SLICE/_local/teacher_${FIGHT}.jsonl"
```

Use the separately approved <=20-fight actual-path timing sample first, measure terminal maximum_record_bytes/RSS/CPU/wall/disk, and revise the symbolic projection before full collection. This delivery allocates no entropy and does not supply a split/collection executor, trainer or approved runtime budget. The raised1MiB worst-case raw reserve is substantial; projection is a bound, not measured disk use. Never reuse fixtures or reporting data as training collection.
