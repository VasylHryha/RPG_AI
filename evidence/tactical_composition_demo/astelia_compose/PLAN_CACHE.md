# Plan: fight memory and a combination library (not built yet; to be built after run 5 ends)

The owner's request (2026-10-04): "plan it as cache etc.. so we can do other research and improvements faster and more efficiently". Each session should
reuse what earlier sessions already proved, and start from scratch only when something that changes the results has changed.

## Why it is safe

A fight is deterministic: the same game code, opponents, settings and seed give the same result. Runs 3 and 4 reproduced their first two rounds exactly. So a
saved result is as good as replaying the fight, as long as nothing that changes it has changed. The fingerprint below decides that, and a spot check catches what
the fingerprint misses.

## 1. Fingerprint: what makes saved results valid

`fp = sha256(formation_sim.js bytes, bc_net.json bytes, the fight settings (scenario, duration, abilities, rules), the opponents' skills (ENEMY), Node version,
cache format version)`. Everything is stored under `cache/<first 16 hex of fp>/`. Changing any part gives a new folder, so that part starts from scratch automatically. Old
folders stay (switching back reuses them).

## 2. Fight memory (`cache/<fp>/fights.jsonl`)

- One line per fight: `{p: hash of the assembly key, opp, seed, swap, m, win, ms}`. Append-only. Only the parent process writes, after every batch. A line is under 4 KB, so
  appends from two runs at once do not interleave. A torn last line (crash) is ignored on load.
- Loaded into the in-memory cache at start; `evaluate()` then plays only fights it does not have.
- **Spot check at start:** replay 8 random saved fights. Any mismatch means the fingerprint missed something, so the tool refuses the folder and says so.
- Kept out of git (`.gitignore`): it can be rebuilt, and it grows (about 1.5 MB per run). Run records keep their own results, as now.

## 3. Combination library (`cache/<fp>/library.json`, committed)

- Every result a run proves is added with its evidence:
  - an accepted single;
  - an accepted pair, with its parts' results alone;
  - an accepted merge;
  - a final unit, with its pieces, profile, selection seeds and score, the run that found it, and its fresh-seed confirmation when there is one.
- Uses:
  - `START=library:best` starts from the best confirmed unit, not novice;
  - `BUNDLES=library` offers each saved pair or unit as one move: a bigger piece, the owner's "connect bigger things";
  - `UNITS` can name library units to merge.
- Run 5's units (`dev/run5_units.json`) and run 4's pair are imported as the first entries. Their fingerprint is recomputed and must match.

## 4. The one rule that does not relax: grading on fresh fights

Reuse is for the **search**. The final check of a run must use seeds that **no run** used to select any piece of the graded assembly, including the pieces inherited
from the library. `cache/<fp>/seeds.json` records every seed's use (selection or confirmation, which run). The tool:
- picks the next unused confirmation block by itself;
- refuses a confirmation seed that was used for selection anywhere in the graded assembly's history.

Confirmation results of the fixed hand-built levels (novice, regular, veteran, elite-fast) are cached like any fight. elite-fast, the slowest, is then played once per seed.

## 5. What it buys (expected; to be measured)

- Rerunning an identical search: almost no fights.
- A new variation (another start, a new piece, another drop rule): it replays only the assemblies it has not met. Early rounds from novice overlap heavily between runs.
- Starting from the library's best unit skips the rounds that rebuild it (runs 1, 3, 4 and 5 each rebuilt the dodging group from novice).

## 6. Build order (after run 5)

1. `cache.js`, a shared module: fingerprint, load, append, spot check, library and seeds read/write.
2. Wire it into `compose_seq.js`: evaluate, start, bundles, confirmation seed choice.
3. `test_cache.js`, run once at the end of the batch:
   - a changed sim byte gives a new folder;
   - an append/load round trip;
   - a torn last line is ignored;
   - a spot-check mismatch is refused;
   - a used selection seed is refused for confirmation.
4. Import run 5 into the library.
5. Measure the speed-up: rerun run 5's first unit from the cache, and count fights and seconds.
