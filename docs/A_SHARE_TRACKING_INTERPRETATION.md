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
## v0.7.11 Performance Interpretation

The v0.7.11 performance layer separates observed virtual tracking from historical reconstruction. In default release mode, only actual available virtual tracking snapshots are used for portfolio observations.

For 2026-06-26, `multi_day_observations=1`, `multi_day_performance_available=false`, `insufficient_history=true`, `first_day_initialization=true`, and `performance_not_yet_observed=true`. Benchmark history can be available while portfolio realized virtual history remains limited.

Do not treat v0.7.11 output as investment advice, an order instruction, a broker workflow, a profit guarantee, or live-trading readiness. Do not read the first-day snapshot as proof that the strategy works.

## v0.7.12 Attribution Interpretation

v0.7.12 reads existing tracking holdings and performance artifacts to diagnose current exposure by holding, industry, candidate source, score bucket, risk bucket, liquidity bucket, benchmark-relative exposure, concentration, and factors.

Because `2026-06-26` is still first-day initialization for the virtual portfolios, the attribution package is structural rather than realized performance evidence. It does not create buy/sell signals, place orders, connect broker, call old `run-daily`, execute official forward dry-run day2, fabricate performance, or claim live trading readiness.
