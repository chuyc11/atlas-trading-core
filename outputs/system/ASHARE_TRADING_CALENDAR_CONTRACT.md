# A-Share Trading Calendar Contract

## Scope
This contract defines trading calendar behavior for SSE, SZSE, and HKEX.
v0.5.9 hardens virtual execution rules but does not start forward dry-run.

## Markets
SSE, SZSE, HKEX

## Boundary
- calendar contract only
- run-daily not called
- forward dry-run not started
- main ledger not written
