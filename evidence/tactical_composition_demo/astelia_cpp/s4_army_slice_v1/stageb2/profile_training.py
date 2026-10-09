"""Bounded TEST_ONLY real-window profiling; no fit, admission or shared locks."""
import argparse,cProfile,itertools,json,os,pstats,time,gc
from pathlib import Path
import runtime as r
import candidate_cache as cc
import training
from loss import install
from train import timing_fights,project
from models import initial

def hotspots(prof):
    stats=pstats.Stats(prof);out=[]
    for (file,line,name),(calls,primitive,self_time,cumulative,callers) in sorted(stats.stats.items(),key=lambda v:v[1][3],reverse=True)[:35]:
        out.append(dict(file=file,line=line,name=name,calls=calls,self_seconds=self_time,cumulative_seconds=cumulative))
    return out

def profile(model,opt,rows,ctx,deadline,path):
    prof=cProfile.Profile();prof.enable()
    value=training.step(model,opt,rows,ctx,None,deadline)
    prof.disable();prof.dump_stats(str(path))
    return value,hotspots(prof)

def before():
    training.environment();index=r.read(r.LOCAL/'round0/INDEX.json')
    fight=timing_fights([f for f in index['fights'] if f['split']=='train'])[0]
    root=r.HERE/'_local/b2prof';root.mkdir(parents=True,exist_ok=True)
    install({role:dict(weights=[1.,1.]) for role in ('melee','ranged','artillery')})
    deadline=time.monotonic()+600
    cc.activate(r.LOCAL/'round0/hier_speed_test',index,r.frames)
    rows=list(itertools.islice(cc.frames(fight['raw_file']),training.WINDOW))
    report=dict(status='TEST_ONLY',phase='before',fight=fight,window_start=0,window_ticks=len(rows),threads=1,nice=os.getpriority(os.PRIO_PROCESS,0),sources=r.sources(),samples={})
    for arm in r.ARMS:
        model,opt=training.make(arm);ctx=(initial(arm,[]),[],None,(0,[]))
        value,hot=profile(model,opt,rows,ctx,deadline,root/('before_'+arm+'.pstats'))
        report['samples'][arm]=dict(steps=[value],hotspots=hot)
        print(json.dumps(dict(arm=arm,phase='before',**value)),flush=True)
        del model,opt;gc.collect()
    r.write(r.HERE/'B2PROF_BEFORE.json',report,exclusive=True)
    return report

def after():
    """20 steps: first/last real stored windows, both panels, all five arms."""
    import prepared_cache as pc
    training.environment();index=r.read(r.LOCAL/'round0/INDEX.json')
    train=[f for f in index['fights'] if f['split']=='train'];val=[f for f in index['fights'] if f['split']=='validation'];test=[f for f in index['fights'] if f['split']=='test']
    chosen=timing_fights(train);validation=timing_fights(val)
    if len(chosen)*2*len(r.ARMS)>20:raise RuntimeError('bounded sample exceeds20 steps')
    selected=dict(index,fights=chosen+validation)
    root=r.HERE/'_local/b2prof';root.mkdir(parents=True,exist_ok=True)
    install({role:dict(weights=[1.,1.]) for role in ('melee','ranged','artillery')})
    start=time.monotonic();deadline=start+600
    cache=pc.prepare(root/'cache_v11',selected,r.frames,deadline)
    pc.activate(root/'cache_v11',selected,r.frames);training.frames=pc.frames;r.data.frames=pc.frames
    report=dict(status='TEST_ONLY',phase='after',threads=1,nice=os.getpriority(os.PRIO_PROCESS,0),sources=r.sources(),samples={},cache=cache,
                selection='largest-frame train/validation fight per panel; first/last declared windows;20 optimizer steps; cold chunk decode before every step',
                target_balance='unity for controlled comparison with BEFORE; actual train-only weights/admission remain host gates')
    for arm in r.ARMS:
        model,opt=training.make(arm);steps=[];panel_samples={};hot=None
        for fight in chosen:
            rows,states,refresh=training.stored(model,fight,4,deadline)
            contexts=list(states.items());measured=[]
            for at,ctx in (contexts[0],contexts[-1]):
                pc.LOADED=pc.LAST=None
                if hot is None:
                    value,hot=profile(model,opt,rows[at:at+training.WINDOW],ctx,deadline,root/('after_'+arm+'.pstats'))
                else:value=training.step(model,opt,rows[at:at+training.WINDOW],ctx,None,deadline)
                measured.append(value);steps.append(dict(tag=fight['tag'],panel=fight['panel'],tick=at,window_ticks=len(rows[at:at+training.WINDOW]),**value))
                print(json.dumps(dict(arm=arm,phase='after',panel=fight['panel'],tick=at,**value)),flush=True)
            vf=next(f for f in validation if f['panel']==fight['panel'])
            diag=training.evaluate(model,[vf],4,None,deadline)
            read_start=time.monotonic();training.window_rows(fight,4);read_seconds=time.monotonic()-read_start
            panel_samples[fight['panel']]=dict(tag=fight['tag'],frames=fight['frames'],refresh_seconds_per_frame=refresh/fight['frames'],read_seconds_per_frame=read_seconds/fight['frames'],step_seconds=max(v['wall_seconds'] for v in measured),validation_prefix_seconds_per_frame=diag['prefix_seconds']/vf['frames'],validation_window_seconds_per_tick=(diag['wall_seconds']-diag['prefix_seconds'])/diag['window_ticks'])
        refresh_total=sum(panel_samples[f['panel']]['refresh_seconds_per_frame']*f['frames'] for f in train)
        read_total=sum(panel_samples[f['panel']]['read_seconds_per_frame']*f['frames'] for f in train)
        step_total=sum(panel_samples[f['panel']]['step_seconds']*len(training.selected_starts(f['frames'],4)) for f in train)
        def diagnostic_seconds(fights):
            return sum(panel_samples[f['panel']]['validation_prefix_seconds_per_frame']*f['frames']+panel_samples[f['panel']]['validation_window_seconds_per_tick']*sum(min(training.WINDOW,f['frames']-at) for at in training.selected_starts(f['frames'],4)) for f in fights)
        validation_seconds=diagnostic_seconds(val);test_seconds=diagnostic_seconds(test)
        epoch=refresh_total+read_total+step_total+validation_seconds
        tail=validation_seconds+2*test_seconds
        report['samples'][arm]=dict(steps=steps,hotspots=hot,panel_samples=panel_samples,per_step_seconds=max(s['wall_seconds'] for s in steps),refresh_seconds_per_epoch=refresh_total,read_seconds_per_epoch=read_total,validation_seconds=validation_seconds,epoch_seconds=epoch,tail_seconds=tail)
        del model,opt,rows,states;gc.collect()
    projection=project(report['samples'],10,4)
    cache_projection=0
    for panel in {f['panel'] for f in index['fights']}:
        q=[(rec,next(f for f in selected['fights'] if f['tag']==rec['tag'])) for rec in cache['records'] if next(f for f in selected['fights'] if f['tag']==rec['tag'])['panel']==panel]
        bytes_per_tick=sum(rec['compressed_bytes']+(root/'cache_v11'/rec['meta_file']).stat().st_size for rec,_ in q)/sum(rec['cached_frames'] for rec,_ in q)
        cache_projection+=bytes_per_tick*sum(len(pc.selected_ticks(f['frames'])) for f in index['fights'] if f['panel']==panel)
    report.update(sample_steps=sum(len(s['steps']) for s in report['samples'].values()),seconds=time.monotonic()-start,
                  cache_projected_bytes=cache_projection,cache_projected_bytes_with_margin=1.2*cache_projection,
                  projection=projection,projection_limitations='TEST_ONLY estimate, four CPU lanes; excludes source/raw admission hashing, train-only class-weight scan and real owner gates; full production measure required')
    r.write(r.HERE/'B2PROF_AFTER.json',report,exclusive=True)
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--phase',choices=('before','after'),required=True)
    a=p.parse_args();globals()[a.phase]()
