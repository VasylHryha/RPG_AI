# GeoMind C0 execution receipt

Implementation: **REVIEW_READY**. Checks: **PASS**. Hypothesis: **NOT_TESTED** (independent interpretation pending).

Manifest: `abbb259819edfdda92089a33680d3170200844ee91084e51f4064f5e0a3bfa9f`. Complete machine-readable data: [results.json](results.json).

| Split/arm | Worlds | Query agreement | Nonconvergence |
|---|---:|---:|---:|
| test/lattice | 100 | 1.000000 | 0 |
| test/continuous | 100 | 1.000000 | 0 |
| test/disconnected | 100 | 1.000000 | 0 |
| test/inconsistent | 100 | 0.001094 | 0 |
| train/lattice | 100 | 1.000000 | 0 |
| train/continuous | 100 | 1.000000 | 0 |
| train/disconnected | 100 | 1.000000 | 0 |
| train/inconsistent | 100 | 0.001094 | 0 |
| validation/lattice | 50 | 1.000000 | 0 |
| validation/continuous | 50 | 1.000000 | 0 |
| validation/disconnected | 50 | 1.000000 | 0 |
| validation/inconsistent | 50 | 0.001875 | 0 |

Agreement against clean truth is not an acceptance gate for intentionally inconsistent worlds; those are checked against least squares and visible residuals.

Elapsed: 123.96s. All fitting, query, serialization and generation timings are retained per world. Direct-edge coverage is zero on the deliberately indirect query set.

No claim of superiority, recursive hierarchy, physical resonance or energy savings. Independent review and later milestones are NOT_RUN.

Next: Independent C0 review before C1.
