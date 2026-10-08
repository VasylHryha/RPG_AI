"""Build a separate driver against hash-admitted objects; preserve net_host.

New driver and a read-only impact hook overlay are compiled. Original engine/collector/contract bytes and
BUILD.json remain immutable. No engine is executed by this build command.
"""
import argparse
from pathlib import Path
import subprocess
import time
from collection import HERE, read, sha, atomic, admission

BINARY=HERE/'_local/stage1_v2/native/stage1_host'


def build():
    admission(); original=sha(HERE/'_local/build/net_host'); record=read(HERE/'BUILD.json')
    out=BINARY.parent; out.mkdir(parents=True,exist_ok=True)
    source='#include "stage1_impacts.h"\n'+(HERE/'rpc.cpp').read_text()
    def replace(a,b):
        nonlocal source
        if source.count(a)!=1:
            raise RuntimeError('supplemental RPC seam drift: '+a)
        source=source.replace(a,b)
    main_start='int main(int argc,char** argv)'
    if source.count(main_start)!=1:
        raise RuntimeError('frozen RPC main seam drift')
    source=source[:source.index(main_start)]
    replace('{"terminal",true}', '{"terminal",true},{"native_shell_totals",stage1_diag::totals(w)}')
    replace('h->shadow=js::truth(js::get(req,"shadow"));',
            'h->shadow=js::truth(js::get(req,"shadow"));auto ab=js::get(req,"ablation");h->ablation=ab.tag==V::Undefined?"intact":js::str(ab);'
            'if(h->ablation!="intact"&&h->ablation!="K0"&&h->ablation!="frozen_phase"&&h->ablation!="topology_only"&&h->ablation!="no_geometry_to_mode"&&h->ablation!="no_mode_to_geometry"&&h->ablation!="no_reset")throw std::invalid_argument("ablation");')
    # One extra public diagnostic snapshot (post-action) measures actual geometry;
    # it never enters policy features or teacher queries.
    replace('{"shadow",js::arr(std::move(shadow))}',
            '{"shadow",js::arr(std::move(shadow))},{"post_joint",host->views.empty()?V(nullptr):snapshot(w,0,astelia::UnitId(js::num(js::get(host->views[0],"self"))),host->tick,host->fight,host->lastLaunch,host->consumed)},'
            '{"phase_state",[&](){js::Args a;for(auto p:host->phases)a.push_back(js::arr({double(p.first),p.second}));return js::arr(std::move(a));}()},'
            '{"phase_motion",[&](){js::Args a;for(auto p:host->lastDrift)a.push_back(js::arr({p.x,p.y}));return js::arr(std::move(a));}()}')
    driver=(HERE/'stage1_driver.cpp').read_text()
    driver=driver.replace('int main(int argc,char** argv)',(HERE/'stage1_stream.cpp').read_text()+'\nint main(int argc,char** argv)')
    seam='?stage1Sequence(req):rpc(req)'
    if driver.count(seam)!=1:
        raise RuntimeError('stream RPC dispatch seam drift')
    driver=driver.replace(seam,'?stage1Sequence(req):(js::str(js::get(req,"operation")).rfind("stage1_stream_",0)==0?stage1Stream(req):rpc(req))')
    driver=driver.replace("<<'\\n';","<<'\\n'<<std::flush;")
    driver=driver.replace('        }\n    }catch', '            if(!collection && js::str(js::get(req,"operation")).rfind("stage1_stream_",0)==0)stage1StreamCollect();\n        }\n    }catch')
    source+='\n'+driver
    generated=out/'driver.cpp'; generated.write_text(source)
    compile0=record['commands'][0]; flags=compile0[:compile0.index('-c')]
    flags+=['-I'+str(HERE),'-I'+str(HERE.parent/'s4_shape_lab_v1')]
    obj=out/'driver.o'; command=[*flags,'-c',str(generated),'-o',str(obj)]
    link=record['links'][0]; objects=[Path(p) for p in link[1:link.index('-o')] if Path(p).name!='rpc.o']
    hashes={str(p):sha(p) for p in objects}
    start=time.monotonic(); subprocess.run(command,check=True,timeout=180)
    combat_source=HERE/'_local/build/combat.cpp'
    combat=combat_source.read_text(); seam='bool hit=false;auto& out=w.stats.shellOut[src->team];'
    if combat.count(seam)!=1:
        raise RuntimeError('native shell impact seam drift')
    combat='#include "stage1_impacts.h"\n'+combat.replace(seam,'stage1_diag::impact(w,shell);'+seam)
    new_combat=out/'impact_combat.cpp'; new_combat.write_text(combat)
    extra=[]; extra_commands=[]
    for src in (new_combat,HERE/'stage1_impacts.cpp'):
        target=out/(src.stem+'.o'); cmd=[*flags,'-c',str(src),'-o',str(target)]
        subprocess.run(cmd,check=True,timeout=180); extra.append(str(target)); extra_commands.append(cmd)
    link_command=[link[0],*[str(p) for p in objects if p.name!='combat.o'],str(obj),*extra,'-o',str(BINARY)]
    subprocess.run(link_command,check=True,timeout=120)
    if original!=sha(HERE/'_local/build/net_host') or hashes!={str(p):sha(p) for p in objects}:
        raise RuntimeError('object/original binary drift during supplemental build')
    value=dict(status='PASS',binary_sha256=sha(BINARY),sources={n:sha(HERE/n) for n in ('rpc.cpp','stage1_driver.cpp','stage1_native_v2.py','stage1_stream.cpp','stage1_impacts.cpp','stage1_impacts.h')},
               original_build_sha256=sha(HERE/'BUILD.json'),original_binary_sha256=original,
               object_sha256=hashes,generated_sha256=sha(generated),combat_source_sha256=sha(combat_source),
               commands=[command,*extra_commands,link_command],
               wall_seconds=time.monotonic()-start,physical_fights=0)
    atomic(HERE/'STAGE1_NATIVE_BUILD_V2.json',value)
    return value


def admit_driver():
    admission(); value=read(HERE/'STAGE1_NATIVE_BUILD_V2.json')
    if value['binary_sha256']!=sha(BINARY) or value['original_build_sha256']!=sha(HERE/'BUILD.json'):
        raise RuntimeError('supplemental binary/build drift')
    if any(sha(HERE/n)!=h for n,h in value['sources'].items()) or any(sha(p)!=h for p,h in value['object_sha256'].items()):
        raise RuntimeError('supplemental driver/object drift')
    return value


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('stage',choices=('build','admit')); args=parser.parse_args()
    print((build() if args.stage=='build' else admit_driver())['status'])
