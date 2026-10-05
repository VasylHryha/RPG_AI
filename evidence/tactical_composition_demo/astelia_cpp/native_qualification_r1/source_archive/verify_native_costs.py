"""Fixed operation costs and production layout admission; no combat cache."""
import argparse,json,pathlib,subprocess,math,os,platform
from result_cache import identity,sha
ROOT=pathlib.Path(__file__).resolve().parent
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=pathlib.Path,required=True);args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    if (args.output/'matched_costs.json').exists():ap.error('use fresh output')
    commands={'js':['node',str(ROOT/'matched_probe.cjs')],'cpp':[str(ROOT/'build/native_matched_probe')]}
    ids={k:identity('js' if k=='js' else 'cpp',v) for k,v in commands.items()};record=dict(status='RUNNING',identities=ids,harness_sha256=sha(pathlib.Path(__file__)),load_before=os.getloadavg(),machine=platform.platform(),samples={'js':[],'cpp':[]})
    for label in ('js','cpp','cpp','js'):
        print('matched costs: '+label,flush=True);run=subprocess.run(commands[label],capture_output=True,text=True,check=True);i=len(record['samples'][label]);(args.output/f'{label}_{i}.jsonl').write_text(run.stdout);(args.output/f'{label}_{i}.stderr.txt').write_text(run.stderr);rows=[json.loads(s) for s in run.stdout.splitlines()];record['samples'][label].append(rows)
        if identity('js' if label=='js' else 'cpp',commands[label])!=ids[label]:raise RuntimeError('probe identity changed')
    def find(rows,kind):return [r for r in rows if r['kind']==kind]
    costs={}
    for kind,cpp_kind in (('geometry','geometry_production'),('network','network'),('fork_playout','fork_playout')):
        js=[r for sample in record['samples']['js'] for r in find(sample,kind)];cpp=[r for sample in record['samples']['cpp'] for r in find(sample,cpp_kind)]
        if not js or not cpp or len({r['operations'] for r in js+cpp})!=1 or any(not math.isfinite(r['checksum']) or not math.isfinite(r['seconds']) or r['seconds']<=0 for r in js+cpp):raise RuntimeError('invalid matched operation proof')
        if any(not math.isclose(r['checksum'],js[0]['checksum'],rel_tol=1e-12,abs_tol=1e-9) for r in js+cpp):raise RuntimeError('matched checksum mismatch: '+kind)
        costs[kind]=dict(operations=js[0]['operations'],speed_up=sum(r['seconds'] for r in js)/len(js)/(sum(r['seconds'] for r in cpp)/len(cpp)),js_checksum=js[0]['checksum'],native_checksum=cpp[0]['checksum'])
    works=[find(s,'fork_work')[0] for label in ('js','cpp') for s in record['samples'][label]]
    if any(w!=works[0] for w in works):raise RuntimeError('fork/playout work differs between engines')
    if works[0]['steps']!=3000 or works[0]['unit_actions']!=300000 or works[0]['projectile_steps']!=9000:raise RuntimeError('matched probe skipped fixed branch work')
    layout={}
    for kind in ('geometry','complete_clone'):
        rows=[r for sample in record['samples']['cpp'] for r in sample if r['kind'].startswith(kind+'_')]
        if len({r['operations'] for r in rows})!=1 or len({r['checksum'] for r in rows})!=1:raise RuntimeError('layout operation/copy equivalence failed')
        labels=('records','columns','production') if kind=='geometry' else ('records','columns')
        sums={label:sum(r['seconds'] for r in rows if r['kind']==kind+'_'+label) for label in labels}
        layout[kind]=dict(operations=rows[0]['operations'],checksum=rows[0]['checksum'],seconds=sums,production_over_columns=sums.get('production',sums['records'])/sums['columns'])
    if any(not find(s,'clone_equivalence')[0]['passed'] for s in record['samples']['cpp']):raise RuntimeError('complete clone failed')
    # The record implementation is selected when neither workload shows a
    # material (>20%) column advantage. Otherwise architecture must be revisited.
    record.update(costs=costs,fork_work=works[0],layout=layout,layout_selection='typed contiguous hot authority records and indexed spatial buckets',layout_policy='revisit if pure columns are over 20 percent faster than the selected production query or complete-authority copy',load_after=os.getloadavg())
    record['status']='MATCHED_COSTS_PASSED' if all(v['speed_up']>1 for v in costs.values()) and all(v['production_over_columns']<=1.2 for v in layout.values()) else 'CHANGES_REQUIRED'
    (args.output/'matched_costs.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(dict(status=record['status'],costs=costs,layout=layout),indent=2));return 0 if record['status']=='MATCHED_COSTS_PASSED' else 1
if __name__=='__main__':raise SystemExit(main())
