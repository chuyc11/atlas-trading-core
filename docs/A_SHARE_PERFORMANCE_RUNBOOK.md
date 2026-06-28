# A-Share Performance Runbook

## Default Current Snapshot

```powershell
python -m trading_core.cli build-and-audit-a-share-multi-day-performance --as-of-date 2026-06-26
```

Expected 2026-06-26 result:

- `overall_passed=true`
- `blocking_reasons=[]`
- long/mid/short observation count is 1
- `sufficient_history=false`
- `insufficient_history=true`
- `first_day_initialization=true`
- `performance_not_yet_observed=true`

## Append Existing Tracking

```powershell
python -m trading_core.cli build-and-audit-a-share-multi-day-performance --as-of-date 2026-06-26 --mode append_from_existing_tracking
```

Append mode is append-only, deduplicates by date, and allows idempotent identical appends. It does not rewrite prior dates.

## Rebuild From Virtual Snapshots

```powershell
python -m trading_core.cli build-and-audit-a-share-multi-day-performance --as-of-date 2026-06-26 --mode rebuild_virtual_performance_series --allow-rebuild
```

Use rebuild mode only for research reconstruction from existing virtual tracking snapshots. Do not label reconstructed history as realized forward performance.

## Safety

Do not connect a broker, do not place orders, do not generate buy/sell signals, do not generate order previews, do not call old `run-daily`, do not execute official forward dry-run day2, and do not fabricate multi-day portfolio history.
