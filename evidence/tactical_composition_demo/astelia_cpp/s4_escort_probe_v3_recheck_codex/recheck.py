"""Stored-only recount. Never writes v3 or invokes a native executable."""
import hashlib,json,pathlib,sys,subprocess,time,math
OUT=pathlib.Path(__file__).resolve().parent
V3=OUT.parent/'s4_escort_probe_v3';REPO=OUT.parents[3]
sys.path.insert(0,str(V3))
from common import sha
start=time.monotonic()
inv=json.loads((V3/'RAW_FILES_LOCAL.json').read_text())
assert {r['path'] for r in inv['files']}=={str(p.relative_to(V3)) for p in (V3/'raw').iterdir() if p.is_file()}
for r in inv['files']:
 p=V3/r['path'];assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],r['path']
d=json.loads((V3/'DECLARATION.json').read_text());assert sha(V3/'DECLARATION.json')==json.loads((V3/'SEAL.json').read_text())['declaration_sha256']
historical={}
for n,h in {**d['protected'],**d['implementation_hashes']}.items():
 if sha(REPO/n)!=h:
  assert n in ('docs/PLAN_CURRENT.md','evidence/tactical_composition_demo/DESIGN_0G.md'),n
  # The sealed pre-run docs live at the implementation commit; do not restore them.
  data=subprocess.check_output(['git','show','a9dfc6f:'+n],cwd=REPO)
  assert hashlib.sha256(data).hexdigest()==h,n
  historical[n]=h
from build_admission import admit
from common import BINARY
identity=admit(BINARY)
assert identity==json.loads((V3/'BUILD.json').read_text())['identity']==json.loads((V3/'CHECKS.json').read_text())['binary_identity']
import analyze,run
fights=json.loads((V3/'FIGHTS.json').read_text());assert len(fights)==120
for r in fights:
 tag,req,_=run.task(d,r['arm'],r['head'],r['cluster'],r['orientation']);assert run.verified(tag,req)==r
controls=[r for r in fights if r['arm']=='P12'];interventions=[r for r in fights if r['arm']!='P12']
assert max(r['utc_end'] for r in controls)<=min(r['utc_start'] for r in interventions)
san=json.loads((V3/'P12_SANITY.json').read_text());assert san['utc']<=min(r['utc_start'] for r in interventions)
recomputed={};comparisons={'gun_ticks':0,'changed_gun_commands':0,'non_gun_P16_commands':0}
original=analyze.verify_guns
from metrics import gun_focus_oracle

def check_guns(row,before,actions,c):
 original(row,before,actions,c)
 if row['arm'] not in (12,16):return
 oracle=gun_focus_oracle(list(before.values()),row['width'],row['height'],False)
 for g in row['gunFocus']:
  q=oracle.get(g['id']);b=g['p12'];command=g['command']
  if q and row['accepted']:
   assert all(math.isclose(b[i],q['command'][i],abs_tol=1e-7) for i in range(4))
   if q['target'] is not None:assert b[4]==q['target']
  comparisons['gun_ticks']+=1
  if row['arm']==16:comparisons['changed_gun_commands']+=b!=command
 if row['arm']==16:
  for p in row['points']:
   assert p['command']==p['p12'],'non-gun policy difference'
   comparisons['non_gun_P16_commands']+=1
analyze.verify_guns=check_guns
analyze.pins=lambda:d
analyze.remaining=lambda:3600
analyze.write=lambda p,v:recomputed.setdefault(pathlib.Path(p).name,v)
analyze.main.__wrapped__()
for name in ('COMPACT.json','SUMMARY.json','ANALYSIS_VERIFICATION.json'):
 assert recomputed[name]==json.loads((V3/name).read_text()),('recount mismatch',name)
# Each observer's terminal units independently reconcile end counts.
import gzip
wins=[]
for r in fights:
 initial=terminal=last=None
 with gzip.open(V3/'raw'/(r['id']+'.jsonl.gz'),'rt') as f:
  for line in f:
   row=json.loads(line)
   if row.get('observerV1'):
    if initial is None:initial=row
    last=row
   if 'controllerStatus' in row:terminal=row
 assert terminal==r['summary'] and last['t']==terminal['t']
 assert [sum(u[1]==s for u in last['units']) for s in (0,1)]==[terminal['survivors'],terminal['enemySurvivors']]
 assert [sum(u[1]==s and u[2]==2 for u in last['units']) for s in (0,1)]==terminal['artilleryAlive']
 assert [sum(u[1]==s for u in initial['units']) for s in (0,1)]==[50,50]
 if r['arm']=='P16' and r['head']=='regular' and terminal['enemySurvivors']==0 and terminal['survivors']>=1 and terminal['t']<150:
  wins.append(dict(cluster=r['cluster'],orientation=r['orientation'],time_s=terminal['t'],own=terminal['survivors'],enemy=terminal['enemySurvivors']))
assert len(wins)==19
v=dict(status='PASS',raw_files_verified=len(inv['files']),reviewed_run_commit='d5044e8',current_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),historical_doc_pins=historical,binary_sha256=identity['binary_sha256'],recount_exact=['COMPACT.json','SUMMARY.json','ANALYSIS_VERIFICATION.json'],same_observation_comparisons=comparisons,P16_regular_wins=wins,paired_clusters=recomputed['COMPACT.json']['paired_clusters'],seconds=time.monotonic()-start,combat_executed=False)
(OUT/'VERIFICATION.json').write_text(json.dumps(v,indent=2)+'\n')
print(json.dumps(v))
