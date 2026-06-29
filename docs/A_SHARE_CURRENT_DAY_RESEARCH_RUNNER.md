# A-Share Current-Day Research Runner

v0.8.1 adds a current-day research workflow runner for A-share research.

The runner requires the v0.8.0 daily data refresh audit to pass before it runs the A-share daily research workflow. Release validation uses:

```bash
python -m trading_core.cli run-and-audit-a-share-current-day-research --as-of-date 2026-06-26 --mode run_research_from_existing_refresh --workflow-mode validate_existing_artifacts
```

The runner writes config, readiness, data-refresh link, workflow plan, workflow execution, stage manifest, artifact index, warning summary, source trace, boundary check, run manifest, owner summary, and audit artifacts.

Boundary:

- v0.8.1 does not generate buy/sell signals
- v0.8.1 does not generate order previews
- v0.8.1 does not place orders
- v0.8.1 does not connect broker
- v0.8.1 does not read real account data
- v0.8.1 does not call old run-daily
- v0.8.1 does not execute official forward dry-run day2
- v0.8.1 does not treat research output as trade instruction

v0.8.2 should add owner-facing dashboard and monitoring.

