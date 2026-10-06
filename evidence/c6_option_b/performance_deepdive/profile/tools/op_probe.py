import copy,sys,time,json
sys.path.insert(0,'/Users/new/RiderProjects/ai_RPG_test')
import numpy as np
from geomind import c6_option_b as O, c6_option_b_parallel as Q
from geomind import c6_r4_field_assay as A, c6_r4_field_protocol as P, c6_r4_field as F
from tools.c6_option_b_compare import compare
def settings():
    s=copy.deepcopy(P.load_settings())
    s.update(formation=.2,exposure=.2,window=.1,descriptor=.05,probe_sample_dt=.025,frame_dt=.025)
    s['detector']['recovery_time']=.05;s['causal'].update(gm_window=.025,mg_window=.05)
    return s
def scenario(parallel,force):
    s=settings();checks=[]
    base=F.medium(P.rng(7,0,1),s['model'])
    grid=A.GridSet([base]*3,s,checks)
    source=P.introduce(grid,7,0,0,0)
    flows=source.run(s['formation'],'prefix')
    q={'selected_members':list(range(8)),'qualified':True}
    orig_q,orig_p=A.qualification,P.rolling_persistence
    def qual(g,f,pert,scope,forced_members=None):
        r=orig_q(g,f,pert,scope,forced_members)
        if forced_members is not None and force:r['qualified']='/no_r/' not in scope
        return r
    def pers(*a):
        rows=orig_p(*a)
        if force:
            for r in rows:r['passed']=True
        return rows
    A.qualification,P.rolling_persistence=qual,pers
    try:
        out={}
        try:
            cell,cont=P.operation(source,q,flows,7,0,1,.3,'turn1')
            out['cell']=cell;out['continuation']=None if cont is None else cont[0].identities()
            out['continuation_checks_shared']=cont is None or cont[0].checks is checks
        except (ValueError,RuntimeError) as e:out['error']=[type(e).__name__,str(e)]
        out['checks']=checks
        return out
    finally:A.qualification,P.rolling_persistence=orig_q,orig_p
def run(parallel,force):
    with O.backend('native'):
        if parallel:
            with Q.parallel() as sch:
                r=scenario(True,force);r['batches']=sch.summary()['concurrent_task_batches']
                return r
        return scenario(False,force)
for force in (True,False):
    t=time.time();a=run(False,force);t1=time.time();b=run(True,force);t2=time.time()
    batches=b.pop('batches')
    res=compare(json.loads(json.dumps(a,default=lambda o:o.tolist())),json.loads(json.dumps(b,default=lambda o:o.tolist())),0.,False)
    print('force',force,'seq',round(t1-t,1),'par',round(t2-t1,1),'batches',batches,'error',a.get('error'),'eligible',a.get('cell',{}).get('operation_eligible'),
          'before_formation',None if 'cell' not in a else a['cell']['before_formation'] is not None,'checks',len(a['checks']),len(b['checks']),'cont',a.get('continuation') is not None,
          'compare',res['passed'],res['numeric_values_compared'],res['failures'][:3])
