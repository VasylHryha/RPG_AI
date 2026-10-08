"""Public script oracle/support; no engine, allocation or physical execution."""
from s0_arithmetic import math, check, slots, candidates, opportunities


def intercept(gun, target):
    lob = gun['lob']
    if not math.isfinite(lob) or lob <= 0:
        raise ValueError('invalid lob')
    tau = math.hypot(target['x']-gun['x'], target['y']-gun['y'])/lob
    for _ in range(3):
        q = [target['x']+target['vx']*tau, target['y']+target['vy']*tau]
        tau = math.hypot(q[0]-gun['x'], q[1]-gun['y'])/lob
    q = [target['x']+target['vx']*tau, target['y']+target['vy']*tau]
    residual = math.hypot(target['vx'], target['vy'])*abs(math.hypot(q[0]-gun['x'],q[1]-gun['y'])/lob-tau)
    if not all(math.isfinite(v) for v in [*q,residual]):
        raise ValueError('nonfinite intercept')
    return q, residual


def retained_threats(s):
    me=check(s)
    def urgency(t):
        when={'shell':t['at'],'own_shell':t['at'],'cast':t['landing_at'],
              'field':max(s['t'],t['from']),'shot':s['t']+max(0,(me['x']-t['x'])*t['dx']+(me['y']-t['y'])*t['dy'])/max(t['speed'],1e-6)}[t['kind']]
        inside=math.hypot(t['x']-me['x'],t['y']-me['y'])<=t['radius']+me['radius']+4
        return not inside,max(0,when-s['t']),('shell','shot','field','cast','own_shell').index(t['kind']),t['ordinal']
    return sorted(s['threats'],key=urgency)[:8]


def reaction(s, threats=None):
    """Copied gun-only net_public::react; public, same order/tie rules."""
    u=check(s); pos=[u['x'],u['y']]; t=s['t']
    if u['guard_until']>t:return False,pos
    threats=s['threats'] if threats is None else threats
    shots=[q for q in threats if q['kind']=='shot']
    best=None;bt=math.inf;side=0
    for q in shots:
        if t-q['born']<.12:continue
        dx,dy=u['x']-q['x'],u['y']-q['y'];along=dx*q['dx']+dy*q['dy'];cross=dx*q['dy']-dy*q['dx']
        if 0<along<=min(q['left'],q['speed']*.4) and abs(cross)<=u['radius']+3 and along<bt:best=q;bt=along;side=cross
    if best:
        k=1 if side>=0 else -1
        return True,[u['x']+best['dy']*30*k,u['y']-best['dx']*30*k]
    for q in threats:
        if q['kind']=='field' and q['from']<=t and q['until']>=t+.5:
            dx,dy=u['x']-q['x'],u['y']-q['y'];d=math.hypot(dx,dy)
            if d<=q['radius']+u['radius']:return True,[u['x']+30,u['y']] if d<.5 else [u['x']+dx*40/d,u['y']+dy*40/d]
    blasts=[(q,q['at'] if q['kind']=='shell' else q['landing_at']) for q in threats if (q['kind']=='shell' and not q['slow']) or (q['kind']=='cast' and q['target']!=u['id'])]
    def cover(p):return sum(math.hypot(p[0]-q['x'],p[1]-q['y'])<=q['radius']+u['radius']+4 for q,_ in blasts)
    first=min((at for q,at in blasts if math.hypot(u['x']-q['x'],u['y']-q['y'])<=q['radius']+u['radius']+4),default=math.inf)
    if not math.isfinite(first):return False,pos
    best=cover(pos);bd=0;active=False;goal=pos;extent=max(8,u['speed']*(first-t+.1))
    for f in (1,.6):
        for j in range(16):
            p=[min(s['width']-u['radius'],max(u['radius'],u['x']+math.cos(j*math.pi/8)*extent*f)),min(s['height']-u['radius'],max(u['radius'],u['y']+math.sin(j*math.pi/8)*extent*f))]
            k=cover(p);d=math.hypot(p[0]-u['x'],p[1]-u['y'])
            if k<best or (k==best and active and d<bd):active=True;goal=p;best=k;bd=d
    return active,goal


def support(s, target, requested=None):
    me=check(s);q,residual=intercept(me,target)
    radius=min(math.hypot(s['width'],s['height']),max(me['splash'],math.hypot(q[0]-target['x'],q[1]-target['y']),0 if requested is None else math.hypot(requested[0]-target['x'],requested[1]-target['y'])))
    points=[[target['x'],target['y']]]
    for f in (.5,1):
        for j in range(16):
            points.append([target['x']+(-1 if s['side'] else 1)*math.cos(j*math.pi/8)*radius*f,target['y']+math.sin(j*math.pi/8)*radius*f])
    legal=[i for i,p in enumerate(points) if 0<=p[0]<=s['width'] and 0<=p[1]<=s['height'] and me['min_range']<=math.hypot(p[0]-me['x'],p[1]-me['y'])<=me['range']]
    desired=q if requested is None else requested
    index=min(legal,key=lambda i:(math.dist(points[i],desired),i)) if legal else None
    return dict(points=points,legal=legal,index=index,lead=q,residual=residual,snap=None if index is None else math.dist(points[index],desired),radius=radius)


def oracle(s):
    me=check(s);_,enemies,_,_=slots(s)
    target=next((e for e in enemies if e['id']==me['target']),None) if me['prep']>0 else (enemies[0] if enemies else None)
    active,goal=reaction(s,retained_threats(s))
    if not active and target:
        dx,dy=target['x']-me['x'],target['y']-me['y'];d=math.hypot(dx,dy);wanted=min(me['range']-1,max(me['min_range']+1,d))
        if d:goal=[me['x']+dx*(d-wanted)/d,me['y']+dy*(d-wanted)/d]
    # Public participation projects an endpoint back into an enemy engagement band.
    def reach(p,e):return me['min_range']<=math.hypot(p[0]-e['x'],p[1]-e['y'])<=me['range']
    if enemies and not any(reach(goal,e) for e in enemies):
        e=enemies[0];dx,dy=goal[0]-e['x'],goal[1]-e['y'];d=math.hypot(dx,dy)
        if d==0:dx,dy=me['x']-e['x'],me['y']-e['y'];d=math.hypot(dx,dy)
        if d==0:dx,d=1,1
        r=min(me['range'],max(me['min_range'],d));goal=[min(s['width']-me['radius'],max(me['radius'],e['x']+dx/d*r)),min(s['height']-me['radius'],max(me['radius'],e['y']+dy/d*r))]
        if not any(reach(goal,e) for e in enemies) and any(reach([me['x'],me['y']],e) for e in enemies):goal=[me['x'],me['y']]
    moves,_=candidates(s,target);mi=min(range(33),key=lambda i:(math.dist(moves[i],goal),i))
    sup=support(s,target) if target else None
    aim=sup['points'][sup['index']] if sup and sup['index'] is not None else None
    start,release=opportunities(s,target,aim)
    return [mi,0 if target is None else enemies.index(target)+1,int(start and not active),int(release and not active),0 if not sup or sup['index'] is None else sup['index']],sup


def encoded_view(s, features):
    """Recover only represented public quantities at the stored float32 precision.

    IDs route categorical pointers; they never become numeric features. HP is a
    fraction here since this oracle needs only living masks. No omitted threat
    or absolute hidden cast state is restored from the source wire.
    """
    x=list(map(float,features));tail=x[-16:];side=s['side'];sign=-1 if side else 1
    px=(tail[3] if side else tail[2])*1000;py=tail[4]*1000
    width=(tail[2]+tail[3])*1000;height=(tail[4]+tail[5])*1000
    f,e,_,_=slots(s);source=[check(s),*f,*([None]*(12-len(f))),*e,*([None]*(12-len(e)))]
    eid=[u['id'] for u in e]
    def pointer(v):
        k=round(v*12)
        return eid[k-1] if 1<=k<=len(eid) else 0
    units=[]
    for i,u in enumerate(source):
        a=x[i*32:(i+1)*32]
        if not a[0]:continue
        row=dict(id=u['id'],team=side if a[18] else 1-side,role=max(range(3),key=lambda j:a[1+j]),x=px+sign*a[4]*100,y=py+a[5]*100,vx=sign*a[6]*200,vy=a[7]*200,hp=a[8],maxhp=1,radius=a[9]*100,speed=a[10]*200,range=a[11]*1000,min_range=a[12]*1000,damage=a[13]*200,cooldown=a[14]*10,cooldown_max=a[15]*10,target=pointer(a[16]))
        if row['team']==side:row.update(prep=a[19]*10,windup=a[20]*10,time_rate=a[21]*4,energy=a[22]*1000,cost=a[23]*1000,guard_until=tail[0]*150+a[24]*10,busy=bool(a[25]),lob=a[26]*1000,splash=a[27]*100,last_launch=-1 if a[30]<0 else tail[0]*150-a[30]*10,consumed=bool(a[31]))
        units.append(row)
    threats=[];now=tail[0]*150
    for i in range(8):
        a=x[800+i*24:824+i*24]
        if not a[0]:continue
        kind='own_shell' if a[22] else ('shell','shot','field','cast')[max(range(4),key=lambda j:a[j+1])]
        threats.append(dict(kind=kind,ordinal=i+1,x=px+sign*a[5]*100,y=py+a[6]*100,dx=sign*a[7],dy=a[8],born=now-a[9]*10,at=now+a[10]*10,radius=a[11]*100,speed=a[12]*1000,left=a[13]*1000,from_=0))
        q=threats[-1];del q['from_'];q.update({'from':now+a[14]*10,'until':now+a[15]*10,'release_at':now+a[16]*10,'landing_at':now+a[17]*10,'caster':pointer(a[18]),'target':s['self'] if a[19] else 0,'slow':bool(a[21]),'damage':a[23]*200})
    return dict(version='NS1',fight=s['fight'],tick=s['tick'],side=side,self=s['self'],t=now,dt=tail[1]/30,width=width,height=height,units=units,threats=threats)
