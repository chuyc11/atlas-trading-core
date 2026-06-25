# A-Share Execution Rules

v0.5.9 hardens A-share / ETF virtual execution rules.

v0.5.9 hardens virtual execution rules but does not start forward dry-run. `run-daily` is not called. The main orders/trades/portfolio/accounts ledger is not written.

v0.6.0 baseline strategy replay reuses these virtual execution rules only in isolated strategy replay paths under `data/replays/strategies/`. It does not start forward dry-run and does not write the main ledger.

## Coverage

- Trading calendar supports SSE / SZSE / HKEX.
- T-day close signal cannot execute same day.
- T+1 execution semantics are explicit.
- T+1 available shares are enforced.
- Suspension, missing price, limit up, and limit down are handled fail-closed.
- ST and new listing handling are defined.
- Board lot and odd lot rules are defined.
- Fee, tax, and slippage model is defined.
- Cash, position, and available shares accounting invariants are checked.
- Isolated ledger invariant audit is required.
- Execution-aware replay smoke runs only in isolated mode.

## Commands

```powershell
python -m trading_core.cli ashare-execution-gap-plan
python -m trading_core.cli ashare-trading-calendar-audit
python -m trading_core.cli execution-timeline-contract
python -m trading_core.cli ashare-price-status-contract
python -m trading_core.cli ashare-lot-and-position-contract
python -m trading_core.cli ashare-execution-cost-contract
python -m trading_core.cli virtual-execution-contract
python -m trading_core.cli audit-isolated-ledger-invariants
python -m trading_core.cli execution-aware-replay-smoke
python -m trading_core.cli reclassify-day1-blockers-after-execution-hardening
python -m trading_core.cli audit-ashare-execution-rules
```

## Boundary

- run-daily not called
- forward dry-run not started
- main ledger not written
- not strategy effectiveness proof
- not live trading readiness
- no broker connected
- ML shadow not used as authorization
- LLM not used for trading decision
- RL not used
- promotion not triggered
