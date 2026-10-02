# C6 R3 implementation checks

The complete everyday test suite passed: 418 tests in 108.58 seconds.
Earlier pre-publication correction run: 416 tests passed in 124.99 seconds.
`CHECKS.json` binds the final tested implementation, fixed protocol and proposal.

These checks qualify implementation behavior, not a scientific hypothesis or
independent acceptance. Nineteen semantic mutants are defined but their probe
runs only through the registered pipeline after development qualification.

The native adapter is built by `.venv/bin/python tools/build_c6_r3.py`; tests
build it themselves and compare against a separate NumPy reference.
The authorized development command is
`.venv/bin/python tools/c6_r3_design_gate.py --output evidence/c6_r3_design_gate --workers 8`.
Arm A is NOT_RUN with its preserved R2 STOP.
