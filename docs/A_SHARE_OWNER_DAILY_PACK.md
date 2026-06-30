# A-Share Owner Daily Pack

v0.8.11 adds an owner-facing daily runbook and owner operations decision pack for the A-share build-output flow.

Primary source:

- `data/equity_build_output_ops_refresh/daily/YYYY-MM-DD/`
- `data/equity_data_quality/a_share_build_output_ops_refresh_audit.json`

Supporting sources:

- v0.8.9 build-output owner dashboard
- v0.8.8 build repeatability
- v0.8.7 gated build_from_existing_data
- v0.8.0 daily data refresh

Outputs:

- `data/equity_owner_daily_pack/daily/YYYY-MM-DD/`
- `outputs/equity_owner_daily_pack/daily/YYYY-MM-DD/`
- `data/equity_data_quality/a_share_owner_daily_pack_audit.json`
- `outputs/audit/A_SHARE_OWNER_DAILY_PACK_AUDIT.md`

Boundary:

- not an investment decision pack
- not a trade instruction
- does not rerun `build_from_existing_data`
- does not refresh public network data
- does not run `full_research_run`
- does not execute remediation actions
- does not send external notifications
- does not generate buy/sell signals
- does not generate order previews
- does not place orders
- does not connect broker
- does not call old run-daily
- does not execute official forward dry-run day2
- does not claim profit or live trading readiness

Recommended next: `v0.8.12-a-share-build-output-daily-pack-history-and-owner-readiness-trends`.
