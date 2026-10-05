"""Negative controls for the previously missing performance/evidence gates."""
import hashlib
import json
import pathlib
import subprocess
import sys
import pytest
from benchmark import measure, qualification
from build_admission import admit

ROOT=pathlib.Path(__file__).resolve().parent


def test_old_binary_cannot_claim_edited_source(tmp_path):
    binary=tmp_path/'host';binary.write_bytes(b'binary identity')
    source=tmp_path/'simulation.cpp';source.write_text('version one')
    record=dict(schema=2,binary_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),
        source_hashes={str(source):hashlib.sha256(source.read_bytes()).hexdigest()},
        engine='native',scope='native_core_slice',sanitized=False,portable=True)
    binary.with_suffix('.build.json').write_text(json.dumps(record))
    assert admit(binary)['scope']=='native_core_slice'
    source.write_text('version two')
    with pytest.raises(RuntimeError,match='source/build mismatch'):
        admit(binary)


def test_below_minimum_and_missing_branches_cannot_qualify():
    native=dict(build=dict(scope='native_complete_engine'))
    groups={k:dict(speed_up=4) for k in ('basic50','elite','elite-fast','artillery-rollout')}
    groups['elite']['speed_up']=2
    assert qualification(groups,native)=='BELOW_MINIMUM'
    assert qualification({'basic50':dict(speed_up=100)},native)=='INCOMPLETE_WORKLOAD'
    assert qualification(groups,dict(build=dict(scope='native_core_slice')))=='INCOMPLETE_NATIVE_ENGINE'
    assert qualification(groups,native,diagnostic=True)=='DIAGNOSTIC_ONLY'


@pytest.mark.parametrize('rows,message', [([{}],'summary schema'),([{'error':'failed'}],'did not complete')])
def test_reported_work_cannot_qualify_bad_output(tmp_path,rows,message):
    host=tmp_path/'host.py'
    host.write_text('import json,sys\nfor s in sys.stdin: pass\n'+
        '\n'.join('print('+repr(json.dumps(row))+')' for row in rows)+'\n'+
        'print(json.dumps(dict(executed_fights=1,executed_steps=100,cache_hits=0)),file=sys.stderr)\n')
    with pytest.raises(ValueError,match=message):
        measure([sys.executable,str(host)],[{'mode':'alone'}])


def test_work_audit_preserves_js_and_counts_internal_steps():
    # Bounded positive control, own development seed. This unblocks trusting
    # the lexical-call instrumentation before any supplemental performance run.
    req=dict(mode='alone',options=dict(seed=20261004,scenario='mirror',duration=.1,width=650,
        army={'melee':1,'ranged':2,'artillery':1},ai=[{'level':'regular','lookahead':
            {'plans':['hold'],'horizon':.1,'dt':.1}}, {'level':'novice'}]))
    data=json.dumps(req)+'\n'
    plain=subprocess.run(['node',str(ROOT/'js_host.cjs')],input=data,text=True,capture_output=True,check=True)
    audited=subprocess.run(['node',str(ROOT/'work_audit_host.cjs')],input=data,text=True,capture_output=True,check=True)
    assert plain.stdout==audited.stdout
    counts=json.loads(audited.stderr)
    assert counts['executed_fights']==1 and counts['executed_steps']>0
    assert counts['forks']>0 and counts['branch_steps']>0 and counts['candidate_models']>0
    assert counts['scope']=='development_work_audit'


def test_unfinished_fight_rejected_even_with_valid_schema(tmp_path):
    from test_result_cache import SUMMARY
    host=tmp_path/'unfinished.py'
    host.write_text('import json,sys\nfor line in sys.stdin: print('+repr(json.dumps(dict(SUMMARY,t=0)))+')\n'
        'print(json.dumps(dict(executed_fights=1,executed_steps=0,cache_hits=0)),file=sys.stderr)\n')
    with pytest.raises(ValueError,match='termination condition'):
        measure([sys.executable,str(host)],[{'mode':'alone','options':{'scenario':'mirror','duration':20}}])


@pytest.mark.parametrize('key',['executed_fights','executed_steps','cache_hits'])
def test_boolean_work_metrics_rejected(tmp_path,key):
    from test_result_cache import SUMMARY
    metrics=dict(executed_fights=1,executed_steps=2700,cache_hits=0);metrics[key]=bool(metrics[key])
    host=tmp_path/'booleans.py'
    host.write_text('import sys,json\nfor line in sys.stdin: print('+repr(json.dumps(SUMMARY))+')\n'
        'print('+repr(json.dumps(metrics))+',file=sys.stderr)\n')
    with pytest.raises(RuntimeError,match='invalid execution metric'):
        measure([sys.executable,str(host)],[{'mode':'alone'}])


def test_step_metric_must_match_completed_fight_times(tmp_path):
    from test_result_cache import SUMMARY
    host=tmp_path/'steps.py'
    host.write_text('import sys,json\nfor line in sys.stdin: print('+repr(json.dumps(SUMMARY))+')\n'
        'print(json.dumps(dict(executed_fights=1,executed_steps=0,cache_hits=0)),file=sys.stderr)\n')
    with pytest.raises(RuntimeError,match='final fight times'):
        measure([sys.executable,str(host)],[{'mode':'alone'}])


def test_supplemental_groups_require_positive_search_work():
    native=dict(build=dict(scope='native_complete_engine'))
    groups={k:dict(speed_up=4,samples={'cpp':[{'execution':{}},{'execution':{}}]})
        for k in ('basic50','elite','elite-fast','artillery-rollout')}
    assert qualification(groups,native)=='MISSING_BRANCH_WORK'
    for name,g in groups.items():
        for sample in g['samples']['cpp']:
            sample['execution']={k:1 for k in ('branch_steps','forks','search_calls','inference_calls','artillery_rollouts')}
    assert qualification(groups,native)=='TIMING_PASSED_AWAITING_WORK_AND_CORRECTNESS_REVIEW'
    groups['elite']['samples']['cpp'][0]['execution']['inference_calls']=0
    assert qualification(groups,native)=='MISSING_BRANCH_WORK'


def test_compiler_bytes_and_object_bytes_invalidate_build_cache(tmp_path,monkeypatch):
    import importlib.util
    spec=importlib.util.spec_from_file_location('checkpoint_builder',ROOT/'build.py')
    builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
    monkeypatch.setattr(builder,'ROOT',tmp_path)
    (tmp_path/'src/native').mkdir(parents=True)
    for name in builder.TARGETS['native'][1]:
        (tmp_path/name).write_text('fixture translation unit\n')
    object_count=len(builder.TARGETS['native'][1])
    (tmp_path/'build.py').write_bytes((ROOT/'build.py').read_bytes())
    (tmp_path/'generate_native_tables.cjs').write_text('fixture recipe\n')
    (tmp_path/'generate_native_network.py').write_text('fixture network recipe\n')
    (tmp_path/'generate_native_catalog.cjs').write_text('fixture catalog recipe\n')
    (tmp_path.parent/'astelia_snapshot').mkdir(exist_ok=True)
    (tmp_path.parent/'astelia_snapshot/formation_sim.js').write_text('fixture frozen source\n')
    (tmp_path.parent/'astelia_snapshot/bc_net.json').write_text('fixture frozen network\n')
    compiler=tmp_path/'compiler';log=tmp_path/'compiles.log'
    def write_compiler(variant):
        compiler.write_text('#!'+sys.executable+'\nimport sys,pathlib\n'
            'if "--version" in sys.argv: print("clang fixture constant version")\n'
            'else:\n out=pathlib.Path(sys.argv[sys.argv.index("-o")+1]);out.write_bytes('+repr(variant.encode())+')\n'
            ' if "-c" in sys.argv:\n  with pathlib.Path('+repr(str(log))+').open("a") as f:f.write("compile\\n")\n')
        compiler.chmod(0o755)
    monkeypatch.setattr(sys,'argv',['build.py','--engine','native','--portable','--compiler',str(compiler)])
    write_compiler('first');builder.main();assert len(log.read_text().splitlines())==object_count
    # Same --version, different executable: every object must be rebuilt.
    write_compiler('second');builder.main();assert len(log.read_text().splitlines())==2*object_count
    (tmp_path/'build/astelia_native_world.o').write_bytes(b'changed object')
    builder.main();assert len(log.read_text().splitlines())==2*object_count+1
