# A0 host commands

Use the same checkout on the host with working `pgrep`, `lsof`, `ps` and `vm_stat`. The sandbox delivery ran no fights. The host is already built locally; rebuild only if its admitted inputs changed. Parent engine/adapters remain read-only.

```sh
cd /Users/new/RiderProjects/ai_RPG_test
.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_army_slice_v1/a0_build.py
.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_army_slice_v1/a0_run.py prepare
caffeinate -i -s .venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_army_slice_v1/a0_run.py pilot
```

Build was measured at 23.10 seconds here; allow about one minute on this host. Preparation should take seconds to a minute. The pilot is exactly eighteen fights, with separate entropy. Historical script timing suggests roughly ten minutes, but O's one-gun planner cost is unmeasured. The pilot result prints each panel's multi-gun share and projects both outcome looks. Those measured projections replace historical estimates.

Read the pilot's mechanism report and projection before proceeding. The runner refuses a panel whose measured remaining projection exceeds the current owner cap. It reads `s4_shape_lab_v1/raw/LAB_CAP.json`; it does not enlarge that setting. A process-discovery or live-RAM refusal also stops before a fight and leaves a per-run receipt.

```sh
caffeinate -i -s .venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_army_slice_v1/a0_run.py run --look 50
.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_army_slice_v1/a0_run.py report --look 50
```

The 50-pair look runs 300 fights total: three arms × two panels × fifty pairs. A serial historical estimate is 1.5–2.5 hours before safety margin; the pilot projection is authoritative for admission. Reporting takes seconds to a few minutes to verify compressed raw files. Read `A0_LOOK_50.json`'s unit and leader decisions. Harm, inadequate multi-gun coverage or a harmful O−T decomposition blocks the next look.

```sh
caffeinate -i -s .venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_army_slice_v1/a0_run.py run --look 100
.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_army_slice_v1/a0_run.py report --look 100
```

The 100-pair look reuses the first fifty and adds 300 fights. Historical total time for all 600 outcome fights is about 3–5 hours serial, spread across the two gated invocations. The current 10,800-second cap applies to each invocation; a pessimistic measured projection may refuse it. Report the measured time to the owner in that case. No automatic cap increase or extra seeds are provided.

Repeat the same pilot or run command after an ordinary cap interruption to reuse verified completions. Interrupted preparation also resumes its sealed entropy transaction. A changed code/binary/request identity blocks reuse: retain that evidence and revise prospectively. A stopped scientific look cannot be crossed by repeating a command. All invocations have their own `A0_RUN_*.json`; raw streams, attempts, requests, entropy, process-gate receipts and the binary remain under gitignored `_local`.

The final decision uses deaths/fight and ratio-of-totals kills per own death, alongside damage, kills/minute and censored elimination time. It reports all twenty C3 cells. A parked leader does not prevent units-alone work when the unit decomposition passes. Training is a future stage and is not implemented or authorized by these commands.

Focused verification already passed: seventeen synthetic tests in 2.46 seconds, including native prepared-event routing, one-gun parity, illegal-aim fallback, precedence, entropy recovery, pairing, censoring, owner caps and resume integrity. Tests ran once after the complete review-fix batch. They ran no fights.
