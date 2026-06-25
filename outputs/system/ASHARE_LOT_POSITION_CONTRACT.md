# A-Share Lot Position Contract

## Scope
This contract defines board lot, odd lot, cash, position, and available-share rules.
v0.5.9 hardens virtual execution rules but does not start forward dry-run.

## Rules
- buy_must_satisfy_board_lot: True
- sell_odd_lot_allowed_when_position_exists: True
- t_day_buy_available_same_day: False
- negative_cash_allowed: False
- negative_position_allowed: False

## Boundary
- lot position contract only
- run-daily not called
- forward dry-run not started
- main ledger not written
