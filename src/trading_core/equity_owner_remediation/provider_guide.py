"""Provider remediation guide."""

from trading_core.equity_owner_remediation.guide_common import build_guide


def build_provider_remediation_guide(as_of_date: str) -> dict:
    return build_guide(
        "A-SHARE-PROVIDER-REMEDIATION-GUIDE",
        as_of_date,
        ["provider_issue"],
        ["Open provider_health_check.json.", "Open provider_fallback_report.json.", "Confirm whether fallback was expected and documented."],
        ["data/equity_data_refresh/daily/{as_of_date}/provider_health_check.json", "data/equity_data_refresh/daily/{as_of_date}/provider_fallback_report.json"],
        ["python -m trading_core.cli build-and-audit-a-share-daily-data-refresh --as-of-date {as_of_date} --mode validate_existing_data"],
    )
