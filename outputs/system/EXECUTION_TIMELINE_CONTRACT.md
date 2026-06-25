# Execution Timeline Contract

## Scope
This contract defines T-day close signal and T+1 execution semantics.
v0.5.9 hardens virtual execution rules but does not start forward dry-run.

## Rules
- same_day_execution_for_close_signal_allowed: False
- execution_date_min_rule: next_trading_day
- future_price_allowed: False
- generated_at_must_be_after_market_close: True
- market_calendar_independent: True

## Boundary
- timeline contract only
- run-daily not called
- forward dry-run not started
- main ledger not written
