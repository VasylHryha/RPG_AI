# C6 R3 development gate: STOP

Development-only receipt; no final seeds, hypothesis verdict or independent acceptance.
The complete implementation at `560ecdb` passed all 418 everyday tests before this single run.
All ten fixed worlds ran once, using eight workers, in 25.047 seconds.

- Qualified initial sources: **0/10**, below the fixed **5/10** development quorum.
- Matched sham preservation and NO-R controls: **PASS** in all ten worlds.
- Numerical checks: **9/10 worlds PASS**; world 4 initial-state dt=.02 versus dt=.005 error was **0.0742828780**, above **0.05**. Its dt=.01 error was 0.0540767467.
- Native versus independent NumPy reference: maximum error 3.5527136788005009e-15.
- Source-attributed candidates failed formation/recovery criteria. Mixed bath/source candidates remain diagnostic, without post-hoc relabeling.
- Second-turn workload never reached. Full panel cost remains **unknown**.
- Final registration, smoke/mutation pipeline and panel: **NOT_RUN**.

| World | Qualified source | Sham/control checks | Initial dt error | Formation-snapshot dt error |
|---|---|---|---|---|
| 0 | No | PASS | 0.008855233 | 0.011217608 |
| 1 | No | PASS | 0.023336584 | 0.025313610 |
| 2 | No | PASS | 0.022529311 | 0.001894166 |
| 3 | No | PASS | 0.025312293 | 0.002429425 |
| 4 | No | PASS | 0.074282878 | 0.001905297 |
| 5 | No | PASS | 0.009093404 | 0.003811265 |
| 6 | No | PASS | 0.010396575 | 0.003369243 |
| 7 | No | PASS | 0.038584740 | 0.003136973 |
| 8 | No | PASS | 0.015255465 | 0.003135130 |
| 9 | No | PASS | 0.006399364 | 0.004540473 |

Receipt SHA256: `25e69d80ef36d12271badd2359bc1bed0e71f1e9acc02bd77a3202b194603b54`.
Both compressed and raw hashes of every world record verified after the run.
Implementation/proposal/protocol and source pin match their pre-run identities.

Decision [0015](../../docs/decisions/0015-c6-r3-development-stop.md) preserves this STOP.
The recorded protocol is not retuned or rerun. Any changed formation attribution,
coupling, numerical procedure or fixture requires a new prospective revision.
Arm A retains its separate R2 STOP.
