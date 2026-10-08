"""Lossless bounded Stage A numeric records; full JSON remains diagnostic-only."""
import gzip
import json
import lzma
import struct
import math
import numpy as np

# coreStep advances the clock before snapshot/prepare, once per physical tick.
CADENCE = 'physical_tick_after_clock_advance'

class PhysicalTicks:
    def __init__(self, dt):
        if not math.isfinite(dt) or not 0 < dt <= .2:raise RuntimeError('invalid physical dt')
        self.dt, self.time, self.count = dt, 0., 0

    def add(self, row):
        expected = self.time + self.dt
        if (row.get('recordingCadence', CADENCE) != CADENCE or
            not math.isfinite(row['t']) or not math.isfinite(row['dt']) or
            abs(row['dt']-self.dt)>1e-12 or abs(row['t']-expected)>1e-7):
            raise RuntimeError('incomplete physical-tick history')
        self.time = expected
        self.count += 1

    def finish(self, terminal_time):
        if self.count and abs(self.time-terminal_time)>1e-7:
            raise RuntimeError('terminal/physical history time mismatch')

MAGIC = b'STAGEASLIM1\n' 
MAX_RECORD = 4 * 1024**2
ARRAYS = ('units', 'own', 'shells', 'shots', 'fields', 'casts', 'networkState')
DROPPED = {
    'labels.raw': 'teacher proposal; losses use executed commands',
    'labels.participation': 'intermediate adapter command; losses use executed commands',
    'labels.react': 'intermediate safety command; losses use executed commands',
    'labels.winner': 'arbitration explanation; not an input, label or mask',
    'observer.actions': 'duplicate post-step command display; executed pre-step labels retained',
    'observer.entries': 'engine display diagnostics; absent from policy inputs and A0 metrics',
    'observer.shotsV6': 'shot audit display; public shots bank retained each physical tick',
    'observer.launchAudit': 'planner diagnostics; public casts and launches retained',
    'observer.battery': 'planner diagnostics; public own resources and casts retained',
    'observer.units[2:]': 'post-step display state; metric needs identity/team counts, pre-step policy units retained',
    'observer.shapeV6 A0 event extras': 'only eligible/joint/applied/rejected and role/rawToExecuted/activeFire/readyLabel enter metrics; id/time/react and planner geometry are redundant diagnostics',
    'observer.shapeV6 non-A0 events': 'planner diagnostics; A0 events/labels retained for metric endpoints',
}

def slim(row):
    row = dict(row)
    if row.get('stageA'):
        row['labels'] = [{k: v for k, v in label.items() if k not in ('raw', 'participation', 'react', 'winner')} for label in row['labels']]
    elif row.get('observerV1'):
        row = {k: row[k] for k in ('observerV1', 'step', 't', 'units', 'shapeV6', 'damage', 'dodges', 'launches')}
        row['units'] = [u[:2] for u in row['units']]
        events=[]
        for e in row['shapeV6']:
            if e.get('a0Event'):events.append({k:e[k] for k in ('a0Event','eligible','joint','applied','rejected')})
            if e.get('a0Label'):events.append({k:e[k] for k in ('a0Label','role','rawToExecuted','activeFire','readyLabel')})
        row['shapeV6']=events
    return row

class Writer:
    def __init__(self, stream):
        self.stream = stream
        self.previous = {}
        stream.write(MAGIC)

    def write(self, source):
        row = slim(source)
        arrays = {}; chunks = []
        family = 'stageA' if row.get('stageA') else 'observer' if row.get('observerV1') else 'other'
        def add(key, value):
            a = np.asarray(value, dtype='<f8')
            # XOR of the exact IEEE-754 bits, never arithmetic subtraction:
            # delta encoding preserves every bit and compresses static fields.
            bits = np.frombuffer(a.tobytes(order='F'), dtype='<u8')
            prior = self.previous.get((family,key))
            delta = prior is not None and prior.shape == bits.shape
            arrays[key] = dict(shape=list(a.shape),delta=delta)
            encoded = np.bitwise_xor(bits,prior) if delta else bits
            chunks.append(encoded.tobytes())
            self.previous[family,key] = bits
        for key in ARRAYS:
            if key in row:
                add(key, row.pop(key))
        if row.get('observerV1'):
            events=row.pop('shapeV6')
            roles=('melee','ranged','artillery')
            add('a0_labels', [[roles.index(e['role']),e['rawToExecuted'],e['activeFire'],e['readyLabel']] for e in events if e.get('a0Label')])
            add('a0_events', [[e['eligible'],e['joint'],e['applied'],e['rejected']] for e in events if e.get('a0Event')])
        if 'history' in row:
            add('history', [[int(k), *v] for k, v in row.pop('history').items()])
        if 'pairModes' in row:
            add('pairModes', [[*map(int, k.split(':')), bool(v)] for k, v in row.pop('pairModes').items()])
        if row.get('stageA'):
            # Keep metadata and executed categorical/mask fields in JSON. Numeric
            # command values are in a binary matrix to remove verbose key repeats.
            meta = []; numeric = []
            for label in row.pop('labels'):
                label = dict(label); c = dict(label.pop('executed'))
                numeric.append([label.pop('id'), *c.pop('goal'), c.pop('target'), c.pop('multiplier'), *(c.pop('aim') or [0, 0])])
                label['executed'] = c
                label['aim_mask'] = source['labels'][len(meta)]['executed']['aim'] is not None
                meta.append(label)
            row['label_meta'] = meta
            add('label_values', numeric)
        header = json.dumps(dict(row=row, arrays=arrays), allow_nan=False, separators=(',', ':')).encode()
        payload = struct.pack('<I', len(header)) + header + b''.join(chunks)
        if len(payload) > MAX_RECORD:raise RuntimeError('compact record exceeds bound')
        self.stream.write(struct.pack('<I', len(payload)) + payload)

def exact(stream, n):
    out = stream.read(n)
    if len(out) != n:raise RuntimeError('truncated compact recording')
    return out

def rows(path):
    if str(path).endswith('.jsonl.gz') or str(path).endswith('.gz'):
        with gzip.open(path, 'rt') as stream:
            for line in stream:yield json.loads(line)
        return
    with lzma.open(path, 'rb') as stream:
        if exact(stream, len(MAGIC)) != MAGIC:raise RuntimeError('recording schema')
        previous = {}
        while True:
            size = stream.read(4)
            if not size:break
            if len(size) != 4:raise RuntimeError('truncated compact length')
            n = struct.unpack('<I', size)[0]
            if not 4 <= n <= MAX_RECORD:raise RuntimeError('compact record bound')
            payload = exact(stream, n);h = struct.unpack('<I', payload[:4])[0]
            if h > n-4:raise RuntimeError('compact header bound')
            header = json.loads(payload[4:4+h]);row = header['row'];at = 4+h
            family = 'stageA' if row.get('stageA') else 'observer' if row.get('observerV1') else 'other'
            for key, descriptor in header['arrays'].items():
                shape=descriptor['shape']
                count = int(np.prod(shape));end = at+count*8
                if end > n:raise RuntimeError('compact array bound')
                bits = np.frombuffer(payload[at:end], dtype='<u8')
                if descriptor['delta']:
                    prior=previous.get((family,key))
                    if prior is None or prior.shape!=bits.shape:raise RuntimeError('missing compact delta base')
                    bits=np.bitwise_xor(bits,prior)
                previous[family,key]=bits
                values = bits.view('<f8').reshape(shape, order='F').tolist();at=end
                if key == 'history':row[key] = {str(int(v[0])):v[1:] for v in values}
                elif key == 'pairModes':row[key] = {f'{int(a)}:{int(b)}':bool(c) for a,b,c in values}
                elif key == 'a0_labels':
                    row.setdefault('shapeV6',[]).extend(dict(a0Label=True,role=('melee','ranged','artillery')[int(role)],rawToExecuted=distance,activeFire=bool(active),readyLabel=bool(ready)) for role,distance,active,ready in values)
                elif key == 'a0_events':
                    row.setdefault('shapeV6',[]).extend(dict(a0Event=True,eligible=eligible,joint=bool(joint),applied=applied,rejected=rejected) for eligible,joint,applied,rejected in values)
                elif key == 'label_values':
                    row['labels'] = []
                    meta = row.pop('label_meta')
                    if len(meta) != len(values):raise RuntimeError('compact label dimensions')
                    for m, v in zip(meta, values):
                        mask=m.pop('aim_mask');m['id']=int(v[0]);m['executed'].update(goal=v[1:3],target=int(v[3]),multiplier=v[4],aim=v[5:7] if mask else None);row['labels'].append(m)
                else:row[key] = values
            if at != n:raise RuntimeError('compact trailing bytes')
            # Restore integer identity fields consumed as native RPC/query keys.
            if row.get('stageA'):
                for u in row['units']:
                    for i in (0,1,2,15):u[i]=int(u[i])
                for u in row['own']:u[0]=int(u[0])
            yield row
