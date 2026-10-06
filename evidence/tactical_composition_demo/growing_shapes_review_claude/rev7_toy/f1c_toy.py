import math
rs=0.556
xs=[3.2-rs*m for m in range(6)]+[0.0]  # S, 5 intermediates, O pinned at 0
g=[1]+[0]*5+[0]; masked=[False]*6+[True]
def run(lam,T=40,dt=0.001):
    th=[0.0]*7;t=0.0;first=None
    while t<T:
        phi=math.pi*t;alpha=0 if t<8 else math.pi/2;new=[]
        for i in range(7):
            d=math.pi
            if not masked[i]:
                r=abs(xs[i]-4);
                if r<3: d+=lam*g[i]*2*math.exp(-r*r/2)*math.sin(phi+alpha-th[i])
            nb=sorted([j for j in range(7) if j!=i and abs(xs[j]-xs[i])<3],key=lambda j:abs(xs[j]-xs[i]))[:8]
            if nb: d+=lam*sum(math.exp(-(xs[j]-xs[i])**2)*math.sin(th[j]-th[i]) for j in nb)/len(nb)
            new.append(th[i]+dt*d)
        th=new;t+=dt
        e=abs((th[6]-math.pi*t-math.pi/2+math.pi)%(2*math.pi)-math.pi)
        if t>8:
            if e<=0.3:
                if first is None: first=t
            else: first=None
    return first
for lam in (8,16,32):
    f=run(lam); print("lambda",lam,"settled entry",None if f is None else round(f,2),"delay",None if f is None else round(f-8,2))
