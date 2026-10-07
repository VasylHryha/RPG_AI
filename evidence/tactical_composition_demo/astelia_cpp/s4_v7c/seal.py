"""Seal validation only, after native parse proof and final noncombat tests."""
from common import *
from protocol import *
from run import validation_plan

def seal():
 started=time.monotonic()
 if (HERE/'SEAL.json').exists():pins();print('Existing seal verified');return
 if (HERE/'DECLARATION.json').exists() or (HERE/'raw').exists():raise RuntimeError('partial seal or combat artifacts; preserve and stop')
 expected=read(REPO/'research/rrg/v0.2.1.expected.json')
 for name,known in expected['expected_sha256'].items():
  if sha(REPO/'research/rrg/v0.2.1'/name)!=known:raise RuntimeError('current audited RRG source mismatch: '+name)
 release=REPO/'research/rrg/v0.2.1';manifest=read(release/'MANIFEST.json')
 if len(manifest['files'])!=23:raise RuntimeError('RRG manifest allocation drift')
 for row in manifest['files']:
  p=release/row['path']
  if sha(p)!=row['sha256'] or p.stat().st_size!=row['bytes']:raise RuntimeError('RRG manifest mismatch: '+row['path'])
 for line in (release/'SHA256SUMS.txt').read_text().splitlines():
  known,name=line.split(maxsplit=1)
  if sha(release/name.lstrip('*'))!=known:raise RuntimeError('RRG checksum mismatch: '+name)
 engineering=read(HERE/'ENGINEERING.json');origin=read(HERE/'THETA_ORIGIN.json');audit=read(HERE/'REQUEST_AUDIT.json')
 inherited_tuning()
 if engineering_inputs()!=engineering['input_hashes']:raise RuntimeError('tested implementation/input drift; run final suite after changes')
 if engineering['build_sha256']!=sha(HERE/'BUILD.json'):raise RuntimeError('tested build drift')
 if engineering['status']!='PASS' or engineering['binary']!=admit(BINARY) or engineering['request_audit_sha256']!=sha(HERE/'REQUEST_AUDIT.json'):raise RuntimeError('engineering/request audit not current')
 if not (HERE/'OWNER_RECHECK.md').read_text().startswith('APPROVE'):raise RuntimeError('owner recheck missing')
 if audit['executed_fights'] or audit['executed_steps'] or audit['worlds_created'] or audit['status']!='PASS' or audit['requests']!=400:raise RuntimeError('noncombat proof failed')
 old=read(ORIGIN/'DECLARATION.json')
 if audit['request_digests']!={tag:digest(rs) for tag,rs,_ in validation_plan(old)}:raise RuntimeError('audited requests changed before seal')
 if sha(HERE/'build/request_check')!=read(HERE/'BUILD.json')['request_checker_sha256']:raise RuntimeError('checker drift')
 if admit(BINARY)!=old['binary'] or (HERE/'protocol.py').read_bytes()!=(ORIGIN/'protocol.py').read_bytes():raise RuntimeError('controller/scientific contract drift')
 from verify_delivery import preservation,entropy
 preservation();entropy()
 hashes={}
 paths=[CPP/n for n in admit(BINARY)['sources']]
 paths+=list(HERE.glob('*.py'))+list(HERE.glob('*.cpp'))+list(HERE.glob('*.md'))+list(HERE.glob('*REQUEST_TEMPLATE.json'))
 paths += [HERE/n for n in ('VALIDATION_SEED_LEDGER.json','THETA_ORIGIN.json','BUILD.json','ENGINEERING.json','REQUEST_AUDIT.json','PRESERVATION.json','FIXTURE.log')]
 paths += list(HERE.glob('CHECK_ATTEMPT_*.json'))+list(HERE.glob('TESTS_*.log'))
 paths += [ORIGIN/n for n in origin['hashes']]
 paths += [CPP/'s4_escort_probe_v3/metrics.py',CPP/'s4_v6.py',CPP/'s4_v4.py',CPP/'s4_deadline.py',CPP/'build_admission.py',REPO/'research/rrg/CURRENT.md',REPO/'research/rrg/v0.2.1.expected.json']
 paths += list(release.rglob('*'))
 for p in paths:
  if p.is_file() and p.name not in FORBIDDEN:hashes[str(p.relative_to(REPO))]=sha(p)
 declaration={key:old[key] for key in ('design_commit','historical_theta','knob_order','bounds','workers','bootstrap','arms','heads','readings','omega0')}
 declaration.update(status='SEALED_BEFORE_VALIDATION_FIGHTS',created_utc=utc(),base_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),binary=admit(BINARY),hashes=hashes,
  ledger_sha256=sha(HERE/'VALIDATION_SEED_LEDGER.json'),theta_origin_sha256=sha(HERE/'THETA_ORIGIN.json'),tuning_origin=origin,
  fights=dict(tuning=0,validation=400),compute_cap_s=3600,compute_scope='v7c validation/analysis/render attempts only; no tuning or engineering charge',
  projection=old['projection'],engineering_sha256=sha(HERE/'ENGINEERING.json'),request_audit_sha256=sha(HERE/'REQUEST_AUDIT.json'),judging_ledger_read=False,retuning=False,
  diagnostic_fix='trace=True wherever validation attributionDiagnostics/decisionDiagnostics requested; all other request fields unchanged',
  preceding_stopped_attempt=dict(version='s4_v7b',commit=ORIGIN_COMMIT,cause='attributionDiagnostics requires trace and decisionDiagnostics; decisionDiagnostics also requires trace',executed_fights=0,executed_steps=0,raw_error='raw/validation_v7_regular_c03_o0.jsonl.gz',interrupted_claim='raw/validation_v7_regular_c02_o1_FAILURE.json',never_replay=True))
 exclusive(HERE/'DECLARATION.json',declaration)
 exclusive(HERE/'SEAL.json',dict(declaration_sha256=sha(HERE/'DECLARATION.json'),created_utc=utc(),seconds=time.monotonic()-started));pins()
 print('Sealed validation only: ordinal 161; 20 fresh clusters; 400 future fights; 0 executed fights/steps')

if __name__=='__main__':seal()
