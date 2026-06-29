# A-Share Build Output Dashboard Runbook

Use:

```bash
python -m trading_core.cli validate-a-share-build-output-owner-dashboard-inputs --as-of-date 2026-06-26
python -m trading_core.cli build-a-share-build-output-owner-dashboard --as-of-date 2026-06-26 --mode build_owner_dashboard_from_build_output
python -m trading_core.cli audit-a-share-build-output-owner-dashboard --as-of-date 2026-06-26
```

Combined:

```bash
python -m trading_core.cli build-and-audit-a-share-build-output-owner-dashboard --as-of-date 2026-06-26 --mode build_owner_dashboard_from_build_output
```

Do not use this command to rerun build, refresh public data, run `full_research_run`, connect broker, create orders, or treat dashboard output as a trade instruction.

