"""Dashboard remediation guide."""

from trading_core.equity_owner_remediation.guide_common import build_guide


def build_dashboard_remediation_guide(as_of_date: str) -> dict:
    return build_guide(
        "A-SHARE-DASHBOARD-REMEDIATION-GUIDE",
        as_of_date,
        ["dashboard_issue"],
        ["Open owner dashboard audit.", "Open dashboard_summary.json.", "Confirm required dashboard cards are present and boundary is clean."],
        ["data/equity_data_quality/a_share_owner_dashboard_audit.json", "data/equity_owner_dashboard/daily/{as_of_date}/dashboard_summary.json"],
        ["python -m trading_core.cli build-and-audit-a-share-owner-dashboard --as-of-date {as_of_date} --mode build_dashboard_from_existing_run"],
    )
