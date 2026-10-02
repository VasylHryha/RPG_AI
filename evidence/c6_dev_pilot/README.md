# C6 development pilot (2026-10-02): NOT EVIDENCE

| Field | Value |
|---|---|
| Status | Development record only. Not registered, not a panel, not a verdict. |
| Requested by | The owner, during review of `experiments/c6_proposal.md`, before approval |
| Run by | Claude (claude-opus-5-5), the proposal's drafter |
| Code | Scratch scripts in this folder. They import the frozen C4/C5 functions; no `geomind/` file was changed. |
| Entropy | Pilot entropy 44444. It is not C5's development entropy (22222) or C6's (33333). No C6 final entropy exists. |
| Used by | `experiments/c6_proposal.md` §3b (results) and §10 (measured costs) |

## Known defect: the level-3 formation result is void

`c6_pilot.py` judged each part's criteria 2–4 over the **parent's** window, about 10× a level-1 unit's own window at level 3. That mixes levels and violates R4 invariant 1. The owner identified the defect.

As a result, the 0/24 level-3 formation recorded in both result files is **void**. The corrected rule judges every part on consecutive windows of its own level's length (proposal §4).

These results remain valid:
- the level-2 harvest outcomes (C5 rules, unchanged);
- the coupling and placement observations;
- the measured costs.

## Files

| File | What it is |
|---|---|
| `c6_pilot.py` | The pilot, **final version**. It covers the level-1/2 harvest with C5's frozen functions and level-3 assembly, formation and detection. Placement modes: sequential disk placement (spacing factor > 0) or contact placement (spacing factor 0). The defective criterion 6 is in `_level3`. |
| `run_pilot.sh` | The command that produced the two result files: 24 level-3 worlds, 320 level-2 worlds, provisional C₃ = 9.6; contact placement, then disk placement at spacing factor 1.0. Both share one harvest, cached in a 1.1 MB pickle that is not kept here; the script regenerates it deterministically. |
| `pilot_contact.json`, `pilot_contact.log` | Contact placement: summary, per-world level-2 outcomes, per-world level-3 candidates and part validity, and per-group harvest values. |
| `pilot_disk1.json`, `pilot_disk1.log` | The same for disk placement (sequential, radius 2.5 × median L₂ / median L₁). |
| `smoke.json` | Code-path smoke from an **earlier version** of the script (joint rejection placement, C₃ = 1.0). Not comparable. |
| `smoke2.json` | Code-path smoke: sequential disk placement at spacing factor 0.6. Every level-3 world failed placement ("no placement"). Joint rejection at 0.3 and 0.6 failed the same way (not saved). |
| `smoke3.json` | Code-path smoke: contact placement at C₃ = 1.0 (short times). Exercised the candidate, recovery and criterion-6 paths. Outcomes not meaningful. |
| `diag.py` | A planned diagnostic of which level-1 criterion fails over long windows. **Never completed:** the first run crashed (missing main guard), and the owner stopped the second, because reasoning from the rule identifies the cause. |
| `c6_coarse_pilot.py` | A planned coarse-readiness check (port variants V1/V2/ALL, per-excitation scoring, channel-matched τ). **Never run.** Kept because the proposal's design gate specifies the same check. |

## Key numbers (from the result files)

**Level 1 → 2 (C5 rules):**
- 2,400 C4 worlds gave 2,669 templates.
- 320 level-2 worlds gave FORMED 148, MERGED 52, DRIFTING 97, APART 4 and OTHER 19.
- 140 of 148 accepted groups were re-accepted alone.

**Level 2 → 3, 24 worlds per placement:**

| Placement | Outcomes | Candidates failing criterion 6 | Candidates failing criterion 5 |
|---|---|---|---|
| Contact | MERGED 22, DRIFTING 2 | 22 of 22 | 13 of 22 |
| Disk | MERGED 14, DRIFTING 9, OTHER 1 | 14 of 15 | 3 of 15 |

**Cost:** formation plus detection took 66–249 s per level-3 world, on one process with 8 running in parallel.

## SHA256 (as committed)

```
4b15bc6d4ddafb9019b925b7c456575e95c8bae89f4e2bb1cd1e7ccfae104f2d  c6_pilot.py
c1f892bd8f61e0d51128c911dd56863004dd88f3b025fadf03911f128e28da88  c6_coarse_pilot.py
33c040aca273c85ac38eee59d58a9a2f090d93ac819afb38a1d93ab8aa411be0  diag.py
e570b8b062cc8bb2dc9f9f886edda08f4ef251a5a98256c5625adf137f32eef3  run_pilot.sh
2ce8091f1066b0de0dbed67b64418954c4b87ae9c100bf08ecb7fbc1e3896dd6  pilot_contact.json
7ebe6cd7c09a11e50c667d8b589301fa025107ec0cc281e2263fb58b450b6a07  pilot_contact.log
573b6931afaa7591d51ccb0916dc38de449587a7112f813368aef1fd235dac72  pilot_disk1.json
394e426cf5be83f970181db1f6f875f42a7b4c391a4613597637444792122228  pilot_disk1.log
62a2256d84f56ff6da2734b9b94342a0ed1595bcc857ab15d53fb1c42950d37a  smoke.json
86bbf4549038369cd32033370d1ce637617f3a4385c8788a4f5f41a70eb192bf  smoke2.json
f45dfb25404de93691f41507a2d497040f255574ce4a2ba56ca6d7ae85fd679e  smoke3.json
```

The scripts expect the repository at `/Users/new/RiderProjects/ai_RPG_test` (hard-coded `ROOT`) and write their outputs to the working directory. They are a record of what ran, not maintained code.
