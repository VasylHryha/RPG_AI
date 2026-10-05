# S2 completed engineering evidence

READY for independent Claude review. [The report](../S2_PLUG_REPORT.md) states the checks, scope, implementation and deviations. Receipt SHA256: `1ae077ba28cdf5e9b13adc8d097457640846cd9defc15d5945b4ce782a13bb29`.

171 tests passed; controller ASan/UBSan passed; 80 no-controller reference requests match the archived admitted build exactly; 228 full-trace passthrough pairs match exactly; 38 untouched-side first-tick decision checks pass; 114 nearest fights complete and repeat identically; nearest/built-in alone elapsed ratio is 0.8327579172 on the same 50 qualification request contexts.

`S2_RECEIPT.json` maps 542 logical raw captures to 310 content-addressed ordinary XZ files under `stdout/`, retaining every raw byte hash. Their decoded data is exactly the original stdout, including all initial/step frames and summaries. Packing reduced 1,868.3 MiB of duplicate gzip captures to 535.8 MiB. `S2_RECEIPT.prepack.json` records the original capture metadata for provenance; its old gzip paths were replaced by the current receipt's `path` mappings. No simulation was rerun or result changed during packing.

Read a logical output using Python:

```python
import json, lzma, pathlib
root = pathlib.Path("evidence/tactical_composition_demo/astelia_cpp/s2_plug_r2")
receipt = json.loads((root / "S2_RECEIPT.json").read_text())
entry = receipt["outputs"]["plumbing/000_builtin.jsonl.gz"]
raw_stdout = lzma.decompress((root / entry["path"]).read_bytes())
```

Verify all archive/decoded identities without running combat with `../pack_s2.py <this-directory> --check`. Input grids, per-pair hashes, compiler/test/sanitizer logs and full source/build identities are retained alongside the archives. The failed preceding compilation attempt is preserved in `../s2_plug_r1/`; no tests or fights ran in that attempt.
