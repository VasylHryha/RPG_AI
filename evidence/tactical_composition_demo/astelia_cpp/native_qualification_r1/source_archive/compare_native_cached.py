"""Quick all-request comparison; zero combat execution and strict cache identity."""
import collections,json
from result_cache import Engine,ROOT,prime_legacy
from compare import difference
def main():
    js=Engine('js',['node',str(ROOT/'js_host.cjs')]);native=Engine('cpp',[str(ROOT/'build/astelia_native')]);prime_legacy(js);counts=collections.Counter()
    for i,line in enumerate((ROOT/'check_fights.jsonl').read_text().splitlines()):
        req=json.loads(line);a=js.cache.load(req);b=native.cache.load(req)
        if a is None or b is None:raise RuntimeError('missing/stale result for request '+str(i)+'; run verify_native.py on this build')
        native.check_input_stats();js.check_input_stats();counts['identical_summary' if difference(a[-1],b[-1]) is None else 'divergent_summary']+=1
    js.close();native.close();print(json.dumps(dict(requests=623,counts=dict(counts),executed_fights=0,cache_policy='identity-bound stored JS and native summaries')));return 0
if __name__=='__main__':raise SystemExit(main())
