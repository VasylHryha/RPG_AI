"""Write LEGACY_EQUIVALENCE.json: the current tactics.py against each recorded version (see legacy.py). Cheap (about a minute); touches no recorded run.

    .venv/bin/python evidence/tactical_composition_demo/tcd_common/verify_legacy.py
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tcd_common import PARENT, fileio, legacy  # noqa: E402


def main():
    import tactics as current
    current_hash = legacy.identity((PARENT/'tactics.py').read_bytes())
    out = {'current_tactics_sha256': current_hash, 'note': 'bit-exact comparison of every primitive the recorded harnesses call, on fixed streams, 2 seeds', 'revisions': {}}
    for name, (rev, short) in legacy.RECORDED.items():
        started = time.time()
        source = legacy.source_at(rev)
        entry = {'commit': rev, 'recorded_hash_prefix': short, 'recovered_hash_matches_run_started': legacy.identity(source).startswith(short)}
        entry.update(legacy.compare(current, legacy.load(source, 'tactics_'+name)))
        entry['seconds'] = round(time.time()-started, 1)
        out['revisions'][name] = entry
        print(name, entry)
    fileio.write_json(Path(__file__).resolve().parent/'LEGACY_EQUIVALENCE.json', out)
    return 0 if all(e['equal'] and e['recovered_hash_matches_run_started'] for e in out['revisions'].values()) else 1


if __name__ == '__main__':
    sys.exit(main())
