# A-Share Multi-Day Performance Tracking

`v0.7.11-a-share-multi-day-portfolio-performance-tracking` adds appendable virtual portfolio performance tracking for the A-share long/mid/short virtual portfolios.

## Scope

The stage reads existing v0.7.8 tracking artifacts, v0.7.9 workflow artifacts, v0.7.10 benchmark artifacts, and local price-panel availability. It writes:

- `data/equity_performance/daily/YYYY-MM-DD/`
- `outputs/equity_performance/daily/YYYY-MM-DD/`
- `data/equity_data_quality/a_share_multi_day_performance_audit.json`
- `outputs/audit/A_SHARE_MULTI_DAY_PERFORMANCE_AUDIT.md`

## Commands

```powershell
python -m trading_core.cli build-a-share-multi-day-performance --as-of-date 2026-06-26
python -m trading_core.cli audit-a-share-multi-day-performance --as-of-date 2026-06-26
python -m trading_core.cli build-and-audit-a-share-multi-day-performance --as-of-date 2026-06-26
```

Modes:

- `current_snapshot`
- `append_from_existing_tracking`
- `rebuild_virtual_performance_series`

`rebuild_virtual_performance_series` requires `--allow-rebuild`. Historical reconstruction must remain labeled separately.

## Boundary

v0.7.11 does not create buy/sell signals, does not place orders, does not connect a broker, does not call old `run-daily`, does not execute official forward dry-run day2, does not fabricate portfolio history, and does not claim live trading readiness.

v0.7.12 adds attribution and risk diagnostics through `data/equity_attribution/daily/YYYY-MM-DD/` and `outputs/equity_attribution/daily/YYYY-MM-DD/`. It distinguishes structural diagnostics from realized performance attribution, keeps limited history explicit, and does not create buy/sell signals, place orders, connect a broker, call old `run-daily`, execute official forward dry-run day2, or fabricate performance.
