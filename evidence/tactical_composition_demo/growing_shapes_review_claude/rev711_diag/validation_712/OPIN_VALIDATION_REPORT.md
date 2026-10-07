VALIDATED AS AN IMPROVEMENT, WITH LIMITS: the root-relative O pin (C2) raises the F5 gate-shape pass rate from 3/10 to 8/10 across five seed sets; its direction matters; F5 outcomes are seed-fragile, so a single-key F5 gate is not reliable

# The root-relative output pin (revision 7.12, C2): tests, mechanism and research

**Date:** 2026-10-07. **Author:** Claude (claude-opus-5-5).
**Why this exists:** the owner, on the proposed pin change, said: "it can not be decision — we should confirm it with tests and explain it etc... maybe do research".
**Status:** pilot evidence only. No verdict, no fixture result.
- **Pinned identity:** every pilot ran in a git worktree at `fd21826`, the reviewed 7.11 identity (pin `e66c8969…e357`), with the unchanged untracked builds copied in. The design file there predates section 19.
- **Instrumentation:** `pilot_common.py`, a live-only class-level recorder, plus:
  - a clone-isolation check;
  - an exact count of 160 steps per training episode;
  - the F5 A/B/E estimator with Harness.F5's guard of 160 decisions per stream.
- **The estimator reproduces the 7.11 fixture exactly** with the unchanged law.

## 1. What was tested

- **Seed robustness:** five key sets per start.
  - Key set 0 = the F5 fixture keys and worlds.
  - Key sets 1–4 = alternative keys (`/altK` suffix) and training worlds 13,000,000 + 100,000·k, a range no registered fixture or development schedule uses.
  - Each key set was run under the **origin pin** (7.11 law, the control) and under **C2** (O at 1.0 toward the lowest-id effective root).
- **Distance sensitivity** (fixture keys, empty start): 0.5 and 1.5, besides 1.0.
- **Direction controls** (key sets 0–2, both starts): O at the same 1.0 distance, but **opposite** to the first root (rotated 180°) or **perpendicular** (+90°).
- **Gate shape:** A ≥ 0.3, B ≥ 0.3 and max E ≥ 0.5, as in F5, but per single run and descriptive.
- All rows are in `SUMMARY.md`, with logs `batt*.log` and `../assay_pilot_*.log`.

## 2. Results

| Rule | Empty start (i) | Seeded start (ii) | Both starts |
|---|---|---|---|
| **Origin pin (7.11)** | 2/5 | 1/5 | **3/10** |
| **C2: toward the first root, 1.0** | **5/5** | 3/5 | **8/10** |
| C2 direction **opposite**, 1.0 (key sets 0–2) | 2/3 | 1/3 | 3/6 |
| C2 direction **perpendicular**, 1.0 (key sets 0–2) | 2/3 | 1/3 | 3/6 |
| Origin pin, key sets 0–2 only (the same seeds as the direction controls) | 2/3 | 1/3 | 3/6 |
| C2 toward the root, key sets 0–2 only | 3/3 | 2/3 | 5/6 |
| C2 toward the root, distance 0.5 (i, key set 0) | 0/1 | — | — |
| C2 toward the root, distance 1.5 (i, key set 0) | 1/1 | — | — |

**Reading:**
1. **C2 is a real improvement in these pilots:** 8/10 against 3/10 for the origin pin, on the same keys.
   - It passes the empty start in all five key sets.
   - The seeded start stays fragile: 3/5, with one narrow miss at max E 0.47.
2. **The direction matters.** At the same distance, O placed opposite or perpendicular to the first root passes no more often than the origin pin (3/6 each, against 5/6 toward the root, on the same seeds). Merely moving O off-centre does not help; moving it **toward where the medium's first root is** does.
3. **The distance matters.** 0.5 failed and 1.5 passed, on one key set. The threshold lies between 0.5 and 1.0 for that key. This is a single-key observation.
4. **F5 outcomes are seed-fragile.** The origin pin's empty start passes 2/5, and its seeded start passes only 1/5.
   - So the 7.11 fixture's "(ii) passes, (i) fails" was largely the luck of one key.
   - **A single-key F5 gate is not a reliable test of growth.** That finding matters for any revision, with or without C2.

## 3. Mechanism (diagnosis §2 plus the research memo `../OPIN_RESEARCH_MEMO.md`)

- **The law is the swarmalator kernel** (O'Keeffe, Hong and Strogatz 2017), made local by the 8-nearest-neighbour rule. The literature finds **compact in-phase discs, not chains**, with all-pairs and with finite-range coupling (memo §1). Our diagnosis measured the same: the cohesive, constant-magnitude pull retracts a lone bridge tip at 0.3–0.6 m.u./s.
- **So a grown cluster's face settles about 1.5–2.4 m.u. from a centred O.**
- **Moving O 1.0 m.u. toward the first root brings O within the strong-edge range (about 1.44 at degree 8) of where that cluster's face comes to rest.**
  - The link then sits on the cluster's resting face, not on a filament.
  - **This is a placement effect, not a new bridging capability** (the memo's inference, supported by our evidence):
    - the direction controls (toward the root works, other directions do not);
    - the distance threshold;
    - the final nearest-element distances to O (0.34–0.6 m.u. in passing C2 runs).
- **The empty-start failure is therefore a geometric limit of this element law:** it does not hold a long one-sided filament. C2 avoids needing one.

## 4. What C2 does and does not claim

- **It does:** a growth medium that starts with no ordinary elements, with its output placed once by a declared, state-dependent rule (toward its first driven root, no task, score or assay lookup). In these pilots it forms a strong sensor→output path and responds through it in most seeds.
- **It does not:**
  - bridge a fixed, distant gap;
  - choose a useful output site autonomously;
  - establish learning, qualification or superiority.
  - **The element law's bridging limit is stated openly.**
- **Literature support for the prior** (memo §3): comparable systems fix seeds or frames from their own state, for example:
  - the seed robots of self-assembling Kilobot swarms;
  - the single seed cell of neural cellular automata;
  - biology splits long gaps with short-range guideposts.
- **The memo's conditions,** all adopted:
  - register the rule before final seeds;
  - state the bridging limit;
  - check the response per site (O now sits nearest one root).

## 5. Recommendation

1. **Adopt C2 as 7.12**, with the claim of §4.
2. **Change the F5 gate from one key per start to several**, because single-key outcomes flip. For example: five key sets per start, with a declared pass-rate criterion, decided in the 7.12 amendment and reviewed. This multiplies F5's cost by about 5 (about 16 min per start per key set on a quiet machine; it can be parallelized).
3. **Investigate the seeded start's fragility** (3/5 even with C2) before relying on (ii) as a reference.
4. **Keep option B** (a mechanically supported law, for example bonds with prestrain) as the long-term route if a growth claim beyond placement is wanted.

## 6. Limits

- One run per configuration. The distance sweep covers one key set; the direction controls cover three.
- Pilots measure only F5's A/B/E. F6–F9, control M/U and development are not measured.
- Every number is a descriptive pilot value, not a verdict.
- **Raw traces** (30 files, 11–12 MB each) stay local in `validation_712/` (gitignored), listed by SHA256 in `RAW_FILES.json`. Receipts are in `growing_shapes/runner/rev711_pilot_*_20261007/`.
