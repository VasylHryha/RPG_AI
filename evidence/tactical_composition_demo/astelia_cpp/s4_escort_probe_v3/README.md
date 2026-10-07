Prepared scripted development probe for DESIGN_0G §19.11 at a9dfc6f. P12 uses the exact original v1 controller; P16 changes gun ordering by static splash value; P17 adds melee escort movement. Policy/declaration seal the clarifications before combat. Codex runs build and focused non-combat checks only.

Claude: from the repository root, run these four commands in order without edits:

```sh
.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_escort_probe_v3/engineering.py
.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_escort_probe_v3/run.py
.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_escort_probe_v3/analyze.py
.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_escort_probe_v3/render.py
```

Engineering compares original v1 P12 and v3 P12 for regular/novice, two seconds each, on separate fresh engineering entropy. It strips ONLY output-only escort audit rows; all other output bytes and contracts must match. The run completes/reports all40 fresh P12 fights before P16 then P17. Every missing combat block checks mandatory pgrep with its own gate receipt; active0h batches wait/recheck30s. Unavailable/error process listing stops before any entropy claim. Verified completions are skipped; ambiguous claim/request/raw without completion stops all new fights and is never replayed/deleted. Resume with the same four scripts. The launcher supplies caffeinate automatically.

Caps: cumulative compute3600s, engineering1200s, all panel blocks combined1200s, analysis1200s, checks600s; at most two workers with owned process-group deadlines. Gate waiting is outside compute stages. Projected time includes600s analysis reserve. No rule/source/seed edits during a run.

See BUILD.json, CHECKS.json, VALIDATION.json and OWNER_RECHECK.md for engineering preparation. Native binary: ../build/astelia_native_escort_probe_v3, admitted against its current source manifest. Raw, scratch, delivery object stores and bundle are locally ignored. DELIVERY_TRANSPORT.json records the normal-hook commit or verified current-HEAD bundle; no push.

Combat/report review remains Claude's task. This is development evidence, not scientific acceptance or v7 permission. DESIGN_0G and PLAN_CURRENT are excluded from edits.
