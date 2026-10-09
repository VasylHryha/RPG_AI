"""Have authenticated Claude author the owner-approved live training cap."""
import runtime as r
import json,subprocess

def main():
    path=r.LOCAL/'TRAIN_CAP.json'
    if path.exists():
        from training_control import training_cap
        cap=training_cap(r.HERE)
        if cap.get('written_by')!='Claude' or cap['cap_seconds']>10800:raise RuntimeError('invalid Stage B2 Claude cap')
        return # Never overwrite a live owner reduction.
    authority=r.read(r.LOCAL/'CAP_AUTHORITY.json')
    if authority.get('approved_by')!='owner' or not 0<authority.get('cap_seconds',0)<=10800:raise RuntimeError('B2 owner cap authority required; do not reuse Stage B approval')
    prompt='Owner B2 cap authority: '+json.dumps(authority)+'. Return only JSON with the identical cap_seconds, date, approval_reference, approved_by owner, written_by Claude, scope Stage B2 concurrent training invocation. No tools.' 
    out=subprocess.run(['claude','-p','--no-session-persistence','--tools=','--',prompt],capture_output=True,text=True,timeout=60)
    if out.returncode:raise RuntimeError('Claude cap authorship failed: '+out.stdout[:300]+out.stderr[:300])
    text=out.stdout.strip()
    if text.startswith('```'):text=text.split('\n',1)[1].rsplit('```',1)[0]
    value=json.loads(text)
    if value.get('written_by')!='Claude' or value.get('approved_by')!='owner' or value.get('cap_seconds')!=authority['cap_seconds'] or value.get('date')!=authority['date']:raise RuntimeError('Claude cap content rejected')
    r.write(r.LOCAL/'CLAUDE_CAP_AUTHORSHIP.json',dict(command=['claude','-p','--no-session-persistence','--tools='],response=text),exclusive=True)
    r.write(path,value,exclusive=True)
if __name__=='__main__':main()
