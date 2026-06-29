"""Monitoring remediation guide."""

from trading_core.equity_owner_remediation.guide_common import build_guide


def build_monitoring_remediation_guide(as_of_date: str) -> dict:
    return build_guide(
        "A-SHARE-MONITORING-REMEDIATION-GUIDE",
        as_of_date,
        ["monitoring_issue", "alert_issue", "insufficient_history_issue"],
        ["Open owner monitoring audit.", "Open alert_event_log.json.", "Check trend snapshots and run history observation count."],
        [
            "data/equity_data_quality/a_share_owner_monitoring_audit.json",
            "data/equity_owner_monitoring/daily/{as_of_date}/alert_event_log.json",
            "data/equity_owner_monitoring/daily/{as_of_date}/run_history_snapshot.json",
        ],
        ["python -m trading_core.cli build-and-audit-a-share-owner-monitoring --as-of-date {as_of_date} --mode build_monitoring_dashboard"],
    )
