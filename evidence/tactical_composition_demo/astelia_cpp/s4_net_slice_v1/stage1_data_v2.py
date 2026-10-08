"""Read-only sealed collection admission and streaming, whole-fight tensor conversion.

No collection helper that recovers/writes receipts is called. Reporting fights are
hashed for provenance but never converted. Converted arrays are local mmap files.
"""
import argparse
from collections import Counter
import json
import math
from pathlib import Path
import shutil
import numpy as np
from collection_v2 import HERE, ROOT, sha, read, atomic, admission
from protocol import split
from stage1_arithmetic import encode,slots,candidates,check,join,native_hypot,identity

HEADS = ('move', 'target', 'start', 'release', 'aim')
DATA = HERE / '_local/stage1_v2/data'


def validate_arithmetic(meta):
    if meta.get('arithmetic')!=identity() or meta.get('arithmetic_source_sha256')!=sha(HERE/'stage1_arithmetic.py'):
        raise RuntimeError('converted arithmetic version/platform drift; preserve stale cache')


def admit():
    from collection_v2 import admit_inventory
    admit_inventory()
    uniqueness=read(ROOT/'UNIQUENESS_COLLECTION.json')
    from stage1_uniqueness import gate,state_hash
    inv=read(ROOT/'INVENTORY.json')
    fingerprints=[]
    for row in inv['rows']:
        rp=read(ROOT/(row['group']+'.receipt.json'))
        if rp['raw_sha256']!=sha(ROOT/(row['group']+'.jsonl')):
            raise RuntimeError('v2 raw collection drift')
        fingerprints.append(dict(cell=row['cell'],guns=row['guns'],orientation=row['orientation'],
            records=rp['record_count'],decision_rows=rp['decision_count'],
            first_k_state_sha256=state_hash(ROOT/(row['group']+'.jsonl'))))
    if gate(fingerprints)!=uniqueness or uniqueness['status']!='PASS':
        raise RuntimeError('v2 uniqueness admission drift/failure')
    inv, seal, ledger = (read(ROOT / name) for name in
                         ('INVENTORY.json', 'SEAL.json', 'LEDGER.json'))
    digest = sha(ROOT / 'INVENTORY.json')
    if seal['inventory_sha256'] != digest or ledger['inventory_sha256'] != digest:
        raise RuntimeError('collection seal/ledger mismatch')
    if admission() != seal['pins'] or sha(HERE/'CONTRACT.md') != seal['pins']['frozen/collection_CONTRACT.md']:
        raise RuntimeError('collection binary/contract/source drift')
    groups = [r['group'] for r in inv['rows']]
    if len(set(groups)) != 200 or inv['total'] != 200 or ledger['pending'] or set(ledger['complete']) != set(groups):
        raise RuntimeError('complete sealed 200-fight collection required')
    for row in inv['rows']:
        if row['split'] != 'report' and split(row['group']) != row['split']:
            raise RuntimeError('whole-fight split drift')
    return inv


def frame_rows(path):
    terminal = False
    with Path(path).open('rb') as f:
        while line := f.readline(1048578):
            if len(line) > 1048577 or not line.endswith(b'\n'):
                raise ValueError('record bound/truncation')
            value = json.loads(line)
            if terminal:
                raise ValueError('record after terminal')
            terminal = bool(value.get('terminal'))
            yield value
    if not terminal:
        raise ValueError('missing terminal')


def decision(s, action):
    """Masks are the existing causal join's masks; labels precede common drift."""
    key = (s['fight'], s['tick'], s['self'])
    events = [dict(fight=key[0], tick=key[1], unit=key[2], decision_tick=key[1],
                   stage=stage, value=value, volley=action.get('volley', 0))
              for stage, value in [('snapshot', s), ('intent', action)]]
    masks = join(events)[key]['masks']
    _, enemies, _, _ = slots(s)
    target = next((u for u in enemies if u['id'] == action['target']), None)
    ti = 0 if target is None else enemies.index(target)+1
    if action['target'] and target is None:
        raise ValueError('unsupported non-none target')
    if ti != action['target_index']:
        raise ValueError('target slot label mismatch')
    moves, aims = candidates(s, target)
    me = check(s)
    legal_aim = [0 <= a[0] <= s['width'] and 0 <= a[1] <= s['height']
                 and me['min_range'] <= native_hypot(a[0]-me['x'],a[1]-me['y']) <= me['range'] for a in aims]
    legal_aim += [False]*(33-len(legal_aim))
    labels = [action['move_index'], ti, int(action['start']), int(action['release']), action['aim_index'] or 0]
    legal = [True]*33 + [True]*(len(enemies)+1)+[False]*(12-len(enemies)) + legal_aim
    if not 0 <= labels[0] < 33 or (masks['aim'] and not legal_aim[labels[4]]):
        raise ValueError('unsupported categorical action')
    # Physical errors are teacher-target-conditioned, never an outcome label.
    offsets = np.zeros((2, 33, 2), dtype=np.float32)
    offsets[0] = moves
    if aims:
        offsets[1] = aims
    return labels, [masks[k] for k in HEADS], legal, offsets


def receipt():
    inv = admit()
    rows, resources = [], Counter()
    counts, split_rows = Counter(), Counter()
    maximum_rss = maximum_record = 0
    for r in inv['rows']:
        path = ROOT/(r['group']+'.jsonl')
        rp = ROOT/(r['group']+'.receipt.json')
        v = read(rp)
        if v['status'] != 'COMPLETE' or v['request'] != r['request'] or v['inventory_sha256'] != sha(ROOT/'INVENTORY.json') or v['raw_sha256'] != sha(path):
            raise RuntimeError('immutable fight receipt/data mismatch: '+r['group'])
        counts['|'.join(str(r[k]) for k in ('cell','guns','orientation','split'))] += 1
        split_rows[r['split']] += v['decision_count']
        for k in ('wall_seconds','cpu_seconds','disk_bytes','record_count','decision_count'):
            resources[k] += v[k]
        maximum_rss = max(maximum_rss, v['rss_bytes'])
        maximum_record = max(maximum_record, v['maximum_record_bytes'])
        rows.append(dict(group=r['group'], split=r['split'], cell=r['cell'], guns=r['guns'], orientation=r['orientation'],
                         raw_sha256=v['raw_sha256'], receipt_sha256=sha(rp),
                         records=v['record_count'], decision_rows=v['decision_count'], disk_bytes=v['disk_bytes']))
    value = dict(status='COLLECTED_VERIFIED', fights=200,
                 inventory_sha256=sha(ROOT/'INVENTORY.json'), ledger_sha256=sha(ROOT/'LEDGER.json'),
                 seal_sha256=sha(ROOT/'SEAL.json'), pins=read(ROOT/'SEAL.json')['pins'],
                 counts_by_cell_guns_orientation_split=dict(sorted(counts.items())), rows_per_split=dict(split_rows),
                 measured_resources={**resources, 'maximum_rss_bytes':maximum_rss,'maximum_record_bytes':maximum_record,
                                     'charged_wall_seconds':read(ROOT/'LEDGER.json')['charged_wall_seconds']}, files=rows)
    path = HERE/'COLLECTION_RECEIPT_V2.json'
    if path.exists() and read(path) != value:
        raise RuntimeError('existing compact collection receipt differs')
    if not path.exists():
        atomic(path, value)
    return value


def convert_fight(row, source, ticks, out, shadow=False):
    """Bounded to one JSON frame plus mmap pages, not a Python fight list."""
    out = Path(out)
    if out.exists():
        raise RuntimeError('refuse to overwrite converted fight')
    out.mkdir(parents=True)
    guns = row['guns']; decisions = (ticks+5)//6
    shapes = dict(x=((decisions,guns,1008),'float32'), pos=((ticks,guns,2),'float64'),
                  alive=((ticks,guns),'bool'), launch=((ticks,guns),'bool'),
                  targets=((ticks,guns,12),'int64'), assignments=((ticks,guns),'int64'),
                  pending=((ticks,guns),'int64'), labels=((decisions,guns,5),'int64'),
                  masks=((decisions,guns,5),'bool'), legal=((decisions,guns,79),'bool'),
                  offsets=((decisions,guns,2,33,2),'float32'), dt=((ticks,),'float64'))
    arrays = {k:np.lib.format.open_memmap(out/(k+'.npy'), mode='w+', dtype=d, shape=s) for k,(s,d) in shapes.items()}
    for a in arrays.values():
        a[:] = 0
    ids = None; assignment = {}; casts = {}; last = 0; seen_decisions = set(); counts = Counter()
    for frame in frame_rows(source):
        if frame.get('terminal'):
            break
        if frame['tick'] != last+1 or frame['fight'] != row['group'] or frame['cell'] != row['cell']:
            raise ValueError('frame chronology/identity')
        last += 1; t = last-1; d = t//6
        if ids is None:
            ids = frame['gun_ids'][:]
            if len(ids) != guns or len(set(ids)) != guns:
                raise ValueError('initial gun identity')
        if not set(frame['gun_ids']).issubset(ids):
            raise ValueError('identity reuse/new gun')
        joint = frame['joint']
        if joint is not None:
            arrays['dt'][t] = joint['dt']
        else:
            arrays['dt'][t] = 1/30
        intents = {e['unit']:e['value'] for e in frame['events'] if e['stage']=='intent'}
        if shadow and t%6 == 0:
            intents = {e['id']:e['action'] for e in frame['shadow']}
            if set(intents) != set(frame['gun_ids']):
                raise ValueError('missing same-tick shadow labels')
        for id in frame['gun_ids']:
            g = ids.index(id); s = {**joint, 'self':id}; me = check(s)
            features, meta = encode(s)
            arrays['alive'][t,g] = True
            arrays['pos'][t,g] = [me['x'],me['y']]
            arrays['targets'][t,g,:len(meta['enemy_ids'])] = meta['enemy_ids']
            arrays['assignments'][t,g] = assignment.get(id,0)
            arrays['pending'][t,g] = me['target'] if me['prep']>0 else 0
            if t%6 == 0:
                if id not in intents:
                    raise ValueError('missing decision intent')
                lab, mask, legal, offsets = decision(s,intents[id])
                arrays['x'][d,g] = features
                arrays['labels'][d,g] = lab
                arrays['masks'][d,g] = mask
                arrays['legal'][d,g] = legal
                arrays['offsets'][d,g] = offsets
                # Recurrent context is the visitor's previous accepted assignment;
                # shadow labels never overwrite the student's visited history.
                actual = next(e['value'] for e in frame['events'] if e['stage']=='intent' and e['unit']==id)
                assignment[id] = actual['target']
                counts['decision_rows'] += 1
                for name,active in zip(HEADS,mask):
                    counts[name+'_active'] += int(active)
        # Strict streaming lifecycle validation of actual visitor events.
        for e in frame['events']:
            origin = (e['decision_tick'],e['unit'])
            if e['stage']=='intent':
                if origin in seen_decisions:
                    raise ValueError('duplicate decision')
                seen_decisions.add(origin)
            elif e['stage']=='cast_start':
                key = (e['cast_tick'],e['unit'])
                if origin not in seen_decisions or key in casts:
                    raise ValueError('cast origin')
                casts[key] = (origin,e['volley'])
            elif e['stage'] in ('consume','launch','cancel','consumed_without_launch'):
                if casts.get((e['cast_tick'],e['unit'])) != (origin,e['volley']):
                    raise ValueError('outcome origin')
                if e['stage']=='launch':
                    arrays['launch'][t,ids.index(e['unit'])] = True
    if last != ticks:
        raise ValueError('receipt tick count')
    for a in arrays.values():
        a.flush()
    meta = dict(group=row['group'],split=row['split'],cell=row['cell'],guns=guns,orientation=row['orientation'],
                ids=ids,ticks=ticks,decisions=decisions,counts=dict(counts), raw_sha256=sha(source),
                shadow=shadow,arithmetic=identity(),arithmetic_source_sha256=sha(HERE/'stage1_arithmetic.py'),
                arrays={k:sha(out/(k+'.npy')) for k in arrays})
    atomic(out/'META.json',meta)
    return meta


def convert():
    seal = receipt(); inv = admit(); DATA.mkdir(parents=True,exist_ok=True)
    if shutil.disk_usage(DATA).free < 5_000_000_000:
        raise RuntimeError('5 GB disk floor required')
    records = []
    for r in inv['rows']:
        if r['split']=='report':
            continue
        target = DATA/r['group']; raw = ROOT/(r['group']+'.jsonl')
        expected = next(v for v in seal['files'] if v['group']==r['group'])
        if (target/'META.json').exists():
            meta = read(target/'META.json')
            validate_arithmetic(meta)
            if meta['raw_sha256'] != expected['raw_sha256'] or any(sha(target/(k+'.npy')) != v for k,v in meta['arrays'].items()):
                raise RuntimeError('converted cache drift')
        else:
            if target.exists():
                raise RuntimeError('incomplete converted directory; preserve and inspect: '+str(target))
            partial = DATA/(r['group']+'.partial')
            if partial.exists():
                raise RuntimeError('incomplete conversion attempt; inspect: '+str(partial))
            meta = convert_fight(r,raw,expected['records'],partial)
            partial.rename(target)
        records.append(meta)
    from stage1_uniqueness import converted_hash,THRESHOLD
    from collections import defaultdict
    dedupe=defaultdict(list)
    for m in records:
        _,arrays=load(m['group'])
        dedupe['|'.join(str(m[k]) for k in ('cell','guns','orientation'))].append(
            dict(group=m['group'],split=m['split'],sha256=converted_hash(arrays)))
    stats={key:dict(fights=len(rows),distinct=len({r['sha256'] for r in rows}),
                   fraction=len({r['sha256'] for r in rows})/len(rows),rows=rows)
           for key,rows in dedupe.items()}
    # Cross-split exact duplicates are disallowed even when overall fraction passes.
    leaked=any(len({r['split'] for r in rows if r['sha256']==digest})>1
               for rows in dedupe.values() for digest in {r['sha256'] for r in rows})
    hashes={r['group']:r['sha256'] for rows in dedupe.values() for r in rows}
    import hashlib
    report=dict(status='PASS' if all(v['fraction']>=THRESHOLD for v in stats.values()) and not leaked else 'FAIL',
                threshold=THRESHOLD,strata=stats,cross_split_duplicates=leaked,
                arrays=['x','labels','pos','launch'],
                dedupe_sha256=hashlib.sha256(json.dumps(hashes,sort_keys=True).encode()).hexdigest())
    atomic(DATA/'DEDUPE.json',report)
    if report['status']!='PASS':
        raise RuntimeError('converted trajectories duplicate or leak across splits; stop before training')
    value = dict(version='NS1-conversion-2',dedupe_sha256=sha(DATA/'DEDUPE.json'),collection_receipt_sha256=sha(HERE/'COLLECTION_RECEIPT_V2.json'),
                 source_sha256=sha(Path(__file__)), fights=records, report_excluded=True)
    atomic(DATA/'INDEX.json',value)
    return value


def load(group, root=DATA):
    p = Path(root)/group
    meta = read(p/'META.json')
    validate_arithmetic(meta)
    return meta, {k:np.load(p/(k+'.npy'),mmap_mode='r') for k in meta['arrays']}


if __name__=='__main__':
    p = argparse.ArgumentParser(); p.add_argument('stage',choices=('receipt','convert')); a=p.parse_args()
    result = receipt() if a.stage=='receipt' else convert()
    print(json.dumps({'fights':len(result.get('files',result.get('fights',[]))), 'status':'PASS'}))
