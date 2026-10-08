"""V6 paired geometry/engagement/rotation overlay, sequential build; no simulation. Inputs remain untouched."""
import importlib.util
import json
import pathlib
import subprocess
import sys
import time
HERE=pathlib.Path(__file__).resolve().parent
CPP=HERE.parent
ADAPTER=CPP/'s4_react_adapter_v1'
BINARY=HERE/'build/tactics_react_host_v6'
sys.path.insert(0,str(CPP))
from build_admission import admit,sha

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def replace_once(s,a,b):
    if s.count(a)!=1: raise RuntimeError('v6 overlay drift: '+a)
    return s.replace(a,b)

def derived_sources():
    lean=load('v5_lean_parent',CPP/'s4_shape_lab_v4/build.py').derived_sources()
    adapter=load('v5_adapter_parent',ADAPTER/'build.py').derived_sources()
    header=(ADAPTER/'react.h').read_text().replace('#include "world.h"','#include "world.h"\n#include "timing.h"\n#include "shapes.h"')
    header=replace_once(header,' bool game=true;', ' std::vector<shapes_v6::Threat> threats;\n std::map<UnitId,double> protection,regeneration;\n bool game=true;')
    header=replace_once(header,'public:\n Controller(', 'public:\n battery_v1::Battery battery;\n shapes_v6::State shape;\n auto& mutableRecords(){return records_;}\n Controller(')
    host=lean.pop('lean_host.cpp')
    host=replace_once(host,'react_v1::configuration(request)','shapes_v6::configuration(request)')
    host=replace_once(host,'react_v1::create(config,request)','shapes_v6::create(config,request)')
    host=replace_once(host,'{"observerV1",true}','{"shapeV6",shapes_v6::audit(w)},{"shotsV6",shapes_v6::shots(w)},{"launchAudit",battery_v1::audits(w)},{"battery",battery_v1::rows(w)},{"observerV1",true}')
    combat=adapter['react_combat.cpp']
    combat=replace_once(combat,'react_v1::prepare(w);','react_v1::prepare(w);battery_v1::prepareDummies(w);')
    combat=replace_once(combat,'react_v1::constrainPrep(w);','battery_v1::central(w);react_v1::constrainPrep(w);')
    combat=replace_once(combat,'for(auto team:packOrder)if(w.packs[team].enabled)artilleryVolley(w,team);','battery_v1::oscillator(w);shapes_v6::geometry(w);for(auto team:packOrder)if(w.packs[team].enabled)artilleryVolley(w,team);')
    combat=replace_once(combat,'bool hit=false;auto& out=w.stats.shellOut[src->team];','battery_v1::landing(w,shell);bool hit=false;auto& out=w.stats.shellOut[src->team];')
    rules=replace_once(adapter['react_rules.cpp'],'w.shots.push_back(std::move(p));','shapes_v6::shot(w,i,p);w.shots.push_back(std::move(p));')
    rules=replace_once(rules,'observer_v1::launch(w,i,sh);','observer_v1::launch(w,i,sh);battery_v1::launch(w,i,sh);')
    call='fireShellAt(w,i,react_v1::aimPoint(w,i,t->pos+(sk.lobLead||(sk.adaptiveLobLead&&steady)?ts.longVelocity*fl:Vec2{})));'
    combat=replace_once(combat,call,call+'battery_v1::fired(w,i);')
    artillery=(CPP/'src/native/artillery.cpp').read_text()
    start=artillery.index('bool fireGate(');end=artillery.index('\nvoid launch(',start)
    gate=artillery[start:end].replace('bool fireGate(','bool copiedFireGate(')
    gate=replace_once(gate,'const auto& skill=w.config->skills[u.team];','auto skill=w.config->skills[u.team];skill.holdWave=0;skill.holdSync=.5;')
    gate=replace_once(gate,'&&p.enabled)',')')
    gate='#include "timing.h"\n#include "artillery.h"\n#include "geometry.h"\nnamespace battery_v1 {\nconstexpr double pi=tau/2;\n'+gate+'\n}\n'
    abilities=(CPP/'src/native/observer_v1_abilities.cpp').read_text().replace('observer_v1::launch(w,i,sh);','observer_v1::launch(w,i,sh);battery_v1::launch(w,i,sh);')
    return {**lean,'planner_copy.cpp':planner_source(),'v5_abilities.cpp':'#include "timing.h"\n'+abilities,'react.h':header,'lean_host.cpp':host,'react_combat.cpp':combat,
            'react_rules.cpp':rules,'adapter_fixture.cpp':(ADAPTER/'fixture.cpp').read_text().replace('../s4_shape_lab_v1/', '../../s4_shape_lab_v1/'),'react.cpp':react_source(),'central_gate.cpp':gate}

def react_source():
    s=(ADAPTER/'react.cpp').read_text().replace('../s4_shape_lab_v1/', '../../s4_shape_lab_v1/')
    s=replace_once(s,'return out;\n}\nReaction react(', 'shapes_v6::threats(w,side,out);return out;\n}\nReaction react(')
    s=replace_once(s,'\n}\nUnitDecision Controller::decide(', '\n shapes_v6::augment(*this);\n}\nUnitDecision Controller::decide(')
    s=replace_once(s,'r.executed.movement=participate(o,id,cmd.movement);', 'r.executed.movement=(shape.arm=="R1"||shape.arm=="E1+R1")?cmd.movement:participate(o,id,cmd.movement);')
    return s

def planner_source():
    s=(CPP/'src/native/artillery.cpp').read_text()
    # Candidate generation, assignment and scoring are copied verbatim. Only
    # output authority is replaced; the projection contains no upcoming guns.
    a=s.index('void launch(');b=s.index('\ndouble artilleryOutcome(',a)
    s=s[:a]+'''void collectPlan(World& w,uint8_t team,const Attack& attack){
 for(size_t i=0;i<attack.shots.size();++i){auto q=attack.shots[i];
  if(q.at>w.time+1e-9)throw std::logic_error("timing-changing planner output");
  q.family=attack.family;q.variant=attack.variant;
  if(i<attack.per.size()){q.prediction=attack.per[i];q.hasPrediction=true;}
  w.packs[team].artilleryQueue.push_back(q);
 }
}'''+s[b:]
    s=s.replace('attackName(', 'copiedAttackName(').replace('attackByName(', 'copiedAttackByName(')
    s=s.replace('double artilleryOutcome(', 'double copiedOutcome(').replace('artilleryOutcome(w,me,', 'copiedOutcome(w,me,')
    s=s.replace('void artilleryVolley(','void copiedPlanner(').replace('launch(w,me,','collectPlan(w,me,')
    s=s.replace('namespace astelia {','namespace shapes_v6 {\nusing namespace astelia;')
    # Dead rollout routine remains copied for traceability; calls the engine
    # only on the sanitized projection and is disabled by declared options.
    s=s.replace('#include "artillery.h"','#include "artillery.h"\n#include "shapes.h"')
    return s

def build():
    start=time.monotonic();parent=ADAPTER/'build/tactics_react_host';parent_id=admit(parent)
    record=json.loads(parent.with_suffix('.build.json').read_text());out=HERE/'build';out.mkdir(exist_ok=True)
    generated=derived_sources()
    for name,content in generated.items():(out/name).write_text(content)
    flags=record['commands'][0][:record['commands'][0].index('-c')]
    flags=[flags[0],'-I'+str(out),'-I'+str(HERE),*flags[1:],'-I'+str(ADAPTER),'-I'+str(CPP/'s4_shape_lab_v1')]
    commands=[];objects=[];reused={}
    def compile(source,obj):
        argv=[*flags,'-c',str(source),'-o',str(obj)];subprocess.run(['nice','-n','15',*argv],check=True,timeout=180);commands.append(argv);return str(obj)
    for name in generated:
        if name.endswith('.cpp') and name!='adapter_fixture.cpp':objects.append(compile(out/name,out/(pathlib.Path(name).stem+'.o')))
    objects.append(compile(HERE/'timing.cpp',out/'timing.o'))
    objects.append(compile(HERE/'shapes.cpp',out/'shapes.o'))
    # Dispatch copied to this folder so quoted react.h resolves to the v5 layout.
    dispatch=(ADAPTER/'dispatch.cpp').read_text().replace('../s4_shape_lab_v1/', '../../s4_shape_lab_v1/');dispatch=replace_once(dispatch,' if(p.name.rfind("dummy_",0)==0)', ' if(p.name=="dummy_advance_fire")return std::make_unique<battery_v1::DodgingDummy>(seed,side);\n if(p.name.rfind("dummy_",0)==0)');(out/'dispatch.cpp').write_text(dispatch)
    objects.append(compile(out/'dispatch.cpp',out/'dispatch.o'))
    skip={'react_host.o','react_combat.o','react_rules.o','react.o','dispatch.o','observer_v1_observer_v1.o','observer_v1_observer_v1_abilities.o'}
    local={a[-1]:a for a in record['commands']}
    for path in record['link'][1:record['link'].index('-o')]:
        if pathlib.Path(path).name in skip:continue
        expected=record.get('reused_object_sha256',{}).get(path)
        if expected:
            if sha(pathlib.Path(path))!=expected:raise RuntimeError('object drift: '+path)
            reused[path]=expected
        elif path in local:
            a=local[path];source=pathlib.Path(a[a.index('-c')+1]);obj=out/('admitted_'+pathlib.Path(path).name)
            objects.append(compile(source,obj))
        else:raise RuntimeError('unbound object: '+path)
    fixture=compile(HERE/'fixture.cpp',out/'fixture.o')
    adapter_fixture=compile(out/'adapter_fixture.cpp',out/'adapter_fixture.o')
    for target,linked in [(BINARY,objects),(out/'shape_fixture',[o for o in objects if not o.endswith('lean_host.o')]+[fixture]),(out/'adapter_fixture',[o for o in objects if not o.endswith('lean_host.o')]+[adapter_fixture])]:
        argv=[record['link'][0],*linked,*reused,'-o',str(target)];subprocess.run(['nice','-n','15',*argv],check=True,timeout=120)
        sources=dict(record['source_hashes'])
        for p in [HERE/'build.py',HERE/'timing.cpp',HERE/'timing.h',HERE/'shapes.cpp',HERE/'shapes.h',HERE/'PLANNER_STATES.json',HERE/'fixture.cpp',*(out/n for n in generated),out/'dispatch.cpp']:
            sources[str(p.relative_to(CPP))]=sha(p)
        manifest=dict(schema=2,engine='shape_lab_v6',scope='native_complete_engine',sanitized=False,portable=False,source_hashes=sources,binary_sha256=sha(target),commands=commands,link=argv,reused_object_sha256=reused,parent=parent_id)
        target.with_suffix('.build.json').write_text(json.dumps(manifest,indent=2)+'\n')
    if admit(parent)!=parent_id:raise RuntimeError('adapter drift during build')
    receipt=dict(status='PASS',seconds=time.monotonic()-start,identity=admit(BINARY),fixture_identity=admit(out/'shape_fixture'),adapter_fixture_identity=admit(out/'adapter_fixture'),fights=0,execution='sequential nice requested; no fights')
    (HERE/'BUILD.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':build()
