# A-Share Benchmark Schema

## Config

`benchmark_config.json` records:

- target version
- as-of date
- benchmark ids
- index code map
- adjusted-close-then-close price policy
- cash benchmark daily return
- lookback and minimum history settings
- placeholder policy
- research-only boundary flags

## Availability

`benchmark_data_availability.json` records each benchmark status:

- `available`
- `missing`
- `placeholder_allowed`
- `failed`

Release runs require CSI300, CSI500, CSI1000, CASH, strict-tradable equal-weight, and candidate-pool equal-weight to be available without placeholder use.

## Returns And NAV

`benchmark_return_snapshot.json` stores daily benchmark returns. `benchmark_nav_snapshot.json` stores NAV with `base_nav=1.0`.

Index benchmark returns use `price_t / price_t-1 - 1`. CASH uses `0.0`. Equal-weight benchmarks use the average daily return of eligible as-of constituents.

## Comparison

`portfolio_benchmark_comparison.json` compares long, mid, and short virtual portfolios against all supported benchmarks. First-day portfolio history is marked `limited_history`; tracking error, information ratio, and correlation remain null until enough observed portfolio history exists.
