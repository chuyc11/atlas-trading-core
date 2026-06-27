# A-share Data Ingestion

v0.7.1 establishes the local A-share data foundation for later full-market stock selection research. It is data ingestion only.

It does not generate stock recommendations, LongScore/MidScore/ShortScore, candidates, watchlists, virtual portfolios, broker instructions, real orders, `run-daily` output, or official forward dry-run day2 artifacts.

## Command Chain

```powershell
python -m trading_core.cli equity-data-source-manifest
python -m trading_core.cli build-a-share-equity-master
python -m trading_core.cli build-a-share-trading-calendar
python -m trading_core.cli ingest-a-share-daily-prices
python -m trading_core.cli ingest-a-share-adjusted-prices
python -m trading_core.cli ingest-a-share-daily-basic
python -m trading_core.cli ingest-a-share-industry-classification
python -m trading_core.cli ingest-a-share-basic-financials
python -m trading_core.cli audit-a-share-data-coverage
python -m trading_core.cli audit-a-share-data-schema
```

Equivalent one-command chain:

```powershell
python -m trading_core.cli build-a-share-data-foundation
```

## Local Artifacts

| Artifact | Purpose |
|---|---|
| `data/equity_universe/equity_master.parquet` | normalized A-share master with exchange, board, ST, and active flags |
| `data/equity_universe/trading_calendar.parquet` | SSE/SZSE/BSE calendar foundation |
| `data/equity_market/daily_price_panel.parquet` | daily OHLCV and amount panel |
| `data/equity_market/adjusted_price_panel.parquet` | adjusted price panel with raw fallback explicitly labeled when needed |
| `data/equity_market/daily_basic_panel.parquet` | total/circulating market cap, turnover, and valuation metrics when available |
| `data/equity_industry/industry_classification.parquet` | industry classification or board-level fallback |
| `data/equity_fundamental/basic_financials_panel.parquet` | basic financial fields with nullable coverage tracking |
| `data/equity_data_quality/a_share_data_source_manifest.json` | provider priority, attempted/succeeded/failed providers, and boundary flags |
| `data/equity_data_quality/a_share_data_coverage_audit.json` | coverage, warnings, hashes, and forbidden-scope boundary flags |
| `data/equity_data_quality/a_share_data_schema_audit.json` | schema, primary key, symbol/date format, and sanity checks |

Human-readable reports are written to `outputs/equity_universe/`, `outputs/equity_data_quality/`, and `outputs/audit/`.

## Current Provider Behavior

The default public path is `qstock_reference_public_http`. It is a trading-core adapter that follows qstock-style public-data ideas without importing third-party qstock code. It uses public historical/delayed market data endpoints and writes only local research data.

If the public endpoint returns a partial page set, times out, or fails, the run records the provider reason in the source manifest and coverage audit. The current release accepts a partial public snapshot only when the core master, calendar, and daily-price foundation remains sufficient for the data-layer release gate.

## Boundary

`external_api_called=true` means only that a public historical/delayed data endpoint was queried. It does not mean real-time trading data, broker connectivity, account access, order submission, or live readiness.

Free public data can be incomplete, delayed, or schema-variable. Later filters and scoring modules must consume the audited local artifacts, not bypass the source manifest and audit layer.

## v0.7.1.1 Historical Extension

v0.7.1.1 adds historical panels under `data/equity_market/history/` and `data/equity_fundamental/history/`. It keeps the same rule: data first, audit first, no scores, no candidates, no virtual portfolios, no broker, and no orders.

## v0.7.1.2 Historical Provider Expansion

v0.7.1.2 fixes the v0.7.1.1 coverage blocker by building a full-market symbol queue from `equity_master.parquet`, running checkpointed provider backfill, writing per-batch and per-symbol manifests, and auditing global coverage against both equity master and the backfill queue.

The release evidence has 5516 price-history symbols, 1326 trading days, and passing historical coverage and feature-readiness audits. It remains data preparation only: no stock scores, no candidates, no watchlists, no virtual portfolios, no broker, no real orders, no `run-daily`, and no day2 forward dry-run.

The historical extension must fail closed if the minimum history window is not met. Single-day v0.7.1 panels cannot be used as a substitute for historical data.

## v0.7.2 Tradable Universe Filter Input

v0.7.2 reads the local artifacts produced by v0.7.1 and v0.7.1.2. It does not call provider APIs directly from the filter stage.

Required inputs include `equity_master`, `trading_calendar`, historical daily price and adjusted-price panels, daily basic history, the as-of daily basic snapshot for market-cap fallback when historical market-cap fields are unavailable, industry classification, financial history, the historical symbol manifest, and the coverage/readiness audits.

The filter writes strict/caution/excluded/unknown buckets only. It does not generate scores, candidates, watchlists, virtual portfolios, broker calls, real orders, `run-daily`, or day2 forward dry-run artifacts.
