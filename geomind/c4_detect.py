"""Label-free resonator detector and effective-unit summary (candidate side of C4).

The detector sees only element states (positions, unwrapped phases, intrinsic
rates) and the dynamics. It never receives arm names, fixture labels or
evaluator data. A group is a resonator only if all five R4 criteria hold:

1. membership: a candidate is a connected component of the coupling graph,
   whose edges join pairs that are close (r < link_factor x median
   nearest-neighbor spacing in that frame) and phase-locked over the window
   (pairwise circular std <= lock_std). It must be matched in every window
   frame with Jaccard >= membership_jaccard and have >= min_size elements;
2. shape: the coefficient of variation of its radius of gyration over the
   window is <= shape_cv;
3. mode lock: every within-group pairwise phase difference has circular
   standard deviation <= lock_std over the window (anti-phase or offset
   patterns are allowed; low coherence is never a rejection);
4. reproducible signature: the collective frequency differs by <= freq_tol
   and the pairwise phase pattern by <= pattern_tol between window halves;
5. recovery: after a bounded kick of fixed size (positions: RMS
   kick_position x spacing; phases: zero-mean, RMS kick_phase), the
   original group is still present at the end of the recovery time in both
   the unkicked control future and the kicked future, and those two
   components agree (each of the three Jaccard scores >= recovery_jaccard).
   The kicked group's phase pattern also matches the control's (max
   pairwise difference <= pattern_tol). A group that fragments or merges,
   even the same way in both futures, does not recover.

Criterion 5 separates a resonator from a clump: without phase coupling a
kicked phase pattern has no restoring force. The kick has fixed size, so a
clump is rejected deterministically.
"""

import numpy as np

from geomind.c4_model import simulate, wrap


def nn_spacing(X):
    d = np.linalg.norm(X[:, None, :] - X[None, :, :], axis=-1)
    np.fill_diagonal(d, np.inf)
    return d.min(1)


def components(X, link_factor, locked):
    """Connected components of the coupling graph (close and locked pairs); returns a label per element."""
    d = np.linalg.norm(X[:, None, :] - X[None, :, :], axis=-1)
    np.fill_diagonal(d, np.inf)
    adj = (d < link_factor * np.median(d.min(1))) & locked
    labels = -np.ones(len(X), dtype=int)
    current = 0
    for start in range(len(X)):
        if labels[start] >= 0:
            continue
        labels[start] = current
        stack = [start]
        while stack:
            u = stack.pop()
            for v in np.flatnonzero(adj[u] & (labels < 0)):
                labels[v] = current
                stack.append(v)
        current += 1
    return labels


def jaccard(a, b):
    a, b = set(a), set(b)
    return len(a & b) / len(a | b) if a | b else 1.0


def best_match(X, members, link_factor, locked):
    labels = components(X, link_factor, locked)
    return max(jaccard(members, np.flatnonzero(labels == c)) for c in np.unique(labels)), labels


def radius_of_gyration(X):
    return float(np.sqrt(((X - X.mean(0)) ** 2).sum(1).mean()))


def pair_differences(th, members):
    """Unwrapped pairwise phase differences th_j - th_i for i < j in members; th may be (F, N) or (N,)."""
    i, j = np.triu_indices(len(members), 1)
    m = np.asarray(members)
    return th[..., m[j]] - th[..., m[i]]


def circular_mean(angles, axis=0):
    return np.angle(np.exp(1j * angles).mean(axis))


def circular_std(angles, axis=0):
    resultant = np.clip(np.abs(np.exp(1j * angles).mean(axis)), 1e-300, 1.0)
    return np.sqrt(np.maximum(-2.0 * np.log(resultant), 0.0))


def locked_pairs(ths, lock_std):
    """(N, N) mask of element pairs whose phase difference has circular std <= lock_std over frames ths (F, N)."""
    return circular_std(ths[:, None, :] - ths[:, :, None], 0) <= lock_std


def window_statistics(xs, ths, members, frame_dt, link_factor, locked):
    """Criteria 1-4 and the effective-state prediction error for one group over one window.

    xs (F, N, 2), ths (F, N) are frames spaced frame_dt apart; members are element indices."""
    frames = len(xs)
    half = frames // 2
    membership = min(best_match(xs[f], members, link_factor, locked)[0] for f in range(frames))
    rg = np.array([radius_of_gyration(xs[f, members]) for f in range(frames)])
    pairs = pair_differences(ths, members)
    lock = float(circular_std(pairs, 0).max())
    span = half * frame_dt
    omega_1 = float((ths[half, members] - ths[0, members]).mean() / span)
    omega_2 = float((ths[2 * half, members] - ths[half, members]).mean() / span)
    pattern_1, pattern_2 = circular_mean(pairs[:half + 1], 0), circular_mean(pairs[half:2 * half + 1], 0)
    centroid = xs[:, members].mean(1)
    predicted_x = centroid[half] + (centroid[half] - centroid[0])
    return {
        "size": int(len(members)),
        "membership_jaccard": float(membership),
        "shape_cv": float(rg.std() / rg.mean()),
        "lock_std": lock,
        "freq_change": abs(omega_2 - omega_1),
        "pattern_change": float(np.abs(wrap(pattern_2 - pattern_1)).max()),
        # Effective-state validity: predict the window end from the first half alone.
        "state_error_position": float(np.linalg.norm(predicted_x - centroid[2 * half]) / rg[2 * half]),
        "state_error_size": float(abs(rg[half] - rg[2 * half]) / rg[2 * half]),
        "state_error_frequency": abs(omega_2 - omega_1),
    }


def kick(x, th, members, rng, position_rms, phase_rms):
    """Fixed-size perturbation of the members: positions RMS position_rms (absolute), phases zero-mean RMS phase_rms."""
    x, th = x.copy(), th.copy()
    dx = rng.normal(size=(len(members), 2))
    dx *= position_rms / np.sqrt((dx ** 2).sum(1).mean())
    dth = rng.normal(size=len(members))
    dth -= dth.mean()
    dth *= phase_rms / np.sqrt((dth ** 2).mean())
    x[members] += dx
    th[members] += dth
    return x, th


def detect(xs, ths, omega, params, dt, frame_dt, thresholds, rngs):
    """Detect resonators in a batch of worlds.

    xs (F, B, N, 2), ths (F, B, N) are window frames ending at the current state;
    omega (B, N) are the elements' intrinsic rates; params is one Params or one per world;
    rngs[b] draws world b's kicks. Returns one list of candidate
    records per world, each with all statistics and an `accepted` flag."""
    t = thresholds
    frames, worlds = xs.shape[0], xs.shape[1]
    candidates, locks = [], [locked_pairs(ths[:, b], t["lock_std"]) for b in range(worlds)]
    for b in range(worlds):
        labels = components(xs[-1, b], t["link_factor"], locks[b])
        for c in np.unique(labels):
            members = np.flatnonzero(labels == c)
            if len(members) >= t["min_size"]:
                stats = window_statistics(xs[:, b], ths[:, b], members, frame_dt, t["link_factor"], locks[b])
                candidates.append((b, members, stats))
    if candidates:
        # Criterion 5: kicked runs against unkicked controls (one control per world), batched.
        x0, th0 = xs[-1], ths[-1]
        kicked_x, kicked_th, kicked_w = [], [], []
        for b, members, _ in candidates:
            spacing = float(np.median(nn_spacing(x0[b, members])))
            kx, kt = kick(x0[b], th0[b], members, rngs[b], t["kick_position"] * spacing, t["kick_phase"])
            kicked_x.append(kx)
            kicked_th.append(kt)
            kicked_w.append(omega[b])
        steps = int(round(t["recovery_time"] / dt))
        bx = np.concatenate([x0, np.array(kicked_x)])
        bt = np.concatenate([th0, np.array(kicked_th)])
        bw = np.concatenate([omega, np.array(kicked_w)])
        plist = list(params) if isinstance(params, (list, tuple)) else [params] * worlds
        end_x, end_th, _ = simulate(bx, bt, bw, plist + [plist[b] for b, _, _ in candidates], dt, steps)
        for n, (b, members, stats) in enumerate(candidates):
            control_labels = components(end_x[b], t["link_factor"], locks[b])
            control_members = max((np.flatnonzero(control_labels == c) for c in np.unique(control_labels)),
                                  key=lambda m: jaccard(members, m))
            original_to_control = jaccard(members, control_members)
            original_to_kicked, _ = best_match(end_x[worlds + n], members, t["link_factor"], locks[b])
            control_to_kicked, _ = best_match(end_x[worlds + n], control_members, t["link_factor"], locks[b])
            difference = pair_differences(end_th[worlds + n], members) - pair_differences(end_th[b], members)
            stats["recovery_original_to_control"] = float(original_to_control)
            stats["recovery_original_to_kicked"] = float(original_to_kicked)
            stats["recovery_control_to_kicked"] = float(control_to_kicked)
            stats["recovery_jaccard"] = float(min(original_to_control, original_to_kicked, control_to_kicked))
            stats["recovery_pattern_error"] = float(np.abs(wrap(difference)).max())
    results = [[] for _ in range(worlds)]
    for b, members, stats in candidates:
        failed = [name for name, ok in criteria_checks(stats, t).items() if not ok]
        results[b].append({"members": members, "stats": stats, "failed": failed, "accepted": not failed})
    return results


def criteria_checks(stats, t):
    return {
        "1_membership": stats["size"] >= t["min_size"] and stats["membership_jaccard"] >= t["membership_jaccard"],
        "2_shape": stats["shape_cv"] <= t["shape_cv"],
        "3_mode_lock": stats["lock_std"] <= t["lock_std"],
        "4_signature": stats["freq_change"] <= t["freq_tol"] and stats["pattern_change"] <= t["pattern_tol"],
        "5_recovery": stats["recovery_jaccard"] >= t["recovery_jaccard"] and stats["recovery_pattern_error"] <= t["pattern_tol"],
    }


def active_unit(x, th, omega_estimate, members, stats):
    """The upper-facing effective state (R4 ActiveUnit). Member indices are not exposed."""
    X = x[members]
    hull = _convex_hull(X)
    return {
        "effective_position": X.mean(0).tolist(),
        "characteristic_size": radius_of_gyration(X),
        "mode_signature": {
            "collective_frequency": float(omega_estimate),
            "coherence": float(np.abs(np.exp(1j * th[members]).mean())),
            "phase_offsets_sorted": np.sort(wrap(th[members] - circular_mean(th[members]))).tolist(),
        },
        "boundary_ports": [X[i].tolist() for i in hull],
        "stability": {k: stats[k] for k in ("membership_jaccard", "shape_cv", "lock_std", "freq_change", "pattern_change",
                                            "recovery_jaccard", "recovery_original_to_control", "recovery_original_to_kicked",
                                            "recovery_control_to_kicked", "recovery_pattern_error", "state_error_position",
                                            "state_error_size", "state_error_frequency")},
    }


def _convex_hull(P):
    """Indices of convex-hull vertices (monotone chain)."""
    order = sorted(range(len(P)), key=lambda i: (P[i][0], P[i][1]))
    if len(order) <= 2:
        return order

    def cross(o, a, b):
        return (P[a][0] - P[o][0]) * (P[b][1] - P[o][1]) - (P[a][1] - P[o][1]) * (P[b][0] - P[o][0])

    lower, upper = [], []
    for i in order:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], i) <= 0:
            lower.pop()
        lower.append(i)
    for i in reversed(order):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], i) <= 0:
            upper.pop()
        upper.append(i)
    return lower[:-1] + upper[:-1]
