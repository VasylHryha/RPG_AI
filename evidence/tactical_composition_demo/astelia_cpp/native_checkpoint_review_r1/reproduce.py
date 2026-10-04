"""Bounded engineering counterexamples, not an acceptance suite or AI panel."""
import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile

OUT=pathlib.Path(__file__).resolve().parent
ROOT=OUT.parent
sys.path.insert(0,str(ROOT))
from benchmark import measure
from build_admission import admit
from result_cache import Engine, prime_legacy, identity


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    before=admit(ROOT/'build/native_core_contract')
    manifest=json.loads((ROOT/'build/native_core_contract.build.json').read_text())
    compiler=manifest['compiler_path']
    objects=[ROOT/'build'/('native_core_contract_'+name+'.o') for name in ('world','combat','spatial')]
    command=[compiler,'-std=c++17','-O3','-fno-fast-math','-ffp-contract=off','-flto=thin',
        '-I'+str(ROOT/'src'),str(OUT/'edge_probe.cpp'),*[str(p) for p in objects],'-o',str(OUT/'edge_probe')]
    hashes={str(p):sha(p) for p in [pathlib.Path(compiler),OUT/'edge_probe.cpp',OUT/'reproduce.py',*objects]}
    compiled=subprocess.run(command,capture_output=True,text=True,check=True)
    (OUT/'compile.stdout.txt').write_text(compiled.stdout)
    (OUT/'compile.stderr.txt').write_text(compiled.stderr)
    probe=subprocess.check_output([str(OUT/'edge_probe')],text=True)
    (OUT/'edge_probe.stdout.json').write_text(probe)
    result={'scope':'bounded_adversarial_engineering_counterexamples','native_build':before,
        'probe_source_hashes':hashes,'compile_command':command,'edge_probe':json.loads(probe)}
    request={'mode':'alone','options':{'scenario':'mirror','duration':20,'seed':2026100409,
        'army':{'melee':1,'ranged':1,'artillery':0},'ai':[{'level':'novice'},{'level':'novice'}]}}
    base=dict(mode='alone',melee=0,ranged=0,artillery=0,total=0,wasted=0,
        monsterDeaths=0,hunterKills=0,aliveSeconds=0,enemyDamage=0,survivors=2,enemySurvivors=2,t=0)
    with tempfile.TemporaryDirectory(prefix='astelia-review-') as tmp:
        tmp=pathlib.Path(tmp)
        fake=tmp/'unfinished.py'
        fake.write_text('import sys,json\nfor line in sys.stdin: print('+repr(json.dumps(base))+')\n'
            'print(json.dumps(dict(executed_fights=True,executed_steps=True,cache_hits=0)),file=sys.stderr)\n')
        timing,rows=measure([sys.executable,str(fake)],[request])
        result['unfinished_fight_accepted']=dict(request=request,returned=rows[0],execution=timing['execution'])

        changing=tmp/'changing.py'
        changing.write_text('import json,sys,pathlib\nfor line in sys.stdin:\n'
            ' p=pathlib.Path(__file__);p.write_text(p.read_text()+"# identity changed\\n")\n'
            ' print('+repr(json.dumps(dict(base,t=20)))+',flush=True)\n')
        engine=Engine('test',[sys.executable,str(changing)],tmp/'changing-cache')
        engine.fight(request)
        entry_exists=engine.cache.path(request).exists()
        try:engine.close();error=None
        except RuntimeError as e:error=str(e)
        result['identity_changed_result_cached']=dict(entry_exists=entry_exists,close_error=error)

        wrong=tmp/'different_js_host.cjs'
        wrong.write_text('const rl=require("readline").createInterface({input:process.stdin});'
            'rl.on("line",line=>{const r=JSON.parse(line);console.log(JSON.stringify({...'+json.dumps(base)+',mode:r.mode||"alone",wasted:999}));});')
        engine=Engine('js',['node',str(wrong)],tmp/'wrong-cache')
        primed=prime_legacy(engine)
        legacy_request=json.loads((ROOT/'check_fights.jsonl').read_text().splitlines()[0])
        cached=engine.fight(legacy_request)[-1]
        fresh=json.loads(subprocess.check_output(engine.command,input=json.dumps(legacy_request)+'\n',text=True))
        counts=engine.counts();engine.close()
        result['different_js_host_primed']=dict(imported=primed,counts=counts,
            cached_equals_actual_host=cached==fresh,cached=cached,fresh=fresh)

    huge=dict(request,options=dict(request['options'],dt=1e308,duration=1e308))
    huge_process=subprocess.run([str(ROOT/'build/astelia_native')],input=json.dumps(huge)+'\n',text=True,capture_output=True,check=True)
    result['huge_finite_dt_output']=json.loads(huge_process.stdout)
    for p,expected in hashes.items():
        if sha(pathlib.Path(p))!=expected:raise RuntimeError('probe inputs changed: '+p)
    if admit(ROOT/'build/native_core_contract')!=before:raise RuntimeError('native source changed')
    result['probe_binary_sha256']=sha(OUT/'edge_probe')
    result['harness_source_hashes']={name:sha(ROOT/name) for name in
        ('benchmark.py','result_cache.py','result_schema.py','build_admission.py')}
    (OUT/'counterexamples.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in
        ('native_build','probe_source_hashes','compile_command','harness_source_hashes')},indent=2))


if __name__=='__main__':main()
