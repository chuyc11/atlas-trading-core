"""Workflow remediation guide."""

from trading_core.equity_owner_remediation.guide_common import build_guide


def build_workflow_remediation_guide(as_of_date: str) -> dict:
    return build_guide(
        "A-SHARE-WORKFLOW-REMEDIATION-GUIDE",
        as_of_date,
        ["workflow_issue", "documentation_issue", "boundary_issue"],
        ["Open current_day_run_manifest.json.", "Open current-day audit JSON.", "Confirm source trace and boundary are clean before any validation rerun."],
        [
            "data/equity_current_day_runs/daily/{as_of_date}/current_day_run_manifest.json",
            "data/equity_data_quality/a_share_current_day_research_run_audit.json",
        ],
        [
            "python -m trading_core.cli run-and-audit-a-share-current-day-research --as-of-date {as_of_date} --mode run_research_from_existing_refresh --workflow-mode validate_existing_artifacts"
        ],
    )
