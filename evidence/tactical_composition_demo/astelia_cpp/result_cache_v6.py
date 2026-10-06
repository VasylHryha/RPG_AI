"""Versioned cache admission preserving every complex diagnostic field."""
import gzip,json,pathlib,tempfile,zlib
from result_cache import Cache as HistoricalCache,identity as historical_identity,encoded,digest,sha,ROOT
from result_schema_v6 import validate_rows

def identity(kind,command):
    value=historical_identity(kind,command)
    value['v6_cache_contract']='complex-summary-v1'
    for name in ('result_cache_v6.py','result_schema_v6.py'):
        value['files'][str(ROOT/name)]=sha(ROOT/name)
    return value

class Cache(HistoricalCache):
    def load(self,request):
        path=self.path(request)
        if not path.exists():return None
        try:
            record=json.loads(gzip.decompress(path.read_bytes()));rows=record['rows']
            if record['identity']!=self.identity or encoded(record['request'])!=encoded(request) or record['rows_sha256']!=digest(rows):raise ValueError('v6 cache identity/request/result mismatch')
            validate_rows(request,rows);return rows
        except (ValueError,KeyError,TypeError,OSError,EOFError,zlib.error,OverflowError):
            self.rejected+=1;return None
    def put(self,request,rows,provenance='fresh v6 host execution'):
        validate_rows(request,rows)
        record=dict(identity=self.identity,request=request,rows=rows,rows_sha256=digest(rows),provenance=provenance)
        payload=gzip.compress(encoded(record),mtime=0)
        with tempfile.NamedTemporaryFile(dir=self.root,delete=False) as stream:
            stream.write(payload);temporary=pathlib.Path(stream.name)
        temporary.replace(self.path(request))
