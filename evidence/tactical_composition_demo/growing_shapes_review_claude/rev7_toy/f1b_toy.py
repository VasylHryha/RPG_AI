import math
# F1b scaffold (14.3): site q=(4,0), S at 3.2 (g=1), two intermediates at r* spacing toward origin (g=0), O next (masked). Positions fixed (toy).
rs=0.556
xs=[3.2,3.2-rs,3.2-2*rs,3.2-3*rs]; g=[1,0,0,0]
def run(lam, T=40, dt=0.002):
    th=[0.0]*4; t=0.0; first=None; err16=None
    while t<T:
        phi=math.pi*t; alpha=0 if t<8 else math.pi/2
        new=[]
        for i in range(4):
            d=math.pi  # omega
            # drive (masked for O)
            if i<3:
                r=abs(xs[i]-4); k=2.0
                d+=lam*g[i]*k*math.exp(-r*r/2)*math.sin(phi+alpha-th[i])
            nb=[j for j in range(4) if j!=i and abs(xs[j]-xs[i])<3]
            d+=lam*sum(math.exp(-(xs[j]-xs[i])**2)*math.sin(th[j]-th[i]) for j in nb)/len(nb)
            new.append(th[i]+dt*d)
        th=new; t+=dt
        e=abs((th[3]-math.pi*t-math.pi/2+math.pi)%(2*math.pi)-math.pi)
        if t>8:
            if e<=0.3 and first is None: first=t
            if e>0.3: first=None if t<16 else first
        if abs(t-16)<dt/2: err16=e
    return first,err16
for lam in (1,2,4,8):
    f,e=run(lam); print("lambda",lam,"first continuous entry",None if f is None else round(f,2),"err at 16 s",round(e,3))
