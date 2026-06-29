# A Share Safe Action Checklist

v0.8.4 converts remediation runbook entries into owner-facing checklist items.

Allowed action types include:

- `inspect_artifact`
- `verify_audit`
- `check_data_freshness`
- `check_provider_status`
- `rerun_safe_data_validation`
- `rerun_safe_current_day_research_validation`
- `rerun_safe_dashboard_build`
- `rerun_safe_monitoring_build`
- `wait_for_more_history`
- `document_known_warning`
- `escalate_to_developer`

Forbidden action types include broker connection, real account reads, order placement, account rebalancing, stock buying, stock selling, and live trading enablement.
