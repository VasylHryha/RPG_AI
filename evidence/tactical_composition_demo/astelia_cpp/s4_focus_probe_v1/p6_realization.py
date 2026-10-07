"""Stored-only review-driven audit of P6 reach opportunities and novice equivalence."""
import pathlib,json,gzip,hashlib,time,math,signal
HERE=pathlib.Path(__file__).resolve().parent

def digest_plain(p):
 h=hashlib.sha256()
 with gzip.open(p,'rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def main():
 start=time.time();awake=time.monotonic();signal.signal(signal.SIGALRM,lambda a,b:(_ for _ in ()).throw(TimeoutError('realization audit cap')));signal.alarm(300)
 rows=json.loads((HERE/'FIGHTS.json').read_text());index={(r['arm'],r['head'],r['cluster'],r['orientation']):r for r in rows};audits=[];same=[]
 for r in rows:
  if r['arm']!='P6':continue
  previous=None;opportunities=actions=0
  with gzip.open(HERE/'raw'/(r['id']+'.jsonl.gz'),'rt') as f:
   for line in f:
    row=json.loads(line)
    if not row.get('observerV1'):continue
    if previous is not None:
     guns=[u for u in previous if u[1]==0 and u[2]==2];enemies=sorted((u for u in previous if u[1]==1 and u[2]==2),key=lambda u:(u[5],u[0]))
     if enemies:
      anchor=next((e for e in enemies if any(g[8]<=math.hypot(g[3]-e[3],g[4]-e[4])<=g[7] for g in guns)),enemies[0]);actual={a[0]:a for a in row['actions'] if a[1]==0}
      for u in previous:
       if u[1]==0 and u[2]==1 and math.hypot(u[3]-anchor[3],u[4]-anchor[4])-u[6]-anchor[6]<=u[7]:
        opportunities+=1
        if u[0] in actual:
         assert actual[u[0]][2]==anchor[0],(r['id'],row['step'],u[0],actual[u[0]][2],anchor[0]);actions+=1
    previous=row['units']
  audits.append(dict(id=r['id'],head=r['head'],reachable_direct_unit_ticks=opportunities,focus_actions=actions))
  if r['head']=='novice':
   p5=index['P5',r['head'],r['cluster'],r['orientation']];a=digest_plain(HERE/'raw'/(p5['id']+'.jsonl.gz'));b=digest_plain(HERE/'raw'/(r['id']+'.jsonl.gz'));same.append(dict(cluster=r['cluster'],orientation=r['orientation'],byte_identical=a==b,p5_plain_sha256=a,p6_plain_sha256=b))
 aggregate={h:dict(reachable_direct_unit_ticks=sum(r['reachable_direct_unit_ticks'] for r in audits if r['head']==h),focus_actions=sum(r['focus_actions'] for r in audits if r['head']==h),fights_with_opportunity=sum(r['reachable_direct_unit_ticks']>0 for r in audits if r['head']==h)) for h in ('regular','novice')}
 result=dict(status='PASS',scope='stored-only confound measurement, no policy/settings/outcome change',aggregates=aggregate,novice_plain_byte_identical_fights=sum(r['byte_identical'] for r in same),novice_comparisons=same,fights=audits,elapsed_seconds=time.time()-start,awake_seconds=time.monotonic()-awake)
 (HERE/'P6_REALIZATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(aggregates=aggregate,novice_plain_byte_identical_fights=result['novice_plain_byte_identical_fights'],awake_seconds=result['awake_seconds'])))
if __name__=='__main__':main()
