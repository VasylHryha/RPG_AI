"""Lossless optional audit spooling. Existing files are never overwritten.

Reports hold content-addressed file receipts; reading a receipt expands exactly
the same ordered records as the in-memory path. Flush at every native boundary
and before receipts/reads. A crash may leave the last buffered boundary partial.
"""
import hashlib
import json
from pathlib import Path


class TraceStore:
    def __init__(self, path, initial=()):
        self.path = Path(path).resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.file = self.path.open('x', buffering=256*1024)
        self.count = 0
        for item in initial:
            self.append(item)

    def append(self, item):
        self.file.write(json.dumps(item, separators=(',', ':'), allow_nan=False)+'\n')
        self.count += 1

    def __len__(self):
        return self.count

    def __iter__(self):
        self.flush()
        with self.path.open() as stream:
            for line in stream:
                yield json.loads(line)

    def flush(self):
        if not self.file.closed:
            self.file.flush()

    def receipt(self):
        self.flush()
        digest = hashlib.sha256()
        with self.path.open('rb') as stream:
            for block in iter(lambda: stream.read(1024*1024), b''):
                digest.update(block)
        return {'format':'ordered-jsonl-v1','path':str(self.path),
                'records':self.count,'bytes':self.path.stat().st_size,'sha256':digest.hexdigest()}

    def close(self):
        self.file.close()
