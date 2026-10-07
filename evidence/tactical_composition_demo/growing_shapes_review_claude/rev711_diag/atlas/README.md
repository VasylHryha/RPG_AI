# Growing Shapes Atlas (the visualization)

- **Published page:** https://claude.ai/artifact/6t2LXndFvARKLjGRRa6gWx (private to the owner).
- **`growing-shapes-atlas.html`** is the published page, with its data embedded. `atlas_template.html` is the same page with a `__DATA__` placeholder.
- **Recorded snapshots (no verdict):** `snap_i_origin.json`, `snap_i_c2.json` and `snap_ii_origin.json`. Positions, phases, roles, and held and strong neighbour lists at 100–800 s, from the F5 fixture keys.
  - They were recorded by `snap_shapes.py` at the reviewed 7.11 identity.
  - Their logs (`snap_*.log`) reproduce the earlier pilot metrics exactly: late connectivity 0.000 / 0.308 / 0.323.
- **Merged frames:** the centre-pin scenario also includes frames 220.1, 220.4, 440.1 and 456.8 s, taken from `../trace.json.gz`, the step-by-step replay of the same run. Their strong links are recomputed from positions with the same rule (8 nearest within 3 m.u.; 32·exp(−r²)/degree ≥ 0.5).
