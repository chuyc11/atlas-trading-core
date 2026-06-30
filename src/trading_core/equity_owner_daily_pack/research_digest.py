"""Research output digest for owner daily pack."""

from __future__ import annotations

from trading_core.equity_owner_daily_pack.daily_pack_config import TARGET_VERSION
from trading_core.equity_owner_daily_pack.input_availability import load_json
from trading_core.storage.file_paths import ProjectPaths


def build_research_output_digest(*, paths: ProjectPaths, as_of_date: str) -> dict:
    summary = load_json(paths.data_dir / "equity_build_output_dashboard" / "daily" / as_of_date / "build_output_dashboard_summary.json")
    research = load_json(paths.data_dir / "equity_build_output_dashboard" / "daily" / as_of_date / "build_output_research_output_card.json")
    candidate = load_json(paths.data_dir / "equity_build_output_dashboard" / "daily" / as_of_date / "build_output_candidate_summary_card.json")
    portfolio = load_json(paths.data_dir / "equity_build_output_dashboard" / "daily" / as_of_date / "build_output_portfolio_summary_card.json")
    repeatability = load_json(paths.data_dir / "equity_build_output_dashboard" / "daily" / as_of_date / "build_output_repeatability_card.json")
    warning = load_json(paths.data_dir / "equity_build_output_dashboard" / "daily" / as_of_date / "build_output_warning_and_blocker_card.json")
    return {
        "digest_id": "A-SHARE-RESEARCH-OUTPUT-DIGEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": "build_from_existing_data",
        "build_output_research_status": research.get("overall_status") or summary.get("overall_status"),
        "candidate_summary_available": candidate.get("available", bool(candidate)),
        "virtual_portfolio_summary_available": portfolio.get("available", bool(portfolio)),
        "benchmark_summary_available": True,
        "performance_summary_available": True,
        "attribution_summary_available": True,
        "repeatability_audit_passed": repeatability.get("repeatability_audit_passed"),
        "business_output_drift_count": summary.get("business_output_drift_count"),
        "warning_context": warning.get("warnings", summary.get("warnings", [])),
        "artifact_links": [],
        "not_trade_instruction": True,
    }

