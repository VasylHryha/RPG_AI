"""Copy Stage A native seams into a separately admitted Stage B2 binary."""
import runtime as r
import subprocess,time
from pathlib import Path

def once(text,old,new):
    if text.count(old)!=1:raise RuntimeError('Stage B2 seam drift: '+old)
    return text.replace(old,new)

def prepare_sources(out):
    for p in (r.A_LOCAL/'build').iterdir():
        if p.suffix in ('.cpp','.h'):(out/p.name).write_bytes(p.read_bytes())
    (out/'stagea.h').write_text((r.STAGEA/'stagea.h').read_text().replace('bool collect=false,parity=false;', 'bool collect=false,parity=false,shadow=false;js::V shadowLabels;').replace('std::string kind;', 'std::string kind;Vec fireThresholds;'))
    text=(r.STAGEA/'stagea.cpp').read_text()
    text=once(text,'kind=js::str(js::get(v,"kind"));','kind=js::str(js::get(v,"kind"));auto ft=js::get(v,"fireThresholds");if(ft.tag!=js::V::Undefined){fireThresholds=nums(ft);if(fireThresholds.size()!=3)throw std::invalid_argument("fire threshold roles");}')
    text=once(text,'c.stage.parity=js::truth(js::get(config,"parity"));','c.stage.parity=js::truth(js::get(config,"parity"));c.stage.shadow=js::truth(js::get(config,"shadow"));')
    text=once(text,'js::V commandJSON(', 'size_t decodeFire(const Weights& w,const Vec& y,size_t role){if(w.fireThresholds.empty())return std::max_element(y.begin()+3,y.begin()+6)-(y.begin()+3);return std::max(y[3],y[5])-y[4]>=w.fireThresholds.at(role)?(y[3]>=y[5]?0:2):1;}\njs::V commandJSON(')
    text=once(text,'auto fire=std::max_element(y.begin()+3,y.begin()+6)-(y.begin()+3);','auto fire=decodeFire(*c.stage.weights,y,uint8_t(u.role));')
    text=once(text,'js::Args outputs;for(auto row:frames.p->items)', 'js::Args outputs,fireClasses;for(auto row:frames.p->items)')
    text=once(text,'outputs.push_back(matrixJSON(infer(s,p,js::num(js::get(row,"dt")),refresh)));','auto values=infer(s,p,js::num(js::get(row,"dt")),refresh);outputs.push_back(matrixJSON(values));js::Args classes;auto units=mat(js::get(row,"units"));std::sort(units.begin(),units.end(),[](auto&a,auto&b){return a[0]<b[0];});size_t index=0;for(auto& u:units)if(u[1]==0)classes.push_back(double(decodeFire(*s.weights,values.at(index++),size_t(u[2]))));fireClasses.push_back(js::arr(std::move(classes)));')
    text=once(text,'{"stageAReplay",true},{"outputs",js::arr(std::move(outputs))}', '{"stageAReplay",true},{"outputs",js::arr(std::move(outputs))},{"fireClasses",js::arr(std::move(fireClasses))}')
    text=once(text,'js::set(row,"labels",js::arr(std::move(labels)));','js::set(row,"labels",js::arr(std::move(labels)));if(c.stage.shadow)js::set(row,"shadowLabels",c.stage.shadowLabels);')
    (out/'stagea.cpp').write_text(text)
    text=(out/'lean_host.cpp').read_text();text='#include "shadow.h"\n'+text
    text=once(text,'if(operation=="stageaReplay")','if(operation=="stagebOracleReplay")return stageb::replay(request);\n  if(operation=="stageaReplay")')
    (out/'lean_host.cpp').write_text(text)
    text=(out/'react.cpp').read_text();text='#include "shadow.h"\n'+text
    text=once(text,'if(side==0)stagea::configure(*p,js::get(request,"stageA"));','if(side==0){stagea::configure(*p,js::get(request,"stageA"));stageb::reset(w,request);}')
    (out/'react.cpp').write_text(text)
    text=(out/'react_combat.cpp').read_text();text='#include "shadow.h"\n'+text
    text=once(text,'react_v1::prepare(w);battery_v1::prepareDummies(w);','stageb::shadow(w);react_v1::prepare(w);battery_v1::prepareDummies(w);')
    (out/'react_combat.cpp').write_text(text)
    from native_patch import apply
    apply(out)

def build():
    from jobs import locked
    with locked():return _build()

def _build():
    start=time.monotonic();parent=r.A_LOCAL/'build/tactics_react_host_stagea'
    admission=r.common.load('stageb_admission',r.CPP/'build_admission.py')
    proof=admission.admit(parent);record=r.read(parent.with_suffix('.build.json'))
    out=r.BINARY.parent;out.mkdir(parents=True,exist_ok=True)
    prepare_sources(out)
    flags=record['commands'][0][:record['commands'][0].index('-c')]
    flags=[flags[0],'-I'+str(out),'-I'+str(r.HERE),*flags[1:]]
    commands=[];objects=[];reused={}
    def compile(p,name=None):
        obj=out/(name or (p.stem+'.o'));argv=[*flags,'-c',str(p),'-o',str(obj)]
        subprocess.run(['nice','-n','15',*argv],check=True,timeout=180);commands.append(argv);objects.append(str(obj))
    local={Path(a[-1]).name:a for a in record['commands']}
    for p in record['link'][1:record['link'].index('-o')]:
        if Path(p).name in local:
            source=Path(local[Path(p).name][local[Path(p).name].index('-c')+1])
            compile(out/source.name if source.parent==parent.parent or source.name=='stagea.cpp' else source,Path(p).name)
        else:
            if r.sha(p)!=record['reused_object_sha256'][p]:raise RuntimeError('reused object drift')
            reused[p]=r.sha(p)
    compile(r.HERE/'shadow.cpp')
    link=[record['link'][0],*objects,*reused,'-o',str(r.BINARY)]
    subprocess.run(['nice','-n','15',*link],check=True,timeout=120)
    if admission.admit(parent)!=proof:raise RuntimeError('Stage A parent drift')
    hashes={k:v for k,v in record['source_hashes'].items() if Path(k).suffix in ('.py','.cpp','.h')}
    hashes.update(r.sources());hashes.update({str(p.relative_to(r.CPP)):r.sha(p) for p in out.iterdir() if p.suffix in ('.cpp','.h')})
    r.write(r.BINARY.with_suffix('.build.json'),dict(schema=2,engine='army_stageb2',scope='native_complete_engine',portable=False,sanitized=False,source_hashes=hashes,binary_sha256=r.sha(r.BINARY),commands=commands,link=link,reused_object_sha256=reused,parent=proof))
    r.write(r.HERE/'BUILD_STAGEB2.json',dict(seconds=time.monotonic()-start,identity=admission.admit(r.BINARY)))
if __name__=='__main__':build()
