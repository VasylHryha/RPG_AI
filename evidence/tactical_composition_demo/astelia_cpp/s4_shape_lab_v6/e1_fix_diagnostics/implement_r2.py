"""Construct reviewable revision files without replacing historical receipts."""
import pathlib
p=pathlib.Path(__file__).resolve().parent.parent
if (p/'E1_REPORTING_R2.json').exists():
    raise RuntimeError('Historical initial construction only; never overwrite a sealed R2 repair')
original=(p/'e1_fix_diagnostics/original/lab.py').read_text()
s=original.replace('from report import stage_data','from report_r2 import stage_data').replace('from report import render','from report_r2 import render')
s=s.replace("    return path,stage_data(stage,look)","    if stage=='mechanism' and SELECTED_ARM=='E1':path=HERE/'MECHANISM_E1_SUMMARY_R2.json'\n    return path,stage_data(stage,look,arm=SELECTED_ARM)")
start=s.index('    with gzip.open',s.index('def verified_record('));end=s.index('    return r',start)
s=s[:start]+'''    receipt_path=RAW/(tag+'_COMPLETE.json')
    continuation=read(HERE/'E1_REPORTING_R2.json')
    if tag in continuation['inherited_receipts']:
        if sha(receipt_path)!=continuation['inherited_receipts'][tag]:
            raise RuntimeError('inherited measurement receipt drift')
    else:
        seal=read(RAW/(tag+'_VERIFIED_R2.json'))
        if seal!=dict(receipt_sha256=sha(receipt_path),metrics_sha256=sha(HERE/'metrics.py')):
            raise RuntimeError('completion measurement seal drift')
    # Existing stats were measured by the original metrics.py; continuation
    # hashes bind those receipt bytes, and the checks above bind raw bytes.
    if r['tag']!=tag or r['native_metrics']['executed_fights']!=1 or any(r['summary']['controllerFailures']):
        raise RuntimeError('completed cell native terminal drift')
''' +s[end:]
s=s.replace('    write(done, record, exclusive=True)\n    return record',"    write(done, record, exclusive=True)\n    write(RAW/(tag+'_VERIFIED_R2.json'),dict(receipt_sha256=sha(done),metrics_sha256=sha(HERE/'metrics.py')),exclusive=True)\n    return record")
s=s.replace("    declaration = read(HERE/'DECLARATION.json')\n    if sha(RAW", "    revision=read(HERE/'E1_REPORTING_R2.json')\n    if sha(HERE/'DECLARATION.json')!=revision['declaration_sha256']:raise RuntimeError('R2 inherited declaration drift')\n    for name,digest in revision['tool_hashes'].items():\n        if sha(HERE/name)!=digest:raise RuntimeError('R2 reporting tool drift: '+name)\n    declaration = read(HERE/'DECLARATION.json')\n    if sha(RAW")
s=s.replace("        if sha(CPP/name)!=digest:\n            raise RuntimeError('lab input drift: '+name)","        original=HERE/'e1_fix_diagnostics/original/lab.py' if name=='s4_shape_lab_v6/lab.py' else CPP/name\n        if sha(original)!=digest:\n            raise RuntimeError('lab input drift: '+name)")
s=s.replace('def records_for(stage):\n    return {p.name.removesuffix', 'def records_for(stage):\n    return {p.name.removesuffix') # replaced below
start=s.index('def records_for(stage):');end=s.index('\n\ndef samples_for',start)
s=s[:start]+'''def records_for(stage,arm=None,look=None):
    arms=comparison_arms(arm) if arm else ARMS
    records={}
    for p in sorted(RAW.glob('*_COMPLETE.json')):
        meta=read(p)['meta']
        if meta['stage']!=stage or meta['arm'] not in arms:continue
        if stage=='mechanism' and arm and meta['group'] not in groups(arm):continue
        if stage=='outcome' and look is not None and meta['pair']>=look:continue
        tag=p.name.removesuffix('_COMPLETE.json')
        records[tag]=verified_record(tag)
    return records
''' +s[end:]
# Done means no re-execution and no replacement RUN/gate/attempt receipts.
s=s.replace('def run(stage,look):\n    ensure_stage(stage,look)', '''def run(stage,look):
    done=HERE/f'RUN_{scope(stage)}.json'
    if done.exists() and read(done)['status']=='DONE' and (stage!='outcome' or read(done)['look']==look):
        report()
        print('Existing DONE stage preserved; read the selected summary before review')
        return
    ensure_stage(stage,look)''')
s=s.replace('    report()\n    print(\'Stage complete',"    report()\n    print('Stage complete")
s=s.replace("if __name__=='__main__': main()", "if __name__=='__main__':\n    sys.modules['lab_r2']=sys.modules[__name__]\n    main()")
# stat-invalidated streaming hashes; all native/source identities still checked.
s=s.replace('from build import BINARY, admit, sha','from build import BINARY\nfrom receipt_identity_r2 import admit, sha')
(p/'lab_r2.py').write_text(s)
# Keep the old import API for historical focused tests, use canonical R2 on CLI.
(p/'lab.py').write_text(original.replace("if __name__=='__main__': main()", "if __name__=='__main__':\n    from lab_r2 import main\n    main()"))
r=(p/'e1_fix_diagnostics/original/report.py').read_text().replace('import lab','import lab_r2 as lab')
r=r.replace('def stage_data(stage,look=None):\n    arm=lab.SELECTED_ARM;arms=lab.selected_arms();records=list(lab.records_for(stage).values())',"def stage_data(stage,look=None,arm=None,records=None):\n    arm=arm or lab.SELECTED_ARM;arms=lab.comparison_arms(arm)\n    if records is None:records=list(lab.records_for(stage,arm=arm,look=look).values())")
r=r.replace("def render():\n    d=lab.identity();saved=lab.SELECTED_ARM;result=", "def render():\n    d=lab.identity();selected=lab.SELECTED_ARM;result=")
start=r.index('    try:\n        for arm in lab.ARMS[1:]:',r.index('def render():'));end=r.index('    points=[]',start)
r=r[:start]+'''    # One snapshot per stage, selected arm only; no global arm mutation.
    records={stage:list(lab.records_for(stage,arm=selected).values()) for stage in ('mechanism','outcome','series')}
    result['arms'][selected]=dict(mechanism=stage_data('mechanism',arm=selected,records=records['mechanism']),outcomes={str(n):stage_data('outcome',n,arm=selected,records=records['outcome']) for n in lab.LOOKS},series=stage_data('series',arm=selected,records=records['series']))
    summary_path,summary=lab.stage_summary('mechanism')
    if summary['complete']:
        if summary_path.exists():
            if lab.read(summary_path)!=summary:raise RuntimeError('stage summary drift')
        else:lab.write(summary_path,summary,exclusive=True)
    lab.write(HERE/f'OBSERVATIONS_{selected}_R2.json',result)
''' +r[end:]
r=r.replace('for arm in lab.ARMS[1:]:','for arm in (selected,):')
r=r.replace("rows=list(lab.records_for('outcome').values());by=", "rows=records['outcome'];by=")
r=r.replace("HERE/'AXIS_CHART.json'","HERE/f'AXIS_CHART_{selected}_R2.json'").replace("HERE/'AXIS_CHART.svg'","HERE/f'AXIS_CHART_{selected}_R2.svg'").replace("HERE/'SHAPE_LAB_REPORT.md'","HERE/f'SHAPE_LAB_REPORT_{selected}_R2.md'")
r=r.replace("![Paired axes](AXIS_CHART.svg)","![Paired axes](AXIS_CHART_{selected}_R2.svg)")
# Format just the link separately rather than converting the prose to f-string.
r=r.replace("+json.dumps(result,indent=2)+'\\n```\\n')", "+json.dumps(result,indent=2)+'\\n```\\n').replace('{selected}',selected)") if False else r
r=r.replace("    from replays import render_selected\n    render_selected([*lab.records_for('outcome').values(),*lab.records_for('series').values()])", "    print(f'Report: {HERE / (\"SHAPE_LAB_REPORT_\"+selected+\"_R2.md\")}; mechanism summary: {summary_path}')")
r=r.replace("'Prepared development observations; no acceptance claim\\n", "f'Prepared development observations; no acceptance claim\\n")
(p/'report_r2.py').write_text(r)
