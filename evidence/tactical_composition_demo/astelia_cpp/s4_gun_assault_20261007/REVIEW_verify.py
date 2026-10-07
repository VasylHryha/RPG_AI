"""Independent stored-only owner review: no engine execution or replay."""
import pathlib,json,gzip,hashlib,collections,math,time
H=pathlib.Path(__file__).resolve().parent;R=H.parents[3]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def read(n):return json.loads((H/n).read_text())
def main():
 start=time.monotonic(); rec=read('FIGHTS.json'); summary=read('SUMMARY.json');identity=read('INPUT_IDENTITY.json');inventory=read('RAW_FILES_LOCAL.json')
 assert len(rec)==120 and len({r['id'] for r in rec})==120
 expected={(a,h,c,o) for a in ['v5_resonator','v6_resonator','v6_morale'] for h in ['regular','novice'] for c in range(10) for o in range(2)}
 assert {(r['arm'],r['head'],r['cluster'],r['orientation']) for r in rec}==expected
 for p,v in inventory.items():assert (H/p).stat().st_size==v['bytes'] and sha(H/p)==v['sha256'],p
 for p,v in identity['protected'].items():assert sha(R/p)==v,p
 for p,v in identity['script_hashes'].items():assert sha(H/p)==v,p
 for p,v in identity['knob_files'].items():assert sha(R/p)==v,p
 assert sha(H.parent/'test_observer_v1.py')==identity['test_sha256']
 for build in ['observer_build','v6_build']:
  v=identity[build];print('build keys',build,list(v))
 compact=[read(r['id']+'_summary.json') for r in rec];cells={}
 for cell,s in summary.items():
  a,h=cell.split('|');rows=[r for r in compact if r['arm']==a and r['head']==h];o=[r['outcomes'] for r in rows]
  assert sum(x['elimination_win'] for x in o)==s['elimination_wins'];assert sum(x['timeout'] for x in o)==s['timeouts']
  assert sum(x['S'] for x in o)/20==s['mean_S'];assert sum(x['guns_destroyed'] for x in o)/20==s['mean_guns_destroyed']
  assert sum(x['own_losses'] for x in o)/20==s['mean_own_losses']
  apps=[ep for r in rows for ep in r['approaches']];assert len(apps)==s['approaches']['count'];assert dict(collections.Counter(ep['outcome'] for ep in apps))==s['approaches']['outcomes']
  for ep in apps:assert ep['exit_t']>=ep['enter_t'] and ep['damage_to_gun']>=0
  cells[cell]=dict(wins=s['elimination_wins'],timeouts=s['timeouts'],approaches=len(apps))
 novice=[g for r in compact if r['head']=='novice' for g in r['gun_deaths']];regular=[d for r in compact if r['head']=='regular' for d in r['own_deaths']]
 assert len(novice)==565 and sum(g['killer']['role']=='artillery' and g['killer']['team']==0 for g in novice)==556
 assert len(regular)==2263 and sum(d['sourceRole']=='artillery' and d['sourceTeam']==1 for d in regular)==1832
 assert sum(d['sourceRole']=='artillery' and d['sourceTeam']==1 and d['gun_only_before_tick'] for d in regular)==595
 selected=[r for r in rec if r['cluster']==0 and r['orientation']==0];recounts=[]
 for r in selected:
  t0=time.monotonic();ticks=events=own=gun=entries=same_tick=duplicate=0;end=None;deaths=[];raw_entries=[];damage=collections.Counter()
  with gzip.open(H/r['raw_file'],'rt') as f:
   for line in f:
    v=json.loads(line)
    if not v.get('observerV1'):end=v;continue
    ticks+=1;events+=len(v['damage']);own+=sum(d['died'] and d['targetTeam']==0 for d in v['damage']);gun+=sum(d['died'] and d['targetTeam']==1 and d['targetRole']=='artillery' for d in v['damage'])
    for d in v['damage']:
     assert d['died']==(d['killer'] is not None)
     assert math.isclose(d['distance'],math.hypot(d['sourceX']-d['targetX'],d['sourceY']-d['targetY']),abs_tol=1e-9)
     damage[str(d['sourceTeam'])+'_'+str(d['targetTeam'])]+=d['dealt']
     if d['died'] and d['targetTeam']==0:deaths.append((d['source'],d['target'],d['t'],d['distance']))
    dead={d['target'] for d in v['damage'] if d['died']}
    for e in v['entries']:
     assert math.hypot(e['from'][0]-e['gunPos'][0],e['from'][1]-e['gunPos'][1])>e['distance']
     raw_entries.append((e['unit'],e['gun'],e['t']));same_tick+=e['unit'] in dead
    entries+=len(v['entries']);duplicate+=sum(n-1 for n in collections.Counter((e['unit'],e['gun']) for e in v['entries']).values())
  c=read(r['id']+'_summary.json');assert own==len(c['own_deaths']) and gun==len(c['gun_deaths'])
  assert deaths==[(d['source'],d['target'],d['t'],d['distance']) for d in c['own_deaths']]
  if r['head']=='regular':assert raw_entries==[(e['unit'],e['gun'],e['enter_t']) for e in c['approaches']]
  assert ticks==r['metrics']['executed_steps']+1 and end==r['summary']
  for a,b,field in [(0,1,'crossTeamDealt'),(1,0,'crossTeamDealt'),(0,0,'friendlyDealt'),(1,1,'friendlyDealt')]:assert math.isclose(damage[str(a)+'_'+str(b)],end[field][a],abs_tol=1e-6)
  recounts.append(dict(id=r['id'],ticks=ticks,events=events,own_deaths=own,enemy_gun_deaths=gun,entries=entries,same_tick_dying_entries=same_tick,duplicate_pair_entries_same_tick=duplicate,seconds=time.monotonic()-t0));print(recounts[-1],flush=True)
 parity=read('PARITY.json');assert sum(c['bytes_compared'] for c in parity['cases'])==657268150
 assert len(parity['cases'])==6 and parity['engineering_fights']==18
 for c in parity['cases']:
  for name in ['historical','off','on']:
   h=hashlib.sha256();length=0
   with gzip.open(H/'raw'/f"parity_{c['arm']}_{c['head']}_{name}.jsonl.gz",'rb') as f:
    for line in f:
     if not line.startswith(b'{"observerV1":true'):h.update(line);length+=len(line)
   assert length==c['bytes_compared'] and h.hexdigest()==c['actions_outcomes_sha256']
 result=dict(status='PASS',scope='stored-only; zero engine fights/tests; full compact arithmetic and inventory hashes; six representative full raw traces; all eighteen parity raw stdout hashes',cells=cells,all_raw_files_verified=len(inventory),protected_files_verified=len(identity['protected']),novice_guns=565,novice_guns_killed_by_own_artillery=556,regular_own_deaths=2263,regular_own_deaths_by_enemy_artillery=1832,regular_gun_only_deaths_by_enemy_artillery=595,parity_bytes=657268150,recounts=recounts,elapsed_seconds=time.monotonic()-start)
 (H/'REVIEW_VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
