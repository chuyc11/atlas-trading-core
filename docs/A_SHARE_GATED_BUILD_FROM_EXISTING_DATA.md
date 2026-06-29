# A-Share Gated Build From Existing Data

v0.8.7 executes the first controlled current-day `build_from_existing_data` dry-run after v0.8.0-v0.8.6 data, current-day, ops center, and ops history audits pass.

The release command is:

```bash
python -m trading_core.cli build-and-audit-a-share-gated-build-from-existing-data --as-of-date 2026-06-26 --mode run_gated_build_from_existing_data
```

Release result:

- preflight gate passed
- workflow mode: `build_from_existing_data`
- workflow audit passed
- comparison completed
- boundary clean
- recommended next version: `v0.8.8-a-share-build-from-existing-data-repeatability-and-diff-stability`

This is research-only and virtual-only. It is not live trading, not an order workflow, and not a trade instruction.

