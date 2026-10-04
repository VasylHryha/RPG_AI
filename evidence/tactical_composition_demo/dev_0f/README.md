# Experiment 0f — development record (own entropy, `DEV_SPEC.json`; NOT a recorded run; nothing registered from it)

Authority: decision 0028 item 12 ("lets try it": drafting and development of the bottom-up proposal). Code: `../zf_core.py` (tests `../test_zf.py`), new files. Task V3 of `../tactics_e2.py`.

| Step | Script | Raw result | Finding |
|---|---|---|---|
| 1 | `dev_step1_greedy.py` | `step1_results.json` | Seeds 0-4: all 88 assemblies scored on the selection roster (100 episodes per opponent); greedy from the rush rule; confirmation on a separate roster (200 episodes per opponent). |
| 2 | `dev_step2_level2_gate.py` | `step2_results.json` | Level-2 gate (seeds 10-14, scripted) and the two-step lookahead on the step-1 tables. |
| 3 | `dev_step3_atomic.py` | `step3_results.json` | Rethink after the owner's challenge ("5 parts is too small"): atomic single-factor scorer pieces, greedy growth from nearest-enemy (seeds 20-23). |

## Step 1: the procedure finds the useful structure and adds memory by itself

- The best of all 88 assemblies is **AIM with a self-loop (memory), feeding MOVE coherently** in all 5 seeds.
- Greedy (single changes, margin 0.02) reaches it in **4 of 5** seeds (paths: rush → NEAR>MOVE or AIM>APPROACH → AIM>MOVE → AIM+self>MOVE). In seed 1 it stops at HP>MOVE (selection 0.735): swapping to AIM gains only +0.003, while AIM plus memory together gain +0.025, a two-change improvement single steps cannot see.
- **Decoys are never wired in** (RAND, DRIFT appear in no greedy path or best assembly).
- Confirmation (fresh roster): greedy's unit 0.734, 0.713 (seed 1, the local optimum), 0.752, 0.731, 0.734; the hand-wired unit (AIM>MOVE, no memory) 0.709, 0.744, 0.698, 0.689, 0.736; the teacher 0.755, 0.749, 0.726, 0.740, 0.760; rush 0.39 to 0.45; four random wirings per seed 0.10 to 0.58. **The self-connection (memory) improves on the hand-wired design** in 4 of 5 seeds.

## Step 2: level 2 cannot be tested on V3; a two-step lookahead fixes the local optimum

- **Level-2 gate fails on V3**: a squad that focuses every unit on one shared target (highest damage plus missing health) gains +0.037, −0.005, −0.005, +0.005, +0.021 over three independent teacher units (median +0.005, gate 0.05); focusing the weakest loses about 0.15. Coordination as tried does not matter in this task, so level 2 needs a task revision in which it does (proposal section 5).
- **Two-step lookahead** (if no single change clears the margin, try every pair of changes before stopping) reaches the exhaustive best in **5 of 5** seeds on the same selection tables. It was chosen on those tables, so it needs confirmation on fresh seeds before any claim.

## Step 3: atomic pieces — the procedure beats the teacher with 2-3 pieces; the size is set by what the task rewards

Diagnosis behind it: the earlier grammar had two slots and coarse pieces (AIM already did the whole targeting job), so no assembly could hold more than about three pieces.
Here targeting is split into single-factor pieces (damage, missing health, in range, distance, ranged unit) plus a noise decoy and memory; connecting a piece adds its score with a weight.

| Seed | Growth path (selection score) | Pieces | Confirmation: found / teacher / nearest / rush |
|---|---|---|---|
| 20 | DIST (0.583) → +DMG×2 (0.772) → +MISS×0.5 (0.792) | 3 | 0.792 / 0.754 / 0.623 / 0.395 |
| 21 | DIST (0.540) → +RANGED×0.5 (0.732) → +memory (0.770) | 2 + memory | 0.804 / 0.756 / 0.625 / 0.420 |
| 22 | DIST (0.600) → +DMG×1 (0.857) | 2 | 0.786 / 0.715 / 0.578 / 0.429 |
| 23 | DIST (0.573) → +DMG×1 (0.812) | 2 | 0.805 / 0.770 / 0.581 / 0.435 |

- The procedure builds targeting from atomic pieces and **beats the hand-written teacher on fresh games in all four seeds** (+0.04 to +0.07), never connecting the decoy.
- It still connects only 2 or 3 pieces: one factor (the target's danger: damage or being ranged) carries almost all of the value in V3, and further pieces do not clear the margin.
  The structure is small because **the task rewards little**, not because the procedure refuses to connect. Bigger structures need a task in which more functions are necessary, an open grammar
  (combiners, conditions, chains), and atomic pieces for movement too (here the stepping rule was fixed).
- Selection scores overstate (seed 22: 0.857 selected, 0.786 confirmed): confirmation on fresh games is needed for every claim.
