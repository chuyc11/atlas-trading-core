# A-Share Ops Trend Baseline Runbook

Run the full local workflow:

```bash
python -m trading_core.cli validate-a-share-ops-history-inputs --as-of-date 2026-06-26
python -m trading_core.cli build-a-share-ops-history-baseline --as-of-date 2026-06-26 --mode build_trend_baselines
python -m trading_core.cli audit-a-share-ops-history-baseline --as-of-date 2026-06-26
```

The combined command is:

```bash
python -m trading_core.cli build-and-audit-a-share-ops-history-baseline --as-of-date 2026-06-26 --mode build_trend_baselines
```

Interpretation:

- one to four real observations: keep `baseline_status=insufficient_history`
- five or more real observations: trend baseline calculations can become available
- synthetic history is not used by the default workflow
- trend baselines are operational diagnostics only

