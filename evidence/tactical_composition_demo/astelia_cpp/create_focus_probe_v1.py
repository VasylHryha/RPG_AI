"""Historical bootstrap helper used once before fights; delivered run/analyze/test scripts are final."""
import pathlib,json,hashlib,secrets,subprocess,time
CPP=pathlib.Path(__file__).resolve().parent;REPO=CPP.parents[2];OLD=CPP/'s4_volley_probe_v1';HERE=CPP/'s4_focus_probe_v1'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def main():
 HERE.mkdir(exist_ok=False)
 prior=json.loads((OLD/'DECLARATION.json').read_text());used=set(prior['development_seeds']+[prior['engineering_seed']]);ledgers={}
 def collect(v):
  if isinstance(v,int):used.add(v)
  elif isinstance(v,list):
   for x in v:collect(x)
  elif isinstance(v,dict):
   for x in v.values():collect(x)
 for n in prior['previous_development_ledgers']:
  if pathlib.Path(n).name=='S4_SEED_LEDGER.json':continue # do not read any judging entropy
  p=REPO/n;collect(json.loads(p.read_text()));ledgers[n]=sha(p)
 for p in [OLD/'DECLARATION.json',CPP/'s4_gun_assault_20261007/raw/DEVELOPMENT_SEED_LEDGER.json']:
  collect(json.loads(p.read_text()));ledgers[str(p.relative_to(REPO))]=sha(p)
 seeds=[]
 while len(seeds)<11:
  x=0xC0000000+secrets.randbelow(0x40000000)
  if x not in used and x not in seeds:seeds.append(x)
 tracked=subprocess.check_output(['git','ls-files','-z'],cwd=REPO).decode().split('\0');protected={n:sha(REPO/n) for n in tracked if n and (REPO/n).is_file()}
 params=dict(commit_margin_px=12,movement_speed_multiplier=1,movement_zero_tolerance_px=1e-9,coincident_direction='positive x',focus_order=['remaining HP ascending','id ascending'],global_anchor='weakest living enemy gun reachable by at least one own gun; if none reachable, weakest living enemy gun',p5_approach='individual reachable weakest gun; otherwise global anchor',p6_direct='global anchor if within native direct reach; otherwise unchanged v6 target',workers=4,fight_cap_seconds=1200,analysis_cap_seconds=1200,total_compute_cap_seconds=3600)
 write(HERE/'DECLARATION.json',dict(status='DECLARED_BEFORE_FIGHTS',created_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),entropy='fresh OS secrets, development high partition; no judging ledger read',development_seeds=seeds[:10],engineering_seed=seeds[10],previous_development_ledgers=ledgers,arms=['P0','P4','P5','P6'],heads=['regular','novice'],orientations=[0,1],controlled_team=0,knobs=prior['knobs'],parameters=params,protected=protected))
 for n in ['run.py','check.py','test_probe.py','deliver.py']:
  s=(OLD/n).read_text().replace('volley_probe_v1','focus_probe_v1').replace('S4_VOLLEY_PROBE','S4_FOCUS_PROBE')
  (HERE/n).write_text(s)
 s=(CPP/'build_volley_probe_v1.py').read_text().replace('volley_probe_v1','focus_probe_v1');(CPP/'build_focus_probe_v1.py').write_text(s)
 write(HERE/'DEVELOPMENT_SEED_LEDGER.json',dict(status='development only; single use, not judging',seeds=seeds[:10],engineering_seed=seeds[10],previous_development_ledgers=ledgers))
if __name__=='__main__':main()
