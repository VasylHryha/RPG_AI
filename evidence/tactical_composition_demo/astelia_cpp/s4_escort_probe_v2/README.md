Prepared scripted development probe, DESIGN_0G §19.10. P12 exact original baseline; P14 target priority only; P15 ranged goal spacing only. Policy and declaration define every boundary and measurement. No combat executed by Codex.

Claude: from repository root run these four commands in order, without edits:

```sh
.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_escort_probe_v2/engineering.py
.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_escort_probe_v2/run.py
.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_escort_probe_v2/analyze.py
.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_escort_probe_v2/render.py
```

Engineering checks byte parity of original and new native P12 for both heads on the separate engineering seed. Run completes/reports P12 before P14/P15. Each missing combat block checks the mandatory process gate; active 0h batches wait with 30-second polls. Process-list errors stop before entropy claims. Verified completions are skipped. Any ambiguous claim/request/raw lacking completion stops all new work; preserve it and never replay/delete. Resume with the same four commands.

Compute caps: overall 3600 s, engineering 1200 s, panel combined 1200 s, analysis 1200 s, checks 600 s; at most two workers. Gate waiting is outside compute stages. All original inputs and this probe's sealed source/binary identities must remain unchanged. If interrupted, run render.py for a partial report; it never produces outcome readings without full analysis.

Read BUILD.json, CHECKS.json, VALIDATION.json and OWNER_RECHECK.md for precombat preparation. Raw fight data, test scratch, compiled artifacts and verified transport bundle remain local/gitignored. A bundle delivery includes DELIVERY_TRANSPORT.json with base/commit/bundle identities and independently fetched blob verification. The local admitted binary is under ../build/astelia_native_escort_probe_v2; it is intentionally not a committed binary artifact.

The final combat report belongs in S4_ESCORT_PROBE.md and COMPACT.json/SUMMARY.json. Claude must review execution/results afterwards. Descriptive development only: no judging, scientific acceptance, status changes, v7 permission or resonator claim. PLAN_CURRENT and DESIGN_0G remain excluded.
