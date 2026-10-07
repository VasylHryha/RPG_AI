# Stored-only night recovery v2

V2 supersedes v1's accounting only. All original validation, receipts, raw data, the RUNNING attempt, the v1 interruption record and launcher remain unchanged. The supplemental manifest binds `HOST_BOOT_EVIDENCE_20261007.json` from commit `4147896`, v1 from `c8241f2`, the original seal and both historical attempts. It binds decision 0031 and records the owner's instruction to Claude to continue, followed by this explicit recovery-v2 authorization. Validation is not resealed; no fights, entropy, scientific rules or acceptance are changed.

The sysctl output contains epoch **1791399114.777526** (boot **2026-10-07T18:51:54.777526Z**). The interrupted attempt started **18:06:31Z**. V2 charges exactly **2723.777526 s**, or **2723.8 s** rounded, instead of v1's **3377.771384 s** through recovery observation. The closed validation charge is **227.16235725 s**, making historical cumulative time **2950.93988325 s**. This still leaves only **649.06011675 s** of the original 3600 s cap, insufficient for analysis that already ran over 45 minutes before reboot.

The two stored stages `analyze_validate` and `render_validate` receive one **shared cumulative 7200 s night allowance**, starting with new v2 attempts. Historical time remains charged and visible separately; it is not deducted from this new allowance or erased. Each new attempt records its budget ID, supplemental manifest hash, declaration/binary identity, historical time, prior night time, remaining allowance and local start. PASS and STOP both consume measured wall time without clipping. No combat stage can use it: launcher choices, ledger calls, attempt calls and runtime combat entry points refuse combat/unknown stages. Direct original commands retain their original 3600 s fence and refuse the preserved RUNNING attempt.

Authority is **decision 0031's rule for launches at or after 22:00 local**, plus **the owner's instruction that Claude continue the work and this explicit 7200 s stored-only allowance**. The supplemental authority binds the batch's earliest start to **2026-10-07T22:00:00+03:00**. The explicit owner grant covers analysis and rendering as one batch, including continuation after midnight; it does not renew on another date. Each attempt records its actual local start and reuses the remaining shared allowance. Earlier starts refuse; changing dates never replenishes the budget. Decision 0031 supplies the initial night authority, while continuation belongs to the owner's explicit two-stage grant.

The launcher verifies the full original seal and unchanged v1 supplemental manifest, then patches only the stored runtime's attempt/deadline handling. It disables `run.execute`, `run.Executor` and `run.validation`. The unchanged analysis reads the 400 stored validation fights and full diagnostics; rendering reads stored analysis. Both use owned monotonic deadlines, a watchdog timer and SIGALRM; no negative-ledger trick or global original-cap edit is used. An exclusive lock covers ledger allocation and execution, preventing overlapping budgets. A new interrupted attempt or stale lock fails closed and needs a new recovery record; v2 does not automatically discount subsequent interruptions. Existing analysis/render outputs are refused rather than overwritten.

Codex does not launch analysis/render in this sandbox. Claude should run from repository root, outside the restricted sandbox. The launcher invokes `caffeinate` before entering the stored runtime. Allow roughly 45–120 minutes for analysis and rendering together; the exact remaining duration is unknown, and the shared 7200 s deadline is authoritative. Do not run the second command if the first fails.

```sh
.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_v7c/analysis_recovery_v2.py analyze validate
.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_v7c/analysis_recovery_v2.py render validate
```

Read-only audits (no trace parsing or fights):

```sh
.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_v7c/analysis_recovery_v2.py ledger validate
.venv/bin/python evidence/tactical_composition_demo/astelia_cpp/s4_v7c/verify_analysis_recovery_v2.py
```

| Stop condition (yes/no) | Action | Responsible role |
|---|---|---|
| Is boot evidence missing, invalid or changed? | Refuse recovery | implementer |
| Does an original or supplemental pin differ? | Stop and investigate without editing history | implementer |
| Is any new unclosed attempt or stale lock present? | Preserve it and require a new recovery decision | implementer |
| Is combat or an unknown stage requested? | Refuse execution under the unchanged 3600 s combat cap | implementer |
| Is the shared night allowance exhausted? | Stop before a new attempt | implementer |
| Is a new attempt starting before the authorized 2026-10-07 22:00 local instant? | Refuse this night allowance | implementer |
| Does a target analysis/render output already exist? | Preserve it and refuse overwrite | implementer |

The recheck and disposition are in `RECOVERY_V2_OWNER_RECHECK.md`. This task explicitly prohibits editing `docs/PLAN_CURRENT.md` and `DESIGN_0G.md`. Verification results are separate new v2 sidecars. No analysis result, S5 authorization or scientific acceptance is claimed by this implementation.

Delivery is based on current HEAD, after the unrelated economy commit `cbe2da2`; the snapshot retains the initial `4147896` observation and intervening paths. It preserves every original/protected hash and mtime. If the primary `.git` is read-only, the new delivery helper creates a commit through normal hooks in an isolated git directory, then verifies a current-HEAD incremental bundle and every committed blob after a fresh fetch. No protected document is staged.

Final focused verification: **149 passed**, pytest **0.60 s**, measured process wall **0.76929575 s**. Synthetic receipts/runtime only; no trace analysis, rendering or fights executed. Earlier failed setup and previous successful batch remain separately recorded.
