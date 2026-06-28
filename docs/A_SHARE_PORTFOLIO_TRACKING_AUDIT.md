# A-Share Portfolio Tracking Audit

`audit-a-share-virtual-portfolio-tracking` validates v0.7.8 tracking artifacts and safety boundaries.

## Checks

- tracking config exists
- tracking manifest exists
- long/mid/short paper ledgers exist
- long/mid/short holdings snapshots exist
- NAV, performance, exposure, benchmark, and source trace snapshots exist
- symbols match v0.7.6 virtual portfolios
- initial virtual capital is recorded
- weight sums are approximately 1.0
- NAV equals cash plus holdings market value
- no duplicate holdings
- no risk-downgraded or excluded-universe symbols are introduced
- no real-account fields are present
- no buy/sell signal, order preview, broker order, real order, or main ledger artifacts are generated
- no positive profit guarantee or live-trading readiness wording is present

## Current Audit Result

For `as_of_date=2026-06-26`:

- overall_passed=true
- blocking_reasons=[]
- warnings=1
- long holdings / ledger records: 30 / 30
- mid holdings / ledger records: 30 / 30
- short holdings / ledger records: 20 / 20
- long/mid/short NAV: 1000000.0 / 1000000.0 / 1000000.0
- long/mid/short weight sums: 1.0 / 1.0 / 1.0

## Boundary

Passing this audit does not authorize real trading. It only confirms that v0.7.8 virtual tracking artifacts are internally consistent and remain inside the research-only boundary.

Recommended next version after a passing audit:

```text
v0.7.10-a-share-benchmark-data-and-performance-comparison
```
