# A-Share Owner Alerting Schema

`alert_rule_config.json` contains local rule definitions. Required rules:

- `BLOCKING_AUDIT_FAILURE`
- `DATA_REFRESH_FAILURE`
- `CURRENT_DAY_RUN_FAILURE`
- `OWNER_DASHBOARD_FAILURE`
- `BOUNDARY_VIOLATION`
- `BROKER_OR_ORDER_SURFACE_DETECTED`
- `OLD_RUN_DAILY_DETECTED`
- `DAY2_EXECUTED_DETECTED`
- `FORBIDDEN_WORDING_DETECTED`
- `WARNING_COUNT_INCREASE`
- `REPEATED_KNOWN_WARNING`
- `PROVIDER_HEALTH_DEGRADED`
- `DATA_FRESHNESS_DEGRADED`
- `MISSING_REQUIRED_ARTIFACT`
- `TREND_ANALYSIS_INSUFFICIENT_HISTORY`

Each rule records:

- `rule_id`
- `severity`
- `enabled`
- `source_artifacts`
- `condition_description`
- `owner_message_template`
- `blocking`
- `requires_minimum_history`

Alert events are written to `alert_event_log.json` and `alert_history_index.json`. Events include `alert_id`, `rule_id`, `severity`, `status`, source, message, owner action, blocking flag, known-non-blocking flag, creation time, and `external_notification_sent`.

Release default:

- `send_external_notifications=false`
- `notification_channels_enabled=[]`
- `external_notification_sent=false` for every event

Alerts are monitoring signals only. They are not trading instructions.
