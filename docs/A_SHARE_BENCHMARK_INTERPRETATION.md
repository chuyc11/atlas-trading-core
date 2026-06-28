# A-Share Benchmark Interpretation

v0.7.10 answers a narrow research question: how the initialized long/mid/short virtual portfolios compare with market and universe benchmarks using available historical benchmark data.

## What It Means

- Benchmark NAV and returns are available for CSI300, CSI500, CSI1000, CASH, strict-tradable equal-weight, and candidate-pool equal-weight.
- Excess return fields compare current virtual portfolio values with benchmark snapshots.
- `limited_history` means the portfolio side has too few observed days for multi-day relative metrics.
- `performance_not_yet_observed=true` means first-day tracking has not accumulated subsequent marks.

## What It Does Not Mean

- It is not a buy/sell signal.
- It is not an order instruction.
- It is not a broker workflow.
- It is not actual account performance.
- It is not a profit guarantee.
- It is not live-trading readiness.

v0.7.11 should extend the portfolio side into multi-day performance tracking before users interpret tracking error, information ratio, correlation, drawdown, or attribution as stable research evidence.

## v0.7.11 Follow-Through

v0.7.11 implements that multi-day performance tracking shell and keeps the first release honest: one portfolio observation is not enough for tracking error, information ratio, beta, correlation, rolling volatility, or stable drawdown statistics. Those metrics remain `insufficient_history` until the minimum observation window is reached.

The v0.7.11 layer still does not create buy/sell signals, place orders, connect a broker, call old `run-daily`, execute official forward dry-run day2, or claim live-trading readiness.
