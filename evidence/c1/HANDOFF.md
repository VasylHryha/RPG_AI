# C1 independent review handoff

Implementation is **REVIEW_READY**, checks **PASS**, independent acceptance **pending**. Prerequisite C0 R003 is independently ACCEPTED in [its receipt](../c0_review/ACCEPTANCE.md). All 12 accepted C0 inputs remain unchanged.

Scope is R4 C1: four separate additive updates from a saved state, stable node ID queue rounds, the same weighted displacement residual law, a 100,000 dynamic edge-visit cap and atomic rollback. The queue uses asynchronous node steps; C0 uses simultaneous steps. This execution distinction is explicitly registered. Candidate code imports neither the sparse reference nor evaluator truth. Full public input preparation and global proof scans are disclosed. Exact initialization is compiled from public constraints and charged separately; it is not claimed as candidate learning.

The complete source is under `source/`; immutable protocol is [c1_manifest.json](source/experiments/c1_manifest.json). Actual report is [contracts.xml](contracts.xml). Results and streamed records are [results.json](results.json) and [instances.jsonl](instances.jsonl). Each case preserves the initial C0 artifact, mutable C1 fork before the transaction, and committed or rejected artifact after the transaction in `states/`. A rejected transaction must preserve the fork bytes; its schema differs from the imported C0 artifact.

Actual commands:

```text
.venv/bin/python -m pytest -q tests/test_c1.py --junitxml=evidence/c1/contracts.xml
.venv/bin/python -m geomind.run_c1 --output evidence/c1 --contract-report evidence/c1/contracts.xml
```

Seven focused checks PASS in 3.64 seconds. The 16-case experiment took 24.76 seconds. Five updates commit: consistent edges at all sizes and an inconsistent edge at 32 nodes. Eleven updates exhaust the cap and remain unresolved: all new nodes and bridges, and inconsistent edges at 128/512/2048 nodes. Every fresh sparse least-squares reference converges. All four engineering gates PASS; maximum committed displacement error is `5.35415e-8`, maximum independently measured energy gap `3.24740e-15`. No update exceeds 100,000 dynamic visits, no fallback occurs, and all disconnected retention, query immutability and reload checks pass.

Post-run integrity inspection checked source and archive hashes, registered manifest identity, exact equality of 16 streamed records to receipt records, unique case identities, actual JUnit hash, all persisted fork/after hashes, every rollback's byte identity, charged visit arithmetic and accuracy of committed answers. This read-only inspection did not regenerate worlds or re-solve them.

Review focus: additive validation and duplicate-edge accounting; merged-component gauge handling; stable queue scheduling; incident-edge and global-certificate budget; rejection visibility to callers; independent reference qualification; wrong/missing answer negative controls; persistence and frozen-parent isolation. Selected numeric array bytes are diagnostic, not peak memory. Setup and full certificates are global work. Wall-clock measurements vary.

H-P and H-L remain INCONCLUSIVE. A correct refusal is engineering compliance, not a useful updated answer. Existing references solve all cases; the active queue's cap limits its practical usefulness. No adaptive-versus-frozen learning comparison, generalization, sublinear work, energy benefit or hierarchy claim follows. Do not tune against these seeds or rewrite historical receipts to hide unresolved updates. Material protocol changes need a new registration and evidence directory.

Next action: independent C1 review and an explicit decision on its negative practical result before the C2 learning experiment. No C2 or hierarchy work has begun. Reuse these verified receipts when possible; any replay must use a fresh output directory and its actual focused contract report.
