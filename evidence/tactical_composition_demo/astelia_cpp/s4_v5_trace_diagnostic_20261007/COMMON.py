"""New observer tools only: no policy changes, tuning or judging imports."""
import hashlib, json, pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
CPP = HERE.parent
REPO = CPP.parents[2]
sys.path.insert(0, str(CPP))
PAIRS = [('resonator', 'regular'), ('morale', 'regular'), ('resonator', 'novice')]
IMPL = '240aea2a2b57d53fc4403338c6f6ce5f5fe80889'
OLD = CPP/'s4_v5_development_20261006_2308'
RAW = HERE/'raw'

def sha(p):
    h = hashlib.sha256()
    with pathlib.Path(p).open('rb') as f:
        for b in iter(lambda: f.read(1024*1024), b''): h.update(b)
    return h.hexdigest()

def write(p, obj):
    pathlib.Path(p).write_text(json.dumps(obj, indent=2, allow_nan=False)+'\n')

def pins():
    from build_admission import admit
    from s4_development import verify_sources
    old = json.loads((OLD/'run_identity.json').read_text())
    assert old['implementation_commit'] == IMPL
    for name, expected in old['code_hashes'].items():
        assert sha(CPP/name) == expected, ('identity drift', name)
    native = admit(CPP/'build/astelia_native')
    assert native == old['build']
    return dict(implementation_commit=IMPL, binary=native, runtime_hashes=old['code_hashes'],
                rrg_source=verify_sources(), selected_knobs_sha256=sha(OLD/'B_best.json'))

def rows(files):
    import gzip
    for file in files:
        with gzip.open(HERE/file, 'rt') as f:
            for line in f: yield json.loads(line)
