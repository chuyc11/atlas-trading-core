# A-Share Daily Workflow Orchestration

`v0.7.9-a-share-daily-workflow-orchestration` adds the orchestration layer for the existing A-share research chain.

It orchestrates:

- v0.7.2 tradable universe
- v0.7.3 multi-horizon features
- v0.7.4 long/mid/short scores
- v0.7.5 candidates
- v0.7.6 virtual portfolios
- v0.7.7 daily briefing
- v0.7.8 virtual portfolio tracking

Supported modes:

- `validate_existing_artifacts`
- `build_from_existing_data`
- `full_research_run`

Default date:

```text
2026-06-26
```

Commands:

```powershell
python -m trading_core.cli preflight-a-share-daily-workflow --as-of-date 2026-06-26
python -m trading_core.cli run-a-share-daily-research-workflow --as-of-date 2026-06-26 --mode validate_existing_artifacts
python -m trading_core.cli audit-a-share-daily-research-workflow --as-of-date 2026-06-26
python -m trading_core.cli run-and-audit-a-share-daily-research-workflow --as-of-date 2026-06-26 --mode validate_existing_artifacts
```

Outputs:

- `data/equity_workflows/daily/YYYY-MM-DD/workflow_config.json`
- `data/equity_workflows/daily/YYYY-MM-DD/workflow_preflight.json`
- `data/equity_workflows/daily/YYYY-MM-DD/workflow_stage_manifest.json`
- `data/equity_workflows/daily/YYYY-MM-DD/workflow_run_manifest.json`
- `data/equity_workflows/daily/YYYY-MM-DD/workflow_source_trace.json`
- `data/equity_workflows/daily/YYYY-MM-DD/workflow_boundary_check.json`
- `data/equity_workflows/daily/YYYY-MM-DD/workflow_summary.json`
- `outputs/equity_workflows/daily/YYYY-MM-DD/A_SHARE_DAILY_WORKFLOW_SUMMARY.md`
- `outputs/equity_workflows/daily/YYYY-MM-DD/A_SHARE_DAILY_WORKFLOW_STAGE_REPORT.md`
- `outputs/equity_workflows/daily/YYYY-MM-DD/A_SHARE_DAILY_WORKFLOW_SOURCE_TRACE.md`
- `data/equity_data_quality/a_share_daily_workflow_audit.json`
- `outputs/audit/A_SHARE_DAILY_WORKFLOW_AUDIT.md`

Boundary:

- workflow orchestration only
- no upstream business module rewrite
- no old `run-daily`
- no official forward dry-run day2
- no broker connection
- no real orders
- no buy/sell signals
- no order previews
- no model profit guarantee
- not live trading ready

Benchmark data and relative performance comparison are implemented by `v0.7.10-a-share-benchmark-data-and-performance-comparison`.
## v0.7.11 Downstream Performance Stage

v0.7.9 orchestrates the daily research workflow through tracking. v0.7.10 adds benchmark comparison. v0.7.11 adds downstream virtual performance tracking without changing the workflow runner or calling old `run-daily`.

The performance stage reads existing workflow, tracking, benchmark, and price artifacts. It writes performance artifacts only under `data/equity_performance/`, `outputs/equity_performance/`, and audit outputs. It does not execute official forward dry-run day2, connect a broker, place real orders, create buy/sell signals, generate order previews, or fabricate portfolio history.

## v0.8.0 Data Refresh Relationship

v0.8.0 validates daily research data freshness and provider health before a current-day workflow runner exists. It does not call this workflow automatically and does not run `run-a-share-daily-research-workflow` unless a later stage explicitly authorizes that behavior.

v0.8.1 should use the refreshed data to run the current-day research workflow.

## v0.8.1 Current-Day Runner Relationship

v0.8.1 wraps this workflow with a data-refresh gate. It first checks the v0.8.0 data refresh audit, then calls `run-and-audit-a-share-daily-research-workflow` for the resolved date. The wrapper writes current-day run manifest, warning summary, source trace, owner summary, and audit artifacts.

The wrapper does not call old `run-daily`, does not execute official forward dry-run day2, does not connect broker, does not read real account data, does not place real orders, and does not convert research output into trade instructions.
