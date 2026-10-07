"""PILOT baseline (no verdict, no patch): the unchanged 7.11 law through pilot_common, to validate
the pilot assay against the recorded fixture (F5(ii): A 1.451, B 1.303, max E 0.8; F5(i): A 0.190,
B 0.209, E 0). Usage: PILOT_ASSAY=1 python -m ...pilot_baseline <i|ii>"""
import sys
from . import pilot_common as P
if __name__ == '__main__':
    P.run(sys.argv[1], 'baseline_assay', keyset=int(sys.argv[2]) if len(sys.argv) > 2 else 0)
