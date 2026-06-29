# A-Share Owner Monitoring Runbook

Prerequisites:

- v0.8.2 owner dashboard audit exists and passed
- v0.8.1 current-day run audit exists and passed
- v0.8.0 data refresh audit exists and passed

Run input validation:

```powershell
python -m trading_core.cli validate-a-share-owner-monitoring-inputs --as-of-date 2026-06-26
```

Build monitoring:

```powershell
python -m trading_core.cli build-a-share-owner-monitoring --as-of-date 2026-06-26 --mode build_monitoring_dashboard
```

Audit monitoring:

```powershell
python -m trading_core.cli audit-a-share-owner-monitoring --as-of-date 2026-06-26
```

One-command path:

```powershell
python -m trading_core.cli build-and-audit-a-share-owner-monitoring --as-of-date 2026-06-26 --mode build_monitoring_dashboard
```

Options:

- `--history-window-days 30`
- `--minimum-history-observations 3`
- `--allow-rebuild-history`
- `--send-external-notifications`

In v0.8.3, `--send-external-notifications` records an unsupported request warning and still sends nothing.
