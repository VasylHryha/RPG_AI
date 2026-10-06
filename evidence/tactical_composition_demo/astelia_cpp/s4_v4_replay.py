"""Deadline-bound replay exports; every output-only decision sample stays in the export."""
import base64
import gzip
import json
from s4_development import ROOT,BINARY,sha
from s3_runner import request


def export_trace(output,name,spec,deadline):
    output.mkdir(parents=True,exist_ok=True)
    spec=dict(spec,trace=True,decisionDiagnostics=True)
    fight=request(spec)
    run=deadline.run([str(BINARY),'--capture-s3','--metrics'],json.dumps(fight)+'\n')
    if run.returncode:raise RuntimeError(run.stderr)
    rows=[json.loads(x) for x in run.stdout.splitlines()]
    terminal=rows[-1]
    if terminal.get('controllerStatus')!='completed' or any(terminal['controllerFailures']):raise RuntimeError('trace controller failure')
    with gzip.open(output/(name+'.jsonl.gz'),'wt') as stream:stream.write(run.stdout)
    frames=[];pending=None;decisions=[];captures=[]
    for row in rows:
        if 'state' in row:
            if pending is not None and pending['step']%3==0:frames.append(pending)
            pending=row
        elif row.get('decisionDiagnostics'):decisions.append(row)
        elif row.get('capture'):
            captures.append(row)
            if pending is not None:
                byid={u['id']:u for u in row['units']}
                for u in pending['state']['units']:
                    if u['id'] in byid:u['controllerState']=byid[u['id']]['state'];u['commitment']=byid[u['id']]['commitment']
    if pending is not None:frames.append(pending)
    for frame in frames:
        frame['state'].pop('debug',None)
        for unit in frame['state']['units']:
            for key in list(unit):
                if key not in ('id','team','role','x','y','hp','alive','target','controllerState','commitment','debug'):del unit[key]
            if 'debug' in unit:unit['debug']={k:unit['debug'][k] for k in ('r','maxhp')}
    payload=dict(spec=spec,request=fight,summary=terminal,frames=frames,width=1200,height=700,
                 decisionDiagnostics=decisions,decisionTraceRateHz=30)
    packed=gzip.compress(json.dumps(payload,separators=(',',':')).encode(),mtime=0)
    (output/(name+'.replay.json.gz')).write_bytes(packed)
    template=(ROOT/'s4_replay.html').read_text()
    (output/(name+'.html')).write_text(template.replace('/*REPLAY_DATA*/null',json.dumps(base64.b64encode(packed).decode())))
    return dict(file=name+'.html',raw=name+'.jsonl.gz',spec=spec,summary=terminal,metrics=json.loads(run.stderr),
                frames=len(frames),decision_ticks=len(decisions),sha256=sha(output/(name+'.jsonl.gz')))
