# Execution Aware Replay Smoke

## Scope
This smoke connects virtual execution rules to an isolated replay sample.
v0.5.9 hardens virtual execution rules but does not start forward dry-run.

## Scenarios
- normal_buy: filled None
- lot_reject: rejected buy_quantity_not_board_lot
- suspended_reject: rejected suspended_order_rejected
- limit_reject: rejected limit_up_buy_rejected
- cash_reject: rejected insufficient_cash_rejected
- same_day_available_reject: rejected sell_exceeds_available_shares
- normal_sell: filled None

## Boundary
- execution-aware replay smoke only
- run-daily not called
- forward dry-run not started
- main ledger not written
