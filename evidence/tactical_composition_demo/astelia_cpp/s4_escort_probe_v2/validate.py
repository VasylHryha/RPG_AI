"""Delivery identity audit; no fights or process inspection."""
from common import *
def main():
 d=pins();identity=admit(BINARY);checks=json.loads((HERE/'CHECKS.json').read_text())
 assert checks['status']=='PASS' and checks['noncombat'] and checks['binary_identity']==identity and checks['declaration_sha256']==sha(HERE/'DECLARATION.json')
 assert (HERE/'OWNER_RECHECK.md').read_text().startswith('APPROVE')
 assert not (HERE/'raw').exists(),'Codex delivery must have no combat claims/raw'
 assert json.loads((HERE/'COMPACT.json').read_text())['status']=='NOT_RUN'
 files=[p for p in sorted(HERE.iterdir()) if p.is_file() and p.suffix not in ('.bundle',) and p.name not in ('VALIDATION.json','GIT_WRITABILITY.json','COMMIT.log','BUNDLE_VERIFY.log','DELIVERY_TRANSPORT.json')]
 files.append(REPO/'docs/reviews/tactical_0g_s1910_probe_review_codex.md')
 assert all(p.stat().st_size<=45_000_000 for p in files)
 write(HERE/'VALIDATION.json',dict(status='PASS',scope='native build and focused noncombat checks only; Claude combat pending',utc=utc(),checked_hashes={str(p.relative_to(REPO)):sha(p) for p in files},binary_identity=identity,protected_files_verified=len(d['protected']),engineering='NOT_RUN',combat='NOT_RUN',judging_ledger_read=False,limits=['Same-family Codex implementation recheck; Claude combat execution and result recheck pending','No native fights or process listing executed by Codex']))
 print('PASS: sealed identities, protected inputs, native admission, focused checks, NOT_RUN combat and size bounds')
if __name__=='__main__':main()
