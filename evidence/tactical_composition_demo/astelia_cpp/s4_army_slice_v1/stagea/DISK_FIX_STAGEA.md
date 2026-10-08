# Stage A disk projection and source revision

Decision 0036 development fix. The collection estimate now uses measured maximum compressed bytes per simulated second and the nearest-rank p99 elimination-time bound from all 600 A0 rev2 look-100 fights. Every censor counts as 150 seconds, including fights that ended earlier through the other army's elimination. Receipt hashes, exact jobs and the A0 ledger identity are checked. The bound is an empirical storage estimate, not a guarantee on unseen fights; previously measured files are never projected below their actual byte count.

There are eight censored fights in the 600-fight distribution. Both p99 and maximum are 150 seconds. Thus this evidence does not support using a shorter duration to pass the old target. The six existing sealed collection completions project approximately 4.232 decimal GB. Recovery retains the original 4 GB target when its compatible measurements fit; here it prospectively declares 5 decimal GB and records the numerical cause. A projection exceeding the revised target still stops. The worst-case 150-second projection remains an explicit diagnostic. The free-space gate remains exactly the previous worst-case measured bytes/fight × remaining × 2 + 5 decimal GB. Its initial reserve remains 13 GB.

The recover-disk command registers a new collection ledger and revises the build manifest's Python source pins without rebuilding or changing the native binary. Only the authorized gating/recovery module and its new policy/tests can change. All native, recording, model, adapter, process-gate and other source hashes must still match. All sealed requests must retain their hashes. Both repository locks protect registration. Pending/active markers are atomically published, and an interruption resumes the exact registered transaction. The original manifest, old ledgers, failure receipts, raw recordings and original completion receipts remain preserved and hash-bound. No living documentation is pinned.

Completed collection fights with identical admitted binary, request/job, compact recording, physical dt and cadence are individually logged for reuse. A different request/job or recording identity is individually logged for resampling at a separate completion destination; old receipts/raw files remain intact. Sealed request drift, binary drift and corrupted artifacts stop recovery. Fixtures are excluded from calibration and the dataset. Reused raw files still undergo the normal validation on sample/run; recovery does not fabricate new completion receipts.

If no compatible old calibration survives, this revision retains 4 GB until fresh samples are available. A fresh projection above 4 GB stops and needs a separate explicit target revision. This preserves the target gate rather than silently increasing an unmeasured budget. That edge does not apply to the supplied host: all six completed collection samples are compatible.

The first recovery attempt stopped before registration because the A0 completion schema has no status field. The correction uses membership and hash in the completed look-100 receipt with exact job/ledger identity. The failed attempt is preserved, and the separate reviewer rechecked the correction before the focused test batch. No collection or training fight was started by the fix workflow.

Production continuation uses existing live LAB_CAP/TRAIN_CAP authority. Planning estimates: remaining timing sample 2–6 minutes, collection 25–75 minutes, audit 15–60 minutes, training measurement 5–20 minutes. Fit/parity/readout calculate their own projections and enforce their caps. A refusal stops the chain; preserve it and resume the failed command after resolving its cause. Passed tests are not repeated. The mechanism-only 20-pair and gated 50/100 looks retain their existing meaning and harm stops. No scientific result acceptance is implied.

Use the following chain from the repository root. Recovery is idempotent after successful local registration. Identity admission must follow recovery because the previous manifest pins the prior Python sources.

```sh
cd /Users/new/RiderProjects/ai_RPG_test
set -e
export STAGEA=evidence/tactical_composition_demo/astelia_cpp/s4_army_slice_v1/stagea
export STAGEA_PYTHON=evidence/tactical_composition_demo/astelia_cpp/s4_net_slice_v1/_local/mlenv/bin/python
export PYTHONPYCACHEPREFIX="$STAGEA/_local/pycache"
unset STAGEA_HOST_TEST
"$STAGEA_PYTHON" "$STAGEA/collect.py" recover-disk
"$STAGEA_PYTHON" -c 'import sys; from pathlib import Path; sys.path.insert(0, str(Path(sys.argv[1]).resolve())); from collect import identity; print(identity()["binary_sha256"])' "$STAGEA"
"$STAGEA_PYTHON" "$STAGEA/collect.py" sample
"$STAGEA_PYTHON" "$STAGEA/collect.py" run
"$STAGEA_PYTHON" "$STAGEA/collect.py" audit
"$STAGEA_PYTHON" "$STAGEA/train.py" measure --epochs 2 --windows 4
"$STAGEA_PYTHON" "$STAGEA/train.py" run
"$STAGEA_PYTHON" "$STAGEA/parity.py"
"$STAGEA_PYTHON" "$STAGEA/readout.py" prepare
"$STAGEA_PYTHON" "$STAGEA/readout.py" run --look 20
"$STAGEA_PYTHON" "$STAGEA/readout.py" run --look 50
"$STAGEA_PYTHON" "$STAGEA/readout.py" run --look 100
```

Final validation: 40 focused tests passed in 40.46 seconds (41.14 seconds measured wall), including real-binary fixtures in test mode. The first attempt stopped after 25 passing tests on a new floating-expression assertion; its source and evidence are preserved. The corrected test and review-driven revision handling were completed before the final batch. The new source revision is logged, preserving all earlier ledger identities and original completion provenance. No passed suite was repeated.

The production gate was checked using the six existing sealed samples: 4.231704 GB projected against the declared 5 GB target; 174 remaining fights require 13.181294 GB under the unchanged formula, with 17.140494 GB actually free. Six samples are registered for reuse, zero for resampling. The native binary and 290 inventoried earlier artifacts are unchanged. The explicitly revised build manifest has an exact preserved original. No production sample/collection, training, parity or readout command ran during this fix. The host chain above is the continuation.
