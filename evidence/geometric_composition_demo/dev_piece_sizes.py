"""DEVELOPMENT record, not the experiment: choose each taught piece's size with a rule fixed in advance.

Rule (written before this ran): for each piece, on the final domains, 1,000 training samples and 10 seeds, take the smallest size in
{16, 32, 64, 128, 256} whose median relative test error is at most 0.005 (half the P1 bar of 0.01); if none qualifies take 256.
Own development entropy (below), separate from the recorded run and the smoke. Pieces only: no composite, no big map, no comparison
is evaluated here, so nothing about the composition claim can influence the sizes."""
import json
import secrets
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import demo  # noqa: E402

GRID = (16, 32, 64, 128, 256)
SEEDS = 10
entropy = secrets.randbits(96)
out = {'dev_entropy': entropy, 'rule': 'smallest M in %s with median rel error <= 0.005, else 256' % (GRID,), 'pieces': {}}
for i, name in enumerate(demo.PIECE_ORDER):
    spec = demo.CONFIG['pieces'][name]
    f = demo.PIECE_FUNCTIONS[name]
    rows = {}
    for M in GRID:
        errors = []
        for seed in range(SEEDS):
            X = demo.uniform(demo.stream(entropy, 1, seed, i), demo.CONFIG['n_piece'], spec['lo'], spec['hi'])
            piece = demo.GeoMap(spec['lo'], spec['hi'], M).fit(X, f(X), demo.stream(entropy, 1, seed, 100+i))
            Xt = demo.uniform(demo.stream(entropy, 4, seed, i), demo.CONFIG['n_test'], spec['lo'], spec['hi'])
            errors.append(demo.rel_error(piece.predict(Xt), f(Xt)))
        rows[M] = {'median': float(np.median(errors)), 'max': float(np.max(errors))}
    chosen = next((M for M in GRID if rows[M]['median'] <= 0.005), 256)
    out['pieces'][name] = {'by_size': rows, 'chosen': chosen, 'domain': spec}
    print(name, 'chosen', chosen, {M: round(r['median'], 5) for M, r in rows.items()})
out['equal_budget_points'] = sum(p['chosen'] for p in out['pieces'].values())
print('equal budget points', out['equal_budget_points'])
(HERE/'dev_piece_sizes.json').write_text(json.dumps(out, indent=1, sort_keys=True))
