# A-Share Build Repeatability Audit

Run:

```bash
python -m trading_core.cli audit-a-share-build-repeatability --as-of-date 2026-06-26
```

The audit checks:

- v0.8.7 gated build audit passed
- repeat build command used `build_from_existing_data`
- repeat build audit passed
- build-vs-build comparison completed
- missing required artifacts are absent
- business output drift count is zero by default
- boundary drift is absent
- protected path modification is absent
- source trace is complete and required source hashes match
- no old run-daily, broker, real orders, buy/sell signals, order preview, real account read, profit guarantee, or live-ready claim occurred

Pre-existing protected paths are allowed only if unchanged.

