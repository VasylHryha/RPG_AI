# Bottom-up composition on the Astelia sandbox (development; not recorded runs)

Exploratory line under decision 0028 (items 13 and 14). The pieces are the 32 skills of the pinned Astelia formation sandbox (`../astelia_snapshot`; values from the
skill definitions and the hand-built levels), the brain (alone, formation, rules) and the formation shape. The start is the hand-built `novice` level. A piece is kept
only if the assembly then wins by more, on paired fights (same battles, both sides). Every number below is development data: settings were changed between runs after
looking at results, so none of it is a registered test.

| Run | Tool | Opponents | Search | Found | Fresh-seed check (19 opponents x 3 seeds x 2 sides = 114 fights) |
|---|---|---|---|---|---|
| 1 | `compose.js` (beam, full sweep per round) | pool doctrines' default skills | 7,520 fights, 13 min | dodgeShots, dodgeShells smart, castDodge | +35.2, 100% won; +23.1 over regular, +22.4 over veteran. Stopped at a ceiling (it already won every fight) |
| 3 | `compose_seq.js` at commit 387455a (one change after another, quick checks) | elite skills without artyRollout | 2,864 fights, about 10 min | dodgeShells, dodgeShots | +11.4, 91% won; +14.3 over regular, +15.5 over veteran; **17.9 below the hand-built elite-fast** |
| 4 | `compose_seq.js` (plus the two-step check and free brain moves) | the same | 8,232 fights, 38 min (the last 23 min only to show nothing more helps) | dodgeShots, dodgeShells smart, castDodge (the last two as a pair) | +21.3, 100% won; +24.1 over regular, +25.3 over veteran; **8.1 (se 1.0) below elite-fast** |

## What made the search faster (run 3)

- **Cheaper opponents.** The elite opponents' `artyRollout` simulates futures before every volley: 11-33 s per fight. Without it a fight takes about 0.7 s and the opponents stay strong (novice loses every fight).
- **One change after another, with quick checks.** Each change plays 4 fights, then 8, 16 and 32, and is dropped at the first stage where it is not ahead. Most changes do nothing or harm and stop after 4 fights. The first change that passes all 32 is kept (chunks of 10 in parallel, promising changes first). A normal round takes 20-60 s and 120-230 fights, against about 1,700 fights for a full sweep.

## Why run 3 stopped early, and the fix (run 4)

`run3_gap_check.js` (`run3_gap_check.txt`) compared hand-built structures with run 3's result on the same battles. Elite's skills **alone** are worse (-6.1). The rules brain
with a formation alone is about neutral (+1.9). **Together** they are better (+6.8). Pieces that hurt alone and help together cannot be found one change at a time.
Run 3 also excluded harmful pieces from its pair search, and moved the brain only one step at a time (alone -> formation costs -7.8).

Run 4 adds a **two-step check** when no single change passes: every change, including harmful ones, is tried as a first step, and every second change is raced on top of
it. It found **castDodge + smart shell dodging: +9.3 together**. castDodge alone changes nothing (gain exactly 0), and smart dodging alone was dropped after 4 noisy fights (-0.5, se 7.1).

## What this shows and what it does not

- Fast bottom-up search works here. It builds a 3-piece AI that beats the hand-built regular and veteran by about 24 on fresh seeds, and it found a pair that only works together.
- **The quick check has a cost.** Four fights are noisy, so a good piece can be dropped early. Run 4's smart dodging was dropped alone and recovered only by the pair check.
- **The search does not reach the hand-built elite** (8 below). Elite uses a bigger group (rules brain, a formation and several skills together) plus look-ahead and the artillery rollout. Groups larger than two parts, and expensive pieces, are still out of reach.
- Not shown: anything about groups of three or more parts, a registered claim, or other tasks.

## Next steps (proposed, not run)

1. **Larger groups.** Let the search try a known group as one move (the owner's "connect bigger things"): for example, the hand-built levels' skill sets as candidate bundles. Or allow a sideways step (a change that costs little) when stuck.
2. **Less noise in the quick check.** Use 8 fights as the first stage, or drop only if clearly behind (gain below -1 standard error), not merely not ahead.
3. **Cost per piece.** Record each piece's time cost, so an expensive piece (artyRollout, about 25x per fight) is a visible trade-off.
