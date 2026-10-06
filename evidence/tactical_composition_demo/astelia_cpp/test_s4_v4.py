"""Section-15 checks and fresh protocol admission; writes only new v4 evidence."""
import concurrent.futures
import gzip
import hashlib
import json
import pathlib
import subprocess
import sys
import time
import pytest
import s4_v4 as V
from s3_runner import request
from build_admission import admit
from s4_deadline import Deadline,BoundedPool

ROOT=V.ROOT


def test_native_synthetic_six_contracts(tmp_path):
    binary=tmp_path/'v4_contract'
    subprocess.run(['clang++','-std=c++17','-O1','-fno-fast-math','-ffp-contract=off','-I'+str(ROOT/'src'),
                    str(ROOT/'native_s4_v4_contract.cpp'),str(ROOT/'src/native/s3_controller.cpp'),'-o',str(binary)],check=True,capture_output=True)
    row=json.loads(subprocess.check_output([str(binary)],text=True))
    assert row['status']=='passed' and row['fights']==0
    V.write(ROOT/'s4_v4_checks/NATIVE_CONTRACT.json',row)


def test_fresh_declaration_equal_amended_protocol():
    import s4_amended,s4_v1,s4_v2,s4_v3,s4_development
    previous={b[1] for mod in (s4_amended,s4_v1,s4_v2,s4_v3) for stage in 'ABC' for split in ('tuning','validation') for b in mod.battles(stage,split)}
    previous|={b[1] for stage in 'ABC' for b in s4_development.battles(stage,validation=True)}
    previous|={b[1] for stage in 'ABC' for rnd in range(8) for b in s4_development.battles(stage,rnd)}
    previous|={s['seed'] for s in json.loads((ROOT/'s3_controllers_r3/default.requests.json').read_text())}
    for failed in ('s4_v4_development_failed_r1','s4_v4_development_failed_r2'):
        prior=json.loads((ROOT/failed/'S4_V4_SEEDS.json').read_text())
        previous|={b[1] for splits in prior['panels'].values() for panel in splits.values() for b in panel}
    seen=set();declaration=json.loads((ROOT/'S4_V4_SEEDS.json').read_text())
    for stage in 'ABC':
        for split in ('tuning','validation'):
            panel=V.battles(stage,split);seeds={b[1] for b in panel}
            assert not seeds&previous and not seeds&seen;seen|=seeds
            assert declaration['panels'][stage][split]==[list(b) for b in panel]
            assert len(panel)==19 if split=='tuning' else all(sum(b[0]==opp and b[2]==setting for b in panel)==100 for opp,_,setting in panel)
            old=s4_v3.battles(stage,split)
            assert [(opp,setting) for opp,_,setting in panel]==[(opp,setting) for opp,_,setting in old]
    assert (V.POPULATION,V.GENERATIONS,V.CLUSTERS,V.WORKERS,V.VALIDATION_N,V.CAP_SECONDS)==(16,16,19,10,100,360*60-V.PRIOR_SECONDS)
    assert V.BOUNDS==s4_v3.BOUNDS and {a:len(b) for a,b in V.BOUNDS.items()}==dict(resonator=11,morale=11,pushpull=3)
    V.verify_sources()


def test_existing_output_refused(tmp_path,monkeypatch):
    monkeypatch.setattr(sys,'argv',['s4_v4.py','--output',str(tmp_path),'--implementation-commit','unused'])
    with pytest.raises(RuntimeError,match='output already exists'):V.main()
    assert not list(tmp_path.iterdir())


def test_cma_all_dimensions_and_equal_budget():
    for arm in V.BOUNDS:
        start=V.defaults(arm);assert V.knobs(arm,V.normalized(arm,start))==start
        V.optimizer.stage='A';es=V.optimizer(arm,start);xs=es.ask()
        assert len(xs)==16 and all(len(x)==len(V.BOUNDS[arm]) for x in xs)
        assert all(0<=v<=1 for x in xs for v in x)
        es.tell(xs,[sum((v-.2)**2 for v in x) for x in xs]);assert es.countiter==1
    assert 38+16*16*38==9766


@pytest.mark.parametrize('arm,params',[('resonator',{'gamma':1}),('morale',{'f':.7}),('pushpull',{'lambda_th':0}),('resonator',{'f_c':1.01}),('morale',{'m_k':.19})])
def test_v4_native_rejects_invalid_knobs(arm,params):
    req=request(dict(arm=arm,skeleton='v4',params=params));req['options']['duration']=0
    assert 'error' in json.loads(subprocess.check_output([str(V.BINARY)],input=json.dumps(req)+'\n',text=True))


@pytest.mark.parametrize('arm',['resonator','morale','pushpull'])
def test_output_only_decisions_leave_complete_actions_identical(arm):
    req=request(dict(arm=arm,skeleton='v4',params=V.defaults(arm),seed=930000000,opponent='novice',setting='s4_melee10',trace=True))
    # Short synthetic integration fixture, not a development objective or panel.
    req['options']['duration']=.2
    req['decisionTrace']=True
    def run(diagnostics):
        fight=dict(req,decisionDiagnostics=diagnostics)
        return [json.loads(x) for x in subprocess.check_output([str(V.BINARY)],input=json.dumps(fight)+'\n',text=True).splitlines()]
    plain=run(False);traced=run(True)
    assert plain==[x for x in traced if not x.get('decisionDiagnostics')]
    decisions=[x for x in traced if x.get('decisionDiagnostics')]
    assert decisions and all(x['units'] for x in decisions)
    assert all(x['prepareTime']==x['t'] for x in decisions)


def test_v0_v1_v2_v3_fixture_bytes():
    jobs=[];specs=json.loads((ROOT/'s3_controllers_r3/default.requests.json').read_text())
    v1=json.loads((ROOT/'s4_v1_checks/PART1_PARITY.json').read_text())['v1_engineering']
    v2=json.loads((ROOT/'s4_v2_checks/PART1_PARITY.json').read_text())['v2_engineering']
    v3=json.loads((ROOT/'s4_v3_checks/PART1_PARITY.json').read_text())['v3_engineering']
    v1map={(x['spec']['arm'],x['spec']['seed'],x['spec']['swapSides']):x['summary'] for x in v1}
    for spec in specs:
        stem=f"{spec['arm']}_{spec['seed']-2026100500:02d}_{int(spec['swapSides'])}"
        expected=(ROOT/'s3_controllers_r3'/(stem+'.summary.json')).read_bytes()
        jobs.append(('s3',dict(spec,skeleton='v0',diagnostics=False),expected))
        if spec['arm'] in ('resonator','morale'):expected=(json.dumps(v1map[(spec['arm'],spec['seed'],spec['swapSides'])],indent=2)+'\n').encode()
        jobs.append(('s3',dict(spec,skeleton='v1',diagnostics=False),expected))
    for entries,skeleton in ((v2,'v2'),(v3,'v3')):
        for entry in entries:jobs.append(('s3',dict(entry['spec'],skeleton=skeleton,diagnostics=False),(json.dumps(entry['summary'],indent=2)+'\n').encode()))
    for directory,skeleton in [('s4_amended_development','v0'),('s4_v1_development','v1'),('s4_v2_development','v2'),('s4_v3_development','v3')]:
        for path in sorted((ROOT/directory/'replays').glob('*.replay.json.gz')):
            payload=json.loads(gzip.decompress(path.read_bytes()));raw=path.with_name(path.name.replace('.replay.json.gz','.jsonl.gz'))
            jobs.append(('replay',dict(payload['spec'],skeleton=skeleton,trace=False),gzip.decompress(raw.read_bytes()).splitlines(keepends=True)[-1]))
    def replay(job,deadline):
        kind,spec,expected=job
        raw=deadline.run([str(V.BINARY)],json.dumps(request(spec))+'\n').stdout
        actual=(json.dumps(json.loads(raw),indent=2)+'\n').encode() if kind=='s3' else raw.encode()
        assert actual==expected,(kind,spec)
        return dict(skeleton=spec['skeleton'],byte_identical=True,summary_sha256=hashlib.sha256(actual).hexdigest())
    pool=BoundedPool(10,Deadline(time.monotonic()+600))
    try:parity=list(pool.map(replay,jobs))
    finally:pool.close()
    V.write(ROOT/'s4_v4_checks/PART1_PARITY.json',dict(fixture_count=len(parity),by_skeleton={v:sum(x['skeleton']==v for x in parity) for v in ('v0','v1','v2','v3')},parity=parity,native_build=admit(V.BINARY)))
