"""Ordered gzip chunks below 50 MB; exclusive creation preserves past evidence."""
import gzip
import hashlib
import json
from pathlib import Path


class Chunks:
    LIMIT=48_000_000  # decoded bytes; compressed gzip overhead stays below 50 MB
    def __init__(self,path,initial=()):
        self.root=Path(path);self.root.mkdir(parents=True,exist_ok=False)
        self.count=0;self.files=[];self.file=None;self.bytes=0
        for row in initial:self.append(row)

    def append(self,row):
        data=(json.dumps(row,separators=(',',':'),allow_nan=False)+'\n').encode()
        if len(data)>self.LIMIT:raise ValueError('one trace record exceeds the chunk cap')
        if self.file is None or self.bytes+len(data)>self.LIMIT:
            self.close();path=self.root/f'{len(self.files):06d}.jsonl.gz';self.files.append(path)
            self.file=gzip.open(path,'xb');self.bytes=0
        self.file.write(data);self.bytes+=len(data);self.count+=1

    def close(self):
        if self.file:self.file.close();self.file=None

    def flush(self):
        if self.file:self.file.flush()

    def __len__(self):return self.count
    def __iter__(self):
        self.close()
        for path in self.files:
            with gzip.open(path,'rt') as stream:
                for line in stream:yield json.loads(line)

    def receipt(self):
        self.close()
        return dict(format='ordered-gzip-jsonl-chunks-v1',records=self.count,
                    files=[dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in self.files])
