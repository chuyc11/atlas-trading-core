# A-Share Ops Run History Baseline

v0.8.6 stores A-share daily ops command center outcomes as append-only history and builds trend baseline artifacts when enough real observations exist.

Release defaults:

- `as_of_date=2026-06-26`
- `history_window_days=90`
- `minimum_required_observations=5`
- `baseline_window_observations=20`
- `allow_synthetic_history=false`
- `allow_rebuild_history=false`

Current release state:

- `run_history_observation_count=1`
- `trend_analysis_available=false`
- `baseline_status=insufficient_history`

The history baseline is operational evidence only. It does not generate order previews, broker actions, or buy/sell instructions.

## v0.8.7 Consumer

v0.8.7 reads the ops history audit, trend sufficiency, health baseline, boundary history, and manifest as a preflight dependency for the first gated `build_from_existing_data` dry-run. The history remains operational evidence only and is not used as a trade signal.
