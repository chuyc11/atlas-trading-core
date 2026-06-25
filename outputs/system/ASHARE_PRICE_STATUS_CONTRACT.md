# A-Share Price Status Contract

## Scope
This contract defines fail-closed tradability rules for A-share and ETF virtual execution.
v0.5.9 hardens virtual execution rules but does not start forward dry-run.

## Statuses
- tradable
- suspended
- missing_price
- limit_up
- limit_down
- st_flagged
- new_listing_restricted
- delisting_risk
- unknown_status

## Boundary
- price status contract only
- run-daily not called
- forward dry-run not started
- main ledger not written
