# A-Share Execution Cost Contract

## Scope
This contract defines fee, tax, slippage, and PIT-safe fill price rules.
v0.5.9 hardens virtual execution rules but does not start forward dry-run.

## Defaults
- commission_bps: 2.9999999999999996
- minimum_commission: 5.0
- stamp_duty_bps_sell: 5.0
- slippage_bps: 10

## Boundary
- execution cost contract only
- run-daily not called
- forward dry-run not started
- main ledger not written
