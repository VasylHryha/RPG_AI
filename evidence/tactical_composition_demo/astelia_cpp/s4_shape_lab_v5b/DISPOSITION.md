One quick separate Codex tooling review under decision 0033. Same-family
review; Claude's mechanism read was inherited unchanged, and outcome review
remains Claude's responsibility. No numeric quality rating or acceptance.

F1 fixed before the focused test batch: `ensure_stage('mechanism', ...)` now
rejects mechanism calibration, run and review in v5b. Those entry points could
otherwise overwrite copied/pinned mechanism gate, run or projection receipts.
The regression calls all three commands with writes/execution forbidden and
checks byte-identical inherited receipts afterwards. The inherited pick is
also explicitly immutable. `prepare` remains verification-only.

The reviewer confirmed original mechanism receipt order is preserved and
reported no additional blocking defect. Repeated CONTINUATION metadata parsing
is finite and covered by the bounded calibration regression; completed raw
streams are never decoded during admission. Focused tests run after these
changes; test and delivery receipts contain measured timings.
