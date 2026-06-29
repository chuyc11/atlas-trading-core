# A-Share Owner Dashboard Schema

Required JSON artifacts under `data/equity_owner_dashboard/daily/YYYY-MM-DD/`:

- `dashboard_config.json`
- `dashboard_input_availability.json`
- `executive_status_card.json`
- `data_freshness_card.json`
- `provider_health_card.json`
- `workflow_status_card.json`
- `research_output_card.json`
- `candidate_summary_card.json`
- `portfolio_summary_card.json`
- `benchmark_summary_card.json`
- `performance_summary_card.json`
- `attribution_summary_card.json`
- `warning_and_blocker_card.json`
- `artifact_navigation_index.json`
- `dashboard_source_trace.json`
- `dashboard_boundary_check.json`
- `dashboard_manifest.json`
- `dashboard_summary.json`

Required Markdown reports under `outputs/equity_owner_dashboard/daily/YYYY-MM-DD/`:

- `A_SHARE_OWNER_DASHBOARD.md`
- `A_SHARE_OWNER_DASHBOARD_COMPACT.md`
- `A_SHARE_OWNER_WARNING_AND_BLOCKER_SUMMARY.md`
- `A_SHARE_OWNER_ARTIFACT_NAVIGATION.md`
- `A_SHARE_OWNER_DASHBOARD_SOURCE_TRACE.md`

Audit artifacts:

- `data/equity_data_quality/a_share_owner_dashboard_audit.json`
- `outputs/audit/A_SHARE_OWNER_DASHBOARD_AUDIT.md`

The dashboard schema is intentionally card-based. Each card has `card_id`, `target_version`, `as_of_date`, status fields, warning fields, and source-derived evidence. Cards may summarize existing upstream artifacts but must not create trading instructions or new market events.
