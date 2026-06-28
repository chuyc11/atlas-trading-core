# A-Share Tracking Interpretation

v0.7.8 tracking answers a narrow research question: how the existing long/mid/short virtual portfolios look when initialized into a virtual paper ledger and marked on the starting date.

## What It Means

- NAV is the virtual portfolio value under the selected valuation price policy.
- Daily return and cumulative return are zero on the first initialization day.
- Drawdown is zero on the first initialization day.
- Exposure summaries show industry and score-weighted concentration for the virtual holdings.
- v0.7.10 replaces the prior index placeholder limitation with a separate benchmark comparison package when real/public index history is available.

## What It Does Not Mean

- It is not a buy/sell signal.
- It is not an order instruction.
- It is not a broker workflow.
- It is not a real portfolio.
- It is not actual account performance.
- It is not a profit guarantee.
- It is not live-trading readiness.

## Reading First-Day Results

For `2026-06-26`, `first_day_initialization=true` and `performance_not_yet_observed=true`. That means the ledger was initialized, but no next-day mark has been observed yet.

Use the tracking report to inspect virtual holdings, NAV, exposure, and boundary status. v0.7.9 orchestrates the daily research workflow around this tracking package; v0.7.10 adds benchmark-relative comparison while keeping first-day portfolio performance limits explicit.
