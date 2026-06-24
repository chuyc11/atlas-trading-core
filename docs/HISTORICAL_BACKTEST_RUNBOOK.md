# Historical ETF Backtest Runbook

Purpose: run local historical ETF backtests for the CHINA ETF universe without downloading data or connecting to any broker.

## Input

Prepare a local CSV with this header:

```text
date,symbol,open,high,low,close,volume,source,quality
```

The runbook supports:

- `hold_strategy`
- `macro_etf_strategy_v1`
- `momentum_strategy_v1`

Benchmarks reviewed:

- `CASH`
- `EQUAL_ETF`
- `CSI300`

## Command

```powershell
python scripts/run_historical_etf_backtest.py --input prices.csv --start-date 2024-01-01 --end-date 2026-06-23
```

## Output

Each run writes to:

```text
work/trading-core/outputs/backtests/YYYYMMDD-HHMMSS/
```

Files:

- `run_config.json`
- `strategy_results.json`
- `benchmark_results.json`
- `backtest_summary.md`
- `limitations.json`

## Review Checklist

- Confirm data coverage and missing data statistics.
- Compare each strategy against CASH, EQUAL_ETF, and CSI300.
- Review costs, turnover, drawdown, and trade counts.
- Review admission gate decisions.
- After `run-backtest-batch`, audit historical artifacts with:

```powershell
python -m trading_core.cli check-consistency-range --start-date 2024-01-01 --end-date 2026-06-23 --mode backtest --artifact-dir work\trading-core\outputs\backtests\batch-YYYYMMDD-HHMMSS
```

- Then assemble the v0.2 real-data validation evidence with:

```powershell
python -m trading_core.cli real-data-validation-report --artifact-dir work\trading-core\outputs\backtests\batch-YYYYMMDD-HHMMSS
```

- Do not promote strategies automatically from this run.
