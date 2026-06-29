# A-Share Owner Dashboard

v0.8.2 adds an owner-facing monitoring dashboard for an existing A-share current-day research run.

The dashboard reads existing artifacts only:

- v0.8.0 daily data refresh artifacts
- v0.8.1 current-day run artifacts
- v0.7.9 workflow artifacts
- v0.7.7 briefing artifacts
- v0.7.8 virtual portfolio tracking artifacts
- v0.7.10 benchmark artifacts
- v0.7.11 performance artifacts
- v0.7.12 attribution artifacts

Commands:

```powershell
python -m trading_core.cli validate-a-share-owner-dashboard-inputs --as-of-date 2026-06-26
python -m trading_core.cli build-a-share-owner-dashboard --as-of-date 2026-06-26 --mode build_dashboard_from_existing_run
python -m trading_core.cli audit-a-share-owner-dashboard --as-of-date 2026-06-26
python -m trading_core.cli build-and-audit-a-share-owner-dashboard --as-of-date 2026-06-26 --mode build_dashboard_from_existing_run
```

Outputs:

- `data/equity_owner_dashboard/daily/YYYY-MM-DD/*.json`
- `outputs/equity_owner_dashboard/daily/YYYY-MM-DD/*.md`
- `data/equity_data_quality/a_share_owner_dashboard_audit.json`
- `outputs/audit/A_SHARE_OWNER_DASHBOARD_AUDIT.md`

Boundary:

- dashboard only
- research only
- virtual only
- no data refresh trigger
- no workflow rerun
- no old `run-daily`
- no official forward dry-run day2
- no broker connection
- no real account data
- no real orders
- no order preview
- no buy/sell signals
- no dashboard-as-trade-instruction

The next planned layer is `v0.8.3-a-share-owner-alerting-and-run-history-monitoring`.

## v0.8.3 Monitoring Consumer

v0.8.3 reads the owner dashboard audit, dashboard cards, warning/blocker card, source trace, boundary, manifest, summary, and owner reports as monitoring inputs.

The monitoring layer adds local alert evaluation and append-only run history. It does not rebuild the dashboard, refresh data, rerun workflow, send external notifications by default, connect broker, place orders, or treat alerts as trade instructions.
