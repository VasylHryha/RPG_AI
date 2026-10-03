"""Geometric composition demo. NOT a milestone, NOT C6 evidence. See README.md and SPECIFICATION.md.

A piece is a small map: points placed in the space of its inputs plus a smooth readout. Small pieces are taught one job each
(add, multiply, divide, square root), wired into bigger pieces, promoted so a wired piece acts as one, and compared with
one big map and with an ordinary small neural network.

    python evidence/geometric_composition_demo/demo.py --write-spec   # once, before the specification commit
    python evidence/geometric_composition_demo/demo.py --smoke        # reduced run, own entropy, own directory
    python evidence/geometric_composition_demo/demo.py --run          # the single recorded run
"""
import argparse
import json
import os
import resource
import secrets
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

# ---------------------------------------------------------------- constants (copied into SPEC.json by --write-spec)

CONFIG = {
    'pieces': {
        'ADD': {'lo': [-2.0, -2.0], 'hi': [20.0, 20.0], 'M': 16},
        'MUL': {'lo': [1.0, 1.0], 'hi': [5.0, 5.0], 'M': 32},
        'SQRT': {'lo': [1.0], 'hi': [40.0], 'M': 16},
        'DIV': {'lo': [0.3, 0.3], 'hi': [4.0, 3.0], 'M': 256}},
    'n_piece': 1000, 'n_promote': 2000, 'M_promote': 64, 'n_test': 5000, 'seeds': 20,
    'distance_domain': [1.0, 4.3], 'diag_domain': [1.0, 3.0],
    'mix_lo': [1.0, 1.0, 0.3, 0.3], 'mix_hi': [3.0, 3.0, 4.0, 3.0], 'n_linear': 3000,
    'monolith': [{'M': 320, 'N': 4000, 'seeds': 20}, {'M': 1280, 'N': 16000, 'seeds': 20},
                 {'M': 5120, 'N': 64000, 'seeds': 10}],
    'mlp': [{'N': 4000, 'epochs': 300}, {'N': 64000, 'epochs': 40}], 'mlp_hidden': 64, 'mlp_batch': 256,
    'mlp_lr': 0.003, 'sigma_factor': 1.2, 'ridge': 1e-8, 'lloyd_iterations': 20, 'soft_cap': 2700.0}
SMOKE = {'n_linear': 900, 'n_piece': 300, 'n_promote': 600, 'n_test': 500, 'seeds': 2,
         'monolith': [{'M': 320, 'N': 1200, 'seeds': 2}, {'M': 640, 'N': 2400, 'seeds': 2}],
         'mlp': [{'N': 1200, 'epochs': 20}], 'soft_cap': 600.0}
PIECE_FUNCTIONS = {
    'ADD': lambda X: X[:, 0] + X[:, 1], 'MUL': lambda X: X[:, 0] * X[:, 1],
    'SQRT': lambda X: np.sqrt(X[:, 0]), 'DIV': lambda X: X[:, 0] / X[:, 1]}
PIECE_ORDER = ('ADD', 'MUL', 'SQRT', 'DIV')


# ---------------------------------------------------------------- io helpers

def atomic_write(path, data):
    path = Path(path)
    tmp = path.with_name(path.name + '.tmp%d' % os.getpid())
    with open(tmp, 'wb') as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def jsonable(value):
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    if isinstance(value, np.ndarray):
        return jsonable(value.tolist())
    if isinstance(value, np.generic):
        return jsonable(value.item())
    if isinstance(value, float) and not np.isfinite(value):
        return 'Infinity' if value > 0 else '-Infinity' if value < 0 else 'NaN'
    return value


def write_json(path, obj):
    atomic_write(path, json.dumps(jsonable(obj), sort_keys=True, indent=1).encode())


def stream(entropy, purpose, seed, key=0):
    return np.random.default_rng(np.random.SeedSequence([entropy, purpose, seed, key]))


# ---------------------------------------------------------------- the geometric piece

def squared_distances(U, P):
    """All squared distances without a 3-D temporary (matrix identity, clipped at zero)."""
    return np.maximum((U**2).sum(1)[:, None]+(P**2).sum(1)[None]-2.0*U@P.T, 0.0)


def assign_nearest(U, P, chunk=2000):
    out = np.empty(len(U), dtype=int)
    for i in range(0, len(U), chunk):
        out[i:i+chunk] = squared_distances(U[i:i+chunk], P).argmin(1)
    return out


def place_points(U, M, rng, iterations):
    """k-means++ start, then Lloyd iterations (competitive learning): the points settle where the inputs live."""
    n, d = U.shape
    if n > 20000:
        U = U[rng.choice(n, 20000, replace=False)]
        n = len(U)
    first = int(rng.integers(n))
    chosen = [first]
    d2 = ((U-U[first])**2).sum(1)
    for _ in range(1, M):
        total = d2.sum()
        j = int(rng.choice(n, p=d2/total)) if total > 0 else int(rng.integers(n))
        chosen.append(j)
        d2 = np.minimum(d2, ((U-U[j])**2).sum(1))
    P = U[chosen].copy()
    for _ in range(iterations):
        a = assign_nearest(U, P)
        counts = np.bincount(a, minlength=M)
        live = counts > 0
        for k in range(d):
            sums = np.bincount(a, weights=U[:, k], minlength=M)
            P[live, k] = sums[live]/counts[live]
    return P


class GeoMap:
    """Points in input space plus a smooth readout. Where the points sit is what the piece knows."""

    def __init__(self, lo, hi, M, sigma_factor=1.2, ridge=1e-8, iterations=20, chunk=4000):
        self.lo, self.hi = np.asarray(lo, float), np.asarray(hi, float)
        self.M, self.sigma_factor, self.ridge, self.iterations, self.chunk = M, sigma_factor, ridge, iterations, chunk

    def unit(self, X):
        return (np.asarray(X, float)-self.lo)/(self.hi-self.lo)

    def features(self, U):
        D = squared_distances(U, self.P)
        return np.hstack([np.exp(-D/(2*self.sigma**2)), U, np.ones((len(U), 1))])

    def fit(self, X, y, rng):
        U = self.unit(X)
        y = np.asarray(y, float)
        self.P = place_points(U, self.M, rng, self.iterations)
        D = squared_distances(self.P, self.P)
        np.fill_diagonal(D, np.inf)
        self.sigma = max(self.sigma_factor*float(np.sqrt(D.min(1)).mean()), 1e-3)
        self.y0, self.scale = float(y.min()), float(y.max()-y.min())
        t = (y-self.y0)/self.scale
        K = self.M+U.shape[1]+1
        A, b = np.zeros((K, K)), np.zeros(K)
        for i in range(0, len(U), self.chunk):
            F = self.features(U[i:i+self.chunk])
            A += F.T@F
            b += F.T@t[i:i+self.chunk]
        lam = self.ridge*np.trace(A)/K
        self.w = np.linalg.solve(A+lam*np.eye(K), b)
        return self

    def predict(self, X):
        U = self.unit(X)
        out = np.empty(len(U))
        for i in range(0, len(U), self.chunk):
            out[i:i+self.chunk] = self.features(U[i:i+self.chunk])@self.w
        return self.y0+self.scale*out


class MLP:
    """Ordinary matrix-math reference: tanh, two hidden layers, Adam, standardized inputs and output."""

    def __init__(self, d, h, rng):
        self.W = [rng.normal(0, np.sqrt(1.0/a), (a, b)) for a, b in ((d, h), (h, h), (h, 1))]
        self.b = [np.zeros(h), np.zeros(h), np.zeros(1)]

    def forward(self, Z):
        h1 = np.tanh(Z@self.W[0]+self.b[0])
        h2 = np.tanh(h1@self.W[1]+self.b[1])
        return h1, h2, (h2@self.W[2]+self.b[2])[:, 0]

    def fit(self, X, y, rng, epochs, batch, lr):
        self.mx, self.sx = X.mean(0), X.std(0)
        self.my, self.sy = float(y.mean()), float(y.std())
        Z, t = (X-self.mx)/self.sx, (y-self.my)/self.sy
        params = self.W+self.b
        m = [np.zeros_like(p) for p in params]
        v = [np.zeros_like(p) for p in params]
        step = 0
        for _ in range(epochs):
            order = rng.permutation(len(Z))
            for i in range(0, len(Z), batch):
                idx = order[i:i+batch]
                z, tt = Z[idx], t[idx]
                h1, h2, out = self.forward(z)
                g = (2.0*(out-tt)/len(idx))[:, None]
                gW2, gb2 = h2.T@g, g.sum(0)
                d2 = (g@self.W[2].T)*(1-h2**2)
                gW1, gb1 = h1.T@d2, d2.sum(0)
                d1 = (d2@self.W[1].T)*(1-h1**2)
                gW0, gb0 = z.T@d1, d1.sum(0)
                grads = [gW0, gW1, gW2, gb0, gb1, gb2]
                step += 1
                for k, (p, gr) in enumerate(zip(params, grads)):
                    m[k] = 0.9*m[k]+0.1*gr
                    v[k] = 0.999*v[k]+0.001*gr**2
                    p -= lr*(m[k]/(1-0.9**step))/(np.sqrt(v[k]/(1-0.999**step))+1e-8)
        return self

    def predict(self, X):
        return self.my+self.sy*self.forward((np.asarray(X, float)-self.mx)/self.sx)[2]


# ---------------------------------------------------------------- wiring and promotion

def count_violations(piece, X, counter, name):
    if counter is None:
        return
    inside = np.all((X >= piece.lo-1e-12) & (X <= piece.hi+1e-12), axis=1)
    counter[name] = counter.get(name, 0)+int((~inside).sum())
    counter['calls_'+name] = counter.get('calls_'+name, 0)+len(X)


def wired_distance(pieces, a, b, counter=None):
    """distance = SQRT(ADD(MUL(a, a), MUL(b, b))): four taught pieces, no further training."""
    xa, xb = np.c_[a, a], np.c_[b, b]
    count_violations(pieces['MUL'], xa, counter, 'MUL')
    count_violations(pieces['MUL'], xb, counter, 'MUL')
    sa, sb = pieces['MUL'].predict(xa), pieces['MUL'].predict(xb)
    xs = np.c_[sa, sb]
    count_violations(pieces['ADD'], xs, counter, 'ADD')
    total = pieces['ADD'].predict(xs)
    xr = total[:, None]
    count_violations(pieces['SQRT'], xr, counter, 'SQRT')
    return pieces['SQRT'].predict(xr)


def wired_mix(pieces, X, counter=None):
    """sqrt(a*b + c/d) = SQRT(ADD(MUL(a, b), DIV(c, d))): all four taught pieces wired once, no further training."""
    xm, xd = X[:, [0, 1]], X[:, [2, 3]]
    count_violations(pieces['MUL'], xm, counter, 'MUL')
    count_violations(pieces['DIV'], xd, counter, 'DIV')
    xs = np.c_[pieces['MUL'].predict(xm), pieces['DIV'].predict(xd)]
    count_violations(pieces['ADD'], xs, counter, 'ADD')
    xr = pieces['ADD'].predict(xs)[:, None]
    count_violations(pieces['SQRT'], xr, counter, 'SQRT')
    return pieces['SQRT'].predict(xr)


def mix_truth(X):
    return np.sqrt(X[:, 0]*X[:, 1]+X[:, 2]/X[:, 3])


def linear_baseline(X, y, Xt):
    """The best straight-line model: the floor any composition must clearly beat."""
    A = np.c_[X, np.ones(len(X))]
    w = np.linalg.lstsq(A, y, rcond=None)[0]
    return np.c_[Xt, np.ones(len(Xt))]@w


def diag4(distance, X):
    """DISTANCE(DISTANCE(a, b), DISTANCE(c, d)): one distance piece reused three times."""
    return distance(distance(X[:, 0], X[:, 1]), distance(X[:, 2], X[:, 3]))


def rel_error(pred, truth):
    return float(np.sqrt(np.mean((pred-truth)**2))/(truth.max()-truth.min()))


def uniform(rng, n, lo, hi):
    lo, hi = np.asarray(lo, float), np.asarray(hi, float)
    return lo+(hi-lo)*rng.random((n, len(lo)))


# ---------------------------------------------------------------- one seed

def run_seed(cfg, entropy, seed):
    out = {'seed': seed}
    pieces = {}
    for i, name in enumerate(PIECE_ORDER):
        spec = cfg['pieces'][name]
        f = PIECE_FUNCTIONS[name]
        X = uniform(stream(entropy, 1, seed, i), cfg['n_piece'], spec['lo'], spec['hi'])
        piece = GeoMap(spec['lo'], spec['hi'], spec['M'], cfg['sigma_factor'], cfg['ridge'], cfg['lloyd_iterations'])
        piece.fit(X, f(X), stream(entropy, 1, seed, 100+i))
        Xt = uniform(stream(entropy, 4, seed, i), cfg['n_test'], spec['lo'], spec['hi'])
        out['piece_'+name] = rel_error(piece.predict(Xt), f(Xt))
        pieces[name] = piece
    lo, hi = cfg['distance_domain']
    Xd = uniform(stream(entropy, 4, seed, 10), cfg['n_test'], [lo, lo], [hi, hi])
    truth_d = np.hypot(Xd[:, 0], Xd[:, 1])
    counter = {}
    wired = lambda a, b: wired_distance(pieces, a, b, counter)
    out['distance'] = rel_error(wired(Xd[:, 0], Xd[:, 1]), truth_d)
    out['violations_distance'] = dict(counter)
    lo4, hi4 = cfg['diag_domain']
    X4 = uniform(stream(entropy, 4, seed, 11), cfg['n_test'], [lo4]*4, [hi4]*4)
    truth4 = np.sqrt((X4**2).sum(1))
    counter4 = {}
    out['diag4'] = rel_error(diag4(lambda a, b: wired_distance(pieces, a, b, counter4), X4), truth4)
    out['violations'] = counter4
    # promotion: sample the wired piece, no ground-truth labels, teach one new map
    Xp = uniform(stream(entropy, 2, seed), cfg['n_promote'], [lo, lo], [hi, hi])
    yp = wired(Xp[:, 0], Xp[:, 1])
    promoted = GeoMap([lo, lo], [hi, hi], cfg['M_promote'], cfg['sigma_factor'], cfg['ridge'], cfg['lloyd_iterations'])
    promoted.fit(Xp, yp, stream(entropy, 2, seed, 1))
    promoted_distance = lambda a, b: promoted.predict(np.c_[a, b])
    wired_on_test = wired(Xd[:, 0], Xd[:, 1])
    out['promoted_distance'] = rel_error(promoted_distance(Xd[:, 0], Xd[:, 1]), truth_d)
    out['closure'] = float(np.sqrt(np.mean((promoted_distance(Xd[:, 0], Xd[:, 1])-wired_on_test)**2))/(truth_d.max()-truth_d.min()))
    out['diag4_promoted'] = rel_error(diag4(promoted_distance, X4), truth4)
    # the mixed task: all four taught pieces wired once, against one big map taught directly and against a straight line
    mlo, mhi = cfg['mix_lo'], cfg['mix_hi']
    Xm = uniform(stream(entropy, 4, seed, 12), cfg['n_test'], mlo, mhi)
    truth_m = mix_truth(Xm)
    counter_m = {}
    out['mix4'] = rel_error(wired_mix(pieces, Xm, counter_m), truth_m)
    out['violations_mix'] = counter_m
    Xl = uniform(stream(entropy, 6, seed, 0), cfg['n_linear'], mlo, mhi)
    out['linear_mix4'] = rel_error(linear_baseline(Xl, mix_truth(Xl), Xm), truth_m)
    Xl2 = uniform(stream(entropy, 6, seed, 1), cfg['n_linear'], [lo, lo], [hi, hi])
    out['linear_distance'] = rel_error(linear_baseline(Xl2, np.hypot(Xl2[:, 0], Xl2[:, 1]), Xd), truth_d)
    Xl4 = uniform(stream(entropy, 6, seed, 2), cfg['n_linear'], [lo4]*4, [hi4]*4)
    out['linear_diag4'] = rel_error(linear_baseline(Xl4, np.sqrt((Xl4**2).sum(1)), X4), truth4)
    for j, spec in enumerate(cfg['monolith']):
        if seed >= spec['seeds']:
            continue
        X = uniform(stream(entropy, 3, seed, j), spec['N'], mlo, mhi)
        mono = GeoMap(mlo, mhi, spec['M'], cfg['sigma_factor'], cfg['ridge'], cfg['lloyd_iterations'])
        mono.fit(X, mix_truth(X), stream(entropy, 3, seed, 100+j))
        out['monolith_%d' % j] = rel_error(mono.predict(Xm), truth_m)
    # ordinary matrix-math reference (descriptive only)
    for j, spec in enumerate(cfg['mlp']):
        X = uniform(stream(entropy, 3, seed, 50+j), spec['N'], mlo, mhi)
        net = MLP(4, cfg['mlp_hidden'], stream(entropy, 5, seed, j))
        net.fit(X, mix_truth(X), stream(entropy, 5, seed, 100+j), spec['epochs'], cfg['mlp_batch'], cfg['mlp_lr'])
        out['mlp_%d' % j] = rel_error(net.predict(Xm), truth_m)
    for key, value in out.items():
        if isinstance(value, float) and not np.isfinite(value):
            raise FloatingPointError('non-finite result for ' + key)
    return out


# ---------------------------------------------------------------- predeclared verdicts

def column(rows, key):
    return np.array([r[key] for r in rows if key in r], float)


def share(values, bar, below=True):
    return float(np.mean(values <= bar)) if below else float(np.mean(values >= bar))


def summary_stats(values):
    return {'median': float(np.median(values)), 'q1': float(np.quantile(values, .25)), 'q3': float(np.quantile(values, .75)),
            'n': int(len(values))}


FLOOR = 0.5   # a composite must be at least twice as good as the best straight line


def violation_share(rows, field, keys):
    return {k: float(np.mean([r[field].get(k, 0)/max(r[field].get('calls_'+k, 1), 1) for r in rows])) for k in keys}


def evaluate(rows, cfg):
    """SPECIFICATION.md rules. SUPPORTED: median and 75% of seeds meet the bar; REFUTED: median misses by the stated factor."""
    out = {}
    pieces = {}
    for name in PIECE_ORDER:
        e = column(rows, 'piece_'+name)
        pieces[name] = {**summary_stats(e), 'share_within_bar': share(e, 0.01)}
    ok = all(p['median'] <= 0.01 and p['share_within_bar'] >= 0.75 for p in pieces.values())
    bad = any(p['median'] > 0.02 for p in pieces.values())
    out['P1_pieces_learn'] = {'pieces': pieces, 'verdict': 'SUPPORTED' if ok else 'REFUTED' if bad else 'INDETERMINATE'}
    d = column(rows, 'distance')
    ld = column(rows, 'linear_distance')
    s2 = np.median(d) <= 0.02 and share(d, 0.02) >= 0.75 and np.median(d) <= FLOOR*np.median(ld)
    out['P2_wiring_works'] = {**summary_stats(d), 'share_within_bar': share(d, 0.02), 'linear_baseline': summary_stats(ld),
                              'effective_bar': min(0.02, FLOOR*float(np.median(ld))),
                              'verdict': 'SUPPORTED' if s2 else 'REFUTED' if np.median(d) > 0.04 else 'INDETERMINATE'}
    g = column(rows, 'mix4')
    lm = column(rows, 'linear_mix4')
    m0 = column(rows, 'monolith_0')
    ratio = m0/g
    composite_ok = bool(np.median(g) <= 0.03 and share(g, 0.03) >= 0.75 and np.median(g) <= FLOOR*np.median(lm))
    s3 = composite_ok and np.median(ratio) >= 3 and share(ratio, 3, below=False) >= 0.75
    r3 = np.median(ratio) < 1.5 or np.median(g) > 0.06
    out['P3_composition_beats_one_big_map'] = {
        'composite': summary_stats(g), 'composite_share_within_bar': share(g, 0.03), 'linear_baseline': summary_stats(lm),
        'effective_bar': min(0.03, FLOOR*float(np.median(lm))), 'composite_clears_its_bar': composite_ok,
        'monolith_equal_budget': summary_stats(m0), 'ratio': summary_stats(ratio),
        'ratio_share_at_least_3': share(ratio, 3, below=False),
        'verdict': 'SUPPORTED' if s3 else 'REFUTED' if r3 else 'INDETERMINATE'}
    medians, comps, matches = [], [], []
    for j in range(len(cfg['monolith'])):
        paired = [r for r in rows if 'monolith_%d' % j in r]
        medians.append(float(np.median([r['monolith_%d' % j] for r in paired])))
        comps.append(float(np.median([r['mix4'] for r in paired])))
        matches.append(medians[-1] <= comps[-1])
    if matches[0]:
        v4 = 'REFUTED'
    elif not composite_ok:
        v4 = 'INDETERMINATE'
    elif len(matches) > 1 and matches[1]:
        v4 = 'INDETERMINATE'
    else:
        v4 = 'SUPPORTED'
    out['P4_data_needed_to_match'] = {
        'monolith_medians': medians, 'composite_median_same_seeds': comps, 'matches': matches,
        'composite_clears_its_bar': composite_ok,
        'smallest_matching_scale_index': next((j for j, m in enumerate(matches) if m), None),
        'scales': [{'M': s['M'], 'N': s['N']} for s in cfg['monolith']], 'verdict': v4}
    dg = column(rows, 'diag4')
    ldg = column(rows, 'linear_diag4')
    c = column(rows, 'closure')
    gp = column(rows, 'diag4_promoted')
    ratio_p = float(np.median(gp)/np.median(dg))
    wired_ok = bool(np.median(dg) <= FLOOR*np.median(ldg))
    s5 = np.median(c) <= 0.01 and ratio_p <= 1.5 and wired_ok
    r5 = np.median(c) > 0.02 or ratio_p > 3
    out['P5_promotion_keeps_it_one_piece'] = {
        'closure': summary_stats(c), 'promoted_distance': summary_stats(column(rows, 'promoted_distance')),
        'diag4_wired': summary_stats(dg), 'diag4_promoted': summary_stats(gp), 'diag4_linear_baseline': summary_stats(ldg),
        'wired_diag4_clears_straight_line_floor': wired_ok, 'diag4_over_wired_ratio': ratio_p,
        'verdict': 'SUPPORTED' if s5 else 'REFUTED' if r5 else 'INDETERMINATE'}
    out['descriptive'] = {
        'mlp': {'mlp_%d' % j: summary_stats(column(rows, 'mlp_%d' % j)) for j in range(len(cfg['mlp']))},
        'mlp_settings': cfg['mlp'],
        'domain_violation_share_distance': violation_share(rows, 'violations_distance', ('MUL', 'ADD', 'SQRT')),
        'domain_violation_share_diag4': violation_share(rows, 'violations', ('MUL', 'ADD', 'SQRT')),
        'domain_violation_share_mix4': violation_share(rows, 'violations_mix', ('MUL', 'DIV', 'ADD', 'SQRT')),
        'seconds_per_seed': summary_stats(column(rows, 'seconds')) if all('seconds' in r for r in rows) else None}
    return out


# ---------------------------------------------------------------- specification, preflight and the run

def write_spec():
    path = HERE/'SPEC.json'
    if path.exists():
        raise SystemExit('SPEC.json already exists; the entropy is generated once')
    write_json(path, {'note': 'Generated once by --write-spec before the specification commit.',
                      'entropy': secrets.randbits(96), 'smoke_entropy': secrets.randbits(96),
                      'config': CONFIG, 'smoke_overrides': SMOKE})
    print('wrote', path)


def preflight(smoke):
    if smoke:
        return {'git': 'not enforced for smoke'}
    rel = str(HERE.relative_to(ROOT))
    for name in ('README.md', 'SPECIFICATION.md', 'SPEC.json', 'demo.py', 'test_demo.py'):
        if subprocess.run(['git', 'ls-files', '--error-unmatch', rel+'/'+name], cwd=ROOT, capture_output=True).returncode:
            raise SystemExit(name+' is not committed; commit the specification and code first')
    status = subprocess.run(['git', 'status', '--porcelain', '--', rel], cwd=ROOT, capture_output=True, text=True).stdout.splitlines()
    dirty = [line for line in status if '/run/' not in line and '/smoke_run/' not in line and not line.endswith(('/run', '/smoke_run'))]
    if dirty:
        raise SystemExit('uncommitted changes: '+'; '.join(dirty))
    return {'git_head': subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, text=True).stdout.strip()}


def main_run(smoke):
    spec = json.loads((HERE/'SPEC.json').read_text())
    cfg = dict(spec['config'])
    if smoke:
        cfg.update(spec['smoke_overrides'])
    entropy = spec['smoke_entropy'] if smoke else spec['entropy']
    guard = preflight(smoke)
    run_dir = HERE/('smoke_run' if smoke else 'run')
    try:
        os.mkdir(run_dir)
    except FileExistsError:
        raise SystemExit('%s exists: the one-shot latch is consumed; no resume, no retry' % run_dir.name)
    started, cpu0 = time.monotonic(), time.process_time()
    summary = {'status': 'INCOMPLETE', 'smoke': smoke, 'reason': 'not finished'}
    rows, errors = [], []
    try:
        (run_dir/'seeds').mkdir()
        import hashlib
        write_json(run_dir/'RUN_STARTED.json', {'smoke': smoke, 'guard': guard, 'numpy': np.__version__,
                                                'demo_sha256': hashlib.sha256((HERE/'demo.py').read_bytes()).hexdigest(),
                                                'test_sha256': hashlib.sha256((HERE/'test_demo.py').read_bytes()).hexdigest(),
                                                'spec_sha256': hashlib.sha256((HERE/'SPEC.json').read_bytes()).hexdigest(),
                                                'python': sys.version.split()[0],
                                                'wall_clock': time.strftime('%Y-%m-%dT%H:%M:%S%z')})
        for seed in range(cfg['seeds']):
            if time.monotonic()-started > cfg['soft_cap']:
                summary['reason'] = 'soft cap reached before seed %d' % seed
                break
            t0 = time.monotonic()
            try:
                row = run_seed(cfg, entropy, seed)
                row['seconds'] = time.monotonic()-t0
                write_json(run_dir/'seeds'/('seed_%02d.json' % seed), row)
                rows.append(row)
            except Exception as error:  # noqa: BLE001 - a failed seed is a missing value, never replaced
                errors.append({'seed': seed, 'error': repr(error)})
                write_json(run_dir/'seeds'/('error_%02d.json' % seed), errors[-1])
        else:
            summary['reason'] = 'complete'
    except BaseException as error:  # noqa: BLE001
        summary['reason'] = 'exception: '+repr(error)
    finally:
        usage = resource.getrusage(resource.RUSAGE_SELF)
        summary.update({'wall_seconds': time.monotonic()-started, 'cpu_seconds': time.process_time()-cpu0,
                        'max_rss_bytes': int(usage.ru_maxrss), 'seeds_expected': cfg['seeds'], 'seeds_complete': len(rows),
                        'seed_errors': errors, 'config': cfg})
        try:
            if summary['reason'] == 'complete' and not errors and len(rows) == cfg['seeds']:
                summary['evaluation'] = evaluate(rows, cfg)
                summary['status'] = 'COMPLETE'
        except Exception as error:  # noqa: BLE001
            summary['evaluation_error'] = repr(error)
        try:
            write_json(run_dir/'SUMMARY.json', summary)
        except Exception as error:  # noqa: BLE001
            atomic_write(run_dir/'SUMMARY.json', json.dumps({'status': 'INCOMPLETE', 'reason': 'summary write failed: '+repr(error)}).encode())
    print(json.dumps({k: summary[k] for k in ('status', 'reason', 'wall_seconds', 'seeds_complete')}, indent=1))
    if summary['status'] == 'COMPLETE':
        print(json.dumps({k: v['verdict'] for k, v in summary['evaluation'].items() if 'verdict' in v}, indent=1))
    return 0 if summary['status'] == 'COMPLETE' else 1


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--write-spec', action='store_true')
    group.add_argument('--run', action='store_true')
    group.add_argument('--smoke', action='store_true')
    args = parser.parse_args()
    if args.write_spec:
        write_spec()
    else:
        sys.exit(main_run(args.smoke))


if __name__ == '__main__':
    main()
