"""Copy admitted v6/A0 seams into Stage A; engine and adapters stay read-only."""
import subprocess
import time
from common import ARMY,BINARY,CPP,HERE,LOCAL,load,read,sha,sources,write

def once(text,old,new):
    if text.count(old)!=1:raise RuntimeError('Stage A seam drift: '+old)
    return text.replace(old,new)

def build():
    start=time.monotonic();base=load('army_stagea_a0build',ARMY/'rev2/a0_build.py');base.HERE=HERE;base.BINARY=BINARY
    admission=load('stagea_admission',CPP/'build_admission.py');parent=admission.admit(base.PARENT);record=read(base.PARENT.with_suffix('.build.json'));out=BINARY.parent;out.mkdir(parents=True,exist_ok=True)
    generated=base.generated_sources()
    react=generated['react.cpp'];react='#include "stagea.h"\n'+react
    react=once(react,' S4V7Controller::prepare(o);',' stagea::begin(*this);\n if(!stage.weights||stage.weights->kind=="N1h")S4V7Controller::prepare(o);')
    react=once(react,'r.candidate.movement=S4V7Controller::decide(o,u.id);','if(stage.weights)r.candidate=stagea::command(*this,u.id);else r.candidate.movement=S4V7Controller::decide(o,u.id);')
    react=once(react,'r.executed.movement=useful;','r.stageRaw=r.candidate;r.executed.movement=useful;r.stageParticipation=r.executed;')
    react=once(react,'shapes_v6::threats(w,side,out);return out;', '''shapes_v6::threats(w,side,out);
 for(const auto& sh:w.shells){const auto* src=w.resolve(sh.source);if(src&&sh.at>w.time)out.stageShells.push_back({sh.pos.x,sh.pos.y,sh.at,sh.splash,double(sh.slow),double(src->team),sh.damage});}
 for(auto i:w.active)if(w.units[i].team==side)out.stageGuns[w.units[i].id]={(w.state[i].lobSpeed>0?w.state[i].lobSpeed:300)*w.state[i].launch,blastRadius(w,i)};
 return out;''')
    react=once(react,'if(auto* p=controller(w,side))p->shadow(shadow);','if(auto* p=controller(w,side)){p->shadow(shadow);if(side==0)stagea::configure(*p,js::get(request,"stageA"));}')
    react=once(react,'if(js::str(k)!="labReact")','if(js::str(k)!="labReact"&&js::str(k)!="stageA")')
    generated['react.cpp']=react
    host=generated['lean_host.cpp'];host='#include "stagea.h"\n'+host
    host=once(host,'if(operation=="catalog")','if(operation=="stageaReplay")return stagea::replay(request);\n  if(operation=="catalog")')
    # Full post-bridge and post-planner labels; snapshot was captured pre-prepare.
    host=once(host,'astelia::coreStep(w);++tick;dumpObserver(tick);','astelia::coreStep(w);++tick;for(auto& cc:w.controllers)if(auto* c=dynamic_cast<react_v1::Controller*>(cc.get()))stagea::record(*c);dumpObserver(tick);')
    host=once(host,'using js::V;', 'using js::V;\nV stageARequestRoot;js::Args stageABatchResults;')
    host=once(host,'V request=js::parse(line), result;', 'V request=js::parse(line), result;stageARequestRoot=request;')
    host=once(host,'js::collect({},0);', 'stageARequestRoot=V();stageABatchResults.clear();js::collect({},0);')
    host=once(host,'js::Args rows;for (auto r:request.p->items) rows.push_back(fight(r,counts,fights,testControllers,capture));result=js::arr(std::move(rows));',
              'stageABatchResults.clear();for (auto r:request.p->items) stageABatchResults.push_back(fight(r,counts,fights,testControllers,capture));result=js::arr(std::move(stageABatchResults));')
    # All tick JSON is serialized here; retain outer batches and trace history.
    host=once(host,'  }\n  counts.branchUnitActions+=', '''    js::Args roots=stageABatchResults;roots.push_back(stageARequestRoot);roots.push_back(request);for(const auto& h:history)roots.push_back(h.second);
    stagea::collectTick(w,std::move(roots),tick);
  }
  stagea::memoryReport(tick,js::arena.size(),js::arena.size(),true);
  counts.branchUnitActions+=''')
    generated['lean_host.cpp']=host
    shapes=generated['shapes.cpp']
    # Config validation passes the local extension only to the copied react layer.
    generated['shapes.cpp']=shapes
    header=(base.PARENT.parent/'react.h').read_text();header='#include "stagea.h"\n'+header
    header=once(header,'Command candidate,reactCandidate,executed;','Command candidate,reactCandidate,executed,stageParticipation,stageRaw;')
    header=once(header,' bool game=true;', ' std::vector<std::array<double,7>> stageShells;std::map<UnitId,std::array<double,2>> stageGuns;\n bool game=true;')
    header=once(header,' battery_v1::Battery battery;',' stagea::State stage;\n battery_v1::Battery battery;')
    (out/'react.h').write_text(header)
    for name in ('shapes.h','timing.h'):(out/name).write_text((CPP/'s4_shape_lab_v6'/name).read_text())
    # Avoid the singleton oracle planner entirely in network fights.
    oracle=(ARMY/'rev2/a0_oracle.cpp').read_text();oracle=once(oracle,'if(!c)return;','if(!c||c->stage.weights)return;')
    generated['a0_oracle.cpp']=oracle
    (out/'a0_oracle.h').write_text((ARMY/'rev2/a0_oracle.h').read_text())
    for name,text in generated.items():(out/name).write_text(text)
    flags=record['commands'][0][:record['commands'][0].index('-c')];flags=[flags[0],'-I'+str(out),'-I'+str(HERE),*flags[1:]]
    commands=[];objects=[];reused={}
    def compile(source,name):
        obj=out/name;argv=[*flags,'-c',str(source),'-o',str(obj)];subprocess.run(['nice','-n','15',*argv],check=True,timeout=180);commands.append(argv);objects.append(str(obj))
    local={argv[-1]:argv for argv in record['commands']}
    for path in record['link'][1:record['link'].index('-o')]:
        name=Path(path).name
        if name.removesuffix('.o')+'.cpp' in generated:compile(out/(name.removesuffix('.o')+'.cpp'),name)
        elif path in record['reused_object_sha256']:
            if sha(path)!=record['reused_object_sha256'][path]:raise RuntimeError('parent object drift')
            reused[path]=sha(path)
        elif path in local:
            argv=local[path];source=Path(argv[argv.index('-c')+1])
            if source.parent in (base.PARENT.parent,CPP/'s4_shape_lab_v6'):
                content=source.read_text().replace('../../s4_',str(CPP/'s4_')).replace('../s4_shape_lab_v1/',str(CPP/'s4_shape_lab_v1')+'/');source=out/source.name;source.write_text(content)
            compile(source,name)
        else:raise RuntimeError('unbound object '+path)
    compile(out/'a0_oracle.cpp','a0_oracle.o');compile(HERE/'stagea.cpp','stagea.o')
    link=[record['link'][0],*objects,*reused,'-o',str(BINARY)];subprocess.run(['nice','-n','15',*link],check=True,timeout=120)
    if admission.admit(base.PARENT)!=parent:raise RuntimeError('parent drift')
    hashes={k:v for k,v in record['source_hashes'].items() if Path(k).suffix in ('.py','.cpp','.h','.json')};hashes.update(sources())
    hashes.update({str(p.relative_to(CPP)):sha(p) for p in out.glob('*') if p.suffix in ('.cpp','.h')})
    write(BINARY.with_suffix('.build.json'),dict(schema=2,engine='army_stagea',scope='native_complete_engine',sanitized=False,portable=False,source_hashes=hashes,binary_sha256=sha(BINARY),commands=commands,link=link,reused_object_sha256=reused,parent=parent))
    write(HERE/'BUILD_STAGEA_SLIM.json',dict(status='BUILT_NOT_FIGHT_VERIFIED',seconds=time.monotonic()-start,identity=admission.admit(BINARY),fights=0))

from pathlib import Path
if __name__=='__main__':build()
