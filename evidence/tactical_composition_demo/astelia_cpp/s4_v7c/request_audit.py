"""Zero-world native parsing of every actual validation request before sealing."""
from common import *
from run import validation_plan

def parse_only(requests):
 built=read(HERE/'BUILD.json');checker=HERE/'build/request_check'
 if sha(checker)!=built['request_checker_sha256'] or sha(HERE/'request_check.cpp')!=built['request_checker_source_sha256']:raise RuntimeError('request checker drift')
 p=subprocess.run([str(checker)],input=''.join(json.dumps(r,allow_nan=False)+'\n' for r in requests),capture_output=True,text=True,timeout=60)
 if p.returncode or p.stderr:raise RuntimeError('request checker failed: '+p.stderr)
 rows=[json.loads(line) for line in p.stdout.splitlines()]
 if len(rows)!=len(requests):raise RuntimeError('parser count mismatch')
 if any(r['executed_steps'] or r['executed_fights'] or r['worlds_created'] for r in rows):raise RuntimeError('nonzero work in request checker')
 return rows

def audit():
 origin=read(HERE/'THETA_ORIGIN.json')
 cells=list(validation_plan(origin));requests=[rs[0] for _,rs,_ in cells]
 if len(cells)!=400:raise RuntimeError('validation allocation mismatch')
 rows=parse_only(requests)
 if any(r.get('status')!='VALID' for r in rows):raise RuntimeError('native parser rejection: '+str([r for r in rows if 'error' in r]))
 receipt=dict(status='PASS',noncombat=True,executed_fights=0,executed_steps=0,worlds_created=0,
  binary_dry_validation=dict(status='NOT_SUPPORTED',reason='s4_v7_host.cpp accepts catalog/contracts/capture/test-controllers/metrics only; valid fight requests immediately create World and increment executed_fights. Combat binary never invoked for templates.'),
  separate_checker=dict(scope='actual unchanged native configuration codec and controller constructors; scalar World::create guard without world construction',sha256=sha(HERE/'build/request_check'),source_sha256=sha(HERE/'request_check.cpp')),
  templates=20,requests=400,orientations=2,arms=['v7','forcedP16','forcedv6','omega0','historicalP16'],heads=['regular','novice'],
  diagnostic_fix='trace=True when validation telemetry=True; decisionDiagnostics and attributionDiagnostics retained',
  request_digests={tag:digest(reqs) for tag,reqs,_ in cells},
  template_hashes={head:sha(HERE/(head.upper()+'_REQUEST_TEMPLATE.json')) for head in ('regular','novice')},
  tuning_sha256=tuning_hash(),ledger_sha256=sha(HERE/'VALIDATION_SEED_LEDGER.json'),
  host_sha256=sha(CPP/'src/native/s4_v7_host.cpp'),codec_sha256=sha(CPP/'src/native/observer_v1_config_codec.cpp'))
 write(HERE/'REQUEST_AUDIT.json',receipt)
 return receipt
