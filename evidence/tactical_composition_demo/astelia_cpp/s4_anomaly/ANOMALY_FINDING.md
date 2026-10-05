# Morale anomaly: inspected before tuning

Matched development seeds 313200000–313200007, both orientations, midpoint morale knobs. The score inversion reproduces: novice −16.6875, regular −4.3125 survivors (eight clusters each). No controller failure.

The 2×2 diagnostic separates the declared brain/formation from the level skills:

| Enemy skills | Alone brain | Line formation brain |
|---|---:|---:|
| Novice | −16.6875 | +1.1250 |
| Regular | −30.1875 | −4.3125 |

Giving either skill bundle the line formation improves morale's score: +17.8125 for novice skills and +25.8750 for regular skills. Regular skills make the enemy stronger within either brain, as expected. The original comparison changed both the brain and the skills. The inversion is a real matchup effect of those intended configurations, dominated in this diagnostic by the formation/brain change; it is not evidence that regular skills are defective or weaker. These eight-cluster diagnostic means do not establish a general causal mechanism beyond the tested configuration swap.

Code: `src/native/config_codec.cpp` sets novice brain alone, abilities off and no leading/dodging; regular defaults to formation and replaces the formation with line, with Auto abilities, raw leading and shell dodging. The narrow runner selects these existing profiles as designed. The diagnostic overrides only brain/formation, preserving each level's skills.

Watched the four selected seed-313200000 fights in the offline HTML viewer, with browser execution checks for loading, playback, scrub and target toggle. At 60.1 seconds the regular line example has 13 own survivors and 10 enemy artillery remaining in a column, with the morale survivors clustered at range. It reaches the 150-second timeout. The novice alone example ends at 46.2 seconds with no own units and 18 enemies. The regular-alone example ends at 36.37 seconds with 32 enemies. The novice-line example also lasts to timeout. These illustrate loss versus residual standoff, consistent with the measured configuration effect. Screenshots and browser checks are in `../s4_checks/`.

No controller equation or skill defect was found; none was changed. Tuning may now begin under the previously committed protocol. Raw `.jsonl.gz` traces are unchanged. Replay payloads were subsequently reduced to viewer fields and gzip-embedded for small self-contained HTML; no fight was rerun for packaging. The original anomaly run identity binds the pre-packaging harness from commit 9690d67; packaging has a separate follow-up commit.
