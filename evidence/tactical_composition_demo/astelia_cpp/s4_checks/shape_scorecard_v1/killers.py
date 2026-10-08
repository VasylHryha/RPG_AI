import gzip,json,sys,collections
from concurrent.futures import ProcessPoolExecutor
def one(f):
    kill=collections.Counter(); dmg=collections.Counter(); dodges=collections.Counter(); shells=collections.Counter(); hitshells=collections.defaultdict(set)
    with gzip.open(f,'rt') as fh:
        for line in fh:
            r=json.loads(line)
            if not r.get('observerV1'): continue
            for d in r['dodges']: dodges[d[1]]+=1
            for l in r['launches']: shells[l[2]]+=1
            for d in r['damage']:
                if d['sourceTeam']!=d['targetTeam']:
                    dmg[(d['targetTeam'],d['sourceRole'])]+=d['dealt']
                    if d['died']: kill[(d['targetTeam'],d['targetRole'],d['sourceRole'])]+=1
    return kill,dmg,dodges,shells
if __name__ == '__main__':
    fs=[a for a in sys.argv[1:]]
    K=collections.Counter();D=collections.Counter();DO=collections.Counter();SH=collections.Counter()
    with ProcessPoolExecutor(4) as ex:
        for k,d,do,sh in ex.map(one,fs): K.update(k);D.update(d);DO.update(do);SH.update(sh)
    n=len(fs)
    print('fights',n)
    for team in (0,1):
        tot=sum(v for (t,r,s),v in K.items() if t==team)
        print(f'team {team} deaths per fight {tot/n:.1f}; by killer role:',{s:round(sum(v for (t,r,ss),v in K.items() if t==team and ss==s)/max(tot,1),3) for s in ('artillery','ranged','melee')})
        for role in ('melee','ranged','artillery'):
            sub={s:v for (t,r,s),v in K.items() if t==team and r==role}; tt=sum(sub.values())
            print(f'   {role} deaths/fight {tt/n:.1f} killed by',{s:round(v/max(tt,1),2) for s,v in sub.items()})
        dt=sum(v for (t,s),v in D.items() if t==team)
        print('   damage taken share by source role',{s:round(v/dt,3) for (t,s),v in D.items() if t==team})
    print('dodges per fight by team',{t:round(v/n,1) for t,v in DO.items()})
    print('launch field[2] counts per fight',{t:round(v/n,1) for t,v in SH.items()})
