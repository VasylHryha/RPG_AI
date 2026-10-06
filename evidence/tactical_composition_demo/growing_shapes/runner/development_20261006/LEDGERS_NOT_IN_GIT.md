# Raw ledgers kept outside git

The 66 raw event and drive ledgers (`*/events.jsonl.gz`, `*/drives.jsonl.gz`, about 14 GB in all, the largest 680 MB) are **not** in main's history. GitHub rejects files over 100 MB, and committing them would make the repository unusable.

- **Identity:** each ledger's SHA256 and byte count are in `ARTIFACTS.json`. Its decoded hash, byte count and record count are in `AUDIT_TRANSPORT.json`. Both are committed.
- **Where the bytes are:**
  1. the owner's local working tree, at the same paths;
  2. Codex's delivery commit `f87158bdf5dad321fae58c64ce4fd90a4d52a976` on the local branch `codex/0h-development`, which holds the complete delivery, ledgers included.
- **Verify a ledger:** `shasum -a 256 <path>` and compare it with `ARTIFACTS.json`.
- **Before deleting the local branch:** move the ledgers to external storage and record the location here.

Every other file of the delivery (reports, results, protocol audit, snapshots and templates in each seed's `REPORT.json.gz`, replays) is committed unchanged. Its blob hashes are identical to the delivery commit.
