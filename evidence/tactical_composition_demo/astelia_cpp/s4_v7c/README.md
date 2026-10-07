# v7c: validation only at committed v7b theta

This delivery preserves DESIGN_0G §§20.1/20.2. No tuning runs or optimizer entropy are allocated. Theta is read from v7b's committed `TUNING.json` and `TUNING_ANALYSIS.json` at `796d0a8c43e5f81533b0b363d856d6a44e33413e`, selected ordinal **161**. `THETA_ORIGIN.json` pins both receipts and their original declaration by SHA256; each use checks the local bytes against that exact commit. Historical P16 uses the unchanged historical theta from that declaration. All native controller source hashes, the combat binary hash `9e8781b7e1004f62d9f4d4964fa855608b3070a9dd07fa4037bfbbd69e9fc2dd`, build manifest and observation fixture are identical to v7b. The binary is copied, never rebuilt.

The preceding v7b validation attempt stopped before any fight or step executed. `raw/validation_v7_regular_c03_o0.jsonl.gz` contains `attributionDiagnostics requires trace and decisionDiagnostics`; its native metrics report 0 executed fights and 0 executed steps. `raw/validation_v7_regular_c02_o1_FAILURE.json` records the consequent interrupted deadline/execution stop. All preceding claims/raw/receipts remain untouched; none are resumed or replayed.

**Exactly one request fix:** enable `trace` whenever validation diagnostics are requested. `decisionDiagnostics` and `attributionDiagnostics` stay enabled. The native host requires trace for both, so merely dropping attribution would still reject the request. This preserves the diagnostic output contract. No other request setting changes. Original JSON templates and `protocol.py` are byte-identical to v7b.

Before sealing, request-builder tests reproduce both linked native rejections and prove trace is the sole changed field. The combat binary has no successful parse-only interface; it is never fed a template during delivery. A separate native checker uses the unchanged codec/registry to parse all 400 actual requests without creating a world or executing a step/fight. `REQUEST_AUDIT.json` records this distinction and binds the complete request grid. See `REQUEST_FIELD_AUDIT.md` for every argument and the zero-world checker scope. The full scoped test suite uses the copied observation fixture and fake records only; repository suites that execute combat are excluded.

`VALIDATION_SEED_LEDGER.json` has **20 fresh unused validation clusters**. Prior development inventories, including v7 and v7b's tuning/validation ledgers, are consulted only to exclude their entropy; none supply validation seeds. No judging ledger is opened. The grid is 20 clusters × 2 orientations × {v7, forcedP16, forcedv6, omega0 at theta; historicalP16 at historical theta} × {regular, novice} = **400 fights**.

Scientific readings remain unchanged: strict enemy elimination before 150 s with own survivors; raw native terminal overshoot at most one tick is retained as a timeout. The regular matched-comparator floor is 21/40; improvement/loss is a difference of at least four wins, match within ±3. v7's own criterion is evaluated independently: ≥21/40 both heads, positive mean S both heads, no failures. Positive/negative/tied clusters, orientation discordance and the 10,000-resample paired-cluster percentile interval use bootstrap seed **20261007** and linear interpolation. Omega0 is the total inherited policy intervention, with duplication disclosed if selected omega is zero. Development observations do not authorize S5 or scientific/inferential claims.

Claude executes only these commands from the repository root, without edits:

```sh
.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_v7c/run.py validate
.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_v7c/analyze.py validate
.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_v7c/render.py validate
```

The mandatory repository-anchored `pgrep -fl` process gate, per-attempt gate receipt, caffeinate wrapper, ten-worker limit, exclusive claims, immutable completions, hash checks and fail-closed resume are inherited. Missing process-list permission, incomplete claims or unclosed attempts stop without replay. Request/cell identity is checked against the sealed grid on resume. Native/controller/numerical/planner failures preserve raw output and stop without scoring or dropping rows.

The **3600-second cap belongs to v7c validation alone**, including its stored analysis/render attempts. v7b tuning and v7c preflight/seal costs are not charged to it. The conservative pre-fight projection remains remaining fights × 0.062 s + prior validation time + 120 s analysis reserve (144.8 s at an unused ledger). The corrected v7b runtime projection remains prior time + elapsed attempt wall time + remaining fights / aggregate completed-fights-per-wall-second + 120 s, with no extra worker multiplier. Its warm-up is min(10, ceil(5% of remaining stage batches at attempt start)); all worker completions count, including those ahead of the queue consumer, and cached completions do not count. The absolute deadline remains active during warm-up. Gate waiting is excluded.

`prepare.py` allocates entropy exactly once. `native_build.py` copies artifacts and builds only the separate checker. `engineering.py` runs the final scoped suite; `seal.py` verifies current audited RRG source inputs, owner recheck, zero-combat request proof, entropy and preservation before writing the declaration. No source changes or ledger replacement are permitted after sealing; changes require a new version and fresh ledger.

The owner's verbatim recheck and disposition are kept in `OWNER_RECHECK.md` here because the owner explicitly forbids editing `docs/PLAN_CURRENT.md`. No PLAN_CURRENT/DESIGN file is edited, staged or pinned. `PRESERVATION.json`/`verify_delivery.py` check protected documents, plan staging and both preceding version trees (bytes and mtimes). Normal hooks and explicit pathspecs govern delivery. If main `.git` is read-only, `deliver.py` creates a normal-hook commit and verified current-HEAD `S4_V7C.bundle` in this directory. No push. Ignored native build products remain local; the unchanged binary/fixture can be copied again from preserved v7b, without rebuilding combat code.

| Stop condition (yes/no) | Action | Responsible role |
|---|---|---|
| Does any identity, request audit, preservation or fresh entropy check fail? | Stop and fix before sealing/fights | implementer |
| Is the process gate unavailable or repository work active? | Stop or wait for a clear recorded gate | Claude executor |
| Is a raw claim incomplete or an attempt unclosed? | Stop without replay | Claude executor |
| Does projected/cumulative validation compute exceed 3600 s? | Stop and retain receipts | Claude executor |
| Does native/controller/numerical/planner execution fail? | Stop without scoring the failed row | Claude executor |
| Does matched forcedP16 regular fall below 21/40? | Report the panel does not support a comparison | drafter |
| Is a rule/source/ledger changed after any validation fight? | Mark invalid and prepare a fresh version | implementer |

Final noncombat verification: 57 tests passed in 9.90 s; measured suite process time 10.128812125 s. The actual native parser accepted all 400 future requests with 0 worlds created, 0 executed fights and 0 executed steps. Codex has not invoked run/analyze/render validation commands. Engineering and request proof are bound by hash before seal.
