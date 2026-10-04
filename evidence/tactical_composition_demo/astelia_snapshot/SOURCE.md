# Pinned snapshot of the Astelia formation sandbox (read-only copy; the owner's own code)

- Source: repository `/Users/new/RiderProjects/astelia-hunte` (VasylHryha/astelia-hunte), `experiments/formation_sandbox/`, taken with `git show 4bb60f21b:<path>`
  (the last commit touching that folder; repository HEAD was `89a25e74c` on 2026-10-04). Nothing in the Astelia repository was changed.
- Files: `formation_sim.js` (sha256 85b16e9b84b42b831dd2e64a7055474b6df902e4c1ffd635e6670fc6fb665733), `bc_net.json` (sha256 d11e9a2da43cb0eb5b8b9539be4ab5834e750b4148121d56e632c75d7fb2e3e5).
- Why a copy: the Astelia sandbox changes daily; experiments here must run against fixed bytes.
- Use: the real game rules (`rules: 'game'`: brute, warden, hound, runner, spitter, shaman; frozen since 2026-10-02 per its README), the `SKILLS` registry (32 documented atomic behaviours),
  the hand-built `LEVELS` (novice, regular, veteran, elite, elite-fast) and the opponent `POOL` (19 doctrines).

## Bug found in this version (reported to the owner; not fixed in the Astelia repository)

`artilleryVolley` (`formation_sim.js:1272`) reads `coming.length`, but `coming` is `null` under the sandbox rules (it is only built under game rules, line 1258).
Every sandbox-rules fight in which planned artillery fire runs (levels veteran, elite) throws `TypeError: Cannot read properties of null (reading 'length')`.
The game-rules path is unaffected. Experiments here use game rules.

## Feasibility check (2026-10-04, 6 quick fights per level against wolfpack, line, storm; game rules)

novice margin −2.8 (1 of 6 won, 0.75 s per fight); regular +12.7 (6/6, 1.2 s); veteran +7.7 (4/6, 1.2 s); elite-fast +46.3 (6/6, 9.3 s with look-ahead).
