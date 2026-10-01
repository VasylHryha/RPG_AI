# R005 fix verification with the independent reviewer's probes

These are copies of the reviewer's scripts from `../c1_r004_independent/`, unchanged. They ran against the R005 candidate, and each script wrote its output next to itself in this directory. The reviewer's original outputs are untouched.

After these probes ran, `geomind/incremental.py` changed only in its module docstring (the energy-bound sentence), so the probed behavior is the committed R005 behavior.

| Finding | Probe | R004 (reviewer) | R005 (this folder) |
|---|---|---|---|
| F2(a): translated near-tolerance node not certified | `probe_certificate.py`, P2 shift 1e5 | PASS, then reload **REJECTED** | PASS, reload OK, `r` certified |
| F2(b): re-anchoring re-gauges the export | `probe_regauge_and_random.py`, P4 (4 cases) | 2 of 4 reloads **REJECTED** | 4/4 reload OK, `r` certified, 7 nodes re-stored |
| F2(c): rounding at coordinate scale 1e3–1e6 | `probe_regauge_and_random.py 300 3,6`, P5 | 1,324 PASS, **11 RELOAD_REJECTED** | 1,338 PASS, **0** rejected; 0 errors above 1e-5 |
| F3: degree overflow | `probe_certificate.py`, P3 | PASS, then reload rejected | **INVALID_STATE**, as C0 `learn` |
| F1: uncharged Θ(R) relation-map copy | `probe_hidden_work.py` | apply 66 → 2,644 µs from 32 to 32,768 nodes | apply 133 → 184 µs, flat (validation 19 → 76 µs) |

**P1** (large bridge shifts) commits and reloads at shifts up to 1e8. At 1e9 and 1e10 it refuses explicitly, and the accepted C0 learner refuses those too.

**P5's maximum displacement error** against dense LS is 7.05e-6 at these coordinate scales, compared with 2.25e-7 in the reviewer's R004 run. It is within the 1e-5 tolerance; the probe counts `ERROR_GT_1e-5`, and that count is zero.

A separate check on 438 R005 commits at the same scales found a maximum error of 3.1e-8. Every placement, relaxation and fallback commit there was below 1e-6. The larger value depends on the probe's chain construction and is consistent with the convergence-tolerance bound: forces below 1e-8 on chains with weights down to 0.25.

Commands, run from the repository root:

```text
.venv/bin/python evidence/c1_r005_fix_checks/probe_certificate.py
.venv/bin/python evidence/c1_r005_fix_checks/probe_regauge_and_random.py 300 3,6
.venv/bin/python evidence/c1_r005_fix_checks/probe_hidden_work.py
```
