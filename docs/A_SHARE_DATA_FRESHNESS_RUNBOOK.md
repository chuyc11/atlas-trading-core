# A-Share Data Freshness Runbook

Use local validation first:

```bash
python -m trading_core.cli build-and-audit-a-share-daily-data-refresh --as-of-date 2026-06-26 --mode validate_existing_data
```

Resolve the latest completed trading day:

```bash
python -m trading_core.cli build-a-share-daily-data-refresh --resolve-latest-completed-trading-day --mode validate_existing_data
```

Default behavior:

- does not use intraday data
- does not select a partially completed trading day
- fails closed on non-trading days unless explicitly waived
- does not call external network providers
- does not trigger the full research workflow

If a critical dataset is stale or missing, repair the data source or run an explicit provider refresh. Do not treat stale fallback data as silently acceptable.
