# Repository process-gate recheck disposition

Owner decision, 2026-10-08: "Fix the gate properly".
Separate Codex reviewer: `v3_gate_recheck` (same family, as explicitly requested).
The verbatim owner request and reviewed hashes are in OWNER_RECHECK_GATE.md.

- G1 FIXED: existing basename file arguments are resolved in the target process cwd; ordinary bare PATH interpreter names are not invented as cwd files. Regression tests cover local JSON input and foreign Python script.
- G2 FIXED: bare native PATH executables use lsof txt entries with the executable basename; dylib entries cannot confer repo ownership. Failed lookup is UNAVAILABLE. Tests cover local/foreign/scratch native paths and lookup failure.
- G3 FIXED: split only option=value arguments; preserve literal equals signs in executable and argument paths. Two regression cases added.
- G4 FIXED: README now identifies V3 as reusing the V1 binary and checks.

The final reviewer found no remaining blocking finding within the bounded scope.
All planned code and test edits preceded the focused test run. Live process discovery
is recorded separately in PROCESS_GATE.json; sandbox availability is not inferred
from mocks. No calibrate/run, drill, series or judging execution is authorized for
this implementer. SCOPE_CHECK.json records unchanged inherited functions and files.
