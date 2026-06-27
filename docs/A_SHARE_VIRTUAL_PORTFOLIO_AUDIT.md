# A-Share Virtual Portfolio Audit

`audit-a-share-virtual-portfolios` validates v0.7.6 virtual portfolio construction artifacts.

```powershell
python -m trading_core.cli audit-a-share-virtual-portfolios --as-of-date 2026-06-26
```

## Checks

The audit verifies:

- portfolio config exists
- portfolio manifest exists
- long, mid, and short virtual portfolio files exist
- weight, industry, and risk/liquidity summary files exist
- portfolio reports exist
- all portfolio symbols are from candidate pools or multi-horizon candidates
- no risk-downgraded symbols appear in main portfolios
- no excluded-universe symbols appear
- no duplicate symbols within each portfolio
- holdings count matches config
- weight sums are approximately 1.0
- single-stock caps are respected
- industry caps are respected
- required disclaimer flags are present
- no buy/sell signal artifacts were generated
- no order preview was generated
- no broker order was generated
- no real order was generated
- no main orders/trades/accounts writes were generated for the as-of date
- no buy/sell/order columns exist
- no profit-guarantee wording is present
- boundary flags are consistent across config and manifest

## Outputs

- `data/equity_data_quality/a_share_virtual_portfolio_construction_audit.json`
- `outputs/audit/A_SHARE_VIRTUAL_PORTFOLIO_CONSTRUCTION_AUDIT.md`

## Passing Release Evidence

For `as_of_date=2026-06-26`:

```text
overall_passed = true
blocking_reasons = []
long_holdings = 30
mid_holdings = 30
short_holdings = 20
long_weight_sum = 1.0
mid_weight_sum = 1.0
short_weight_sum = 1.0
risk_downgraded_symbols_included = []
excluded_universe_symbols_included = []
recommended_next_version = v0.7.7-a-share-daily-stock-selection-briefing
```

Warnings note that raw `industry_level_1` contains `Unclassified`; the audit uses documented fallback industry buckets for cap checks.

## Boundary

Passing audit does not approve real trading, buy/sell signals, broker order previews, real orders, profit claims, or live-trading readiness.

The audit must fail closed if real portfolio, buy/sell signal, order preview, broker order, real order, broker, profit-guarantee, or live-readiness artifacts appear in the v0.7.6 virtual portfolio stage.
