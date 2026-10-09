"""Have authenticated Claude author the owner-approved live training cap."""
import runtime as r
import json,subprocess

def main():
    path=r.LOCAL/'TRAIN_CAP.json'
    if path.exists():
        from training_control import training_cap
        cap=training_cap(r.HERE)
        if cap.get('written_by')!='Claude' or cap['cap_seconds']>12600:raise RuntimeError('invalid Stage B Claude cap')
        return # Never overwrite a live owner reduction.
    prompt='Owner explicitly approved Stage B on 2026-10-09 about 06:45 EEST, "ok lets do it, as you suggest": diagnose, fire calibration, 10 epochs with 4 windows/fight and concurrent 4 arms. Owner approved maximum 3 h per training invocation and asks Claude to write TRAIN_CAP. Return only JSON: cap_seconds 10800, approved_by owner, date 2026-10-09, written_by Claude, scope Stage B concurrent training invocation, approval_reference with the quotation above. No tools.'
    out=subprocess.run(['claude','-p','--no-session-persistence','--tools=','--',prompt],capture_output=True,text=True,timeout=60)
    if out.returncode:raise RuntimeError('Claude cap authorship failed: '+out.stdout[:300]+out.stderr[:300])
    text=out.stdout.strip()
    if text.startswith('```'):text=text.split('\n',1)[1].rsplit('```',1)[0]
    value=json.loads(text)
    if value.get('written_by')!='Claude' or value.get('approved_by')!='owner' or value.get('cap_seconds')!=10800 or value.get('date')!='2026-10-09':raise RuntimeError('Claude cap content rejected')
    r.write(r.LOCAL/'CLAUDE_CAP_AUTHORSHIP.json',dict(command=['claude','-p','--no-session-persistence','--tools='],response=text),exclusive=True)
    r.write(path,value,exclusive=True)
if __name__=='__main__':main()
