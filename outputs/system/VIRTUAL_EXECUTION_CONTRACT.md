# Virtual Execution Contract

## Scope
This contract integrates A-share execution hardening rules for isolated virtual execution.
v0.5.9 hardens virtual execution rules but does not start forward dry-run.

## Integrated Rules
- calendar
- T+1
- tradability
- lot rules
- cash/position/available shares
- fees/taxes/slippage
- reject reason
- fill reason
- isolated output path
- protected path guard

## Boundary
- virtual execution contract only
- run-daily not called
- forward dry-run not started
- main ledger not written
