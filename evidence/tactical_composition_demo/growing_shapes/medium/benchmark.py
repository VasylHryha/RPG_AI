"""Fixed synthetic integration timing only. No growth/task/learning experiment."""
import json
import math
import random
import time
from medium import Medium, Params

def benchmark(steps=300):
    output=[]
    for n in [50,200,500]:
        rng=random.Random(17)
        with Medium(17,Params(window=32)) as m:
            # Fixed density avoids making the larger case artificially easier.
            side=math.sqrt(n)
            for _ in range(n):
                m.add(rng.uniform(-side/2,side/2),rng.uniform(-side/2,side/2),rng.uniform(-math.pi,math.pi),rng.uniform(-.03,.03))
            start=time.perf_counter()
            m.step(.01,steps)
            elapsed=time.perf_counter()-start
            output.append({'N':n,'steps':steps,'dt':.01,'seconds':elapsed,'steps_per_second':steps/elapsed,
                           'active_couplings':m.cost(0,0)['active_couplings'],
                           'includes':['grid rebuild','RK4','window recording','strain fit','ctypes call'],
                           'growth_rules':False})
    return output

if __name__=='__main__':
    print(json.dumps(benchmark(),indent=2))
