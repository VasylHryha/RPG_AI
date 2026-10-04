# Initial diagnostic, not final qualification

These are the unchanged outputs from the first six-request diagnostic batch.
It stopped on an elite trace mismatch. The frozen fight inputs for the reached
requests are unchanged in the final check set. The source/binary identities in
`checks.json` describe that earlier build, not the final C++ code.

The mismatch was traced to a last-bit difference in V8 `sin(9π/8)` when the
vendored math was built with contraction disabled. That build setting was
corrected before `checks_r1` and `checks_r2`. Both differing trace bodies are
retained here. `../checks_r2/checks.json` is the final receipt.
