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


def bootstrap_median_ci(values, rng, resamples=4000, level=0.95):
    """Percentile bootstrap interval for the median over seeds (seeds are replicates of one environment, not independent tasks)."""
    values = np.asarray(values, float)
    idx = rng.integers(len(values), size=(resamples, len(values)))
    meds = np.median(values[idx], axis=1)
    lo, hi = np.quantile(meds, [(1-level)/2, 1-(1-level)/2])
    return float(np.median(values)), float(lo), float(hi)


def paired_median_ci(a, b, rng, resamples=4000, level=0.95):
    """Median of per-seed differences a-b with a paired bootstrap interval."""
    return bootstrap_median_ci(np.asarray(a, float)-np.asarray(b, float), rng, resamples, level)
