"""Summaries, bootstrap intervals and the registered ratio rule."""
import numpy as np


def col(rows, key):
    return np.array([r[key] for r in rows if r.get(key) is not None], float)


def stats(values):
    values = np.asarray(values, float)
    return {'median': float(np.median(values)), 'q1': float(np.quantile(values, .25)), 'q3': float(np.quantile(values, .75)), 'n': int(len(values))}


def share(mask):
    return float(np.mean(mask))


def ratio_verdict(wired, big, factor=3.0):
    """Rows-needed ratio. A design that never reaches the level (inf) earns no credit, so inf against inf is INDETERMINATE, never SUPPORTED."""
    if not np.isfinite(wired) and not np.isfinite(big):
        return 'INDETERMINATE'
    return 'SUPPORTED' if big >= factor*wired else 'REFUTED' if big <= wired else 'INDETERMINATE'


def by_seed(rows, key):
    """{seed: value} for one endpoint. Every row must carry a finite value: a missing or non-finite endpoint is an error, never a silently dropped seed."""
    out = {}
    for r in rows:
        value = r.get(key)
        if value is None or not np.isfinite(value):
            raise ValueError('endpoint %r is missing or non-finite for seed %r' % (key, r.get('seed')))
        if r['seed'] in out:
            raise ValueError('duplicate seed %r' % (r['seed'],))
        out[r['seed']] = float(value)
    return out


def paired_by_seed(rows, key_a, key_b):
    """Per-seed differences a-b built from explicit seed identities (the same seeds on both sides), as an array ordered by seed."""
    a, b = by_seed(rows, key_a), by_seed(rows, key_b)
    if a.keys() != b.keys():
        raise ValueError('the two endpoints do not cover the same seeds')
    return np.array([a[s]-b[s] for s in sorted(a)])


def bootstrap_median_ci(values, rng, resamples=4000, level=0.95):
    """Percentile bootstrap interval for the median over seeds (seeds are replicates of one environment, not independent tasks)."""
    values = np.asarray(values, float)
    if values.ndim != 1 or len(values) < 2 or not np.isfinite(values).all():
        raise ValueError('need a finite one-dimensional sample of at least two seeds')
    idx = rng.integers(len(values), size=(resamples, len(values)))
    meds = np.median(values[idx], axis=1)
    lo, hi = np.quantile(meds, [(1-level)/2, 1-(1-level)/2])
    return float(np.median(values)), float(lo), float(hi)


def paired_median_ci(a, b, rng, resamples=4000, level=0.95):
    """Median of per-seed differences a-b with a paired bootstrap interval. The arrays must already be aligned by seed and have equal length
    (build them with `paired_by_seed`); a shape mismatch is an error, never a broadcast."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    if a.shape != b.shape:
        raise ValueError('paired samples must have the same shape, got %s and %s' % (a.shape, b.shape))
    return bootstrap_median_ci(a-b, rng, resamples, level)
