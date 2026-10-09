"""Zero-combat O label replay. Persistent O memory follows each public prefix."""
import runtime as r
import contextlib,json,subprocess,time,select

@contextlib.contextmanager
def oracle(request,timeout=600):
    child=subprocess.Popen([str(r.BINARY)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1)
    started=time.monotonic();first=True
    def label(row):
        nonlocal first
        rpc=dict(operation='stagebOracleReplay',frame={k:v for k,v in row.items() if k not in ('labels','studentLabels','shadowLabels','networkState')})
        if first:rpc['request']=request;first=False
        child.stdin.write(json.dumps(rpc,allow_nan=False,separators=(',',':'))+'\n');child.stdin.flush()
        remaining=timeout-(time.monotonic()-started)
        if remaining<=0 or not select.select([child.stdout],[],[],remaining)[0]:raise TimeoutError('offline oracle replay timeout')
        line=child.stdout.readline()
        if not line:raise RuntimeError('oracle replay exited: '+child.stderr.read()[:1000])
        result=json.loads(line)
        if 'error' in result or result.get('combat_steps')!=0:raise RuntimeError('oracle replay: '+str(result)[:1000])
        return result['shadowLabels']
    try:yield label
    finally:
        child.stdin.close()
        try:child.wait(timeout=5)
        except subprocess.TimeoutExpired:child.kill();child.wait()
        child.stdout.close();child.stderr.close()
