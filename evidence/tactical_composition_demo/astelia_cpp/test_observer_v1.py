"""Single end-of-batch check of the new host and frozen historical dispatch."""
import gzip,hashlib,json,pathlib,subprocess,sys
import pytest
ROOT=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'s4_gun_assault_20261007'))
from common import *

def test_versioned_copies_are_exact_except_observation_hooks():
 native=CPP/'src/native'
 for stem in ('world','combat_rules','abilities'):
  s=(native/('observer_v1_'+stem+'.cpp')).read_text().replace('#include "observer_v1.h"\n','',1)
  s=s.replace('  observer_v1::hit(*this,*src,*dst,amount,dealt);\n','').replace('observer_v1::launch(w,i,sh);','')
  s=s.replace('  const auto observerFrom=u.pos;\n','').replace('\n  observer_v1::movement(*this,slot,observerFrom);','')
  s=s.replace('\n  const auto observerFrom=w.units[i].pos;','').replace('observer_v1::movement(w,i,observerFrom);','')
  assert s==(native/(stem+'.cpp')).read_text()
 codec=(native/'observer_v1_config_codec.cpp').read_text().replace('"attributionDiagnostics","killerTelemetry"});','"attributionDiagnostics"});',1).replace('  boolean(request,"killerTelemetry",false);\n','',1).replace('if(c.decisionTrace&&!boolean(request,"trace",false)&&!boolean(request,"killerTelemetry",false))','if(c.decisionTrace&&!boolean(request,"trace",false))')
 assert codec==(native/'config_codec.cpp').read_text()
 assert_pins()

def test_historical_and_v6_no_combat_contract_stdout_identical():
 values=[]
 for arg in ('--attribution-contract','--v6-contract'):
  old=subprocess.run([str(CPP/'build/astelia_native_v6'),arg],capture_output=True,timeout=60,check=True)
  new=subprocess.run([str(BINARY),arg],capture_output=True,timeout=60,check=True)
  assert old.stdout==new.stdout and old.stderr==new.stderr
  values.append(dict(argument=arg,stdout_sha256=hashlib.sha256(new.stdout).hexdigest(),bytes=len(new.stdout),byte_identical=True))
 write(HERE/'HISTORICAL_CONTRACTS.json',dict(status='PASS',rows=values,fights=0))

@pytest.mark.parametrize('arm,head,orientation',[(a,h,int(h=='regular')) for a in ARMS for h in ('novice','regular')])
def test_actions_outcomes_and_damage_ledger_identical(arm,head,orientation):
 ledger=json.loads((RAW/'DEVELOPMENT_SEED_LEDGER.json').read_text());seed=ledger['engineering_seeds'][ARMS.index(arm)]
 outputs=[];metrics=[];observer=[];reqs=[]
 for name,on,binary in [('historical',False,CPP/'build/astelia_native_v6'),('off',False,BINARY),('on',True,BINARY)]:
  req=request_for(arm,head,seed,orientation,on,trace=True);reqs.append(req)
  run=subprocess.run([str(binary),'--metrics'],input=(json.dumps(req)+'\n').encode(),capture_output=True,timeout=90,check=True)
  path=RAW/f'parity_{arm}_{head}_{name}.jsonl.gz'
  with gzip.GzipFile(filename=str(path),mode='wb',mtime=0) as f:f.write(run.stdout)
  lines=run.stdout.splitlines(keepends=True);obs=[json.loads(l) for l in lines if l.startswith(b'{"observerV1":true')]
  outputs.append(b''.join(l for l in lines if not l.startswith(b'{"observerV1":true')));metrics.append(run.stderr)
  if on:observer=obs
 assert outputs[0]==outputs[1]==outputs[2];assert metrics[0]==metrics[1]==metrics[2]
 # State contains both armies' exact decisions. Observer actions must describe the same records.
 ticks=[json.loads(l) for l in outputs[2].splitlines() if b'"state"' in l];summary=json.loads(outputs[2].splitlines()[-1])
 assert 'error' not in summary,summary
 assert len(observer)==len(ticks)>10
 for obs,tick in zip(observer,ticks):
  assert obs['step']==tick['step']
  expected=[[d['id'],d['team'],d['target'] or 0,d['x'],d['y'],d['multiplier'],d['stop'],d['release'],d['move'],d['keep'],d['post'],d['bound'],d['inReach']] for d in tick['state'].get('decisions',[])]
  assert obs['actions']==expected
 events=[d for o in observer for d in o['damage']];deaths=[d for d in events if d['died']]
 assert events and len({d['target'] for d in deaths})==len(deaths)
 assert sum(d['targetTeam']==0 for d in deaths)==50-summary['survivors']
 assert sum(d['targetTeam']==1 for d in deaths)==50-summary['enemySurvivors']
 assert all(d['killer']==d['source'] for d in deaths)
 records_path=HERE/'PARITY_CASES.json'
 rows=json.loads(records_path.read_text()) if records_path.exists() else []
 rows.append(dict(arm=arm,head=head,orientation=orientation,engineering_seed=seed,actions_outcomes_sha256=hashlib.sha256(outputs[0]).hexdigest(),bytes_compared=len(outputs[0]),ticks=len(ticks),damage_events=len(events),deaths=len(deaths),summary=summary,metrics=json.loads(metrics[0])))
 write(records_path,rows)
 if len(rows)==6:write(HERE/'PARITY.json',dict(status='PASS',cases=rows,telemetry_on_off_and_historical_bytes_identical=True,heads=['novice','regular'],arms=ARMS,engineering_fights=18,diagnostic_fights=0))
