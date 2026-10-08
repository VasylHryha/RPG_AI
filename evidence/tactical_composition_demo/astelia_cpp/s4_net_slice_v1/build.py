"""Sequential new-folder native build; no engine execution. All ancestors read-only."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
CPP=HERE.parent
OUT=HERE/'_local/build'
sys.path.insert(0,str(CPP))
from build_admission import admit,sha

def once(s,a,b):
    if s.count(a)!=1:raise RuntimeError('overlay drift: '+a)
    return s.replace(a,b)

def generated():
    # Extract immutable policy-free observe helpers, copied REACT teacher, participation only.
    s=(CPP/'s4_react_adapter_v1/react.cpp').read_text()
    helpers=s[s.index('const control::ObservedUnit& unit('):s.index('Controller* controller(')]
    functions=s[s.index('Reaction react('):s.index('const Snapshot& Controller::snapshot')]
    mechanics='#include "public_mechanics.h"\n#include "geometry.h"\nnamespace net_public {\nnamespace {\n'+helpers+'}\n'+functions+'}\n'
    # Reuse the v6 public projection exactly, not its v7/REACT controller or live World.
    v6=(CPP/'s4_shape_lab_v6/shapes.cpp').read_text()
    project=v6[v6.index('World project('):v6.index('std::vector<PlannedShot> plan(')]
    projection='#include "teacher.h"\nnamespace slice_teacher {\nVec2 pos(const control::ObservedUnit& u){return {u.x,u.y};}\n'+project+'}\n'
    planner=(CPP/'src/native/artillery.cpp').read_text()
    a=planner.index('void launch(');b=planner.index('\ndouble artilleryOutcome(',a)
    planner=planner[:a]+'''void collectPlan(World& w,uint8_t team,const Attack& attack){
 for(size_t i=0;i<attack.shots.size();++i){auto q=attack.shots[i];
  if(q.at>w.time+1e-9)throw std::logic_error("delayed teacher schedule");
  q.family=attack.family;q.variant=attack.variant;
  if(i<attack.per.size()){q.prediction=attack.per[i];q.hasPrediction=true;}
  w.packs[team].artilleryQueue.push_back(q);
 }
}'''+planner[b:]
    planner=planner.replace('attackName(', 'copiedAttackName(').replace('attackByName(', 'copiedAttackByName(').replace('double artilleryOutcome(', 'double copiedOutcome(').replace('artilleryOutcome(w,me,','copiedOutcome(w,me,').replace('void artilleryVolley(', 'void copiedPlanner(').replace('launch(w,me,','collectPlan(w,me,').replace('namespace astelia {','namespace slice_teacher {\nusing namespace astelia;').replace('#include "artillery.h"','#include "artillery.h"\n#include "teacher.h"')
    combat=(CPP/'src/native/combat.cpp').read_text()
    combat=once(combat,'prepareControllers(w);','net_slice::bind(w);prepareControllers(w);')
    combat=once(combat,'else decideUnit(w,i);','else net_slice::builtinDecision(w,i);')
    combat=once(combat,'controllerDecision(w,i)','net_slice::decide(w,i)')
    combat=once(combat,'for(auto i:w.active)gamePrep(w,i,dt*w.state[i].timeRate);','net_slice::prePrep(w);for(auto i:w.active)gamePrep(w,i,dt*w.state[i].timeRate);net_slice::postPrep(w);')
    combat=once(combat,'for (const auto& hit:w.meleeHits)', 'net_slice::finishTick(w);for (const auto& hit:w.meleeHits)')
    combat=once(combat,'double before=t?', 'const bool sliceAimLegal=net_slice::actAimReach(w,i);double before=t?')
    combat=once(combat,'d.release==Release::Artillery&&prepared(w,i)','d.release==Release::Artillery&&prepared(w,i)&&sliceAimLegal')
    combat=once(combat,'fireShellAt(w,i,t->pos+(sk.lobLead||(sk.adaptiveLobLead&&steady)?ts.longVelocity*fl:Vec2{}));','fireShellAt(w,i,net_slice::aimPoint(w,i,t->pos+(sk.lobLead||(sk.adaptiveLobLead&&steady)?ts.longVelocity*fl:Vec2{})));')
    rules=(CPP/'src/native/observer_v1_combat_rules.cpp').read_text()
    rules=once(rules,'w.state[i].prep=0;if(w.config->rules','net_slice::consumedAck(w,i);w.state[i].prep=0;if(w.config->rules')
    rules=once(rules,'w.shells.push_back(sh);','net_slice::launchedAck(w,i,sh);w.shells.push_back(sh);')
    return {'public_mechanics.cpp':mechanics,'teacher_projection.cpp':projection,'teacher_planner.cpp':planner,'combat.cpp':'#include "host.h"\n'+combat,'rules.cpp':'#include "host.h"\n'+rules}

def build():
    start=time.monotonic();OUT.mkdir(parents=True,exist_ok=True)
    parent=CPP/'s4_shape_lab_v1/build/tactics_lab_host';identity=admit(parent)
    record=json.loads(parent.with_suffix('.build.json').read_text());cmd=record['commands'][0]
    flags=cmd[:cmd.index('-c')]+['-I'+str(HERE),'-I'+str(CPP/'s4_shape_lab_v1')]
    commands=[];objects=[];sources={}
    def compile(source,obj):
        argv=[*flags,'-c',str(source),'-o',str(obj)];subprocess.run(argv,check=True,timeout=300);commands.append(argv);sources[str(source)]=sha(source);objects.append(str(obj))
    for i,cmd in enumerate(record['commands'][:5]):compile(Path(cmd[cmd.index('-c')+1]),OUT/f'overlay_{i}.o')
    compile(CPP/'s4_shape_lab_v1/lab_dispatch.cpp',OUT/'dispatch.o')
    for name,content in generated().items():
        path=OUT/name;path.write_text(content);compile(path,OUT/(path.stem+'.o'))
    for name in ('schema','models','cast','collector','teacher','host','integration'):
        compile(HERE/(name+'.cpp'),OUT/(name+'.o'))
    skip={'lab_host.o','lab_combat.o','lab_dispatch.o','observer_v1_observer_v1_combat_rules.o',*(f'overlay_{i}.o' for i in range(5))}
    reused={}
    for path in record['link'][1:record['link'].index('-o')]:
        if Path(path).name in skip:continue
        expected=record.get('reused_object_sha256',{}).get(path)
        if not expected or sha(Path(path))!=expected:raise RuntimeError('unbound/drift object '+path)
        reused[path]=expected
    links=[]
    # Host exposes fixture RPC by default. Physical collection requires explicit --collect.
    common=list(objects)
    for name in ('rpc','fixture'):
        objects=[];compile(HERE/(name+'.cpp'),OUT/(name+'.o'));target=OUT/('net_host' if name=='rpc' else 'native_fixture')
        argv=[record['link'][0],*common,*objects,*reused,'-o',str(target)];subprocess.run(argv,check=True,timeout=120);links.append(argv)
    if admit(parent)!=identity:raise RuntimeError('parent drift during build')
    # Living docs never pinned. Local frozen bytes and new source bytes are pinned.
    for p in [*HERE.glob('*.h'),*HERE.glob('*.cpp'),*HERE.glob('*.py'),HERE/'CONTRACT.md',HERE/'requirements.lock',* (HERE/'frozen').glob('*')]:sources[str(p)]=sha(p)
    payload={'status':'PASS','seconds':time.monotonic()-start,'fights':0,'commands':commands,'links':links,'sources':sources,'reused_object_sha256':reused,'parent_identity':identity,'binaries':{p.name:sha(p) for p in (OUT/'net_host',OUT/'native_fixture')}}
    (HERE/'BUILD.json').write_text(json.dumps(payload,indent=2)+'\n');print('Native build PASS',payload['seconds'])
if __name__=='__main__':build()
