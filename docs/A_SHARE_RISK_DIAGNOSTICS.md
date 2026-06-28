# A-Share Risk Diagnostics

v0.7.12 adds risk diagnostics for the existing research-only virtual portfolios.

Diagnostics include:

- weighted average risk score
- weighted average liquidity score
- weighted average composite score
- max single holding weight
- top 5 and top 10 holding concentration
- max industry weight
- industry count
- effective number of holdings
- Herfindahl index
- risk downgraded exposure
- excluded universe exposure
- unclassified industry exposure
- low liquidity exposure
- high risk exposure

Diagnostic flags are informational only:

- `concentrated_top5`
- `concentrated_industry`
- `contains_risk_downgraded`
- `contains_excluded_universe`
- `low_liquidity_cluster`
- `unclassified_industry_high`

These flags are not buy/sell signals, not order instructions, and not live trading readiness claims.
