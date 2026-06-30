# A-Share Build Output Owner Dashboard

v0.8.9 refreshes the owner dashboard from stable `build_from_existing_data` outputs.

It reads v0.8.8 repeatability evidence, v0.8.7 gated build evidence, v0.8.2 validate-source dashboard evidence, and v0.8.0 data refresh evidence. It then writes a separate build-output dashboard under:

- `data/equity_build_output_dashboard/daily/YYYY-MM-DD/`
- `outputs/equity_build_output_dashboard/daily/YYYY-MM-DD/`
- `data/equity_data_quality/a_share_build_output_owner_dashboard_audit.json`
- `outputs/audit/A_SHARE_BUILD_OUTPUT_OWNER_DASHBOARD_AUDIT.md`

Boundary:

- prefers build output over validate-source artifacts
- requires repeatability audit passed
- requires `business_output_drift_count=0`
- distinguishes pre-existing protected paths from modified protected paths
- does not rerun `build_from_existing_data`
- does not refresh public network data
- does not run `full_research_run`
- does not call old run-daily
- does not connect broker
- does not place orders
- dashboard output is not a trade instruction

Recommended next: `v0.8.10-a-share-build-output-monitoring-remediation-and-ops-refresh`.

## v0.8.10 downstream consumer

v0.8.10 consumes this build-output dashboard as the primary owner-facing source for monitoring, remediation, ops center, and ops history refreshes.

It does not rerun `build_from_existing_data`, does not refresh public network data, does not run `full_research_run`, does not execute remediation actions, does not send external notifications, does not connect broker, does not place orders, and does not treat ops refresh as trade instruction.

## v0.8.11 downstream consumer

v0.8.11 uses the v0.8.10 ops refresh, which itself consumes this dashboard, to generate an owner daily runbook and owner operations decision pack.

The daily pack remains operations-only and research-only. It does not rerun `build_from_existing_data`, refresh public network data, run `full_research_run`, execute remediation actions, send external notifications, generate buy/sell signals, generate order previews, connect broker, place orders, call old run-daily, execute official forward dry-run day2, or treat the pack as a trade instruction.
