CHANGES_REQUIRED
Reviewer family: Codex (separate same-family reviewer)

Owner request, verbatim:

> Recheck what you did please, check if it is the best we can do, we want 10 out of 10 or above 9 - it's fine to break the things or fully rework. Check for issues, conflicts, gaps.

Medium: recount.py derives1200x700 from the Config struct default, but admitted observer_v1_config_codec.cpp uses gameConfig(), and observer_v1_world.cpp sets1400x800. Raw action clipping confirms x1400. Post-outside counts and report arena provenance are therefore wrong. Correct only stored observer audit dimensions; retain original fight pins, all outcomes and policy. No fight rerun is necessary.

Independent checks: all eight aggregate cells reconcile; all160 raw/request hashes/templates,2632 protected hashes and original fight source pins match. Eight full cluster0/orientation0 streams independently reconcile casualty/shell/first-kill metrics, exposure, simultaneity/PCA, staging flags, native action clipping and escort geometry. The first audit stopped because it followed the incorrect1200x700 assumption; subsequent native-source/raw diagnosis established1400x800.

Discrepancies: [{"id": "P9_regular_c00_o0", "actual_arena": [1400, 800], "correct_post_outside_gun_ticks": 602, "reported_post_outside_gun_ticks": 1626}, {"id": "P9_novice_c00_o0", "actual_arena": [1400, 800], "correct_post_outside_gun_ticks": 51, "reported_post_outside_gun_ticks": 970}]

Core regular outcomes support the declared no-improvement reading: zero eliminations and all own guns lost in every arm. Preserve bundle, commitment-window, survivor-denominator and P9 realization cautions.

Stored-only audit, no fights/engine runs/project tests. Caffeinated attempts and conservative diagnostic reservation total 22.890s.
