"""Validate the release's local integrity and editorial structure.

Does not check remote availability, experimental validity, or full theorem correctness.
Uses Python standard library. Rerun after any edit, then regenerate release checksums.
"""
from __future__ import annotations
from pathlib import Path
import hashlib
import json
import re
import zipfile

P=Path(__file__).resolve().parents[1]

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> dict:
    output=P/'checks/package_validation.json'
    if not output.exists(): output.write_text('{"status":"pending"}\n')
    problems=[]
    register=json.loads((P/'sources.json').read_text())
    cases=register['cases']; extras=register['further_reading']
    ids=[s['id'] for s in cases]; dois=[s['doi'].lower() for s in cases+extras]
    if len(ids)!=len(set(ids)): problems.append('Duplicate case IDs')
    if len(dois)!=len(set(dois)): problems.append('Duplicate registered DOIs')
    if set(ids)!={f'E{i:02d}' for i in range(1,23)}: problems.append('Unexpected case-ID set')
    for s in cases:
        for k in ['id','title','authors','year','doi','url','publication','evidence_type','rrg_relation','arrows','finding','externally_supplied','scope_limit','read_coverage','checked_on']:
            if not s.get(k): problems.append(f"{s['id']}: empty {k}")
        if not re.fullmatch(r'10\.\d{4,9}/\S+',s['doi']): problems.append(f"Malformed DOI: {s['id']}")
        if not set(s['arrows'])<=set(f'C{i}' for i in range(8)): problems.append(f"Unknown claim: {s['id']}")
    catalogue=(P/'06_evidence_catalog.md').read_text()
    for i in ids:
        if catalogue.count(f'<a id="{i.lower()}"></a>')!=1: problems.append(f'Missing/duplicate anchor {i}')
    active=list(P.glob('*.md'))+[P/'foundations/ERRATA.md']
    links_checked=0
    for f in active:
        text=f.read_text()
        # Ignore code spans/fences before testing math delimiter balance.
        clean=re.sub(r'```.*?```','',text,flags=re.S)
        clean=re.sub(r'`[^`\n]*`','',clean)
        stack=[]
        for m in re.finditer(r'(?<!\\)\\[\[\]]',clean):
            if m.group()=='\\[':
                if stack: problems.append(f'{f.name}: nested display delimiter')
                stack.append(m.start())
            elif not stack: problems.append(f'{f.name}: unmatched display close')
            else: stack.pop()
        if stack: problems.append(f'{f.name}: unclosed display math')
        if text.count('```')%2: problems.append(f'{f.name}: odd code fences')
        for m in re.finditer(r'\[[^\]]*\]\(([^)]+)\)',text):
            target=m.group(1)
            if target.startswith(('https://','http://','mailto:')): continue
            stem,_,anchor=target.partition('#')
            path=(f.parent/stem).resolve() if stem else f
            links_checked+=1
            if not path.exists(): problems.append(f'{f.name}: missing local link {target}')
            elif anchor and path.suffix=='.md' and anchor.startswith('e') and re.fullmatch(r'e\d\d',anchor):
                if f'<a id="{anchor}"></a>' not in path.read_text(): problems.append(f'{f.name}: missing anchor {target}')
    baseline=json.loads((P/'checks/baseline_hashes.json').read_text())
    preserved=[]
    for rel,expected in baseline.items():
        match=digest(P/rel)==expected
        preserved.append({'path':rel,'matches_original':match})
        if not match: problems.append(f'Original snapshot changed: {rel}')
    archive_checks=[]
    for zpath in sorted((P/'archive').glob('*.zip')):
        with zipfile.ZipFile(zpath) as z:
            bad=z.testzip()
            archive_checks.append({'path':str(zpath.relative_to(P)),'member_count':len(z.infolist()),'integrity_passed':bad is None})
            if bad: problems.append(f'{zpath.name}: bad ZIP member {bad}')
    mathcheck=json.loads((P/'checks/verification_results.json').read_text())
    if mathcheck['status']!='passed':problems.append('Math spot checks did not pass')
    report=dict(status='passed' if not problems else 'failed',primary_case_count=len(cases),further_reading_count=len(extras),
        deterministic_math_test_groups=mathcheck['number_of_test_groups'],active_markdown_files_checked=len(active),
        local_links_checked=links_checked,duplicate_case_ids=False if len(ids)==len(set(ids)) else True,
        duplicate_registered_dois=False if len(dois)==len(set(dois)) else True,
        originals=preserved,archive_integrity=archive_checks,problems=problems,
        limitations=['No remote-link availability recheck by this script','Historical 01–03 and archive text excluded from active syntax lint; known issues documented in foundations/ERRATA.md','No independent scientific replication or universal proof validation'])
    output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'case_count':len(cases),'local_links':links_checked,'problems':problems}))
    if problems: raise SystemExit(1)
    return report

if __name__=='__main__': main()
