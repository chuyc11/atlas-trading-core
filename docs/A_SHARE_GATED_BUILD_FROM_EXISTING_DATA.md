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

## v0.8.8 repeatability handoff

v0.8.8 consumes the v0.8.7 gated build evidence and repeats the same `build_from_existing_data` workflow for the same `as_of_date`. It adds build-vs-build comparison, deterministic field normalization, warning comparison, source trace stability, boundary stability, and protected path pre/post snapshots.

v0.8.8 distinguishes pre-existing protected paths from modified protected paths. Existing `data/orders` or `data/trades` are informational if unchanged; new, modified, or deleted protected files are blocking.

v0.8.8 remains research-only and virtual-only. It does not refresh public network data, does not run `full_research_run`, does not generate buy/sell signals, does not place orders, does not connect broker, does not call old run-daily, does not execute official forward dry-run day2, and does not treat repeatability as a trade instruction.
