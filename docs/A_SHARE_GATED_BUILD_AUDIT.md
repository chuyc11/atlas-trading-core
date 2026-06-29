# A-Share Gated Build Audit

Run:

```bash
python -m trading_core.cli audit-a-share-gated-build-from-existing-data --as-of-date 2026-06-26
```

The audit checks:

- required gated build JSON and Markdown artifacts exist
- preflight gate passed
- ops history, ops center, current-day, and data refresh audits passed
- workflow command used `build_from_existing_data`
- gated execution was performed
- workflow audit passed
- validate-vs-build comparison completed
- missing required artifacts are absent
- boundary drift is absent
- source trace is complete
- no old `run-daily`, day2, broker, real orders, buy/sell signals, or order preview occurred
- build output is not treated as a trade instruction

