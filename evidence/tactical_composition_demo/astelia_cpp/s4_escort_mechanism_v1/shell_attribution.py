#!/usr/bin/env python3
"""Exact stored-shell attribution supplement, no simulations or engine imports.
Matches artillery damage to unique source+scheduled-impact within one tick.
Complements analyze.py to resolve intentional targeting versus incidental splash.
"""
import collections as C
import gzip,json,pathlib,time
from analyze import SOURCE,HERE,sha,verify,dump,binof,ROLES,cohort

def analyze_shells(f):
 pending=C.defaultdict(list);shells=[];registry=None;previous=None;attributions=C.Counter()
 with gzip.open(SOURCE/'raw'/(f['id']+'.jsonl.gz'),'rt') as stream:
  for line in stream:
   if '"observerV1":true' not in line[:70] and '"observerV1": true' not in line[:70]:continue
   r=json.loads(line)
   if registry is None:registry={u[0]:u for u in r['units']};previous=r;continue
   dt=r['t']-previous['t'];assert abs(dt-1/30)<1e-10
   for l in r['launches']:
    assert not l[8] and not l[9]
    s=dict(source=l[0],target=l[1],side=l[2],born=l[5],at=l[6],aim=cohort(registry[l[1]]),hp=C.Counter(),victims=C.defaultdict(set))
    shells.append(s);pending[l[0]].append(s)
   for d in r['damage']:
    if d['sourceRole']!='artillery' or d['dealt']<=0:continue
    due=[s for s in pending[d['source']] if -1e-9<=d['t']-s['at']<=dt+1e-7]
    assert len(due)==1,('ambiguous shell',f['id'],d,due)
    s=due[0];v=cohort(registry[d['target']]);s['hp'][v]+=d['dealt'];s['victims'][v].add(d['target'])
    if d['died'] and d['sourceTeam']==0 and d['targetTeam']==1 and d['targetRole']=='ranged':
     for cutoff in (20,30):
      if d['t']<cutoff:attributions[(cutoff,s['aim'])]+=1
   for src in pending:pending[src]=[s for s in pending[src] if r['t']-s['at']<=dt+1e-7]
   previous=r
 c=C.Counter()
 for s in shells:
  source='own' if s['side']==0 else 'enemy';b=binof(s['born']);key=(b,source,s['aim'])
  c[key+('shells',)]+=1
  for victim,hp in s['hp'].items():
   c[key+('hp_to_'+victim,)]+=hp;c[key+('victims_'+victim,)]+=len(s['victims'][victim]);c[key+('successful_on_'+victim,)]+=1
 return dict(id=f['id'],arm=f['arm'],head=f['head'],shells=[dict(bin=b,source=src,aim=aim,metric=metric,value=v) for (b,src,aim,metric),v in sorted(c.items())],early_enemy_ranged_artillery_last_hits=[dict(before=cutoff,aim=aim,kills=v) for (cutoff,aim),v in sorted(attributions.items())])
def main():
 start=time.monotonic();v=verify();fights=json.loads((SOURCE/'FIGHTS.json').read_text());rows=[]
 for i,f in enumerate(fights):
  rows.append(analyze_shells(f))
  if (i+1)%20==0:print('shells',i+1,flush=True)
 cells=[]
 for arm in ('P11','P12','P13'):
  for head in ('regular','novice'):
   fs=[f for f in rows if f['arm']==arm and f['head']==head];c=C.Counter();k=C.Counter()
   for f in fs:
    for r in f['shells']:c[(r['bin'],r['source'],r['aim'],r['metric'])]+=r['value']
    for r in f['early_enemy_ranged_artillery_last_hits']:k[(r['before'],r['aim'])]+=r['kills']
   cells.append(dict(arm=arm,head=head,n=len(fs),shells=[dict(bin=b,source=src,aim=aim,metric=metric,value=x) for (b,src,aim,metric),x in sorted(c.items())],early_enemy_ranged_artillery_last_hits=[dict(before=cutoff,aim=aim,kills=x) for (cutoff,aim),x in sorted(k.items())]))
 dump(HERE/'SHELL_ATTRIBUTION.json',dict(status='DONE',scope='exact stored artillery impact attribution',raw_verification=v,script_sha256=sha(HERE/'shell_attribution.py'),elapsed_s=time.monotonic()-start,cells=cells,fights=rows))
if __name__=='__main__':main()
