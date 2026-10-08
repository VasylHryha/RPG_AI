"""Instrument the copied JSON allocator with a recorded frame; no combat."""
import gzip
import json
import subprocess
from common import CPP, HERE, LOCAL, sha, write

def probe():
    failed = LOCAL/'raw/train_0000_9d48acc6753c473a.jsonl.stdout'
    frame = None
    count = stage_bytes = raw_bytes = zipped = truncated_bytes = 0
    row_counts = {};dynamic_keys=[]
    compressor = __import__('zlib').compressobj(1, __import__('zlib').DEFLATED, 31)
    with failed.open('rb') as stream:
        for line in stream:
            raw_bytes += len(line);zipped += len(compressor.compress(line))
            try:row = json.loads(line)
            except json.JSONDecodeError:
                if line.endswith(b'\n'):raise
                truncated_bytes += len(line)
                continue
            key = 'stageA' if row.get('stageA') else 'observerV1' if row.get('observerV1') else 'other'
            row_counts[key] = row_counts.get(key, 0)+1
            if row.get('stageA'):
                count += 1;stage_bytes += len(line);dynamic_keys.append(list(row['pairModes']))
                if frame is None:frame = line
    zipped += len(compressor.flush())
    if frame is None:raise RuntimeError('failed evidence has no Stage A rows')
    out = LOCAL/'memory_probe';out.mkdir(parents=True, exist_ok=True)
    binary = out/'json_alloc_probe'
    subprocess.run(['clang++', '-std=c++17', '-O2', '-I'+str(CPP/'src'), '-I'+str(HERE), str(HERE/'memory_probe.cpp'), '-o', str(binary)], check=True)
    runs = [json.loads(subprocess.run([str(binary), mode], input=frame, capture_output=True, check=True).stdout) for mode in ('no-gc', 'gc')]
    key_stream = b''.join((json.dumps(keys)+'\n').encode() for keys in dynamic_keys)
    dynamic_runs=[json.loads(subprocess.run([str(binary), mode], input=key_stream, capture_output=True, check=True).stdout) for mode in ('dynamic-cached', 'dynamic-flat')]
    result = dict(dynamic_layout_probes=dynamic_runs, max_pair_keys=max(map(len,dynamic_keys)), unique_pair_layouts=len({tuple(keys) for keys in dynamic_keys}),scope='copied value allocator; reparse/serialize a real failed-attempt frame; no combat',
                  failed_sha256=sha(failed), failed_bytes=raw_bytes, truncated_final_row_bytes=truncated_bytes, row_counts=row_counts, stage_frames=count, stage_bytes=stage_bytes,
                  average_stage_frame_bytes=stage_bytes/count, failed_gzip_level1_bytes=zipped,
                  projected_150s_raw_bytes=raw_bytes*4500/count,
                  projected_180_fights_raw_bytes=1.2*180*raw_bytes*4500/count,
                  projected_180_fights_gzip_bytes=1.2*180*zipped*4500/count,
                  projection_basis='partial failed trace extrapolated to 4500 ticks; 20 percent collection margin; fixture/sample must replace',
                  probes=runs)
    write(HERE/'MEMORY_PROBE_STAGEA.json', result)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':probe()
