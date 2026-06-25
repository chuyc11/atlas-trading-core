# Virtual Execution Model

The v0.5.9 virtual execution model integrates calendar, T+1, tradability, lot, cost, and accounting rules for isolated virtual execution tests.

This is not broker integration and not live trading readiness.

v0.6.0 baseline strategy replay uses this model for isolated historical replay only. Baseline strategy pack is research-only and does not start forward dry-run.

## Model

- Calendar: SSE / SZSE / HKEX with explicit holidays and weekend handling.
- Timeline: T-day close signal is eligible no earlier than the next market trading day.
- Tradability: suspended, missing price, blocked limit side, ST, new listing, delisting risk, and unknown status do not silently fill.
- Quantity: A-share / ETF buy orders must satisfy the 100-share board lot; sell odd lots are allowed when holdings and available shares exist.
- Availability: T-day buys become available on T+1.
- Costs: commission, minimum commission, stamp duty, and slippage enter trade records and cash accounting.
- Ledger: rejected orders require reject reason; filled trades require fill price and cost fields.
- Isolation: smoke ledgers are written under `data/replays/global_briefing/execution_aware_smoke/`.
- Strategy replay isolation: v0.6.0 baseline strategy ledgers are written under `data/replays/strategies/`.

## Boundary

- isolated virtual execution only
- run-daily not called
- forward dry-run not started
- main ledger not written
- not forward validation
- not strategy effectiveness proof
- not live trading readiness
