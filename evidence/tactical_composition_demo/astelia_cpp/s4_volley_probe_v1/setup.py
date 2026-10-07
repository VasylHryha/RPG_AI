import pathlib,sys,json,secrets,subprocess,hashlib,time
HERE=pathlib.Path(__file__).resolve().parent;CPP=HERE.parent;REPO=CPP.parents[2];sys.path.insert(0,str(CPP))
from build_admission import admit,sha
from s4_development import verify_sources
from s3_v6_runner import request
if __name__=='__main__':
 if (HERE/'DECLARATION.json').exists():raise RuntimeError('no reuse')
 verify_sources();build=admit(CPP/'build/astelia_native_observer_v1');old=set();seen={}
 def visit(v):
  if isinstance(v,dict):
   for x in v.values():visit(x)
  elif isinstance(v,list):
   for x in v:visit(x)
  elif type(v)==int:old.add(v)
 for p in CPP.rglob('*SEED_LEDGER.json'):
  if 'build' not in p.parts:visit(json.loads(p.read_text()));seen[str(p.relative_to(REPO))]=sha(p)
 for p in CPP.glob('s4*development*/*seeds.json'):visit(json.loads(p.read_text()));seen[str(p.relative_to(REPO))]=sha(p)
 seeds=[]
 while len(seeds)<11:
  s=3000000000+secrets.randbelow(1000000000)
  if s not in old and s not in seeds:seeds.append(s)
 knobs=json.loads((CPP/'s4_v6_development_20261007_025024/B_best.json').read_text())['resonator']
 protected={n:sha(REPO/n) for n in subprocess.check_output(['git','ls-files','evidence/tactical_composition_demo/astelia_cpp','evidence/tactical_composition_demo/astelia_snapshot','STATUS.json','docs/PLAN_CURRENT.md','evidence/tactical_composition_demo/DESIGN_0G.md'],cwd=REPO,text=True).splitlines() if (REPO/n).is_file()}
 declaration=dict(status='DECLARED_BEFORE_FIGHTS',entropy='OS secrets development only, no judging data read',development_seeds=seeds[:10],engineering_seed=seeds[-1],previous_development_ledgers=seen,arms=['P0','P1','P2','P3'],heads=['regular','novice'],orientations=[0,1],controlled_team=0,knobs=knobs,parameters=dict(k=3,max_hold_s=1.5,acquisition_window_s=.8,direct_release_enemy_guns_below=4,safety_margin_px=12,retreat_grid_px=20),projection_minutes=[10,20],compute_cap_s=3600,protected=protected,observer_build=build,interpretation='descriptive scripted feasibility only; fixed S4 sandboxAbilities=false, skill Auto; no tuning')
 (HERE/'DECLARATION.json').write_text(json.dumps(declaration,indent=2)+'\n')
 req=request(dict(arm='resonator',skeleton='v6',params=knobs,opponent='regular',seed=seeds[-1],setting='s4_full_head',controlledSide=0))
 (HERE/'ENGINEERING_REQUEST.json').write_text(json.dumps(req,indent=2)+'\n')
 start=time.monotonic();compiler=CPP/'build/astelia_native_observer_v1.build.json';manifest=json.loads(compiler.read_text());argv=manifest['commands'][0][:];argv=argv[:argv.index('-c')]+['-c',str(HERE/'prerequisites.cpp'),'-o',str(HERE/'prerequisites.o')];subprocess.run(argv,check=True)
 objects=[str(CPP/'build'/('observer_v1_'+pathlib.Path(n).stem+'.o')) for n in build['sources'] if n.endswith('.cpp') and n.startswith('src/native/') and not n.endswith('host_observer_v1.cpp')]
 # The linked build manifest is the authoritative ordered object list, including contracts.
 objects=[o for o in manifest['link'][1:-2] if not o.endswith('observer_v1_host_observer_v1.o')]
 for command in manifest['commands']:
  obj=pathlib.Path(command[-1]);stamp=obj.with_suffix('.fingerprint').read_text().splitlines();fingerprint=hashlib.sha256((json.dumps(manifest['source_hashes'],sort_keys=True)+json.dumps(command)).encode()).hexdigest();assert stamp==[fingerprint,sha(obj)],str(obj)
 subprocess.run([manifest['link'][0],str(HERE/'prerequisites.o'),*objects,'-o',str(HERE/'prerequisites')],check=True)
 r=subprocess.run([str(HERE/'prerequisites')],input=json.dumps(req)+'\n',text=True,capture_output=True,check=True,timeout=30)
 (HERE/'PREREQUISITES.json').write_text(json.dumps(dict(rows=[json.loads(l) for l in r.stdout.splitlines()],elapsed_s=time.monotonic()-start,request_sha256=sha(HERE/'ENGINEERING_REQUEST.json'),binary_sha256=sha(HERE/'prerequisites')),indent=2)+'\n');print(r.stdout)
