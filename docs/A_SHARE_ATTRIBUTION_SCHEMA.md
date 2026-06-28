# A-Share Attribution Schema

Primary output directory:

- `data/equity_attribution/daily/YYYY-MM-DD/`
- `outputs/equity_attribution/daily/YYYY-MM-DD/`

Required JSON artifacts:

- `attribution_config.json`
- `attribution_data_availability.json`
- `holding_contribution_snapshot.json`
- `industry_contribution_snapshot.json`
- `candidate_source_contribution_snapshot.json`
- `score_bucket_contribution_snapshot.json`
- `risk_bucket_contribution_snapshot.json`
- `liquidity_bucket_contribution_snapshot.json`
- `benchmark_relative_attribution_snapshot.json`
- `portfolio_concentration_diagnostics.json`
- `risk_diagnostics_snapshot.json`
- `liquidity_diagnostics_snapshot.json`
- `industry_diagnostics_snapshot.json`
- `factor_exposure_snapshot.json`
- `attribution_limitations.json`
- `attribution_source_trace.json`
- `attribution_manifest.json`
- `attribution_boundary_check.json`
- `attribution_summary.json`

Required reports:

- `A_SHARE_ATTRIBUTION_SUMMARY.md`
- `HOLDING_AND_INDUSTRY_ATTRIBUTION.md`
- `SCORE_RISK_LIQUIDITY_DIAGNOSTICS.md`
- `BENCHMARK_RELATIVE_ATTRIBUTION.md`
- `ATTRIBUTION_LIMITATIONS.md`
- `ATTRIBUTION_SOURCE_TRACE.md`

The schema keeps realized performance attribution separate from structural exposure diagnostics. In limited-history mode, realized performance attribution fields remain unavailable or explicitly marked `insufficient_history`.
