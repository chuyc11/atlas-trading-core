# A-Share Owner Monitoring

v0.8.3 adds owner alerting and run history monitoring for the A-share research system.

It reads existing artifacts only:

- v0.8.2 owner dashboard artifacts and audit
- v0.8.1 current-day run artifacts and audit
- v0.8.0 data refresh artifacts and audit
- existing warning, blocking, provider, workflow, and dashboard status cards

It writes local monitoring artifacts under:

- `data/equity_owner_monitoring/daily/YYYY-MM-DD/`
- `data/equity_owner_monitoring/history/`
- `outputs/equity_owner_monitoring/daily/YYYY-MM-DD/`
- `data/equity_data_quality/a_share_owner_monitoring_audit.json`
- `outputs/audit/A_SHARE_OWNER_MONITORING_AUDIT.md`

Release commands:

```powershell
python -m trading_core.cli validate-a-share-owner-monitoring-inputs --as-of-date 2026-06-26
python -m trading_core.cli build-a-share-owner-monitoring --as-of-date 2026-06-26 --mode build_monitoring_dashboard
python -m trading_core.cli audit-a-share-owner-monitoring --as-of-date 2026-06-26
python -m trading_core.cli build-and-audit-a-share-owner-monitoring --as-of-date 2026-06-26 --mode build_monitoring_dashboard
```

Boundary:

- local alert artifacts only
- no external notifications by default
- no data refresh
- no research workflow rerun
- no old `run-daily`
- no official forward dry-run day2
- no broker connection
- no real account reads
- no real orders
- no order preview
- no buy/sell signals
- no alert-as-trade-instruction

The next planned layer is `v0.8.4-a-share-owner-remediation-runbook-and-action-checklist`.
# v0.8.4 follow-up

v0.8.4 consumes owner monitoring artifacts and turns warnings, blockers, alerts, and insufficient-history states into owner remediation runbooks and safe action checklists.

The v0.8.4 layer does not execute remediation actions, does not refresh data, does not rerun research workflow, does not generate buy/sell signals, does not place orders, does not connect broker, does not call old run-daily, does not execute official forward dry-run day2, and does not treat remediation as trade instruction.

Recommended next version after v0.8.4 is `v0.8.5-a-share-daily-ops-command-center`.
