"""Data freshness, schema, and coverage remediation guides."""

from trading_core.equity_owner_remediation.guide_common import build_guide


def build_data_freshness_remediation_guide(as_of_date: str) -> dict:
    return build_guide(
        "A-SHARE-DATA-FRESHNESS-REMEDIATION-GUIDE",
        as_of_date,
        ["freshness_issue"],
        ["Open dataset_freshness_validation.json.", "Check the requested date and resolved data date.", "Review data_gap_report.json for missing coverage."],
        ["data/equity_data_refresh/daily/{as_of_date}/dataset_freshness_validation.json", "data/equity_data_refresh/daily/{as_of_date}/data_gap_report.json"],
        ["python -m trading_core.cli build-and-audit-a-share-daily-data-refresh --as-of-date {as_of_date} --mode validate_existing_data"],
    )


def build_schema_coverage_remediation_guide(as_of_date: str) -> dict:
    return build_guide(
        "A-SHARE-SCHEMA-COVERAGE-REMEDIATION-GUIDE",
        as_of_date,
        ["schema_issue", "coverage_issue"],
        ["Open dataset_schema_validation.json.", "Open dataset_coverage_summary.json.", "Classify known nullable fields separately from blocking schema failures."],
        [
            "data/equity_data_refresh/daily/{as_of_date}/dataset_schema_validation.json",
            "data/equity_data_refresh/daily/{as_of_date}/dataset_coverage_summary.json",
        ],
        ["python -m trading_core.cli build-and-audit-a-share-daily-data-refresh --as-of-date {as_of_date} --mode validate_existing_data"],
    )
