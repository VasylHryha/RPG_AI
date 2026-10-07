"""Stored-only recount: no native execution, no original receipt writes."""
import ast,collections,gzip,hashlib,json,math,pathlib,subprocess,sys,time
OUT=pathlib.Path(__file__).resolve().parent
V4=OUT.parent/'s4_escort_probe_v4';REPO=OUT.parents[3]
sys.path.insert(0,str(V4))
from common import sha
start=time.monotonic()
inv=json.loads((V4/'RAW_FILES_LOCAL.json').read_text())
assert {r['path'] for r in inv['files']}=={str(p.relative_to(V4)) for p in (V4/'raw').iterdir() if p.is_file()}
for r in inv['files']:
 p=V4/r['path'];assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],r['path']
d=json.loads((V4/'DECLARATION.json').read_text())
assert sha(V4/'DECLARATION.json')==json.loads((V4/'SEAL.json').read_text())['declaration_sha256']
for n,h in {**d['protected'],**d['implementation_hashes']}.items():assert sha(REPO/n)==h,n
from common import pins,checked_binary
assert pins()==d
identity=checked_binary()
old=json.loads((V4.parent/'s4_escort_probe_v3/DECLARATION.json').read_text())
assert identity==d['exact_v3']['binary_identity']==json.loads((V4.parent/'s4_escort_probe_v3/BUILD.json').read_text())['identity']
for h in d['heads']:
 a=json.loads((V4/(h.upper()+'_REQUEST_TEMPLATE.json')).read_text());b=json.loads((V4.parent/'s4_escort_probe_v3'/(h.upper()+'_REQUEST_TEMPLATE.json')).read_text());a['options']['seed']=b['options']['seed'];assert a==b
used=set()
def collect(v):
 if type(v) is int:used.add(v)
 elif isinstance(v,list):
  for x in v:collect(x)
 elif isinstance(v,dict):
  for x in v.values():collect(x)
ledger=json.loads((V4/'DEVELOPMENT_SEED_LEDGER.json').read_text())
for n,h in ledger['previous_development_ledgers'].items():assert sha(REPO/n)==h;collect(json.loads((REPO/n).read_text()))
fresh=d['development_seeds']+[d['engineering_seed']]
assert len(fresh)==len(set(fresh))==21 and not set(fresh)&used
assert all(0xC0000000<=x<=0xffffffff for x in fresh)
assert ledger['seeds']==d['development_seeds'] and ledger['engineering_seed']==d['engineering_seed']
import analyze,run
fights=json.loads((V4/'FIGHTS.json').read_text());assert len(fights)==160
for r in fights:
 tag,req,_=run.task(d,r['arm'],r['head'],r['cluster'],r['orientation']);assert run.verified(tag,req)==r
controls=[r for r in fights if r['arm']=='P12'];interventions=[r for r in fights if r['arm']=='P16']
san=json.loads((V4/'P12_SANITY.json').read_text())
assert max(r['utc_end'] for r in controls)<=san['utc']<=min(r['utc_start'] for r in interventions)
assert {k:v for k,v in san.items() if k!='utc'}=={k:v for k,v in run.sanity(controls).items() if k!='utc'}
comparisons=collections.Counter();original=analyze.verify_guns
from metrics import gun_focus_oracle
initials={};wins=[]
def check_guns(row,before,actions,c):
 original(row,before,actions,c)
 oracle=gun_focus_oracle(list(before.values()),row['width'],row['height'],False)
 for g in row['gunFocus']:
  q=oracle.get(g['id']);b=g['p12'];command=g['command']
  if q and row['accepted']:
   assert all(math.isclose(b[i],q['command'][i],abs_tol=1e-7) for i in range(4))
   if q['target'] is not None:assert b[4]==q['target']
  comparisons['gun_ticks']+=1
  if row['arm']==16:
   assert b[5]==command[5];comparisons['P16_changed_gun_targets']+=b[4]!=command[4];comparisons['P16_changed_gun_movement']+=b[:4]!=command[:4]
 if row['arm']==16:
  for p in row['points']:assert p['command']==p['p12'];comparisons['P16_non_gun_commands']+=1
analyze.verify_guns=check_guns
# Recompute sealed measurement functions, disabling ONLY the completion shortcut
# and redirecting outputs to memory. No stage decorator or main script execution.
module=ast.parse((V4/'analyze.py').read_text());fn=next(n for n in module.body if isinstance(n,ast.FunctionDef) and n.name=='main');fn.decorator_list=[]
fn.body=[n for n in fn.body if not (isinstance(n,ast.If) and isinstance(n.test,ast.Call) and isinstance(n.test.func,ast.Attribute) and n.test.func.attr=='exists')]
recomputed={};analyze.write=lambda p,v:recomputed.setdefault(pathlib.Path(p).name,v);analyze.remaining=lambda:3600
exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),str(OUT/'recheck.py'),'exec'),analyze.__dict__)
analyze.main()
for name in ('COMPACT.json','SUMMARY.json','ANALYSIS_VERIFICATION.json'):assert recomputed[name]==json.loads((V4/name).read_text()),('recount mismatch',name)
print('FULL RECOUNT EXACT MATCH',flush=True)
# Independent terminal/event reconciliation and paired initial snapshots.
for r in fights:
 initial=terminal=last=None;deaths=[]
 with gzip.open(V4/'raw'/(r['id']+'.jsonl.gz'),'rt') as f:
  for line in f:
   row=json.loads(line)
   if row.get('observerV1'):
    if initial is None:initial=row
    last=row;deaths.extend(x for x in row['damage'] if x['died'])
   if 'controllerStatus' in row:terminal=row
 assert terminal==r['summary'] and last['t']==terminal['t']
 assert [sum(u[1]==s for u in last['units']) for s in (0,1)]==[terminal['survivors'],terminal['enemySurvivors']]
 assert [sum(u[1]==s and u[2]==2 for u in last['units']) for s in (0,1)]==terminal['artilleryAlive']
 assert [sum(u[1]==s for u in initial['units']) for s in (0,1)]==[50,50]
 assert len(deaths)==len(set(x['target'] for x in deaths))==100-len(last['units'])
 assert {u[0] for u in initial['units']}-{x['target'] for x in deaths}=={u[0] for u in last['units']}
 key=(r['head'],r['cluster'],r['orientation'])
 if r['arm']=='P12':initials[key]=initial
 else:assert initials[key]==initial
 if r['head']=='regular' and terminal['enemySurvivors']==0 and terminal['survivors']>=1 and terminal['t']<150:
  wins.append(dict(arm=r['arm'],cluster=r['cluster'],orientation=r['orientation'],time_s=terminal['t'],own=terminal['survivors'],enemy=terminal['enemySurvivors']))
assert collections.Counter(x['arm'] for x in wins)=={'P12':12,'P16':34}
v=dict(status='PASS',raw_files_verified=len(inv['files']),reviewed_run_commit='f0bb8a6',current_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),binary_sha256=identity['binary_sha256'],recount_exact=['COMPACT.json','SUMMARY.json','ANALYSIS_VERIFICATION.json'],same_observation_comparisons=dict(comparisons),regular_wins=wins,paired_clusters=recomputed['COMPACT.json']['paired_clusters'],seconds=time.monotonic()-start,combat_executed=False)
(OUT/'VERIFICATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps({k:v for k,v in v.items() if k not in ('paired_clusters','regular_wins')}))
