# A-Share Workflow Runbook

Default date:

```text
2026-06-26
```

## Validate Existing Artifacts

Use this mode when the v0.7.2-v0.7.8 artifacts already exist and should not be regenerated.

```powershell
python -m trading_core.cli run-and-audit-a-share-daily-research-workflow --as-of-date 2026-06-26 --mode validate_existing_artifacts
```

Expected result:

- `overall_passed=true`
- `blocking_reasons=[]`
- 11 stages passed
- no upstream artifact rebuild
- no old run-daily
- no broker
- no real orders
- no buy/sell signals
- no order previews

## Build From Existing Data

Use this mode only when the historical research panels already exist and the A-share research chain may be rebuilt from those panels.

```powershell
python -m trading_core.cli run-a-share-daily-research-workflow --as-of-date 2026-06-26 --mode build_from_existing_data
```

This mode must not download data, connect a broker, call old run-daily, execute official forward dry-run day2, place real orders, generate buy/sell signals, or generate order previews.

## Full Research Run

Use this mode for the complete safe research chain. Public historical data refresh remains disabled by default.

```powershell
python -m trading_core.cli run-a-share-daily-research-workflow --as-of-date 2026-06-26 --mode full_research_run
```

Public data refresh requires explicit authorization:

```powershell
python -m trading_core.cli run-a-share-daily-research-workflow --as-of-date 2026-06-26 --mode full_research_run --allow-public-data-refresh
```

Even when enabled, refresh is limited to public historical/research data sources. It must not use real-time trading data, broker APIs, account APIs, order APIs, or execution APIs.

## Failure Handling

If a critical stage fails, the workflow must stop, mark later critical stages blocked or not run, write blocking reasons, and fail the workflow audit. A success release tag must not be created when the workflow audit fails.

## Next Work

`v0.7.10-a-share-benchmark-data-and-performance-comparison` should add CSI300, CSI500, CSI1000, cash, equal-weight universe benchmark data, excess return, tracking error, relative drawdown, source trace, and benchmark audit.
