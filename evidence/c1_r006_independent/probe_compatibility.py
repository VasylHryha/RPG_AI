"""Narrow independent serialization, compatibility-update and v5 migration audit."""
import gzip, json, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from geomind.geometry import Constraint, Observation, digest
from geomind.c1_cases import save_initial_state
from geomind.incremental import IncrementalGeometry, _C1V5State
HASH = digest({'review': 'r006-independent'})
base = Observation(('a', 'b'), (Constraint('a', 'b', (1.0, 0.0)),))
saved, _ = save_initial_state(base, HASH)
rows = []
for dtype in (np.float32, np.int64, np.float64):
    for field in ('edge_offset', 'weight', 'new_node_offset', 'relation_vector'):
        value = dtype(1)
        if field == 'edge_offset': delta = ((), (Constraint('a', 'b', (value, 0.0), 2.0),), ())
        elif field == 'weight': delta = ((), (Constraint('a', 'b', (1.0, 0.0), dtype(2)),), ())
        elif field == 'new_node_offset': delta = (('c',), (Constraint('b', 'c', (value, 0.0)),), ())
        else: delta = ((), (), (('unused-but-persisted', (value, 0.0)),))
        for path in ('apply', 'update'):
            state = IncrementalGeometry.from_saved(saved)
            before = state.export()
            if path == 'apply': trace = state.apply(*delta, HASH)
            else:
                observation = Observation(tuple(sorted(base.nodes + delta[0])), base.edges + delta[1], base.relations + delta[2])
                trace = state.update(observation, HASH)
            expected = 'PASS' if dtype is np.float64 and field != 'relation_vector' else 'INVALID_STATE'
            # A new manifest with existing unlabelled constraints is independently invalid.
            assert trace['status'] == expected, (dtype, field, path, trace)
            after = state.export()
            assert expected == 'PASS' or after == before
            assert IncrementalGeometry.load(after).export() == after
            rows.append({'dtype': dtype.__name__, 'field': field, 'path': path, 'status': trace['status'], 'unchanged_if_refused': expected == 'PASS' or after == before, 'reload': 'PASS'})
# Relation-backed case reaches the serialization guard rather than the unrelated manifest check.
isolated = Observation(('a',), ())
isolated_saved, _ = save_initial_state(isolated, HASH)
for dtype in (np.float32, np.int64, np.float64):
    value = dtype(1)
    delta = (('b',), (Constraint('a', 'b', (value, 0.0), 1.0, 'r'),), (('r', (value, 0.0)),))
    for path in ('apply', 'update'):
        state = IncrementalGeometry.from_saved(isolated_saved)
        before = state.export()
        trace = state.apply(*delta, HASH) if path == 'apply' else state.update(Observation(('a','b'), delta[1], delta[2]), HASH)
        expected = 'PASS' if dtype is np.float64 else 'INVALID_STATE'
        assert trace['status'] == expected, trace
        after = state.export()
        assert expected == 'PASS' or after == before
        assert IncrementalGeometry.load(after).export() == after
        rows.append({'dtype': dtype.__name__, 'field': 'backed_relation_vector', 'path': path, 'status': trace['status'], 'reload': 'PASS'})
archive = ROOT / 'evidence/c1_r005/states/32_bridge_w0_queue_after.json.gz'
encoded = gzip.decompress(archive.read_bytes()).decode().rstrip('\n')
old, current = _C1V5State.load(encoded), IncrementalGeometry.from_saved(encoded)
names = json.loads(encoded)['nodes']
assert all(old.query(a,b) == current.query(a,b) for a in names for b in names)
assert IncrementalGeometry.load(current.export()).export() == current.export()
output = {'serialization_cases': rows, 'v5_migration_pairs': len(names)**2, 'v5_migration': 'PASS', 'checks': 'PASS'}
Path(__file__).with_suffix('.out.json').write_text(json.dumps(output, indent=2) + '\n')
print(json.dumps({'cases': len(rows), 'migration_pairs': len(names)**2, 'checks': 'PASS'}))
