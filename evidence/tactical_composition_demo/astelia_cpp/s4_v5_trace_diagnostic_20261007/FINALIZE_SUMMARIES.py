"""Remove an unmeasured reserved field; all measured values remain unchanged."""
import gzip,json
from COMMON import HERE,RAW,write,sha

def main():
    snapshot=RAW/'PRE_FIX_COMPACT_SUMMARIES.jsonl.gz'
    if snapshot.exists():raise RuntimeError('Preserve existing correction snapshot; do not repeat')
    count=0
    with gzip.open(snapshot,'wt',compresslevel=1) as f:
        for p in sorted(HERE.glob('p*_SUMMARY.json')):
            text=p.read_text();f.write(json.dumps(dict(file=p.name,original_sha256=sha(p),original=json.loads(text)))+'\n')
            obj=json.loads(text)
            for u in obj['units']:
                assert u.pop('nearest_gun_mode_switches')==0;count+=1
            write(p,obj)
    assert count==3000
    write(HERE/'SUMMARY_CORRECTION.json',dict(unused_placeholder_removed='nearest_gun_mode_switches',
        units=count,measured_values_changed=False,snapshot_file=str(snapshot.relative_to(HERE)),snapshot_sha256=sha(snapshot),
        main_analysis_source_unchanged=True,reproduction='Run ANALYZE.py then FINALIZE_SUMMARIES.py in a fresh reconstruction directory, never rerun RUN_ONCE.py'))

if __name__=='__main__':main()
