# A-share Data Quality Audit

v0.7.1 uses two release gates for the A-share data foundation:

- coverage audit: `python -m trading_core.cli audit-a-share-data-coverage`
- schema audit: `python -m trading_core.cli audit-a-share-data-schema`

Both audits are data-only. They do not authorize trading, day2 execution, `run-daily`, scores, candidates, virtual portfolios, broker connectivity, or real orders.

## Coverage Audit

Machine-readable output:

```text
data/equity_data_quality/a_share_data_coverage_audit.json
```

Human-readable output:

```text
outputs/audit/A_SHARE_DATA_COVERAGE_AUDIT.md
```

The audit checks:

- required foundation artifacts exist.
- equity master, trading calendar, and daily price panel are non-empty.
- adjusted price, daily basic, industry, and financial artifacts are present or partial coverage is explicitly recorded.
- symbol coverage and date coverage are sufficient for the data-foundation release gate.
- duplicate rows, impossible prices, negative volume/amount, and negative market cap are rejected.
- provider warnings are surfaced from the source manifest.
- artifact hashes are recorded for reproducibility.
- forbidden-scope flags remain false.

Release pass requires:

```text
overall_passed=true
blocking_reasons=[]
boundary.data_ingestion_only=true
boundary.selection_generated=false
boundary.scores_generated=false
boundary.virtual_portfolio_generated=false
boundary.official_forward_dry_run_status_unchanged=true
boundary.day2_executed=false
boundary.run_daily_called=false
boundary.broker_connected=false
boundary.real_orders_placed=false
```

Warnings are allowed only when they are explicit data limitations, such as partial public provider snapshots, raw adjusted-price fallback, board-level industry fallback, or nullable financial fields.

## Schema Audit

Machine-readable output:

```text
data/equity_data_quality/a_share_data_schema_audit.json
```

Human-readable output:

```text
outputs/audit/A_SHARE_DATA_SCHEMA_AUDIT.md
```

The audit checks:

- required columns.
- source and source timestamp.
- no duplicate primary keys.
- A-share symbol format.
- date/report-date format.
- price sanity and high/low consistency.
- non-negative volume, amount, and market-cap fields.
- financial fields numeric when present.

Schema warnings should remain separate from blocking errors. A blocking schema error means downstream filters and scores must not consume the artifact.

## Current v0.7.1 Evidence

The current data foundation run records:

- `coverage.overall_passed=true`
- `schema.overall_passed=true`
- `blocking_reasons=[]`
- 5867 symbols in the equity master.
- 5513 symbols in daily price and adjusted price artifacts.
- 5867 symbols in daily basic, industry, and basic financial artifacts.
- one public snapshot date, `2026-06-26`
- 282 calendar trading-day rows across SSE/SZSE/BSE
- source raw coverage ratio 1.0 against raw total 5867
- observed exchanges: BSE, SSE, SZSE

Current warnings are data-quality evidence, not recommendations:

- daily price panel missing 354 master symbols in the current public snapshot.
- raw adjusted-price fallback.
- board-level industry fallback.
- nullable basic financial numeric fields.

## v0.7.1.1 Historical Audits

v0.7.1.1 adds:

```text
data/equity_data_quality/a_share_historical_panel_coverage_audit.json
outputs/audit/A_SHARE_HISTORICAL_PANEL_COVERAGE_AUDIT.md
data/equity_data_quality/a_share_feature_readiness_audit.json
outputs/audit/A_SHARE_FEATURE_READINESS_AUDIT.md
```

The historical coverage audit is fail-closed. If price history has fewer than 3000 symbols, fewer than 700 trading days, fewer than 3000 symbols with 120d history, or fewer than 2500 symbols with 250d history, `overall_passed=false`.

## v0.7.1.2 Historical Provider Expansion Audits

v0.7.1.2 adds root-cause, queue, checkpoint, batch, and per-symbol evidence:

```text
data/equity_data_quality/a_share_historical_backfill_root_cause.json
data/equity_data_quality/a_share_historical_backfill_symbol_queue.json
data/equity_data_quality/a_share_historical_backfill_checkpoint.json
data/equity_data_quality/a_share_historical_backfill_symbol_manifest.json
data/equity_data_quality/backfill_batches/
```

The historical coverage audit now also reports `coverage_global`, including coverage versus `equity_master.parquet` and the backfill queue. Failed readiness recommends `v0.7.1.3-a-share-historical-data-source-upgrade`; passed readiness recommends `v0.7.2-a-share-tradable-universe-filter`.
