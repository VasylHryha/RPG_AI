"""Fail-closed complete-state comparison and the authorized eight-episode smoke."""
from collections import Counter
from dataclasses import asdict
import gzip
import hashlib
import json
import math
from pathlib import Path
import struct
import time
import numpy as np
from .protocol import Calibration, template_hash
from .run import Run
from ..world.world import Library

HERE = Path(__file__).resolve().parent
ATOL = RTOL = 1e-10


def snapshot(data):
    """Decode every v2 serialization field; assert complete byte consumption."""
    data = bytes.fromhex(data) if isinstance(data,str) else data
    pos = 0
    def read(fmt):
        nonlocal pos
        values = struct.unpack_from('='+fmt,data,pos)
        pos += struct.calcsize('='+fmt)
        return list(values)
    def string():
        nonlocal pos
        n = read('Q')[0]
        result = data[pos:pos+n].decode()
        pos += n
        return result
    def rows(fmt):
        return [read(fmt) for _ in range(read('Q')[0])]
    def pairs():
        return rows('Qd')
    result = [string()]
    assert result[0] == 'growing-medium-v2'
    result += [read('7d4i'),read('15d3i'),read('4i2d2Q'),rows('Q5di4d3i'),
               rows('Q8d'),rows('Q7d')]
    result.append([[pairs(),pairs(),rows('Q4di')] for _ in range(read('Q')[0])])
    events = []
    for _ in range(read('Q')[0]):
        event = [read('d'),string(),rows('Q')]
        event.append([[string(),read('d')] for _ in range(read('Q')[0])])
        events.append(event)
    result.extend([events,string()])
    assert pos == len(data), (pos,len(data))
    return result


def normalize(value):
    if isinstance(value,np.ndarray):
        return normalize(value.tolist())
    if isinstance(value,dict):
        return {str(k):normalize(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):
        return [normalize(v) for v in value]
    if isinstance(value,np.generic):
        return value.item()
    return value


class Compare:
    def __init__(self):
        self.scalars = self.exact = 0
        self.max_abs = self.max_ratio = 0.
    def check(self,a,b,path='root',exact=False):
        a,b = normalize(a),normalize(b)
        if isinstance(a,dict):
            assert isinstance(b,dict) and a.keys()==b.keys(), f'{path}: keys'
            # Digest is checked independently; its numeric content is compared below.
            for k in a:
                if k in ('final_type_id','type_id'):
                    continue
                if k == 'native':
                    self.check(snapshot(a[k]),snapshot(b[k]),path+'.native')
                else:
                    self.check(a[k],b[k],path+'.'+k,exact or k in
                        ('death','death_timers','novelty','novelty_timers','birth_steps','world_step','index','time','clock','step','check_time','admission_time'))
        elif isinstance(a,list):
            assert isinstance(b,list) and len(a)==len(b), f'{path}: length'
            for i,(x,y) in enumerate(zip(a,b)):
                self.check(x,y,f'{path}[{i}]',exact)
        elif isinstance(a,float) and not isinstance(b,bool) and isinstance(b,(float,int)):
            assert math.isfinite(a) and math.isfinite(b), f'{path}: nonfinite'
            if exact:
                assert struct.pack('=d',a)==struct.pack('=d',float(b)), f'{path}: exact {a} != {b}'
                self.exact += 1
            else:
                error = abs(a-b)
                ratio = error/(ATOL+RTOL*abs(b))
                self.max_abs,self.max_ratio = max(self.max_abs,error),max(self.max_ratio,ratio)
                assert ratio<=1, f'{path}: {a} != {b}, tolerance fraction {ratio}'
                self.scalars += 1
        else:
            assert a==b, f'{path}: {a!r} != {b!r}'
            self.exact += 1
    def report(self):
        return vars(self)


def medium_state(m):
    return {'native':m.native.save().hex(),'frames':[asdict(f) for f in m.frames],
            'death':m.death,'novelty':m.novelty,'birth_steps':m.birth_steps,
            'step':m.step_index,'events':m.events,
            'drives':[[getattr(d,k) for k,_ in d._fields_] for d in m.drives]}


def verify_hashes(report):
    assert report['final_type_id'] == template_hash(report['final_template'])
    for item in report['snapshots']:
        assert item['type_id'] == template_hash(item['template'])


def comparison():
    # Reuse already-frozen validation measurements; no new calibration panel.
    baseline = json.loads((HERE/'SMOKE.json').read_text())
    rows = {k:Calibration(**v) for k,v in baseline['frozen_validation']['calibration'].items()}
    library = Library()
    runs, timings = [], {}
    compare = Compare()
    try:
        for backend in ('reference','native'):
            run = Run(105051,rows,episodes=8,backend=backend,library=library,audit=True)
            runs.append(run)
            started = time.perf_counter()
            for episode in range(8):
                run.episode(episode)
            timings[backend] = {'wall_seconds':time.perf_counter()-started,
                'training_seconds':run.timing['training'],'training_steps':run.exposure['training_steps'],
                'ms_per_world_step':run.timing['training']*1000/run.exposure['training_steps'],
                'batch_calls':run.batch_calls}
        reports = [r.report() for r in runs]
        for report in reports:
            verify_hashes(report)
            assert report['complete'] and report['invalid'] is None
            assert report['exposure']['training_steps'] == 1280
            report.pop('timing')
        audit = {'label':'engineering-only; no section-10 run, projection or judging seeds',
            'reports':reports,'endpoints':[r.step_audit for r in runs],
            'final_states':[medium_state(r.medium) for r in runs]}
        with gzip.open(HERE/'PERF_SMOKE.json.gz','wt') as f:
            json.dump(audit,f,separators=(',',':'),allow_nan=False)
        compare.check(reports[0],reports[1],'smoke')
        compare.check(runs[0].step_audit,runs[1].step_audit,'every_endpoint')
        compare.check(medium_state(runs[0].medium),medium_state(runs[1].medium),'final_complete_state')
        # Existing receipt is corroborating evidence, not rewritten or reclassified.
        previous = baseline['smoke']
        compare.check(previous['events'],reports[0]['events'],'previous_smoke_events')
        compare.check(previous['drive_schedule'],reports[0]['drive_schedule'],'previous_smoke_drives')
        result = {'status':'PASS','seed':105051,'episodes':8,'comparison':compare.report(),
            'timings':timings,'speedup':timings['reference']['ms_per_world_step']/timings['native']['ms_per_world_step'],
            'events':dict(Counter(e['rule'] for e in reports[0]['events'])),
            'declaration_sha256':hashlib.sha256((HERE/'PERF_COMPARISON.md').read_bytes()).hexdigest(),
            'audit_sha256':hashlib.sha256((HERE/'PERF_SMOKE.json.gz').read_bytes()).hexdigest(),
            'source_sha256':{str(p.relative_to(HERE.parents[3])):hashlib.sha256(p.read_bytes()).hexdigest()
                for p in [*HERE.glob('*.py'),HERE.parent/'medium/design_0h.py',HERE.parents[1]/'DESIGN_0H.md']},
            'native_build':json.loads((HERE/'_build/build.json').read_text())}
        (HERE/'PERF_CHECKS.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps({k:v for k,v in result.items() if k!='native_build'},indent=2))
    finally:
        for r in runs:
            r.close()


if __name__ == '__main__':
    comparison()
