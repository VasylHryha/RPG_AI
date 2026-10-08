# NS1 pre-data batch collection tooling

Round-2 N1–N5 and the missing orchestrator are implemented. Read CONTRACT.md, DECISION_N1.md and REPORT_COLLECTION.md. Prior deliverable1b documents/receipts are preserved under frozen/deliverable1b_* and Claude round2 is copied under frozen. No fights, collection, training or ES run by the implementer. Fixture exports remain untrained.

Claude's execution commands, from repository root:

```sh
SLICE=evidence/tactical_composition_demo/astelia_cpp/s4_net_slice_v1
python3 "$SLICE/collection.py" sample --fights 20
python3 "$SLICE/collection.py" project
python3 "$SLICE/collection.py" collect --fights 200
```

The first sample command seals recorded entropy, all200 requests and whole-group splits before any run. One worker; sample draws already completed are reused by collect. The timing sample excludes independently allocated report draws. A12–20-fight sample is supported; sealed sample size cannot change. Caps include unsuccessful physical launches:20 sample and200 total. The local owner LAB_CAP.json in s4_shape_lab_v1/raw is read live as time authority. collect requires sample/project, enough disk/time/RSS headroom, repository process gate CLEAR and unchanged build/source/contract/request hashes. Foreign heavy processes are ignored with recorded reasons; unresolved ownership fails closed; vanished-process discovery retries once.

Raw files, inventory, ledger, process gate, measured SAMPLE.json and PROJECTION.json live under _local/collection. Complete receipts and data are immutable; partial attempts remain separate. Resuming uses the same command and sealed inventory, never fresh entropy. Do not edit receipts or seals to bypass drift. No dataset packer/trainer is delivered yet. Reporting splits must be excluded from all fitting/selection.

Build and focused verification are already performed for this delivery; results are in REPORT_COLLECTION.md. Rebuild only if sources drift, before a new seal. build.py pins frozen copies of documents, not living external files. Standalone arithmetic also accepts `project.py --mean-record-bytes VALUE --maximum-record-bytes VALUE`; these values must come from the actual-path sample. No measured size means SIZES_REQUIRED, not the1MiB storage estimate.
