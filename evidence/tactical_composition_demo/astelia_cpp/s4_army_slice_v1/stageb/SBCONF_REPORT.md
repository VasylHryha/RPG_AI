# Stage B live controls and smoke delivery

Recovery revision 3 is sealed and was separately rechecked. Owner config is read by the recovery launcher, outside source pins. New operational receipts record its hash, and archived config transitions include returns to a previously used config. Training maximum/live cap, DAgger/lab caps, native and recurrent float32 parity rules, calibrated-fire rules, disk reserve/projection factor, RSS and RAM reserves are declared in config.

Original training sources, binary, round-0 budget/index, calibrated fits and earlier recovery receipts remain unchanged. Revision 3 protects exactly 59 original training-relevant sources at their round-0 hashes, with only the already-authorized evaluator change and enumerated new/revised recovery tooling. Historical fixed ceilings remain conservative compatibility guards; the active config does not weaken them.

Self-run evidence: **PASS**, all seven test-mode smoke steps on the actual native host binary, **8.966 s** total. Two measurement steps and one scratch training step per arm; one parity sequence per arm; one regular and one C3 paired fixture across all six policies. Training-only target balance is read from the original budget; tiny calibration uses fixture rows only. Scratch data and reports are development wiring evidence only. No real ledger/output or production training artifact is written by smoke.

| Step | Verdict | Seconds | Python peak RSS bytes | Native peak RSS bytes | Free disk after, bytes |
|---|---|---:|---:|---:|---:|
| preflight | PASS | 1.536 | 213696512 | 0 | 29728763904 |
| admission | PASS | 0.000 | 317980672 | 0 | 29698965504 |
| collect | PASS | 0.147 | 327319552 | 7110656 | 29698723840 |
| measure | PASS | 0.665 | 372916224 | 0 | 29698682880 |
| train | PASS | 0.705 | 379142144 | 0 | 29693374464 |
| parity | PASS | 1.407 | 385581056 | 7962624 | 29693337600 |
| readout | PASS | 2.250 | 386138112 | 10846208 | 29683183616 |

Peak Python RSS: 386,138,112 bytes (368.25 MiB). Native peak: 10,846,208 bytes (10.34 MiB). Scratch footprint at final step: 15,417,432 bytes. Final free disk: 29,683,183,616 bytes. Process/RAM discovery is disabled only in explicit test mode; the default host smoke has real gates. Production host smoke and long runs were not started in this batch.

Focused tests: final 85 passed in 4.03 s (4.95 s command). Initial 84-pass planned batch is retained in the receipt; an actual chain-admission refusal required one historical-proof correction and the final failure-driven batch. The separate reviewer checked fixes and final receipts and found no remaining blocker. Recheck is Codex-family, read-only; no cross-family scientific acceptance claim.

Prior measured round-1 projections: **225 min quiet**, **421 min loaded** (other Codex job plus desktop apps). Planned after **22:00 Europe/Kiev**. Config training cap is **16,200 s / 270 min**. The existing REFUSED loaded measurement is preserved; the host measure command takes a new prospective sample and refuses to replace admitted budgets or any round containing training artifacts.

Time/RAM/disk budgets and the complete host block are in HOST_COMMANDS_STAGEB.md. Recheck and disposition are in OWNER_RECHECK_SBCONF.md. The session changed-path ledger is UNCOMMITTED_SBCONF.txt. No stageb2, stagea, rev2 or PLAN_CURRENT.md edits were made by this job.
