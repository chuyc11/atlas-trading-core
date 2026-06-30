# A Share Build Output Ops Refresh

v0.8.10 refreshes monitoring, remediation, ops center, and ops history from the v0.8.9 build-output dashboard.

It uses `build_from_existing_data` as source workflow mode and writes:

- `data/equity_build_output_ops_refresh/daily/YYYY-MM-DD/`
- `outputs/equity_build_output_ops_refresh/daily/YYYY-MM-DD/`
- `data/equity_data_quality/a_share_build_output_ops_refresh_audit.json`
- `outputs/audit/A_SHARE_BUILD_OUTPUT_OPS_REFRESH_AUDIT.md`

Boundary:

- does not rerun `build_from_existing_data`
- does not refresh public network data
- does not run `full_research_run`
- does not execute remediation actions
- does not send external notifications
- does not generate buy/sell signals
- does not generate order previews
- does not connect broker
- does not place orders
- does not call old run-daily
- does not execute official forward dry-run day2
- does not treat ops refresh as trade instruction

Recommended next: `v0.8.11-a-share-build-output-daily-runbook-and-owner-decision-pack`.

## v0.8.11 downstream consumer

v0.8.11 consumes this build-output ops refresh as the primary source for the owner daily runbook and owner operations decision pack.

The downstream daily pack reads the v0.8.10 monitoring/remediation/ops/history refresh artifacts and supporting v0.8.9-v0.8.0 evidence. It does not rerun `build_from_existing_data`, does not refresh public network data, does not run `full_research_run`, does not execute remediation actions, does not send external notifications, does not connect broker, does not place orders, does not generate buy/sell signals or order previews, and does not treat the owner decision pack as an investment or trading decision.
