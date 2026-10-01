# GeoMind C0 review verification

Implementation: **REVIEW_READY**. Checks: **PASS**. Hypothesis adjudication: **NOT_TESTED**.

[Machine-readable receipt](results.json); [streamed individual worlds](instances.jsonl); [actual contract test report](contracts.xml).

Experiment: `geomind-c0-r4-003`. Manifest: `3372cbc15b65728180606d94d8380d14a334bdb4fb3a2c280d53fb482d28a249`.

| Split/arm | Worlds | Endpoint | Agreement | Unresolved/invalid |
|---|---:|---|---:|---:|
| test/lattice | 100 | clean agreement | 1.000000 | 0 |
| test/continuous | 100 | clean agreement | 1.000000 | 0 |
| test/disconnected | 100 | clean agreement | 1.000000 | 0 |
| test/inconsistent | 100 | least-squares agreement | 1.000000 | 0 |
| test/noisy | 100 | least-squares agreement | 1.000000 | 0 |
| train/lattice | 100 | clean agreement | 1.000000 | 0 |
| train/continuous | 100 | clean agreement | 1.000000 | 0 |
| train/disconnected | 100 | clean agreement | 1.000000 | 0 |
| train/inconsistent | 100 | least-squares agreement | 1.000000 | 0 |
| train/noisy | 100 | least-squares agreement | 1.000000 | 0 |
| validation/lattice | 50 | clean agreement | 1.000000 | 0 |
| validation/continuous | 50 | clean agreement | 1.000000 | 0 |
| validation/disconnected | 50 | clean agreement | 1.000000 | 0 |
| validation/inconsistent | 50 | least-squares agreement | 1.000000 | 0 |
| validation/noisy | 50 | least-squares agreement | 1.000000 | 0 |

Elapsed: 331.50s. No settings selected from these final worlds. Baseline coverage, conditional/total accuracy, independent residuals and paired cost differences are retained.

Noisy/inconsistent arms use least-squares agreement as their endpoint; exact truth is also reported separately. Direct-only lookup has zero coverage on indirect queries and is separately measured on exposed pairs.

Initial experiment and failed checks remain historical evidence. No hierarchy, resonance or energy result is implied.

Next: Independent acceptance of reviewed C0 before C1.
