"""Shared, corrected tooling for the exploratory tactical-composition line (NOT a milestone, NOT C6 evidence).

New experiments import only this package. The recorded harnesses (demo.py, change.py, change2.py) and the recorded versions of tactics.py stay
byte-frozen: their RUN_STARTED.json hashes pin them. What was repaired here, and why, is listed in tcd_common/CHANGES.md.
"""
import sys
from pathlib import Path

PARENT = Path(__file__).resolve().parent.parent
if str(PARENT) not in sys.path:
    sys.path.insert(0, str(PARENT))
