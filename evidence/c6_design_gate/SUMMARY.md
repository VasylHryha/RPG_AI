# C6 development design gate: summary (2026-10-02)

**NOT EVIDENCE.** This is development entropy 33333, under proposal §9 and amendments A1 and A2, which the owner
re-approved before this run. It is a design gate, not a registered panel, and no hypothesis verdict follows from it.

| Field | Value |
|---|---|
| Tool | `tools/c6_design_gate.py` at commit 50fb770 (Codex, reviewed by Claude), run unchanged |
| Engine | C++ build pinned to `Apple clang version 21.0.0 (clang-2100.3.34.2)` (build/c6/BUILD.json) |
| Run | Executed by the owner's Claude session on the owner's instruction; about 18 min on 8 processes |
| Raw record | `results.json.gz` (gzip -9, lossless) |
| SHA-256 of results.json.gz | `a6b6069bd4ebf3b6280ca0060f54a5ad2df4ef399194215996dd4f9f366cacdb` |
| SHA-256 of the uncompressed results.json | `02ea2b3e0b4d610131babe2d6f1d8205e54a1143bb5411bb82183b79baf0992b` (97 MB; not committed for size) |

## Outcome: STOP at stop rule 2 (after formation pass 1, before pass 2, as amendment A1 requires)

- **Equivalence check 4: passed.** 10 level-2 and 5 level-3 development worlds; native and NumPy outcomes and
  candidate sets were identical, with a maximum statistic difference of 0.0 and zero neighbour mismatches. Stop
  rule 14 was not triggered.
- **Formation pass 1, at provisional C₂ = 3.2 and C₃ = 9.6:**

  | Level | Formed | Outcomes | Candidate criteria failed |
  |---|---|---|---|
  | 2 | **18 of 30** | MERGED 7, DRIFTING 2, OTHER 3 | criterion 6: 7; criterion 5: 4; criterion 1: 2; criterion 4: 1 |
  | 3 | **0 of 30** | **MERGED 29**, DRIFTING 1 | criterion 6: 29; criterion 5: 16; criterion 4: 9; criterion 3: 5; criterion 1: 2 |

- **Isolated timescales from pass 1:** τ₁ had 81 measurements and τ₂ had 18, with none censored. **τ₃ had 0
  measurements**, because no level-3 group formed. C₃ is therefore undefined, stop rule 2 fires, and pass 2 and
  every later gate step were not run.

## Why the level-3 candidates fail criterion 6

This is a descriptive breakdown of the stored validity records, computed by Claude from results.json.

| What was checked | In the 30 level-3 worlds | Same check in the level-2 worlds |
|---|---|---|
| Level-2 parts overlapping **each other** (union of hulls > 0.2) | 7 of 150 parts (median 0.014) | n/a |
| Level-2 parts' own criteria 2–4 on own-level windows | failed in 4 of 150 | n/a |
| **Level-1 units inside the level-2 parts overlapping each other** (> 0.2) | **167 of 606 units (27.6%); present in all 30 worlds** | 11 of 150 (7.3%) |
| Level-1 units' own criteria 2–4 on own-level windows | failed in 27 of 606 | n/a |

The commonest single cause, in 17 of 30 worlds, was level-1 overlap alone.

**Reading:**
- The level-2 groups stay geometrically distinct from one another and mostly keep their own dynamics.
- What fails is one level lower: over the level-3 observation window (W = 30 C₃ = 288 time units, with geometry
  checked across all of it), the C4 units *inside* the level-2 groups interpenetrate far more often than over the
  level-2 window (96 time units).
- This development data cannot distinguish two causes: pressure from contact with other level-2 groups, or slow
  intrinsic fusion of level-2 groups over longer times. A test of the same templates alone over the same window
  would separate them.

## What this does not establish

These are development data, not a registered panel, so there is no H-C or H-M verdict. The proposal's
next-step options apply (§9): run the recorded panel anyway to record the negative, write a decision record, or
authorize a redesign in a new proposal. The owner decides.
