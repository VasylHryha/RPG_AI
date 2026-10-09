"""Compatibility command: B2 authority now lives in OWNER_APPROVALS.json."""
from training_control import training_cap
from common import HERE
if __name__=='__main__':
    import json
    print(json.dumps(training_cap(HERE)))
