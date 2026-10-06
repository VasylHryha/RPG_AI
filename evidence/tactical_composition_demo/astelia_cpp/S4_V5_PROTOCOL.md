# v5 Part 1 protocol

Authority: owner conditional implementation request, section-17 amendments and Codex round-2 APPROVE_WITH_NOTES. The pinned design snapshot is S4_V5_DESIGN_PIN.md (SHA256 46c57c0d7b38cf64f1f2b90a0df2e91b46021fb6a3e34d1b2d25a1094a45dd12). Amendments override preceding prose. A/B only; no C, judging, registration, S5 or scientific acceptance. This delivery does not execute development.

Native v5 aliases v3 policy exactly: range-aware distances, binary out-ranged commit/escape hysteresis ±0.2, no travel-time hold, no commit focus. H/F/HF/v4 remain labelled variants. Counts 11/11/3, nearest untuned. CMA 4.5.0, population 16, sigma .25, 16 generations, unchanged RNG rule and [0,1] mapping, 19 fixed common clusters, two orientations per cluster. Every tuned arm gets 9,766 accounted evaluations per completed stage, including hits. A begins at midpoints; B begins at A's tuning-selected incumbent. Validation never selects knobs. Fixed generations remain even if optimizer stop diagnostics fire.

A selects novice melee10 mean S. B separately averages ten novice and nine regular tuning clusters. Novice mean >=0 is eligible. Compare (eligible, regular mean S) lexicographically; stable earlier exact ties. CMA loss is -regular S for eligible, 101-regular S for ineligible. Since S lies in [-50,50], the loss bands [-50,50] and [51,151] enforce precisely the incumbent ranking. No damage/timing/gun tie-breaks. Selection receipts include both means, eligibility and role omegas, including ineligible selections and B stops. Omega is diagnostic only.

Validation: all four arms, 100 paired clusters per endpoint; A novice melee10, B full-head novice and regular. After all-arm validation, resonator novice mean <=0 stops independently of tuning eligibility. B regular validation mean must be strictly >-7.62; equality fails progress. Report both gates. A passes CONTINUE; B passes PROGRESS, otherwise STOP. Never READY_FOR_S5. C is explicitly not_run even after progress. Report S intervals and guns alive, timeouts, cross-team damage, conditional elimination times and censored timeouts. Raw rows retain all descriptive data; these never affect selection.

Fresh S4_V5_SEEDS.json declares independent development entropy and prior-ledger/source inventory with hashes. An exclusive permanent LEDGER_USED.json claim prevents reuse; existing output is refused. Tuning shares seeds across candidates/generations/arms, B validation shares seed IDs across heads. Declaration never reads judging entropy. Expected maximum: 58,596 tuning + 2,400 validation = 60,996 fights, no extra replay fights.

Runtime allowance: full 360 minutes for this new v5 run, absolute monotonic deadline from main entry. Ten workers; bounded in-flight submissions; every worker gets the deadline; subprocess allowance clamped to remaining time; active children terminated and pending futures cancelled on stops. Before each generation project remaining work using at least .062 wall-seconds/fight or observed fresh rate, whichever is slower; stop before exceeding remaining allowance. Code, tests, reviewed pin, optimizer files and admitted binary are verified before launch and during execution. No edits during development. Permanent claims and partial/failure receipts are retained; retry requires a fresh revision and ledger.

Conservative cost: 4–6 hours from section 17, with fewer fights than historical A/B/C; actual v5 duration is unmeasured. Floor projection alone is about 63 minutes, not an empirical estimate. Run only after tonight's C6 timing and when the laptop is free. Hard cap may stop an over-budget attempt. No development is authorized by this readiness delivery.

| Yes/no condition | Action | Responsible role |
|---|---|---|
| Is a pinned input/binary/source different or the ledger consumed? | Stop before combat and preserve the attempt. | implementer |
| Is resonator novice validation mean <=0 after all-arm A or B? | Stop and report the gate. | implementer |
| Is resonator B regular validation mean <=-7.62? | Report STOP with selected omegas. | implementer |
| Is remaining projected work beyond the deadline, or has the deadline expired? | Terminate active work and preserve failure evidence. | implementer |
| Did B pass both gates? | Report development PROGRESS and stop after B. | implementer |
| Is C proposed? | Declare a later reviewed allocation before execution. | drafter |
