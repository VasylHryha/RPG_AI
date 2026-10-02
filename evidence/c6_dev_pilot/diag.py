import json, pickle, sys
import numpy as np
from concurrent.futures import ProcessPoolExecutor
ROOT="/Users/new/RiderProjects/ai_RPG_test"; sys.path.insert(0, ROOT)
from geomind import c5_experiment as E
from geomind.c4_experiment import model_params
from geomind.c4_model import simulate
from geomind.c5_units import unit_validity
C5M=json.loads(open(ROOT+"/experiments/c5_manifest.json").read()); C4M=E.load_c4(C5M)
P=model_params(C4M)["intact"]; S=E.settings(C5M,C4M); T1=S["t1"]; DT=S["dt"]
C3=9.6; FR=C3; W=30*C3
def one(g):
    k=int(g["units"].max())+1
    fe=int(round(FR/DT)); nwin=3
    _,_,(xs,ths)=simulate(g["x"][None],g["th"][None],g["om"][None],P,DT,int(round(nwin*W/DT)),fe)
    xs,ths=xs[:,0],ths[:,0]
    out=[]
    # C5 window (96, frames every 3.2) for reference: first 96 time units at frame 3.2 -> use every 3.2? approximate with level-3 frames: skip
    per=len(xs)//nwin
    for w in range(nwin):
        sl=slice(w*per, w*per+per+1)
        v=unit_validity(xs[sl],ths[sl],g["units"],list(range(k)),FR,T1["link_factor"])
        out.append(v)
    return out
def main():
    _,_,_,groups,_,_=pickle.load(open("harvest_44444_320.pkl","rb"))
    groups=[g for g in groups if g["alone_ok"]][:96]
    with ProcessPoolExecutor(8) as pool: res=list(pool.map(one,groups))
    lim={"shape_cv":T1["shape_cv"],"lock_std":T1["lock_std"],"freq_change":T1["freq_tol"],"pattern_change":T1["pattern_tol"],"hull_overlap":0.2}
    for w in range(3):
        units=[u for r in res for u in r[w]]
        fails={k:round(np.mean([u[k]>lim[k] for u in units]),3) for k in lim}
        anyf=np.mean([any(u[k]>lim[k] for k in lim) for u in units])
        q={k:[round(float(np.percentile([u[k] for u in units],p)),4) for p in (50,90,99)] for k in lim}
        print(f"window {w}: units {len(units)} any-fail {anyf:.3f} by-criterion {fails}")
        print("   p50/p90/p99", q)
    grp=[np.mean([all(u[k]<=lim[k] for k in lim) for u in r[0]])==1 for r in res]
    print("groups with all units valid in window 0:", sum(grp), "/", len(res))

if __name__=="__main__":
    main()
