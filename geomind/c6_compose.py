"""Element-contact assembly and rigid published-centroid operations at any level."""
import numpy as np
from geomind.c5_compose import shift_units, rotate_units, pad, decouple_offsets, unit_kick
from geomind.c6_levels import Owner, published_series


def contact_solve(points, cluster, target, direction):
    """First inward crossing, bracketed by .02, then bisected on the outside of .6."""
    direction = np.asarray(direction, float)
    direction /= np.linalg.norm(direction)
    points = np.asarray(points, float)
    cluster = np.asarray(cluster, float)
    target = np.asarray(target, float)
    extent = np.max(np.linalg.norm(cluster-target, axis=1)) + np.max(np.linalg.norm(points, axis=1)) + 0.62
    distance = lambda r: float(np.min(np.linalg.norm(points[:, None] + target + r*direction - cluster[None], axis=-1)))
    outer = extent
    while outer > 0:
        inner = max(0., outer-0.02)
        if distance(inner) <= 0.6:
            for _ in range(60):
                mid = (inner+outer)/2
                gap = distance(mid)
                if 0.6 <= gap <= 0.600001:
                    return target+mid*direction, gap
                if gap < 0.6:
                    inner = mid
                else:
                    outer = mid
            raise RuntimeError("contact bisection did not converge")
        outer = inner
    return None


def remap_owner(owner, offset):
    if not owner.children:
        return Owner(element=owner.element+offset, C=owner.C, source_path=owner.source_path)
    return Owner(tuple(remap_owner(c, offset) for c in owner.children), C=owner.C, source_path=owner.source_path)


def assemble(templates, rng, C):
    xs, ths, oms, parts, retries, rates = [], [], [], [], [], []
    for template in templates:
        angle = rng.uniform(0, 2*np.pi)
        rotation = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
        x = template["x"] @ rotation.T
        misses = []
        if xs:
            target = np.mean([published_series(p, np.concatenate(xs)[None],
                                               np.concatenate(ths)[None])[0][0] for p in parts], axis=0)
            while True:
                direction = rng.uniform(0, 2*np.pi)
                solution = contact_solve(x, np.concatenate(xs), target, [np.cos(direction), np.sin(direction)])
                if solution is not None:
                    shift, gap = solution
                    x += shift
                    break
                misses.append(float(direction))
        else:
            gap = None
        th = template["th"] + rng.uniform(-np.pi, np.pi)
        rate = float(rng.uniform(-0.096/C, 0.096/C))
        omega = np.asarray(template.get("omega", np.zeros(len(th)))) + rate-template["isolated_rate"]
        parts.append(remap_owner(template["owner"], sum(map(len, xs))))
        xs.append(x)
        ths.append(th)
        oms.append(omega)
        rates.append(rate)
        retries.append({"misses": misses, "gap": gap})
    owner = Owner(tuple(parts), C=C)
    return np.concatenate(xs), np.concatenate(ths), np.concatenate(oms), owner, {"placement": retries, "rates": rates}


def labels_for(owner, count):
    labels = np.full(count, -1, int)
    for i, part in enumerate(owner.children):
        labels[list(part.members)] = i
    return labels


def scale_parts(x, th, owner, scale):
    """Uses unweighted published centroids, including unequal-size composite children."""
    centres = [published_series(c, x[None], th[None])[0][0] for c in owner.children]
    centre = np.mean(centres, axis=0)
    labels = labels_for(owner, len(x))
    return shift_units(x, labels, range(len(centres)), [(scale-1)*(p-centre) for p in centres])


def kick_parts(x, th, owner, units, dx, dth):
    labels = labels_for(owner, len(x))
    return shift_units(x, labels, units, dx), rotate_units(th, labels, units, dth)
