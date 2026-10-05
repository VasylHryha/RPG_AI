"""Section 14 admission, fresh development boundaries and exact predecessor fixtures."""
import concurrent.futures
import gzip
import hashlib
import json
import subprocess
import sys
import pytest
import s4_v3 as V
import s4_v1 as V1
import s4_v2 as V2
import s4_development as ORIGINAL
import s4_amended as OLD
from s3_runner import request
from build_admission import admit
from test_s3_controllers import s3_build


def test_fresh_declaration_equal_protocol_and_knob_dimensions():
    declared=json.loads((V.ROOT/'S4_V3_SEEDS.json').read_text())
    previous={b[1] for mod in (OLD,V1,V2) for stage in 'ABC' for split in ('tuning','validation') for b in mod.battles(stage,split)}
    previous|={b[1] for stage in 'ABC' for b in ORIGINAL.battles(stage,validation=True)}
    previous|={b[1] for stage in 'ABC' for rnd in range(8) for b in ORIGINAL.battles(stage,rnd)}
    previous|={s['seed'] for s in json.loads((V.ROOT/'s3_controllers_r3/default.requests.json').read_text())}
    seen=set()
    for stage in 'ABC':
        for split in ('tuning','validation'):
            panel=V.battles(stage,split)
            assert declared['panels'][stage][split]==[list(b) for b in panel]
            seeds={b[1] for b in panel};assert not seeds&previous and not seeds&seen;seen|=seeds
            if split=='tuning':assert len(panel)==19
            else:assert all(sum(b[0]==opp and b[2]==setting for b in panel)==100 for opp,_,setting in panel)
    assert (V.POPULATION,V.GENERATIONS,V.CLUSTERS,V.WORKERS,V.VALIDATION_N)==(16,16,19,10,100)
    assert {arm:len(b) for arm,b in V.BOUNDS.items()}==dict(resonator=11,morale=11,pushpull=3)
    assert set(V.BOUNDS['pushpull'])=={'G','f_c','m_k'}
    assert all('f' not in b and 'gamma' not in b for b in V.BOUNDS.values())
    assert V.CAP_SECONDS==360*60-34.48*60
    V.verify_sources()


def test_existing_output_refused_without_fights(tmp_path,monkeypatch):
    monkeypatch.setattr(sys,'argv',['s4_v3.py','--output',str(tmp_path),'--implementation-commit','unused'])
    with pytest.raises(RuntimeError,match='output already exists'):V.main()
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize('arm,params',[('resonator',{'gamma':1}),('morale',{'f':.7}),('pushpull',{'lambda_th':0}),('resonator',{'f_c':1.01}),('morale',{'m_k':.19}),('resonator',{'lambda_th':3.01})])
def test_v3_knob_rejections(s3_build,arm,params):
    req=request(dict(arm=arm,skeleton='v3',params=params));req['options']['duration']=0
    row=json.loads(subprocess.check_output([str(V.BINARY)],input=json.dumps(req)+'\n',text=True))
    assert 'error' in row


def test_v0_v1_v2_fixture_bytes_and_v3_engineering(s3_build,tmp_path):
    root=V.ROOT;specs=json.loads((root/'s3_controllers_r3/default.requests.json').read_text())
    stored_v1=json.loads((root/'s4_v1_checks/PART1_PARITY.json').read_text())['v1_engineering']
    v1_results={(x['spec']['arm'],x['spec']['seed'],x['spec']['swapSides']):x['summary'] for x in stored_v1}
    jobs=[]
    for spec in specs:
        index=spec['seed']-2026100500;stem=f"{spec['arm']}_{index:02d}_{int(spec['swapSides'])}"
        expected=(root/'s3_controllers_r3'/(stem+'.summary.json')).read_bytes()
        jobs.append(('s3_v0',dict(spec,skeleton='v0',diagnostics=False),expected,stem))
        if spec['arm'] in ('resonator','morale'):
            expected=(json.dumps(v1_results[(spec['arm'],spec['seed'],spec['swapSides'])],indent=2)+'\n').encode()
        jobs.append(('s3_v1',dict(spec,skeleton='v1',diagnostics=False),expected,stem))
    for directory,skeleton in [('s4_amended_development','v0'),('s4_v1_development','v1'),('s4_v2_development','v2')]:
        for path in sorted((root/directory/'replays').glob('*.replay.json.gz')):
            payload=json.loads(gzip.decompress(path.read_bytes()))
            raw=path.with_name(path.name.replace('.replay.json.gz','.jsonl.gz'))
            expected=gzip.decompress(raw.read_bytes()).splitlines(keepends=True)[-1]
            jobs.append((directory,dict(payload['spec'],skeleton=skeleton,trace=False),expected,path.name))
    stored_v2=json.loads((root/'s4_v2_checks/PART1_PARITY.json').read_text())['v2_engineering']
    for entry in stored_v2:
        expected=(json.dumps(entry['summary'],indent=2)+'\n').encode()
        jobs.append(('s3_v2',dict(entry['spec'],skeleton='v2',diagnostics=False),expected,str(entry['spec'])))
    def replay(job):
        kind,spec,expected,label=job
        raw=subprocess.check_output([str(V.BINARY)],input=json.dumps(request(spec))+'\n',text=True)
        actual=(json.dumps(json.loads(raw),indent=2)+'\n').encode() if kind.startswith('s3') else raw.encode()
        assert actual==expected,(kind,spec)
        return dict(kind=kind,fixture=label,byte_identical=True,summary_sha256=hashlib.sha256(actual).hexdigest())
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:parity=list(pool.map(replay,jobs))
    def engineering(spec):
        req=request(dict(spec,skeleton='v3',diagnostics=False))
        run=subprocess.run([str(V.BINARY),'--capture-s3','--metrics'],input=json.dumps(req)+'\n',text=True,capture_output=True,check=True)
        rows=run.stdout.splitlines(keepends=True);result=json.loads(rows[-1])
        assert result['controllerStatus']=='completed' and result['controllerFailures']==[0,0]
        capture=''.join(x for x in rows if json.loads(x).get('capture'))
        refinement=json.loads(subprocess.check_output([str(s3_build),'--refinement'],input=capture,text=True))
        assert refinement['samples']>0 and refinement['maximum']<.02
        return dict(spec=dict(spec,skeleton='v3'),summary=result,refinement=refinement,metrics=json.loads(run.stderr))
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:fresh=list(pool.map(engineering,[s for s in specs if s['arm'] in ('resonator','morale')]))
    # Reverification must never replace the committed Part 1 receipt.
    V.write(tmp_path/'PART1_PARITY.json',dict(parity=parity,fixture_count=len(parity),v3_engineering=fresh,native_build=admit(V.BINARY),contract_build=admit(s3_build)))


def test_v3_optimizer_full_dimensions_and_fixed_equal_budget():
    for arm in V.BOUNDS:
        start=V.defaults(arm);assert V.knobs(arm,V.normalized(arm,start))==start
        V.optimizer.stage='A';es=V.optimizer(arm,start);xs=es.ask()
        assert len(xs)==16 and all(len(x)==len(V.BOUNDS[arm]) for x in xs)
        assert all(0<=v<=1 for x in xs for v in x)
        es.tell(xs,[sum((v-.2)**2 for v in x) for x in xs]);assert es.countiter==1
    assert 38+16*16*38==9766
