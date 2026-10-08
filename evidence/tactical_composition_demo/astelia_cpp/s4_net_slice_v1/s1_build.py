"""New script-only native pilot bridge; unchanged ancestor objects/sources read-only."""
import argparse
from pathlib import Path
import subprocess
import time
from collection import HERE, sha, read, admission
from s0_analysis import DESIGN_COMMIT

OUT=HERE/'_local/s0s1/native'
BINARY=OUT/'s1_host'
RECORD=HERE/'S1_BUILD.json'


def once(source, old, new):
    if source.count(old)!=1:raise RuntimeError('native seam drift: '+old)
    return source.replace(old,new)


def generate():
    # Base generated planner is bound by the original build, not regenerated
    # from living design docs. Add provenance without changing scoring/assignment.
    planner=(HERE/'_local/build/teacher_planner.cpp').read_text()
    planner='#include "s1_script.h"\n'+planner
    planner=once(planner,'struct Cluster {double score;Vec2 point;};','struct Cluster {double score;Vec2 point;UnitId focus;};')
    planner=once(planner,'clusters.push_back({double(count)*guns,center});','clusters.push_back({double(count)*guns,center,w.units[i].id});')
    planner=once(planner,'std::vector<Attack> attacks;attacks.push_back', 's1_script::Provenance origin;std::vector<s1_script::Provenance> origins(1);std::vector<Attack> attacks;attacks.push_back')
    planner=once(planner,'attacks.push_back({family,variant,std::move(points),{},0});','attacks.push_back({family,variant,std::move(points),{},0});origins.push_back(origin);')
    planner=once(planner,'clusters.insert(clusters.begin(),{1e9,center});','clusters.insert(clusters.begin(),{1e9,center,w.units[enemies[k]].id});origin={w.units[enemies[k]].id,center};')
    planner=once(planner,'const auto center=clusters[k].point;','const auto center=clusters[k].point;origin={clusters[k].focus,center};')
    planner=once(planner,'const auto center=led(guns[k]);','const auto center=led(guns[k]);origin={w.units[guns[k]].id,center};')
    planner=once(planner,'std::vector<Attack> scored;','std::vector<s1_script::Provenance> scoredOrigins;std::vector<Attack> scored;')
    planner=once(planner,'scored.push_back(std::move(attack));','scoredOrigins.push_back(origins.at(size_t(&attack-attacks.data())));scored.push_back(std::move(attack));')
    planner=once(planner,'collectPlan(w,me,scored[best]);','s1_script::selectedSource=scoredOrigins.at(best);collectPlan(w,me,scored[best]);')
    planner=once(planner,'q.family=attack.family;q.variant=attack.variant;','q.family=attack.family;q.variant=attack.variant;if(attack.family!=AttackFamily::Singles&&attack.family!=AttackFamily::Left)s1_script::plannerSources[w.units[q.gun.slot].id]=s1_script::selectedSource;')
    # Delayed shapes are logged/rejected by wrapper rather than aborting a fight.
    planner=once(planner,'if(q.at>w.time+1e-9)throw std::logic_error("delayed teacher schedule");','/* delayed queue entries retained for explicit rejection */')
    teacher=(HERE/'teacher.cpp').read_text();helper=teacher[teacher.index('net_public::Snapshot view('):teacher.index('\n}\nLabels query')]
    controller=(HERE/'s1_controller.cpp').read_text().replace('PUBLIC_VIEW_HELPER',helper)
    host=(HERE/'host.cpp').read_text();a=host.index('void Host::prepare(');b=host.index('astelia::UnitDecision Host::decide(',a)
    host=host[:a]+host[b:]
    host=once(host,'astelia::decideUnit(w,i);}', 'astelia::decideUnit(w,i);if(h&&h->ablation=="s1_moving"&&w.units[i].team==1&&w.state[i].decision.release!=astelia::Release::None){auto& d=w.state[i].decision;d.move=true;d.goal={w.units[i].pos.x,400+110*std::sin(w.time*1.3+double(w.units[i].id))};d.multiplier=1;}}')
    host+='\n'+controller
    rpc=(HERE/'rpc.cpp').read_text();rpc=rpc[:rpc.index('int main(int argc,char** argv)')]
    rpc=once(rpc,'bool teacher=arm=="teacher";if(!teacher&&arm!="N1"&&arm!="N1r"&&arm!="N2")throw std::invalid_argument("collection arm");','bool teacher=true;if(arm!="T-unit-alone"&&arm!="T-unit+wrapper")throw std::invalid_argument("script-only pilot arms");s1_script::reset(arm=="T-unit+wrapper");')
    rpc=once(rpc,'config->skills[1].dodgeShells=true;','config->skills[1].dodgeShells=true;bool moving=js::truth(js::get(req,"moving"));if(moving){config->skills[1].smartShells=true;config->skills[1].castDodge=true;}')
    rpc=once(rpc,'w.add(side,astelia::Role(role),{x,y});','auto ref=w.add(side,astelia::Role(role),{x,y});if(role==2){w.units[ref.slot].cooldown=js::num(js::get(u,"initial_cooldown"));w.state[ref.slot].prep=js::num(js::get(u,"initial_prep"));}')
    rpc=once(rpc,'h->shadow=js::truth(js::get(req,"shadow"));','h->shadow=false;h->ablation=moving?"s1_moving":"s1_static";')
    rpc=once(rpc,'{"shadow",js::arr(std::move(shadow))}', '{"shadow",js::arr(std::move(shadow))},{"post_joint",host->views.empty()?V(nullptr):snapshot(w,0,astelia::UnitId(js::num(js::get(host->views[0],"self"))),host->tick,host->fight,host->lastLaunch,host->consumed)}')
    rpc=once(rpc,'{"terminal",true}', '{"terminal",true},{"native_shell_totals",stage1_diag::totals(w)}')
    rpc+='''\nint main(int argc,char** argv){try{if(argc!=2||std::string(argv[1])!="--collect")throw std::runtime_error("explicit pilot --collect required");std::string line;while(std::getline(std::cin,line)){collect(js::parse(line));js::collect({},0);}}catch(const std::exception& e){std::cerr<<e.what()<<'\\n';return 1;}}\n'''
    combat=(HERE/'_local/build/combat.cpp').read_text()
    combat=once(combat,'bool hit=false;auto& out=w.stats.shellOut[src->team];','stage1_diag::impact(w,shell);bool hit=false;auto& out=w.stats.shellOut[src->team];')
    rules=(HERE/'_local/build/rules.cpp').read_text()
    rules=once(rules,'s.dashReady=w.time+cooldown/s.timeRate;', 's.dashReady=w.time+cooldown/s.timeRate;if(u.team==1)if(auto* h=dynamic_cast<net_slice::Host*>(w.controllers[0].get()))h->collector.record(h->tick,u.id,"enemy_dash",js::obj({{"primitive","native_player_shot_dash"}}));')
    return dict(s1_rules='#include "s1_script.h"\n'+rules,s1_planner=planner,s1_host=host,s1_rpc='#include "s1_script.h"\n#include "stage1_impacts.h"\n'+rpc,s1_combat='#include "stage1_impacts.h"\n'+combat)


def build():
    if RECORD.exists():raise RuntimeError('existing build: use admit or a new revision; never overwrite')
    ancestor_pins=admission();record=read(HERE/'BUILD.json');start=time.monotonic();OUT.mkdir(parents=True,exist_ok=True)
    flags=record['commands'][0];flags=flags[:flags.index('-c')]+['-I'+str(HERE),'-I'+str(HERE.parent/'s4_shape_lab_v1')]
    link=record['links'][0];objects=[Path(p) for p in link[1:link.index('-o')] if Path(p).name not in ('rpc.o','host.o','teacher_planner.o','combat.o','rules.o')]
    original_objects={str(p):sha(p) for p in objects};sources={}
    # Original generated seams must equal committed BUILD hashes.
    for p in (HERE/'_local/build/teacher_planner.cpp',HERE/'_local/build/combat.cpp'):
        if record['sources'].get(str(p))!=sha(p):raise RuntimeError('base generated source drift')
    commands=[];extras=[]
    for name,source in generate().items():
        p=OUT/(name+'.cpp');p.write_text(source);o=OUT/(name+'.o');cmd=[*flags,'-c',str(p),'-o',str(o)];subprocess.run(cmd,check=True,timeout=180);commands.append(cmd);extras.append(str(o));sources[str(p)]=sha(p)
    for p in (HERE/'stage1_impacts.cpp',):
        o=OUT/(p.stem+'.o');cmd=[*flags,'-c',str(p),'-o',str(o)];subprocess.run(cmd,check=True,timeout=180);commands.append(cmd);extras.append(str(o))
    cmd=[link[0],*map(str,objects),*extras,'-o',str(BINARY)];subprocess.run(cmd,check=True,timeout=120);commands.append(cmd)
    if original_objects!={str(p):sha(p) for p in objects}:raise RuntimeError('read-only reused object drift')
    inputs=[HERE/'s1_build.py',HERE/'s1_controller.cpp',HERE/'s1_script.h',HERE/'stage1_impacts.cpp',HERE/'stage1_impacts.h',HERE/'BUILD.json',HERE/'teacher.cpp',HERE/'host.cpp',HERE/'rpc.cpp']
    value=dict(design_commit=DESIGN_COMMIT,physical_fights=0,ancestor_pins=ancestor_pins,wall_seconds=time.monotonic()-start,binary_sha256=sha(BINARY),sources={**sources,**{str(p):sha(p) for p in inputs}},objects=original_objects,commands=commands)
    RECORD.write_text(__import__('json').dumps(value,indent=2)+'\n');return value


def admit():
    v=read(RECORD)
    if admission()!=v['ancestor_pins']:raise RuntimeError('ancestor admission drift')
    if sha(BINARY)!=v['binary_sha256'] or any(sha(p)!=h for p,h in {**v['sources'],**v['objects']}.items()):raise RuntimeError('script pilot build drift')
    return v
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=('build','admit'));a=p.parse_args();print(__import__('json').dumps((build() if a.stage=='build' else admit()),indent=2))
