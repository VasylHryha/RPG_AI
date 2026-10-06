import json,collections,sys
calls=[json.loads(l) for l in open(sys.argv[1])]
def frames(c):return c[5]//int(round(0.005/c[6]))+1
def sim(budget,sel,width,probation=False):
    lru=collections.OrderedDict();used=0;saved=0.;hits=0;prob=collections.OrderedDict()
    cost={}
    for c in calls:
        if not sel(c):continue
        k=c[0];sz=frames(c)*width(c)*8
        if c[1]==1:cost[k]=c[9]
        if k in lru:
            lru.move_to_end(k);hits+=1;saved+=cost[k];continue
        if probation and k not in prob:
            prob[k]=1
            if len(prob)>4096:prob.popitem(last=False)
            continue
        lru[k]=sz;used+=sz
        while used>budget:used-=lru.popitem(last=False)[1]
    return hits,saved
el=lambda c:c[7]
w_el=lambda c:3*c[3]+2*c[2]
nc0=lambda c:c[4]==0
w0=lambda c:2*c[2]
noneligible=lambda c:c[4]>0 and not c[7]
wall=lambda c:2*c[2]+c[4]*(3*c[3]+2*c[2])
for mb in (256,512,768,1024,1536,4096):
    h,s=sim(mb*2**20,el,w_el);h2,s2=sim(mb*2**20,el,w_el,True)
    print(f'eligible {mb} MiB: admit-all hits {h} saved {s:.1f}s | probation hits {h2} saved {s2:.1f}s')
for mb in (32,64,128,256):
    h,s=sim(mb*2**20,nc0,w0);print(f'medium-only {mb} MiB: hits {h} saved {s:.1f}s')
for mb in (64,128,256):
    h,s=sim(mb*2**20,noneligible,wall);print(f'non-eligible full {mb} MiB: hits {h} saved {s:.1f}s')
