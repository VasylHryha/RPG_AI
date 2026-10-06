"""Pinned no-combat section-18.2 prerequisite; independent Python complex RK4."""
import argparse
import hashlib
import itertools
import json
import math
import pathlib
import shutil
import subprocess
import time

ROOT = pathlib.Path(__file__).resolve().parent
CHECKS = ROOT / 's4_v6_numerical_checks'
BINARY = ROOT / 'build/native_s4_v6_numerics'
Z_EDGE = 6000 ** (1 / 3) + math.sqrt(2) + 1

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + '\n')

def declaration():
    cases = []
    phases = [('real+', 1+0j), ('real-', -1+0j), ('imag+', 1j),
              ('imag-', -1j), ('oblique+', .6+.8j), ('oblique-', -.6-.8j)]
    signed = lambda values: [0] + [s*v for v in values if v for s in (-1, 1)]
    def add(label, mu, K, Kt, units):
        cases.append(dict(id=label, mu=mu, K=K, K_t=Kt, dt=1/30, units=units))
    for mu, omega, pressure, radius in itertools.product(
            [-2,-1,0,1,2], signed([0,1,2]), signed([0,1,10,100,1000,6000]), [0,.5,2,20,Z_EDGE]):
        for phase, direction in (phases if radius else [('zero', 0j)]):
            z = radius*direction
            label = f'isolated/mu={mu}/omega={omega}/P={pressure}/r={radius:.17g}/{phase}'
            add(label,mu,0,0,[[1,0,0,0,omega,pressure,z.real,z.imag]])
    # Freeze positions, previous assignments and distinct coupled geometries.
    patterns = {
        'pair_equal_empty': [(0,0,0, .5+.5j), (1,0,0,.5+.5j)],
        'pair_opposing_singleton': [(0,0,7,1j), (1,0,7,-1j)],
        'pair_asymmetric_singleton': [(0,0,7,.1+0j),(1,0,7,1+0j)],
        'pair_oblique_opposing': [(0,0,7,.3+.4j),(.7,.3,7,-1.2-1.6j)],
        'triple_cancelling': [(0,0,7,.5+.5j),(1,0,7,1j),(2,0,7,-1j)],
        'triple_asymmetric_lists': [(0,0,7,2+0j),(1,0,7,.1j),(3.5,0,0,-.6-.8j)],
        'triple_edge_opposing': [(0,0,7,Z_EDGE+0j),(.7,.3,7,-Z_EDGE*1j),(3.5,0,7,.3+.4j)],
        'triple_equal_real': [(0,0,7,.5+0j),(1,0,7,.5+0j),(2,0,7,.5+0j)],
    }
    for K,Kt,mu,omega,magnitude in itertools.product([0,1,5],[0,1,5],[-2,0,2],[-2,0,2],[1,100,6000]):
        for name, pattern in patterns.items():
            for sign in (-1,1):
                units = [[i+1,target,x,y,omega if i%2==0 else -omega,
                          magnitude*sign*(-1 if i%2 else 1),z.real,z.imag]
                         for i,(x,y,target,z) in enumerate(pattern)]
                add(f'{name}/mu={mu}/omega={omega}/P={sign*magnitude}/K={K}/Kt={Kt}',mu,K,Kt,units)
    return dict(schema=1, status='DECLARED_NO_COMBAT_BEFORE_CHECK', design='18.2 > 18.1 > 18',
                dt=1/30, amplitude_edge=Z_EDGE, component_tolerance=1e-3, commitment_tolerance=.02,
                implementation_tolerance=1e-9, reference='independent Python complex RK4; 4n equal substeps',
                fixture_scope='isolated, coupled pairs/triples; no controller/fights/entropy',
                patterns={n:[[x,y,t,z.real,z.imag] for x,y,t,z in p] for n,p in patterns.items()},cases=cases)

def build():
    compiler=shutil.which('clang++') or shutil.which('g++')
    if not compiler:raise RuntimeError('C++ compiler missing')
    sources=['native_s4_v6_numerics.cpp','src/native/s4_v6_complex.cpp']
    inputs=sources+['src/native/s4_v6_complex.h','src/js_value.h','s4_v6_numerics.py']
    hashes={name:sha(ROOT/name) for name in inputs}
    argv=[compiler,'-std=c++17','-O3','-fno-fast-math','-ffp-contract=off','-I'+str(ROOT/'src'),
          *[str(ROOT/n) for n in sources],'-o',str(BINARY)]
    BINARY.parent.mkdir(exist_ok=True)
    started=time.monotonic();r=subprocess.run(argv,capture_output=True,text=True,timeout=120)
    (CHECKS/'BUILD.stdout.txt').write_text(r.stdout);(CHECKS/'BUILD.stderr.txt').write_text(r.stderr)
    record=dict(argv=argv,returncode=r.returncode,elapsed_seconds=time.monotonic()-started,source_hashes=hashes)
    if r.returncode:write(CHECKS/'BUILD.json',record);raise RuntimeError('numerical fixture build failed')
    if any(sha(ROOT/n)!=h for n,h in hashes.items()):raise RuntimeError('source changed during build')
    record.update(binary_sha256=sha(BINARY),compiler=subprocess.check_output([compiler,'--version'],text=True),
                  scope='no_combat_numerical_kernel',fights=0)
    write(CHECKS/'BUILD.json',record)

def reference(case, steps):
    # Independent topology, group construction and ODE, never calling native RHS.
    units=case['units'];mu=case['mu'];K=case['K'];Kt=case['K_t'];h=case['dt']/steps
    z=[complex(u[6],u[7]) for u in units]
    ns=[];groups=[]
    for i,u in enumerate(units):
        nearby=[(math.hypot(v[2]-u[2],v[3]-u[3]),v[0],j) for j,v in enumerate(units)
                if j!=i and math.hypot(v[2]-u[2],v[3]-u[3])<3]
        ns.append([(j,math.exp(-r*r)) for r,_,j in sorted(nearby)[:8]])
        groups.append([j for j,v in enumerate(units) if j!=i and u[1]!=0 and v[1]==u[1]])
    def derivative(values):
        out=[]
        for i,(u,zi) in enumerate(zip(units,values)):
            d=complex(mu,u[4])*zi-(zi.real*zi.real+zi.imag*zi.imag)*zi-u[5]
            if ns[i]:d+=K*sum(w*(values[j]-zi) for j,w in ns[i])/len(ns[i])
            if groups[i]:d+=Kt*(sum(values[j] for j in groups[i])/len(groups[i])-zi)
            out.append(d)
        return out
    for _ in range(steps):
        k1=derivative(z)
        k2=derivative([v+h*d/2 for v,d in zip(z,k1)])
        k3=derivative([v+h*d/2 for v,d in zip(z,k2)])
        k4=derivative([v+h*d for v,d in zip(z,k3)])
        z=[v+h*(a+2*b+2*c+d)/6 for v,a,b,c,d in zip(z,k1,k2,k3,k4)]
    return z

def acceptance():
    if (CHECKS/'ACCEPTANCE.json').exists():raise RuntimeError('preserve previous no-combat result; do not rerun')
    pin=json.loads((CHECKS/'INPUTS.json').read_text())
    if any(sha(ROOT/n)!=h for n,h in pin['hashes'].items()):raise RuntimeError('pre-check fixture/source drift')
    declared=json.loads((CHECKS/'FIXTURES.json').read_text());cases=declared['cases']
    started=time.monotonic()
    run=subprocess.run([str(BINARY)],input=''.join(json.dumps(c,allow_nan=False)+'\n' for c in cases),
                       capture_output=True,text=True,timeout=120)
    (CHECKS/'NATIVE_ROWS.jsonl').write_text(run.stdout);(CHECKS/'NATIVE.stderr.txt').write_text(run.stderr)
    if run.returncode:raise RuntimeError('native numerical fixture process failed')
    native=[json.loads(row) for row in run.stdout.splitlines()]
    if len(native)!=len(cases):raise RuntimeError('native fixture row coverage mismatch')
    results=[];failures=[];maxima={name:dict(value=0,case=None) for name in ('real','imag','commitment','implementation')}
    counts={};retries=0
    clip=lambda x:max(-1,min(1,x))
    for case,row in zip(cases,native):
        result=dict(id=case['id'],n=row['n'],Z=row['Z'],retries=row['retries'],accepted=row['accepted'],reason=row['reason'])
        if not row['accepted']:
            result['status']='FAIL';failures.append(result);results.append(result);continue
        initial_Z=max(max(abs(complex(u[6],u[7])) for u in case['units']),
                      max(abs(u[5]) for u in case['units'])**(1/3)+math.sqrt(max(case['mu'],0)))+1
        expected_Z=initial_Z*(2**row['retries'])
        expected_n=max(1,math.ceil(case['dt']*(abs(case['mu'])+max(abs(u[4]) for u in case['units'])
                                             +3*expected_Z**2+case['K']+case['K_t'])))
        if row['retries'] not in (0,1) or row['n']!=expected_n or abs(row['Z']-expected_Z)>1e-12:
            raise RuntimeError('native policy accounting disagrees with independent formula: '+case['id'])
        if len(row['units'])!=len(case['units']) or any(len(u)!=2 for u in row['units']):
            raise RuntimeError('native unit/component coverage mismatch: '+case['id'])
        counts[str(row['n'])]=counts.get(str(row['n']),0)+1;retries+=row['retries']
        coarse=reference(case,expected_n);fine=reference(case,4*expected_n)
        actual=[complex(*u) for u in row['units']]
        if any(not math.isfinite(z.real) or not math.isfinite(z.imag) for values in (actual,coarse,fine) for z in values):
            raise RuntimeError('nonfinite native/reference component: '+case['id'])
        errors=dict(real=max(abs(a.real-b.real) for a,b in zip(actual,fine)),
                    imag=max(abs(a.imag-b.imag) for a,b in zip(actual,fine)),
                    commitment=max(abs(clip(a.real)-clip(b.real)) for a,b in zip(actual,fine)),
                    implementation=max(abs(a-b) for a,b in zip(actual,coarse)))
        if not all(math.isfinite(e) for e in errors.values()):raise RuntimeError('nonfinite reference/accuracy result')
        failed=[name for name,e in errors.items() if e> (1e-3 if name in ('real','imag') else .02 if name=='commitment' else 1e-9)]
        result.update(errors=errors,status='FAIL' if failed else 'PASS',failed_checks=failed,
                      native=[[a.real,a.imag] for a in actual],reference_4n=[[a.real,a.imag] for a in fine])
        for name,e in errors.items():
            if e>maxima[name]['value']:maxima[name]=dict(value=e,case=case['id'])
        if failed:failures.append(result)
        results.append(result)
    write(CHECKS/'ACCEPTANCE_ROWS.json',results)
    write(CHECKS/'FAILING_CASES.json',failures)
    summary=dict(status='NOT_READY' if failures else 'PASS',cases=len(cases),failures=len(failures),
                 passing=len(cases)-len(failures),max_errors=maxima,substep_counts=counts,retries=retries,
                 elapsed_seconds=time.monotonic()-started,fights=0,
                 fixture_declaration_sha256=sha(CHECKS/'FIXTURES.json'),input_pin_sha256=sha(CHECKS/'INPUTS.json'),
                 native_rows_sha256=sha(CHECKS/'NATIVE_ROWS.jsonl'),all_results_sha256=sha(CHECKS/'ACCEPTANCE_ROWS.json'),
                 failing_cases_sha256=sha(CHECKS/'FAILING_CASES.json'))
    write(CHECKS/'ACCEPTANCE.json',summary)
    return summary

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--declare-build',action='store_true');args=ap.parse_args()
    if not args.declare_build:ap.error('acceptance is run once by pytest, after the completed kernel/fixture change batch')
    CHECKS.mkdir(exist_ok=False)
    write(CHECKS/'FIXTURES.json',declaration())
    build()
    names=['s4_v6_numerics.py','native_s4_v6_numerics.cpp','src/native/s4_v6_complex.cpp','src/native/s4_v6_complex.h',
           'test_s4_v6_numerics.py','s4_v6_numerical_checks/FIXTURES.json','build/native_s4_v6_numerics',
           '../../../docs/reviews/tactical_0g_s18_design_review_codex_r3.md','../DESIGN_0G.md']
    write(CHECKS/'INPUTS.json',dict(hashes={n:sha(ROOT/n) for n in names},fights=0))
    print(json.dumps(dict(cases=len(declaration()['cases']),fixture_sha256=sha(CHECKS/'FIXTURES.json'),fights=0)))

if __name__=='__main__':main()
