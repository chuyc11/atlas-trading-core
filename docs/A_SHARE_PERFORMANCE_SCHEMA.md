# A-Share Performance Schema

v0.7.11 writes machine-readable performance artifacts under `data/equity_performance/daily/YYYY-MM-DD/`.

## Core Artifacts

- `performance_config.json`
- `performance_data_availability.json`
- `portfolio_nav_series.json`
- `portfolio_return_series.json`
- `portfolio_drawdown_series.json`
- `portfolio_relative_performance_series.json`
- `portfolio_benchmark_relative_series.json`
- `holding_mark_to_market_series.json`
- `performance_metric_snapshot.json`
- `performance_limitations.json`
- `performance_append_log.json`
- `performance_source_trace.json`
- `performance_manifest.json`
- `performance_boundary_check.json`
- `performance_summary.json`

## Required Flags

Every release artifact preserves:

- `research_only=true`
- `virtual_only=true`
- `not_investment_advice=true`
- `not_order_instruction=true`
- `not_profit_guarantee=true`
- `not_live_trading_ready=true`

## Limited History Fields

When only 2026-06-26 is available:

- `portfolio_observation_count=1`
- `minimum_required_observations=20`
- `sufficient_history=false`
- `insufficient_history=true`
- `first_day_initialization=true`
- `performance_not_yet_observed=true`

Rolling volatility, tracking error, information ratio, beta, correlation, and rolling drawdown statistics remain `insufficient_history` with `value=null` until the minimum observation window exists.

## Holding MTM

Holding rows include symbol, name, virtual shares, mark price, position value, target weight, actual weight, unrealized PnL, unrealized return, and source tracking ledger. They do not include order ids, fill ids, broker order ids, buy signals, sell signals, or execution status.
