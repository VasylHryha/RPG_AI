# A0 host commands

Use the same checkout on the host with working `pgrep`, `lsof`, `ps` and `vm_stat`. The original sandbox delivery ran no fights. After the A0 transport fix, rebuild to refresh the admitted runner fingerprint, then explicitly recover the known pre-data tooling failure. Parent engine/adapters remain read-only.

```sh
cd /Users/new/RiderProjects/ai_RPG_test
.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_army_slice_v1/a0_build.py
.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_army_slice_v1/a0_run.py repair-tooling
.venv/bin/python -m pytest -q evidence/tactical_composition_demo/astelia_cpp/s4_army_slice_v1/test_a0.py evidence/tactical_composition_demo/astelia_cpp/s4_army_slice_v1/test_a0_host.py
caffeinate -i -s .venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_army_slice_v1/a0_run.py pilot
```

The original build was measured at 23.10 seconds here; allow about one minute on this host. Recovery should take seconds. It preserves the original declaration, ledger, sealed requests and all failed raw/attempt bytes. It permits only the known efcf591 runner repair, with identical native binary bytes and no valid prior fight data. For a fresh folder without failed evidence, use `a0_run.py prepare` instead of `repair-tooling`. The pilot is exactly eighteen fights, with separate entropy. Historical script timing suggests roughly ten minutes, but O's one-gun planner cost is unmeasured. The pilot result prints each panel's multi-gun share and projects both outcome looks. Those measured projections replace historical estimates.

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

Repeat the same pilot or run command after an ordinary cap interruption to reuse verified completions. Interrupted preparation also resumes its sealed entropy transaction. A changed code/binary/request identity blocks reuse outside the explicit pre-data tooling recovery. Retry raw files carry new attempt IDs; attempt receipts and the printed retry notice name the preserved prior attempt and cause. Unknown host failures require an explicit diagnosis before retry. A stopped scientific look cannot be crossed by repeating a command. All invocations have their own `A0_RUN_*.json`; raw streams, attempts, requests, entropy, process-gate receipts and the binary remain under gitignored `_local`.

The final decision uses deaths/fight and ratio-of-totals kills per own death, alongside damage, kills/minute and censored elimination time. It reports all twenty C3 cells. A parked leader does not prevent units-alone work when the unit decomposition passes. Training is a future stage and is not implemented or authorized by these commands.

The original seventeen synthetic tests missed the JSONL boundary. Focused verification now includes real native-host smoke tests for O, O+G and T, using sealed three-second copies of real pilot requests and the production launch, process discovery, RAM checks and metrics parser. Those copies do not become pilot/outcome completions. The command above runs both test files once; allow about a minute. If process discovery is unavailable in a sandbox, the integration tests fail closed before host launch; run that exact test command on the host. Validation of this fix is recorded separately in `A0FIX_VALIDATION.md`.

Each fight sends one compact UTF-8 JSON document plus one newline. The sealed file's bytes/hash stay unchanged. The wire format and hash are recorded in attempt/completion receipts. `--metrics` is deliberately absent: observer frames and the terminal summary are stdout regardless of that flag, which only adds stderr work counters. `a0_metrics.measure()` consumes stdout telemetry; any stderr is still a failure requiring review.
