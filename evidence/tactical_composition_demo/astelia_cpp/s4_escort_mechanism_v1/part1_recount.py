"""Stored-only reviewer recount. Never imports/calls run, seal, engineering or combat.

Verify the local inventory before parsing traces. Reuse the sealed pure numeric
analyzers, after source inspection, to compare EVERY SUMMARY/COMPACT value.
A separate trace scan reconciles all terminal units, deaths and HP independently.
All writes are new part1_* files; original receipts and raw files are read-only.
"""
import collections,gzip,hashlib,importlib.util,json,math,pathlib,sys,time
OUT=pathlib.Path(__file__).resolve().parent
SRC=OUT.parent/'s4_escort_probe_v1'
REPO=OUT.parents[3]
START=time.monotonic()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def load(p):return json.loads(p.read_text())
def save(n,d):(OUT/n).write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
inventory=load(SRC/'RAW_FILES_LOCAL.json')['files']
for e in inventory:
 p=SRC/e['path'];assert p.stat().st_size==e['bytes'] and sha(p)==e['sha256'],e['path']
assert {str(p.relative_to(SRC)) for p in (SRC/'raw').iterdir() if p.is_file()}=={e['path'] for e in inventory}
print('Verified raw inventory',len(inventory),flush=True)
d=load(SRC/'DECLARATION.json');old=load(SRC/'DECLARATION_BEFORE_SHARED_HEAD_REFRESH.json');seal=load(SRC/'SEAL.json')
assert sha(SRC/'DECLARATION.json')==seal['declaration_sha256']
assert sha(SRC/'DECLARATION_BEFORE_SHARED_HEAD_REFRESH.json')==seal['original_declaration_sha256']
changes=[]
def diff(a,b,p=''):
 if isinstance(a,dict) and isinstance(b,dict):
  for k in a.keys()|b.keys():
   if k not in a or k not in b:changes.append(p+k)
   else:diff(a[k],b[k],p+k+'/')
 elif a!=b:changes.append(p.rstrip('/'))
diff(old,d)
assert set(changes)=={'protected/docs/PLAN_CURRENT.md','precombat_metadata_refresh'},changes
for name,h in d['implementation_hashes'].items():assert sha(REPO/name)==h,name
assert sha(SRC/'POLICY.md')==d['policy_sha256']
ledger=load(SRC/'DEVELOPMENT_SEED_LEDGER.json');assert sha(SRC/'DEVELOPMENT_SEED_LEDGER.json')==d['development_ledger_sha256'];assert ledger['seeds']==d['development_seeds'] and ledger['engineering_seed']==d['engineering_seed']
assert len(set(d['development_seeds']+[d['engineering_seed']]))==11
for head,h in d['template_sha256'].items():assert sha(SRC/(head.upper()+'_REQUEST_TEMPLATE.json'))==h
build=load(SRC/'BUILD.json')['identity'];assert sha(SRC.parent/'build/astelia_native_escort_probe_v1')==build['binary_sha256']
for name,h in build['sources'].items():assert sha(SRC.parent/name)==h,name
fights=load(SRC/'FIGHTS.json');sanity=load(SRC/'P11_SANITY.json')
assert len(fights)==120
assert {(r['arm'],r['head'],r['cluster'],r['orientation']) for r in fights}=={(a,h,c,o) for a in d['arms'] for h in d['heads'] for c in range(10) for o in d['orientations']}
assert max(r['utc_end'] for r in fights if r['arm']=='P11')<=sanity['utc']<=min(r['utc_start'] for r in fights if r['arm']!='P11')
assert seal['utc']<min(r['utc_start'] for r in fights)
for r in fights:
 tag=r['id'];c=load(SRC/'raw'/(tag+'_CLAIM.json'));complete=load(SRC/'raw'/(tag+'_COMPLETE.json'));req=load(SRC/'raw'/(tag+'_request.json'));expected=load(SRC/(r['head'].upper()+'_REQUEST_TEMPLATE.json'));expected['options'].update(seed=d['development_seeds'][r['cluster']],swapSides=bool(r['orientation']),duration=150);expected['options']['ai'][0].update(controller=r['arm'],skeleton='escort_probe_v1')
 assert req==expected and r==complete
 assert c['declaration_sha256']==seal['declaration_sha256'] and c['binary']==r['binary']==build
 assert r['claim_sha256']==sha(SRC/'raw'/(tag+'_CLAIM.json')) and c['request_sha256']==r['request_sha256']==sha(SRC/'raw'/(tag+'_request.json'))
 assert r['raw_sha256']==sha(SRC/'raw'/(tag+'.jsonl.gz')) and r['stderr_sha256']==sha(SRC/'raw'/(tag+'_stderr.log'))
 gate=SRC/c['gate']['path'];assert sha(gate)==c['gate']['sha256'];g=load(gate);assert g['status']=='CLEAR' and g['utc_end']<=r['utc_start'];assert g['declaration_sha256']==seal['declaration_sha256']
 assert r['metrics']['executed_fights']==1 and all(r['metrics'][k]==0 for k in ['forks','search_calls','branch_steps','artillery_rollouts'])
print('Verified all requests, claims, completions, code and binary',flush=True)
# Read-only import; no __main__, stage wrapper, gate, or subprocess is called.
sys.path.insert(0,str(SRC));spec=importlib.util.spec_from_file_location('sealed_escort_numeric',SRC/'analyze.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
a.remaining=lambda:1
recount={}
def capture(p,v):recount[p.name]=v
a.write=capture
source=(SRC/'analyze.py').read_text();body=source[source.index(' rows=[];per=[]'):source.index("if __name__=='__main__':")]
exec("def reviewer_reaggregate():\n d="+repr(d)+"\n fights="+repr(fights)+"\n"+body,a.__dict__)
a.reviewer_reaggregate()
for n in ['COMPACT.json','SUMMARY.json','ANALYSIS_VERIFICATION.json']:assert recount[n]==load(SRC/n),n
print('Exact equality of every numeric receipt field',flush=True)
# Independent reconciliation, separate from the reused numerical analyzer.
checked=[];wins=[]
for r in fights:
 initial=None;latest=None;terminal=None;dead=set();hp=collections.Counter();step=-1
 with gzip.open(SRC/'raw'/(r['id']+'.jsonl.gz'),'rt') as f:
  for line in f:
   q=json.loads(line)
   if q.get('observerV1'):
    assert q['step']==step+1;step=q['step'];latest=q
    if initial is None:initial={u[0]:u for u in q['units']};assert len(initial)==100
    for e in q['damage']:
     hp[e['target']]+=e['dealt']
     if e['died']:assert e['target'] not in dead;dead.add(e['target'])
   elif 'controllerStatus' in q:terminal=q
 alive={u[0]:u for u in latest['units']};assert set(initial)-dead==set(alive)
 for uid,u in initial.items():assert math.isclose(u[5]-alive.get(uid,[0]*6)[5],hp[uid],abs_tol=1e-7),(r['id'],uid)
 own=sum(u[1]==0 for u in alive.values());enemy=sum(u[1]==1 for u in alive.values());guns=[sum(u[1]==s and u[2]==2 for u in alive.values()) for s in [0,1]]
 assert terminal==r['summary'] and terminal['survivors']==own and terminal['enemySurvivors']==enemy and terminal['artilleryAlive']==guns and terminal['t']==latest['t']
 assert terminal['controllerStatus']=='completed' and not any(terminal['controllerFailures'])
 item=dict(id=r['id'],t=terminal['t'],own_survivors=own,enemy_survivors=enemy,own_guns=guns[0],enemy_guns=guns[1],all_deaths_and_HP_reconciled=True)
 checked.append(item)
 if r['head']=='regular' and r['arm'] in ['P12','P13'] and enemy==0 and own>0 and terminal['t']<150:wins.append(item)
assert len(wins)==11
save('part1_recount.json',dict(status='PASS',raw_inventory_files=len(inventory),raw_inventory_sha256=sha(SRC/'RAW_FILES_LOCAL.json'),declaration_sha256=seal['declaration_sha256'],summary_sha256=sha(SRC/'SUMMARY.json'),compact_sha256=sha(SRC/'COMPACT.json'),sealed_numeric_reaggregation_exact=True,review_method='Audited sealed pure numeric functions reused; separate independent full trace HP/death/survivor reconciliation',metadata_changes_before_fights=changes,P11_end=max(r['utc_end'] for r in fights if r['arm']=='P11'),P11_reported=sanity['utc'],first_intervention=min(r['utc_start'] for r in fights if r['arm']!='P11'),regular_intervention_wins=wins,fight_reconciliation=checked,elapsed_s=time.monotonic()-START))
print('PASS',time.monotonic()-START,flush=True)
