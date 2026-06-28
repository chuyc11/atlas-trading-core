# A-Share Data Refresh Audit

Audit command:

```bash
python -m trading_core.cli audit-a-share-daily-data-refresh --as-of-date 2026-06-26
```

Combined release E2E command:

```bash
python -m trading_core.cli build-and-audit-a-share-daily-data-refresh --as-of-date 2026-06-26 --mode validate_existing_data
```

The audit verifies:

- required artifacts exist
- all required datasets are present or correctly reported
- critical datasets pass
- schema validation passes
- freshness validation passes
- coverage validation passes
- trading calendar covers `as_of_date`
- daily price and index price include the target date
- CSI300, CSI500, and CSI1000 index data are present
- provider fallback is recorded
- source trace is complete and hash-checked where practical
- no broker, account, or order provider is used
- boundary fields remain clean

This audit is a data-readiness gate, not a trading-readiness gate.
