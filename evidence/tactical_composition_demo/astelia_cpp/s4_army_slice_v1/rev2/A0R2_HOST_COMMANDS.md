# A0 rev-2 host handoff

Current checkout: isolated build completed in 21.32 seconds, same-state proof passed, 20 focused tests passed. Fresh entropy and 618 requests are already sealed. All three real-host integration cases were attempted once and stopped before launch at process discovery (`pgrep` exit 3 / sysmond unavailable). No fights or pilot/outcome invocations ran. Do not repeat passing focused tests for unchanged code.

Run on the same checkout on the actual host, with working `pgrep`, `lsof`, `ps` and `vm_stat`. These commands use only rev 2; the original look remains evidence. Approximate times below use rev-1's measured full-150-second equivalents (O 4.19 s, O+G 4.10 s, T 6.34 s) and rev-2's all-arm teacher-history cost. No rev-2 fight time has been measured.

```sh
cd /Users/new/RiderProjects/ai_RPG_test
a0r2_dir=evidence/tactical_composition_demo/astelia_cpp/s4_army_slice_v1/rev2
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q --confcutdir="$a0r2_dir" --basetemp="$a0r2_dir/_local/host_test_tmp" "$a0r2_dir/test_a0r2_host.py"
.venv/bin/python "$a0r2_dir/a0_run.py" prepare
caffeinate -i -s .venv/bin/python "$a0r2_dir/a0_run.py" pilot
```

Host integration: allow 5–20 seconds for three separate three-second native fixture requests; these validate transport/metrics/resource admission and do not count as pilot/outcome completions. `prepare`: about 1–3 seconds, idempotent verification of the already sealed entropy. Pilot: provisional 2–3 minutes for eighteen fights, serial. Read its mechanism result and projections before proceeding. A host integration failure must be diagnosed before any pilot; a gate or RAM refusal is preserved and must not be bypassed.

After the pilot passes and its measured projection is within the live owner cap:

```sh
caffeinate -i -s .venv/bin/python "$a0r2_dir/a0_run.py" run --look 50
.venv/bin/python "$a0r2_dir/a0_run.py" report --look 50
```

Look 50: provisional 35–50 minutes for 300 fights; the fresh pilot's measured projection is authoritative, including its 20% margin. Report: allow about 30–90 seconds for raw validation. The live owner wall cap is read without a living-doc pin. All original harm/decomposition/coverage/continuation rules remain in force. Read the new `A0_LOOK_50.json`; no training or automatic look-100 execution follows this handoff.

If local build/proof artifacts are missing after copying the checkout, reconstruct them before the commands above:

```sh
.venv/bin/python "$a0r2_dir/a0_build.py"
.venv/bin/python "$a0r2_dir/a0_equivalence.py"
```

Allow 30–60 seconds for build and 10–20 seconds for the state-only proof (the measured proof here was 13.44 seconds; see its receipt). Preserve `_local/PREPARATION.json`, `_local/A0_LEDGER.json` and requests if transferring this prepared revision. A changed source/binary identity refuses reuse; never delete seals to force a new run under an existing declaration. The build/proof commands run no fights.
