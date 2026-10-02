"""Owner-side recursion and evaluator diagnostics; the detector sees summaries only."""
from dataclasses import dataclass
from collections import Counter

import numpy as np

from geomind import c5_detect
from geomind.c4_detect import (_convex_hull, circular_mean, radius_of_gyration,
                               window_statistics, nn_spacing)
from geomind.c5_units import clip_convex, polygon_area


@dataclass(frozen=True)
class Owner:
    """Private ownership. Primitive leaves hold an element index; composites hold children."""
    children: tuple = ()
    element: int = -1
    C: float = 1.0
    source_path: tuple = ()

    @property
    def members(self):
        if not self.children:
            return (self.element,)
        return tuple(m for c in self.children for m in c.members)

    @property
    def depth(self):
        return 0 if not self.children else 1 + self.children[0].depth

    def __post_init__(self):
        if self.children:
            if len(set(self.members)) != len(self.members):
                raise ValueError("ownership is not disjoint")
            if len({c.depth for c in self.children}) != 1:
                raise ValueError("children must share a level")
        elif self.element < 0:
            raise ValueError("primitive needs an element")


def published_series(owner, xs, ths):
    """Unweighted centroid/circular phase of immediate children at every frame."""
    if not owner.children:
        return xs[:, owner.element], np.unwrap(ths[:, owner.element])
    rows = [published_series(c, xs, ths) for c in owner.children]
    return (np.mean([r[0] for r in rows], axis=0),
            np.unwrap(circular_mean(np.stack([r[1] for r in rows], axis=-1), axis=-1)))


def child_series(owner, xs, ths):
    rows = [published_series(c, xs, ths) for c in owner.children]
    return np.stack([r[0] for r in rows], axis=1), np.stack([r[1] for r in rows], axis=1)


def thresholds(base, C):
    return c5_detect.level2_thresholds(base, C)


def horizon(owner):
    return max([100 * owner.C] + [30 * c.C for c in descendants(owner) if c.children])


def descendants(owner):
    for child in owner.children:
        yield child
        yield from descendants(child)


def _halfplane(poly, a, b, inside):
    """Clip a convex piece by either side of a directed line."""
    if len(poly) < 3:
        return np.empty((0, 2))
    cross = lambda p: (b[0]-a[0])*(p[1]-a[1]) - (b[1]-a[1])*(p[0]-a[0])
    out = []
    for p, q in zip(poly, np.roll(poly, -1, axis=0)):
        sp, sq = cross(p), cross(q)
        ip, iq = (sp >= 0, sq >= 0) if inside else (sp <= 0, sq <= 0)
        if ip:
            out.append(p)
        if ip != iq and sp != sq:
            out.append(p + (q-p)*sp/(sp-sq))
    return np.asarray(out).reshape(-1, 2)


def subtract_convex(subject, clip):
    """Disjoint convex partition of subject minus clip (boundaries have zero area)."""
    # Disjoint pieces must stay intact: cutting by every supporting line would create
    # gratuitous subdivisions, then amplify them when the union is canonicalized again.
    if polygon_area(clip_convex(subject, clip)) == 0:
        return [subject]
    remainder, out = subject, []
    for a, b in zip(clip, np.roll(clip, -1, axis=0)):
        piece = _halfplane(remainder, a, b, False)
        if polygon_area(piece) > 0:
            out.append(piece)
        remainder = _halfplane(remainder, a, b, True)
        if polygon_area(remainder) == 0:
            break
    return out


def union_pieces(hulls):
    """Exact planar union represented by interior-disjoint convex pieces."""
    out = []
    for hull in hulls:
        if polygon_area(hull) == 0:
            continue
        pending = [hull]
        for old in out:
            pending = [p for piece in pending for p in subtract_convex(piece, old)]
        out.extend(pending)
    return out


def shape(owner, x):
    """Union of level-one hulls, never the enclosing hull of a composite."""
    if all(not c.children for c in owner.children):
        points = x[list(owner.members)]
        return [points[_convex_hull(points)]]
    return union_pieces([p for c in owner.children for p in shape(c, x)])


def overlap(pieces, other):
    own = sum(map(polygon_area, pieces))
    if own <= 0:
        return float("inf")
    return sum(polygon_area(clip_convex(a, b)) for a in pieces for b in other) / own


def geometric_validity(parts, xs):
    rows = [{"hull_overlap": 0.0, "degenerate": False} for _ in parts]
    for x in xs:
        shapes = [shape(p, x) for p in parts]
        for i, part in enumerate(parts):
            X = np.array([published_series(c, x[None], np.zeros((1, len(x))))[0][0]
                          for c in part.children])
            L = radius_of_gyration(X)
            area = sum(map(polygon_area, shapes[i]))
            rows[i]["degenerate"] |= area <= 1e-12 * L * L or area <= 0
            for j in range(len(parts)):
                if i != j:
                    rows[i]["hull_overlap"] = max(rows[i]["hull_overlap"], overlap(shapes[i], shapes[j]))
    return rows


def dynamic_validity(part, xs, ths, times, parent_C, base):
    """Original children, complete non-overlapping own-level windows, trailing remainder omitted."""
    t = thresholds(base, part.C)
    start = times[-1] - max(30*parent_C, 30*part.C)
    windows = []
    count = int(np.floor((times[-1]-start)/(30*part.C) + 1e-10))
    for w in range(count):
        wanted = start + w*30*part.C + np.arange(31)*part.C
        idx = np.searchsorted(times, wanted - 1e-8)
        if np.any(idx >= len(times)) or not np.allclose(times[idx], wanted, rtol=0, atol=1e-7):
            return {"ok": False, "reason": "INSUFFICIENT_OBSERVATION", "windows": windows}
        X, Th = child_series(part, xs[idx], ths[idx])
        stats = window_statistics(X, Th, np.arange(len(part.children)), part.C,
                                  t["link_factor"], np.ones((len(part.children),)*2, bool))
        ok = all(np.isfinite(stats[k]) and stats[k] <= t[limit] for k, limit in
                 (("shape_cv", "shape_cv"), ("lock_std", "lock_std"),
                  ("freq_change", "freq_tol"), ("pattern_change", "pattern_tol")))
        windows.append({"start": float(wanted[0]), "end": float(wanted[-1]), "stats": stats, "ok": ok})
    return {"ok": bool(windows) and all(w["ok"] for w in windows),
            "reason": None if windows else "INSUFFICIENT_OBSERVATION", "windows": windows}


def recursive_validity(owner, xs, ths, times, base, top_C=None, observation_W=None):
    """Owner-computed criterion six; its output, not ownership, crosses the detector boundary."""
    top_C = owner.C if top_C is None else top_C
    if observation_W is None:
        observation_W = max([30*top_C] + [30*c.C for c in descendants(owner) if c.children])
    start = times[-1] - observation_W
    parent_times = start + np.arange(int(np.floor(observation_W/owner.C + 1e-10))+1)*owner.C
    idx = np.searchsorted(times, parent_times - 1e-8)
    observed = np.all(idx < len(times)) and np.allclose(times[idx], parent_times, rtol=0, atol=1e-7)
    geometry = geometric_validity(owner.children, xs[idx]) if observed else [
        {"hull_overlap": float("inf"), "degenerate": True} for _ in owner.children]
    rows = []
    for child, geo in zip(owner.children, geometry):
        dynamic = dynamic_validity(child, xs, ths, times, top_C, base)
        nested = recursive_validity(child, xs, ths, times, base, top_C, observation_W) if any(c.children for c in child.children) else []
        rows.append({**geo, "dynamic": dynamic, "children": nested,
                     "geometry": {"observed": bool(observed), "start": float(start),
                                  "end": float(times[-1]), "frame_dt": owner.C,
                                  "frames": len(parent_times),
                                  "reason": None if observed else "INSUFFICIENT_OBSERVATION"},
                     "reason": "INSUFFICIENT_OBSERVATION" if not observed else dynamic["reason"],
                     "ok": observed and dynamic["ok"] and not geo["degenerate"] and
                     geo["hull_overlap"] <= 0.2 and all(r["ok"] for r in nested)})
    return rows


def detect_level(series, validity, thresholds_n, kick_runner, rng):
    """ONE candidate path. Callback returns only published control/kicked endpoint summaries."""
    X, Theta = series
    found, locked = c5_detect.candidates(X, Theta, thresholds_n["frame_dt"], thresholds_n)
    out = []
    for units, stats in found:
        dx, dth = c5_detect.unit_kick(X[-1], Theta[-1], units, rng, thresholds_n)
        cx, ct, kx, kt = kick_runner(units, dx, dth)
        stats.update(c5_detect.recovery(units, cx, ct, kx, kt, locked, thresholds_n))
        stats["parts_alive"] = all(validity[int(u)]["ok"] for u in units)
        failed = [k for k, ok in c5_detect.criteria_checks(stats, thresholds_n).items() if not ok]
        out.append({"units": units.tolist(), "stats": stats, "failed": failed, "accepted": not failed})
    return out


outcome = c5_detect.outcome


@dataclass(frozen=True)
class MembershipDecoder:
    """Fixed evaluator membership only; no offsets and no refresh operation."""
    groups: tuple

    def lift(self, response, count):
        out = np.zeros((len(response), count, response.shape[-1]))
        for i, members in enumerate(self.groups):
            out[:, list(members)] = response[:, [i]]
        return out


def linear_summary(response, grouping):
    return np.stack([np.mean(response[..., list(g), :], axis=-2) for g in grouping], axis=-2)


def scored_set(real, alternative, probe, count):
    excluded = set(next(g for g in real if probe in g)) | set(next(g for g in alternative if probe in g))
    return tuple(i for i in range(count) if i not in excluded)


def response_norm(response, length):
    from geomind.c4_model import wrap
    return float(np.sqrt(np.mean(wrap(response[..., 2])**2)) +
                 np.sqrt(np.mean(np.sum(response[..., :2]**2, axis=-1) / np.asarray(length)**2)))


def pair_contrast(truth, real, alternative, probe, length, real_prediction=None, alternative_prediction=None):
    """A single scored set, uncorrected alternative error minus real error."""
    count = truth.shape[1]
    scored = scored_set(real, alternative, probe, count)
    if not scored:
        return {"status": "SKIPPED", "scored": scored}
    def error(group, prediction):
        summary = linear_summary(truth, group) if prediction is None else prediction
        lifted = MembershipDecoder(tuple(map(tuple, group))).lift(summary, count)
        return response_norm((truth-lifted)[:, scored], length)
    er, ea = error(real, real_prediction), error(alternative, alternative_prediction)
    return {"status": "TESTED", "scored": scored, "real_error": er,
            "alternative_error": ea, "contrast": ea-er}


def draw_probes(subparts, rng):
    """This API has no grouping argument. Call before constructing alternatives."""
    return rng.choice(len(subparts), size=4, replace=False).tolist()


def contact_graph(subparts, x, params):
    from geomind.c4_model import Batch, neighbors
    idx, mask, _ = neighbors(x[None], Batch(params, 1))
    labels = np.full(len(x), -1, int)
    for i, members in enumerate(subparts):
        labels[list(members)] = i
    adj = np.zeros((len(subparts),)*2, bool)
    for p, qs in enumerate(idx[0]):
        for q, active in zip(qs, mask[0, p]):
            if active and labels[p] >= 0 and labels[q] >= 0 and labels[p] != labels[q]:
                adj[labels[p], labels[q]] = adj[labels[q], labels[p]] = True
    return adj


def connected(group, adjacency):
    todo, reached = set(group), {group[0]}
    stack = [group[0]]
    while stack:
        p = stack.pop()
        new = {q for q in todo-reached if adjacency[p, q]}
        reached |= new
        stack.extend(new)
    return reached == todo


def canonical_partition(groups):
    return tuple(sorted(tuple(sorted(g)) for g in groups))


def alternative_groupings(real, adjacency, rng, K=20):
    """A2 seeded region growing, bounded to 2,000 attempts, without replacement."""
    labels = {u: i for i, g in enumerate(real) for u in g}
    sizes = list(map(len, real))
    neighbours = {u: set(np.flatnonzero(adjacency[u])) for u in labels}
    alternatives, seen, records = [], set(), []
    real_key = canonical_partition(real)
    for attempt in range(2000):
        if len(alternatives) >= K:
            break
        profile = rng.permutation(sizes).tolist()
        remaining, groups, reason = set(labels), [], None
        for size in profile:
            seed = int(rng.choice(sorted(remaining)))
            group = [seed]
            remaining.remove(seed)
            frontier = neighbours[seed] & remaining
            while len(group) < size:
                if not frontier:
                    reason = 'STUCK'
                    break
                new = int(rng.choice(sorted(frontier)))
                group.append(new)
                remaining.remove(new)
                frontier = (frontier | neighbours[new]) & remaining
            if reason:
                break
            groups.append(tuple(group))
        key = canonical_partition(groups)
        if reason is None:
            if any(len({labels[u] for u in g}) < 2 for g in groups):
                reason = 'UNMIXED'
            elif key == real_key:
                reason = 'REAL_PARTITION'
            elif key in seen:
                reason = 'DUPLICATE'
        accepted = reason is None
        records.append({'attempt': attempt+1, 'size_profile': profile,
                        'accepted': accepted, 'rejection_reason': reason,
                        'partition': key if accepted else None})
        if accepted:
            seen.add(key)
            alternatives.append(groups)
    return {'status': 'TESTED' if alternatives else 'NOT_TESTED', 'alternatives': alternatives,
            'attempts': len(records), 'acceptances': len(alternatives),
            'rejections': dict(Counter(r['rejection_reason'] for r in records if not r['accepted'])),
            'records': records, 'K': K, 'max_attempts': 2000}


def compactness(grouping, centroids, element_spacing):
    return float(np.mean([radius_of_gyration(centroids[list(g)])/element_spacing for g in grouping]))


def diffusion_diagnostic(adjacency, tau, times, initial, censored=False):
    """Reported only. Verdict code receives no diagnostic values."""
    from geomind.c6_effective import matrix_exp
    adjacency = np.asarray(adjacency, bool) | np.asarray(adjacency, bool).T
    np.fill_diagonal(adjacency, False)
    reason = None
    if censored or not np.isfinite(tau) or tau <= 0:
        reason = "INVALID_OR_CENSORED_TAU"
    elif not connected(tuple(range(len(adjacency))), adjacency):
        reason = "DISCONNECTED"
    L = np.diag(adjacency.sum(1)) - adjacency.astype(float)
    # A connected graph has exactly one structural zero mode. Remove that mode by
    # index rather than adding an unregistered eigenvalue cutoff.
    positive = np.linalg.eigvalsh(L)[1:]
    positive = positive[positive > 0]
    if reason is None and not len(positive):
        reason = "NO_POSITIVE_MODE"
    if reason:
        return {"status": "NOT_COMPUTED", "reason": reason}
    return {"status": "COMPUTED", "response": np.array([
        matrix_exp(-L*t/(tau*positive[0])) @ initial for t in times])}


def unit_specificity(pairs):
    valid = [r["contrast"] for r in pairs if r["status"] == "TESTED"]
    return {"status": "TESTED" if valid else "NOT_TESTED", "value": float(np.mean(valid)) if valid else None,
            "skipped": len(pairs)-len(valid), "pairs": pairs}
