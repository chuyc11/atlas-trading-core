# A-Share Virtual Portfolio Construction

`v0.7.6-a-share-virtual-portfolio-construction` consumes the v0.7.5 candidate package and builds three research-only virtual portfolios:

- `long_virtual_portfolio`
- `mid_virtual_portfolio`
- `short_virtual_portfolio`

The stage answers one question: how should long, mid, and short research candidates be arranged into virtual target portfolios for future virtual tracking?

It does not answer what to buy, what to sell, what to submit to a broker, or how to rebalance a real account.

## Commands

```powershell
python -m trading_core.cli build-a-share-virtual-portfolios --as-of-date 2026-06-26
python -m trading_core.cli audit-a-share-virtual-portfolios --as-of-date 2026-06-26
python -m trading_core.cli build-and-audit-a-share-virtual-portfolios --as-of-date 2026-06-26
```

The default `as_of_date` is `2026-06-26`. The builder requires an exact candidate directory by default. Use `--allow-latest-candidate-date` only for explicit historical catch-up runs.

Optional holdings:

```powershell
python -m trading_core.cli build-a-share-virtual-portfolios --as-of-date 2026-06-26 --long-holdings 30 --mid-holdings 30 --short-holdings 20
```

## Construction Method

- Long portfolio uses long candidates first, with multi-horizon candidates as fallback.
- Mid portfolio uses mid candidates first, with multi-horizon candidates as fallback.
- Short portfolio uses short candidates first, with multi-horizon candidates as fallback.
- Risk-downgraded candidates are excluded from main virtual portfolios.
- Excluded universe symbols are excluded.
- Caution and unknown symbols are excluded by default.
- All portfolios are long-only, unlevered, and derivatives-free.

Weights are deterministic research target weights. They combine horizon percentile/rank, risk, liquidity, industry, fundamental, composite score, and confidence. They are capped by single-stock and industry limits, then normalized to 100%.

## Artifacts

Machine-readable artifacts:

- `data/equity_portfolios/daily/YYYY-MM-DD/portfolio_construction_config.json`
- `data/equity_portfolios/daily/YYYY-MM-DD/long_virtual_portfolio.json`
- `data/equity_portfolios/daily/YYYY-MM-DD/long_virtual_portfolio.parquet`
- `data/equity_portfolios/daily/YYYY-MM-DD/mid_virtual_portfolio.json`
- `data/equity_portfolios/daily/YYYY-MM-DD/mid_virtual_portfolio.parquet`
- `data/equity_portfolios/daily/YYYY-MM-DD/short_virtual_portfolio.json`
- `data/equity_portfolios/daily/YYYY-MM-DD/short_virtual_portfolio.parquet`
- `data/equity_portfolios/daily/YYYY-MM-DD/portfolio_weight_summary.json`
- `data/equity_portfolios/daily/YYYY-MM-DD/portfolio_industry_exposure.json`
- `data/equity_portfolios/daily/YYYY-MM-DD/portfolio_risk_liquidity_summary.json`
- `data/equity_portfolios/daily/YYYY-MM-DD/portfolio_manifest.json`

Human-readable reports:

- `outputs/equity_portfolios/daily/YYYY-MM-DD/LONG_VIRTUAL_PORTFOLIO.md`
- `outputs/equity_portfolios/daily/YYYY-MM-DD/MID_VIRTUAL_PORTFOLIO.md`
- `outputs/equity_portfolios/daily/YYYY-MM-DD/SHORT_VIRTUAL_PORTFOLIO.md`
- `outputs/equity_portfolios/daily/YYYY-MM-DD/PORTFOLIO_CONSTRUCTION_SUMMARY.md`

Audit artifacts:

- `data/equity_data_quality/a_share_virtual_portfolio_construction_audit.json`
- `outputs/audit/A_SHARE_VIRTUAL_PORTFOLIO_CONSTRUCTION_AUDIT.md`

## Release Evidence

The release run for `as_of_date=2026-06-26` passed:

```text
long_holdings = 30
mid_holdings = 30
short_holdings = 20
long_weight_sum = 1.0
mid_weight_sum = 1.0
short_weight_sum = 1.0
long_max_single_weight = 0.037139
mid_max_single_weight = 0.036981
short_max_single_weight = 0.055804
long_max_industry_weight = 0.25
mid_max_industry_weight = 0.25
short_max_industry_weight = 0.30
overall_passed = true
blocking_reasons = []
recommended_next_version = v0.7.7-a-share-daily-stock-selection-briefing
```

## Boundary

v0.7.6 is a virtual portfolio construction stage.

Virtual portfolios are not real portfolios. Virtual target weights are not order instructions. Virtual portfolios do not connect brokers. Virtual portfolios do not place real orders. They are inputs for v0.7.7 daily stock selection briefing and future virtual tracking.

These remain forbidden:

- real portfolio generation
- buy/sell signal generation
- broker order preview generation
- real order generation
- broker connection
- real orders
- `run-daily`
- official forward dry-run day2 execution
- live-trading readiness claims
- model profit guarantee claims

Daily AI stock selection briefing is handled by v0.7.7. Virtual portfolio tracking and paper ledger work is implemented in v0.7.8.
