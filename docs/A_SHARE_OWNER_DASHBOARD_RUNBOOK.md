# A-Share Owner Dashboard Runbook

Prerequisite:

- A current-day research run already exists for the target `as_of_date`.
- The data refresh, workflow, briefing, tracking, benchmark, performance, and attribution artifacts for the same resolved date are available.

Run:

```powershell
python -m trading_core.cli validate-a-share-owner-dashboard-inputs --as-of-date 2026-06-26
python -m trading_core.cli build-a-share-owner-dashboard --as-of-date 2026-06-26 --mode build_dashboard_from_existing_run
python -m trading_core.cli audit-a-share-owner-dashboard --as-of-date 2026-06-26
```

One-command build and audit:

```powershell
python -m trading_core.cli build-and-audit-a-share-owner-dashboard --as-of-date 2026-06-26 --mode build_dashboard_from_existing_run
```

Options:

- `--mode`: one of `validate_existing_dashboard_inputs`, `build_dashboard_from_existing_run`, `audit_existing_dashboard`
- `--allow-date-mismatch`: permit resolved date to differ from requested date
- `--fail-on-missing-optional-card`: reserved strict mode for optional cards
- `--compact-only`: write only the compact report when building a non-release local view

Do not run this command to refresh data or rerun research. Use v0.8.0/v0.8.1 commands for those stages.
