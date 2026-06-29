# A Share Ops Center Runbook

Use the ops command center as a daily owner-facing operations control plane.

Standard release commands:

```bash
python -m trading_core.cli validate-a-share-daily-ops-inputs --as-of-date 2026-06-26
python -m trading_core.cli build-a-share-daily-ops-center --as-of-date 2026-06-26 --mode aggregate_existing_ops_artifacts
python -m trading_core.cli audit-a-share-daily-ops-center --as-of-date 2026-06-26
```

This runbook is not a trading system. It does not refresh data by default, does not rerun current-day research by default, does not execute remediation actions, does not generate buy/sell signals, does not place orders, and does not connect broker.
