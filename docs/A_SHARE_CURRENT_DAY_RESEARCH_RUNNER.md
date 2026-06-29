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

## v0.8.2 Owner Dashboard Consumer

v0.8.2 consumes the v0.8.1 current-day run package and builds an owner-facing monitoring dashboard from existing artifacts only.

It reads the current-day audit, data refresh audit, workflow audit, briefing, tracking, benchmark, performance, and attribution outputs, then writes dashboard cards, reports, source trace, boundary, manifest, summary, and an owner dashboard audit.

The dashboard does not refresh data, rerun workflow, call old `run-daily`, execute official forward dry-run day2, connect broker, read real account data, place orders, generate buy/sell signals, generate order previews, or turn research output into trade instructions.

## v0.8.3 Owner Monitoring Consumer

v0.8.3 consumes the v0.8.2 owner dashboard and v0.8.1 current-day run audit trail to build local alert and run-history monitoring. It does not invoke the current-day runner, does not rerun workflow, does not refresh data, and does not send external notifications by default.

Alerts are system-health prompts only. They are not trading instructions, broker status, real-account state, or order plans.

## v0.8.7 Gated build_from_existing_data Dry-Run

v0.8.7 runs the first preflight-gated current-day `build_from_existing_data` dry-run after the v0.8.0-v0.8.6 data, current-day, ops center, and ops history audits pass.

The gated path uses:

```bash
python -m trading_core.cli build-and-audit-a-share-gated-build-from-existing-data --as-of-date 2026-06-26 --mode run_gated_build_from_existing_data
```

It does not refresh public network data, does not run `full_research_run`, does not call old `run-daily`, does not execute official forward dry-run day2, does not connect broker, does not place orders, and does not treat build output as trade instruction.
