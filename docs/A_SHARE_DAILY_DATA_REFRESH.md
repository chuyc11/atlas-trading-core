# A-Share Daily Data Refresh

v0.8.0 adds daily data refresh and provider hardening for A-share research data.

The release writes:

- data refresh config
- trading-day date resolution
- provider registry snapshot
- provider health check
- provider execution log
- dataset refresh plan and result
- schema, freshness, and coverage validation
- data gap report
- provider fallback report
- source trace, manifest, boundary check, summary, and audit

Release E2E uses `validate_existing_data`, which reads local research panels and does not call external network providers.

Boundary:

- v0.8.0 does not generate buy/sell signals
- v0.8.0 does not place orders
- v0.8.0 does not connect broker
- v0.8.0 does not call old run-daily
- v0.8.0 does not execute official forward dry-run day2
- v0.8.0 validates data freshness and coverage
- v0.8.1 should use refreshed data to run current-day research workflow

## v0.8.1 Consumer

v0.8.1 consumes the data refresh audit as a required gate. If the audit fails or has blocking reasons, the current-day research workflow must not run. Passing data refresh is still not trading readiness; the current-day runner remains research-only and does not connect broker, place orders, generate buy/sell signals, generate order previews, call old run-daily, or execute official forward dry-run day2.
