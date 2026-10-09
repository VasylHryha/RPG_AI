# Stage B round-1 host chain, recovery revision 3

Planned after **22:00 Europe/Kiev**, with the other Codex job and desktop apps quiet. The measured round-1 projection was **225 minutes on a quiet machine**, and **421 minutes under load** (other Codex job plus desktop apps). These are prior observations, not guarantees. The training maximum and live cap are **16,200 seconds / 270 minutes**. The loaded projection exceeds that cap.

Run the complete block below on the real host. It stops at the first refusal/failure. The head command verifies the already-sealed revision 3; the default smoke uses the real repository lock, process discovery and RAM/RSS/disk gates. Every smoke write goes into a fresh directory under Stage B's `_local/smoke/`; it reads original provenance and uses the real binary without changing production ledgers, budgets, exports or checkpoints.

The launcher reads `OWNER_APPROVALS.json`. Its JSON is excluded from source pins; snapshots and chronological config transitions are retained, and new receipts bind the config SHA256. Do not hand-edit source files or build artifacts between these stages. The historical training/runtime code remains byte-identical, with conservative fixed compatibility ceilings retained. Use this launcher for the current config-controlled chain.

The active round-1 budget is a REFUSED loaded measurement. `measure` archives that receipt byte-for-byte and takes a new prospective sample only if no training artifacts exist. An early process/admission refusal restores the old active refusal; a new measured refusal is retained. ADMITTED budgets and any round containing training artifacts are never replaced. No epochs/windows are reduced to fit the cap.

```sh
cd /Users/new/RiderProjects/ai_RPG_test
export STAGEB=evidence/tactical_composition_demo/astelia_cpp/s4_army_slice_v1/stageb
export STAGEB_PYTHON=evidence/tactical_composition_demo/astelia_cpp/s4_net_slice_v1/_local/mlenv/bin/python
export PYTHONDONTWRITEBYTECODE=1
caffeinate -i -s /bin/zsh -e <<'STAGEB_CHAIN'
"$STAGEB_PYTHON" "$STAGEB/eval_revision.py" recover-eval-chain --round 0 --revision 3
"$STAGEB_PYTHON" "$STAGEB/eval_revision.py" smoke --round 1
"$STAGEB_PYTHON" "$STAGEB/eval_revision.py" measure --round 1
"$STAGEB_PYTHON" "$STAGEB/eval_revision.py" run --round 1
"$STAGEB_PYTHON" "$STAGEB/eval_revision.py" parity --round 1
"$STAGEB_PYTHON" "$STAGEB/eval_revision.py" readout-prepare --round 1
"$STAGEB_PYTHON" "$STAGEB/eval_revision.py" readout-run --round 1 --look 20
STAGEB_CHAIN
```

| Stage | Time budget / planning estimate | RAM/RSS | Disk |
|---|---|---|---|
| Chain head | seconds; hash/provenance checks only | Python process | existing artifacts read, small config snapshot |
| Smoke | at most 300 s active chain; usually under two minutes | two PyTorch threads, 2 GiB Python/process cap; 512 MiB fixture/native profile cap | 5 GB reserve; measured fixture scratch about 15.5 MB |
| Measure | expected 3–20 min; live 16,200 s maximum | at most 2 GiB per process | 5 GB reserve plus receipts |
| Fit | quiet prior projection 225 min; loaded 421 min refuses; live maximum 270 min | up to four workers, two threads each, 2 GiB per worker, plus parent | 5 GB reserve plus durable epochs/exports |
| Parity | expected 10–25 min; live training cap | 2 GiB per process | 5 GB reserve plus streamed parity receipts |
| Readout preparation | seconds; seals paired entropy only | Python process | small requests/ledger under reserve |
| Look 20 | expected 20–60 min; measured admission under live lab cap | 2 GiB per process | measured full-duration storage projection at config multiplier 2 plus 5 GB reserve |

Production gates additionally require 512 MiB available RAM. DAgger and lab caps are separately declared in config (currently 16,200 s). Later cap reductions tighten active deadlines; cap increases do not extend an admitted invocation.

Codex self-ran `smoke --round 1 --test-mode` against the actual host binary: all seven steps PASS in 8.97 s. It collected tiny full-army fixtures, measured two optimizer steps per arm, trained one additional scratch step per arm, calibrated/exported, checked one native parity sequence per arm, and exercised the original readout report on one pair per regular/C3 panel across all six policies. Test mode skips process/RAM discovery and does not certify production host admission or learned quality.
