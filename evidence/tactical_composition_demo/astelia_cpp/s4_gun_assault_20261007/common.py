"""Observer-only diagnostic inputs and integrity helpers. No judging/tuning API."""
import hashlib,json,pathlib,sys
HERE=pathlib.Path(__file__).resolve().parent
CPP=HERE.parent
REPO=CPP.parents[2]
RAW=HERE/'raw'
BINARY=CPP/'build/astelia_native_observer_v1'
sys.path.insert(0,str(CPP))
ARMS=['v6_resonator','v6_morale','v5_resonator']
KNOB_FILES={'v6':CPP/'s4_v6_development_20261007_025024/B_best.json',
            'v5':CPP/'s4_v5_development_20261006_2308/B_best.json'}
ROLES=['melee','ranged','artillery','hunter','archer','player']
def sha(p):
 h=hashlib.sha256()
 with pathlib.Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def write(p,v):pathlib.Path(p).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def selected():
 return {a:json.loads(KNOB_FILES[a[:2]].read_text())[a[3:]] for a in ARMS}
def request_for(arm,head,seed,orientation,telemetry=True,trace=False):
 from s3_v6_runner import request
 req=request(dict(arm=arm[3:],skeleton=arm[:2],params=selected()[arm],opponent=head,seed=seed,
                  swapSides=bool(orientation),controlledSide=0,setting='s4_full_head',endCounts=True,trace=trace))
 if telemetry:req['killerTelemetry']=True
 req['decisionTrace']=True
 return req

def assert_pins():
 from build_admission import admit
 from s4_development import verify_sources
 record=json.loads((HERE/'INPUT_IDENTITY.json').read_text())
 for n,h in record['protected'].items():
  assert sha(REPO/n)==h,('protected input drift',n)
 for n,h in record['knob_files'].items():assert sha(REPO/n)==h,('knob drift',n)
 for n,h in record['script_hashes'].items():assert sha(HERE/n)==h,('script drift',n)
 assert sha(RAW/'DEVELOPMENT_SEED_LEDGER.json')==record['ledger_sha256']
 assert admit(BINARY)==record['observer_build']
 assert admit(CPP/'build/astelia_native_v6')==record['v6_build']
 verify_sources()
