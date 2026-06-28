# A-Share Performance Audit

`audit-a-share-multi-day-performance` validates the v0.7.11 performance package.

## Checks

The audit verifies:

- required artifacts exist
- target version matches v0.7.11
- long/mid/short portfolio ids are present
- benchmark ids are present
- observation counts match the generated series
- first-day initialization is flagged when only one observation exists
- insufficient history is flagged without blocking release
- `performance_not_yet_observed=true` is preserved
- daily return, cumulative return, drawdown, and holding MTM math pass
- benchmark-relative metrics do not fabricate portfolio history
- source trace is complete and hashes match where available
- future data is not used
- historical performance is not fabricated
- boundary fields remain clean
- old `run-daily` was not called
- official forward dry-run day2 was not executed
- broker connection, real orders, buy/sell signals, and order previews remain false

## Release Gate

The release gate is `overall_passed=true` and `blocking_reasons=[]`. For the 2026-06-26 release, limited history is expected as a warning because only one portfolio observation exists.
