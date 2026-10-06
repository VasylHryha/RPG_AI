"""Separate binary/host/dispatch; all historical source files stay untouched."""
import hashlib,json,pathlib,platform,shutil,subprocess,time
from build import ROOT,COMBAT_SOURCES
from build_admission import sha

def main():
    sources=['src/native/host_v6.cpp','src/native/config_codec.cpp','native_s4_attribution_contract.cpp',
             'native_s4_v6_contract.cpp','src/native/s4_v6_complex.cpp','src/native/s4_v6_controller.cpp',
             'src/native/s4_v6_dispatch.cpp',*COMBAT_SOURCES]
    compiler=pathlib.Path(shutil.which('clang++') or shutil.which('g++')).resolve()
    headers=sorted((ROOT/'src').rglob('*.h'))
    extra=[ROOT/'build_v6.py',ROOT/'build.py',ROOT/'native_s4_v4_contract.cpp',
           *[ROOT/('s4_attribution_checks/baseline_native/'+n) for n in ('v4_contract.cpp','s3_controller.cpp','s3_controller.h')]]
    inputs=[ROOT/n for n in sources]+headers+extra
    hashes={str(p.relative_to(ROOT)):sha(p) for p in inputs}
    common=[str(compiler),'-std=c++17','-O3','-fno-fast-math','-ffp-contract=off','-fwrapv',
            '-I'+str(ROOT/'src'),'-mcpu=native' if platform.machine()=='arm64' else '-march=native']
    commands=[];objects=[];started=time.monotonic();target=ROOT/'build/astelia_native_v6';target.parent.mkdir(exist_ok=True)
    for n in sources:
        obj=target.parent/('v6_'+pathlib.Path(n).stem+'.o');argv=common+(['-DmakeController=makeHistoricalController'] if n=='src/native/controller.cpp' else [])+["-c",str(ROOT/n),'-o',str(obj)]
        fingerprint=hashlib.sha256((json.dumps(hashes,sort_keys=True)+json.dumps(argv)).encode()).hexdigest()
        stamp=obj.with_suffix('.fingerprint');stored=stamp.read_text().splitlines() if stamp.exists() else []
        if not obj.exists() or stored!=[fingerprint,sha(obj)]:
            print('build',n,flush=True);subprocess.run(argv,check=True,timeout=120);stamp.write_text(fingerprint+'\n'+sha(obj)+'\n')
        commands.append(argv);objects.append(str(obj))
    link=[str(compiler),*objects,'-o',str(target)];subprocess.run(link,check=True,timeout=120)
    if any(sha(ROOT/n)!=h for n,h in hashes.items()):raise RuntimeError('source changed during build')
    manifest=dict(schema=2,engine='native_v6',scope='native_complete_engine',sanitized=False,portable=False,
                  source_hashes=hashes,binary_sha256=sha(target),commands=commands,link=link,
                  elapsed_seconds=time.monotonic()-started,compiler=subprocess.check_output([str(compiler),'--version'],text=True),compiler_sha256=sha(compiler))
    target.with_suffix('.build.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(dict(binary_sha256=manifest['binary_sha256'],elapsed_seconds=manifest['elapsed_seconds'])))

if __name__=='__main__':main()
