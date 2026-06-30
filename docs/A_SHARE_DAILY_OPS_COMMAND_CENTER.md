# A Share Daily Ops Command Center

## v0.8.6 downstream history baseline

The v0.8.6 ops history baseline reads the v0.8.5 daily ops command center artifacts and appends the current ops run into `data/equity_ops_history/history/ops_run_history_index.json`.

Use:

```bash
python -m trading_core.cli build-and-audit-a-share-ops-history-baseline --as-of-date 2026-06-26 --mode build_trend_baselines
```

The first release baseline has one real observation, so trend analysis is intentionally unavailable and `baseline_status=insufficient_history`. The baseline is research-only and does not generate orders, broker activity, or buy/sell instructions.

## v0.8.7 gated current-day build consumer

v0.8.7 consumes the v0.8.5 ops center and v0.8.6 ops history audit trail as preflight evidence before running `build_from_existing_data`. The preflight gate requires ops health score >= 60, zero blocking issues, clean history boundaries, and passed data/current-day/ops audits.

v0.8.5 adds a daily ops command center for the A-share research system.

It aggregates existing data refresh, current-day research, owner dashboard, owner monitoring, and owner remediation artifacts into one owner-facing operations control plane.

Boundary:

- v0.8.5 aggregates existing ops artifacts by default
- v0.8.5 does not refresh data by default
- v0.8.5 does not rerun current-day research by default
- v0.8.5 does not execute remediation actions
- v0.8.5 does not generate buy/sell signals
- v0.8.5 does not place orders
- v0.8.5 does not connect broker
- v0.8.5 does not call old run-daily
- v0.8.5 does not execute official forward dry-run day2
- v0.8.5 does not treat ops output as trade instruction
- v0.8.6 should deepen run history and trend baselines

## v0.8.10 build-output ops refresh

v0.8.10 refreshes ops center and ops history outputs from the v0.8.9 build-output dashboard. It carries build-output monitoring, remediation, health score, module status, issue summary, action summary, owner next steps, and source trace into a separate refresh package under `data/equity_build_output_ops_refresh/` and `outputs/equity_build_output_ops_refresh/`.

The refresh uses `build_from_existing_data` as source workflow mode and does not rerun the build workflow, refresh public network data, run `full_research_run`, execute remediation actions, send external notifications, generate buy/sell signals, place orders, connect broker, call old run-daily, execute official forward dry-run day2, or treat ops refresh as trade instruction. v0.8.11 should build a daily owner decision pack and runbook from this refreshed build-output ops layer.
