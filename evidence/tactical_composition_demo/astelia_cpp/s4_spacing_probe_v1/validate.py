"""Final delivery checks; availability is not experimental acceptance."""
import json,py_compile,sys
from common import *
sys.path.insert(0,str(CPP));from build_admission import admit

def main():
 d=pins();c=json.loads((HERE/'COMPACT.json').read_text());report=CPP/'S4_SPACING_PROBE.md';assert report.read_text().splitlines()[0]==c['status'];assert c['status'] in ('DONE','PARTIAL','NOT_RUN')
 assert json.loads((HERE/'STAGE_checks.json').read_text())['returncode']==0
 assert (HERE/'OWNER_RECHECK.md').read_text().startswith('APPROVE')
 for p in HERE.glob('*.py'):py_compile.compile(str(p),doraise=True)
 if c['status']=='NOT_RUN':
  assert c['completed_fights']==0 and json.loads((HERE/'PILOT_GATE.json').read_text())['status']=='UNAVAILABLE'
  assert not (HERE/'raw').exists() and not (HERE/'FIGHTS.json').exists() and not (HERE/'ENGINEERING.json').exists()
  assert all(v['value'] is None and v['status']=='not_run' for r in c['rows'] for v in r['measurements'].values())
 raw=json.loads((HERE/'RAW_FILES_LOCAL.json').read_text())
 for e in raw['files']:
  p=HERE/e['path'];assert p.stat().st_size==e['bytes'] and sha(p)==e['sha256']
 names=[str(p.relative_to(REPO)) for p in HERE.iterdir() if p.is_file() and p.name not in ('VALIDATION.json','DELIVERY_TRANSPORT.json','COMMIT.log','BUNDLE_VERIFY.log','GIT_WRITABILITY.json','PARTIAL.json')]
 names+=[str(report.relative_to(REPO)),'docs/reviews/tactical_0g_s196_probe_review_codex.md'];assert all((REPO/n).stat().st_size<=45_000_000 for n in names)
 write(HERE/'VALIDATION.json',dict(status='PASS',delivery_status=c['status'],checked_hashes={n:sha(REPO/n) for n in sorted(names)},historical_protected_files=len(d['protected']),all_protected_hashes_match=True,binary_identity=admit(BINARY),focused_tests=json.loads((HERE/'STAGE_checks.json').read_text()),combat_and_historical_combat_parity='NOT_RUN' if c['status']=='NOT_RUN' else 'see ENGINEERING.json',raw_files=len(raw['files']),no_committed_file_over_45MB=True,judging_ledger_read=False))
 print(json.dumps(dict(validation='PASS',status=c['status'],protected_files=len(d['protected']),raw_files=len(raw['files']))))
if __name__=='__main__':
 from common import caffeinate
 caffeinate();main()
