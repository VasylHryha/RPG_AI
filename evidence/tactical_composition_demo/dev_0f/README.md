# Experiment 0f — development record (own entropy, `DEV_SPEC.json`; NOT a recorded run; nothing registered from it)

Authority: decision 0028 item 12 ("lets try it": drafting and development of the bottom-up proposal). Code: `../zf_core.py` (tests `../test_zf.py`), new files. Task V3 of `../tactics_e2.py`.

| Step | Script | Raw result | Finding |
|---|---|---|---|
| 1 | `dev_step1_greedy.py` | `step1_results.json` | Seeds 0-4: all 88 assemblies scored on the selection roster (100 episodes per opponent); greedy from the rush rule; confirmation on a separate roster (200 episodes per opponent). |
| 2 | `dev_step2_level2_gate.py` | `step2_results.json` | Level-2 gate (seeds 10-14, scripted) and the two-step lookahead on the step-1 tables. |

## Step 1: the procedure finds the useful structure and adds memory by itself

- The best of all 88 assemblies is **AIM with a self-loop (memory), feeding MOVE coherently** in all 5 seeds.
- Greedy (single changes, margin 0.02) reaches it in **4 of 5** seeds (paths: rush → NEAR>MOVE or AIM>APPROACH → AIM>MOVE → AIM+self>MOVE). In seed 1 it stops at HP>MOVE (selection 0.735): swapping to AIM gains only +0.003, while AIM plus memory together gain +0.025, a two-change improvement single steps cannot see.
- **Decoys are never wired in** (RAND, DRIFT appear in no greedy path or best assembly).
- Confirmation (fresh roster): greedy's unit 0.734, 0.713 (seed 1, the local optimum), 0.752, 0.731, 0.734; the hand-wired unit (AIM>MOVE, no memory) 0.709, 0.744, 0.698, 0.689, 0.736; the teacher 0.755, 0.749, 0.726, 0.740, 0.760; rush 0.39 to 0.45; four random wirings per seed 0.10 to 0.58. **The self-connection (memory) improves on the hand-wired design** in 4 of 5 seeds.

## Step 2: level 2 cannot be tested on V3; a two-step lookahead fixes the local optimum

- **Level-2 gate fails on V3**: a squad that focuses every unit on one shared target (highest damage plus missing health) gains +0.037, −0.005, −0.005, +0.005, +0.021 over three independent teacher units (median +0.005, gate 0.05); focusing the weakest loses about 0.15. Coordination as tried does not matter in this task, so level 2 needs a task revision in which it does (proposal section 5).
- **Two-step lookahead** (if no single change clears the margin, try every pair of changes before stopping) reaches the exhaustive best in **5 of 5** seeds on the same selection tables. It was chosen on those tables, so it needs confirmation on fresh seeds before any claim.
