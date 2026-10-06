# Revision-6 integration delivery

Codex:GPT-6, 2026-10-06. Base HEAD `2bd6965`; approved section 18.6 design SHA256 `2abda7e2409920fee3ad71779f224e75cce272c547ad2c4c87cfc87fb91b408b`.

Use `REV6_INTEGRATION_BUNDLE.tar.gz` with `REV6_INTEGRATION_MANIFEST.json` and `REV6_INTEGRATION_BUNDLE_VERIFIED.json`. The archive contains the new versioned source, final report, pre-result seed inventory, historical stop report/inventory and original stop packet, actual native build identities/images, test logs (including failed attempts) and construct-only evidence. It contains no historical raw bulk ledgers or other-session work. All member paths are within `evidence/tactical_composition_demo/growing_shapes/`; all members are below 50 MB. The verification file reports the actual archive digest and per-member byte/hash checks.

`.git` is read-only under the supplied permissions. No commit, staging operation, hook bypass or push was attempted. When importing, preserve unrelated dirty/staged work and every file in `REV6_BASELINE_IDENTITY.json`. Import only the manifest's bounded paths. Keep `rev6_history/SPECIFICATION_STOP_REPORT.md` and the old `REV6_SPECIFICATION_STOP_PACKET.tar.gz` as the original stop record. The final active report is `REV6_INTEGRATION_REPORT.md`.

Suggested scoped commit message:

```
Implement revision-6 growing-shapes integration and gated fixture harness

Assisted-by: Codex:GPT-6
```

The two `_rev6_build/` images are verified on this macOS workspace; their linked dependency paths are absolute. For another checkout, explicitly rebuild the versioned images, using the unchanged existing world build as a dependency:

```
.venv/bin/python -m evidence.tactical_composition_demo.growing_shapes.runner.build_rev6
```

No legacy image is rebuilt implicitly. The existing world/medium 5.1 source and images remain unchanged. If the original world build is absent or stale, the versioned builder refuses rather than changing that prerequisite silently.

The final affected suite passed **29 tests in 1.09 s**. It has not been repeated after that PASS. Reproduce only if imported source/build identities differ or an implementation review introduces changes:

```
.venv/bin/python -m pytest -q -x evidence/tactical_composition_demo/growing_shapes/runner/test_rev6.py --basetemp=evidence/tactical_composition_demo/growing_shapes/runner/_rev6_build/pytest-tmp -o cache_dir=evidence/tactical_composition_demo/growing_shapes/runner/_rev6_build/pytest-cache
```

`REV6_CONSTRUCT_ONLY.json` has zero integrated steps. F6/F8 carry explicit checkpoint dependency recipes; their real states await the approved F5 execution. F1–F8, all training and evaluation panels remain **NOT_RUN**. The 2,842-key seed inventory and 128 donor entries precede any result; F8's two consumers and F6's world ranges/pairs are present.

The report's first line is **NOT_READY**: implementation and bounded contracts are complete, but section 14.9's separate implementation-review gate remains open. Obtain that review and the owner's separate fixture authorization before F1–F8. The future APIs default to denied execution; no grant is included in this packet. Development additionally needs its own approval and the fixture gates. Cost estimates are inherited rate proxies, not measured fixture timings or upper bounds.

Assisted-by: Codex:GPT-6
