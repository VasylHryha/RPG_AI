"""Label-free level-2 detector: the C4 detector applied one level up (candidate side of C5).

Inputs are only the level-1 units' upper-facing states over the window: centroids X (F, M, 2),
unwrapped unit phases Theta (F, M) and each unit's own validity S. The detector never
receives member lists, intrinsic rates or fixture labels. Criterion 5 needs the futures of a
rigid unit kick; the experiment integrates the full model and returns only unit states.

Criteria 1-5 are the frozen C4 functions (components, locked_pairs, window_statistics, kick,
best_match, jaccard, pair_differences) with the C4 thresholds; only time quantities are scaled
by the single registered factor T (level2_thresholds). Criterion 6 is new and stated for every
level: each member unit stays a valid unit of its own level over the window (its own C4
criteria 2-4 on its original members, with the level-1 thresholds) and does not interpenetrate
another unit (hull area overlap). For primitives it is vacuous.
"""

import numpy as np

from geomind.c4_detect import (best_match, components, criteria_checks as c4_criteria, jaccard, kick, locked_pairs,
                               nn_spacing, pair_differences, window_statistics)
from geomind.c4_model import wrap

TIME_KEYS = ("window", "frame_dt", "recovery_time")


def level2_thresholds(level1, T):
    """The C4 thresholds one level up: identical except times (x T) and the frequency tolerance (/ T)."""
    t = dict(level1)
    for key in TIME_KEYS:
        t[key] = level1[key] * T
    t["freq_tol"] = level1["freq_tol"] / T
    return t


def candidates(X, Theta, frame_dt, t):
    """Components of the unit coupling graph (close and locked units) with >= min_size units, and their
    window statistics (criteria 1-4 and the effective-state errors). Returns (list of (units, stats), locked)."""
    locked = locked_pairs(Theta, t["lock_std"])
    labels = components(X[-1], t["link_factor"], locked)
    found = []
    for c in np.unique(labels):
        units = np.flatnonzero(labels == c)
        if len(units) >= t["min_size"]:
            found.append((units, window_statistics(X, Theta, units, frame_dt, t["link_factor"], locked)))
    return found, locked


def imposed(X, Theta, groups, frame_dt, t):
    """Window statistics for groups given from outside (the decoupled controls), so a control is never empty."""
    locked = locked_pairs(Theta, t["lock_std"])
    return [(np.asarray(g), window_statistics(X, Theta, np.asarray(g), frame_dt, t["link_factor"], locked)) for g in groups], locked


def unit_kick(X_last, Theta_last, units, rng, t):
    """Criterion-5 kick at unit level: the C4 kick on unit centroids and unit phases.
    Returns per-unit displacement (len(units), 2) and phase deltas (len(units),), applied rigidly."""
    spacing = float(np.median(nn_spacing(X_last[units])))
    kx, kt = kick(X_last, Theta_last, units, rng, t["kick_position"] * spacing, t["kick_phase"])
    return (kx - X_last)[units], (kt - Theta_last)[units]


def recovery(units, control_X, control_Theta, kicked_X, kicked_Theta, locked, t):
    """Criterion 5 with the C4 R003 rule: the original unit set must be matched in the control future and in
    the kicked future, the two matched groups must agree, and the inter-unit phase pattern must return."""
    labels = components(control_X, t["link_factor"], locked)
    control_units = max((np.flatnonzero(labels == c) for c in np.unique(labels)), key=lambda m: jaccard(units, m))
    original_to_control = jaccard(units, control_units)
    original_to_kicked, _ = best_match(kicked_X, units, t["link_factor"], locked)
    control_to_kicked, _ = best_match(kicked_X, control_units, t["link_factor"], locked)
    difference = pair_differences(kicked_Theta, units) - pair_differences(control_Theta, units)
    return {"recovery_original_to_control": float(original_to_control),
            "recovery_original_to_kicked": float(original_to_kicked),
            "recovery_control_to_kicked": float(control_to_kicked),
            "recovery_jaccard": float(min(original_to_control, original_to_kicked, control_to_kicked)),
            "recovery_pattern_error": float(np.abs(wrap(difference)).max())}


def parts_alive(validity, units, level1, max_hull_overlap):
    """Criterion 6: every member unit passes its own criteria 2-4 (level-1 thresholds) and no other unit's
    hull covers more than max_hull_overlap of its hull area. Returns (ok, worst values)."""
    rows = [validity[u] for u in units]
    ok = all(r["shape_cv"] <= level1["shape_cv"] and r["lock_std"] <= level1["lock_std"]
             and r["freq_change"] <= level1["freq_tol"] and r["pattern_change"] <= level1["pattern_tol"]
             and r["hull_overlap"] <= max_hull_overlap for r in rows)
    worst = {k: max(r[k] for r in rows) for k in ("shape_cv", "lock_std", "freq_change", "pattern_change", "hull_overlap")}
    return ok, worst


def criteria_checks(stats, t):
    """Criteria 1-5 exactly as C4 (with the level-2 thresholds), plus criterion 6."""
    return {**c4_criteria(stats, t), "6_parts_alive": bool(stats["parts_alive"])}


def outcome(world_candidates, contact):
    """Per-world formation outcome, first that applies: FORMED, MERGED, DRIFTING, APART, OTHER."""
    if any(c["accepted"] for c in world_candidates):
        return "FORMED"
    if any("6_parts_alive" in c["failed"] for c in world_candidates):
        return "MERGED"
    if contact and (not world_candidates or any("3_mode_lock" in c["failed"] for c in world_candidates)):
        return "DRIFTING"
    if not contact:
        return "APART"
    return "OTHER"
