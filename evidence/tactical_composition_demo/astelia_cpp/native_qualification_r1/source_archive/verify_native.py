"""Exhaustive native engineering coverage; JS is explicitly stored reference data.

Visit every request even when summaries differ. Fresh native execution, complete
traces, physical invariants and repeat execution qualify the implementation;
whole-fight numerical identity remains a diagnostic under the approved rewrite.
"""
import argparse,collections,gzip,json,pathlib,time
from result_cache import Engine,Cache,DEFAULT_CACHE,prime_legacy,sha,encoded,digest,identity
from result_schema import validate_rows,finite
from compare import difference
ROOT=pathlib.Path(__file__).resolve().parent

def trace_invariants(request,rows):
    validate_rows(request,rows)
    if 'error' in rows[-1]:raise ValueError(rows[-1]['error'])
    options=request.get('options',{});width=options.get('width',1400);height=options.get('height',800);previous={}
    for frame in rows[:-1]:
        units=frame['state']['units'];ids={u['id'] for u in units}
        for u in units:
            if u['target'] is not None and u['target'] not in ids:raise ValueError('trace target is not world-local')
            if u['alive'] and u['hp']<=0:raise ValueError('living unit has no health')
            old=previous.get(u['id'])
            if old and (u['hp']>old['hp']+1e-8 or (u['alive'] and not old['alive'])):raise ValueError('health increased or identity resurrected')
            debug=u.get('debug',{})
            if debug and (not all(finite(debug[k]) for k in ('prep','ep','epMax','r','maxhp')) or debug['prep']<0 or debug['ep']<0 or debug['ep']>debug['epMax']+1e-8):raise ValueError('invalid casting/energy state')
            if frame['step'] and u['alive'] and not (-1e-8<=u['x']<=width+1e-8 and -1e-8<=u['y']<=height+1e-8):raise ValueError('unit outside arena')
            previous[u['id']]=u
    return len(rows)-1

def semantic(rows):
    return [dict(step=r['step'],state=dict(t=r['state']['t'],units=[{k:v for k,v in u.items() if k not in ('bits','debug')} for u in r['state']['units']])) for r in rows[:-1]]+[rows[-1]]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=pathlib.Path,required=True);args=ap.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    if (args.output/'coverage.json').exists():ap.error('use fresh evidence directory')
    contract=json.loads((ROOT/'native_contract.json').read_text());requests=[json.loads(s) for s in (ROOT/'check_fights.jsonl').read_text().splitlines()];traces=set(contract['coverage']['trace_ids'])
    if len(requests)!=623 or sha(ROOT/'check_fights.jsonl')!=contract['coverage']['requests_sha256']:raise RuntimeError('coverage input drift')
    native=Engine('cpp',[str(ROOT/'build/astelia_native')],cache_dir=None,request_timeout=300)
    native_cache=Cache(DEFAULT_CACHE,native.identity)
    js=Engine('js',['node',str(ROOT/'js_host.cjs')]);imported=prime_legacy(js)
    started=time.perf_counter();counts=collections.Counter();receipt=dict(status='RUNNING',native_identity=native.identity,reference_identity=js.identity,
        inputs_sha256=sha(ROOT/'check_fights.jsonl'),harness_sha256=sha(pathlib.Path(__file__)),reference_policy='stored canonical frozen JS only; no fresh JS combat in coverage',imported_reference_entries=imported,counts={},traces=[],determinism=[])
    def save():
        receipt.update(counts=dict(counts),native=native.counts(),reference=js.counts(),elapsed_seconds=time.perf_counter()-started)
        (args.output/'coverage.json').write_text(json.dumps(receipt,indent=2)+'\n')
    save()
    try:
        with (args.output/'outcomes.jsonl').open('w') as journal:
            for i,request in enumerate(requests):
                trace=i in traces;req=dict(request,trace=True,debug=True) if trace else request
                reference_req=dict(request,trace=True) if trace else request
                reference=js.cache.load(reference_req)
                if reference is None:raise RuntimeError('missing admitted stored reference '+str(i))
                try:
                    rows=native.fight(req);validate_rows(req,rows)
                    native.check_input_stats();native_cache.put(request,[rows[-1]],'terminal summary of fresh exhaustive native coverage');native_cache.put(req,rows,'fresh exhaustive native coverage')
                    if 'error' in rows[-1]:classification='NATIVE_ERROR'
                    elif 'error' in reference[-1]:classification='KNOWN_SOURCE_ERROR_REPAIRED' if reference[-1]['error']=="Cannot read properties of null (reading 'length')" else 'SOURCE_ERROR_REQUIRES_REVIEW'
                    else:classification='IDENTICAL_SUMMARY' if difference(reference[-1],rows[-1]) is None else 'COMPLETED_DIVERGENT_SUMMARY'
                    if trace and 'error' not in rows[-1]:
                        frames=trace_invariants(req,rows);payload=b'\n'.join(encoded(r) for r in rows)+b'\n';name=f'trace_{i:04d}.jsonl.gz';(args.output/name).write_bytes(gzip.compress(payload,mtime=0))
                        receipt['traces'].append(dict(check_id=i,frames=frames,file=name,sha256=sha(args.output/name),first_semantic_difference=difference(semantic(reference),semantic(rows))))
                    if i in traces or i in (0,100,200,300,400,500,600,622):
                        repeat=native.fight(req);equal=encoded(rows)==encoded(repeat);receipt['determinism'].append(dict(check_id=i,equal=equal))
                        if not equal:classification='NONDETERMINISTIC'
                    counts[classification]+=1;journal.write(json.dumps(dict(check_id=i,classification=classification,request=request,reference=reference[-1],native=rows[-1],first_summary_difference=difference(reference[-1],rows[-1])),separators=(',',':'))+'\n')
                except Exception as error:
                    counts['CHECK_FAILURE']+=1;journal.write(json.dumps(dict(check_id=i,classification='CHECK_FAILURE',error=str(error)))+'\n')
                journal.flush();save()
                if (i+1)%25==0:print(f'{i+1}/623 {dict(counts)}',flush=True)
        receipt['status']='NATIVE_COVERAGE_PASSED' if not any(counts[k] for k in ('NATIVE_ERROR','SOURCE_ERROR_REQUIRES_REVIEW','NONDETERMINISTIC','CHECK_FAILURE')) and len(receipt['traces'])==20 else 'CHANGES_REQUIRED'
        # Quick subsequent comparisons can use current native results, bound to
        # this build. A hit must execute zero new fights, then a seed change misses.
        cached=Engine('cpp',native.command,cache_dir=ROOT/'build'/('cache_probe_'+args.output.name));sample=requests[0];first=cached.fight(sample);before=cached.counts();second=cached.fight(sample);after=cached.counts()
        changed=json.loads(json.dumps(sample));changed['options']['seed']+=104729;cached.fight(changed)
        receipt['cache_probe']=dict(first_equals_second=first==second,before=before,after=after,after_seed_change=cached.counts());cached.close()
        if before['executed']!=1 or before['executed']!=after['executed'] or after['cached']!=before['cached']+1:raise RuntimeError('cache replay ran combat')
        if identity('cpp',native.command)!=native.identity:raise RuntimeError('engine changed during coverage')
        save();print(json.dumps(dict(status=receipt['status'],counts=receipt['counts'],elapsed_seconds=receipt['elapsed_seconds']),indent=2));return 0 if receipt['status']=='NATIVE_COVERAGE_PASSED' else 1
    finally:native.close();js.close()
if __name__=='__main__':raise SystemExit(main())
