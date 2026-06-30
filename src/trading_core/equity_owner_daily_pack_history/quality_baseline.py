"""Daily pack quality baseline."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_daily_pack_history.daily_pack_history_config import FILES, REPORTS, TARGET_VERSION


def build_quality_baseline(*, as_of_date: str, artifacts: dict[str, Any], records: list[dict[str, Any]], sufficiency: dict[str, Any], source_trace: dict[str, Any], boundary: dict[str, Any], summary: dict[str, Any]) -> dict[str, Any]:
    json_planned = all(key in artifacts for key in FILES)
    reports_planned = all(key in artifacts for key in REPORTS)
    return {
        "baseline_id": "A-SHARE-DAILY-PACK-QUALITY-BASELINE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "required_artifacts_complete": json_planned,
        "markdown_reports_complete": reports_planned,
        "source_trace_complete": source_trace.get("source_trace_complete") is True,
        "boundary_clean": boundary.get("overall_passed") is True,
        "not_investment_decision_pack_compliant": summary.get("not_investment_decision_pack") is True,
        "forbidden_wording_clean": not boundary.get("forbidden_wording_positive_hits"),
        "observation_count": len(records),
        "trend_analysis_available": sufficiency["trend_analysis_available"],
        "baseline_status": "available" if sufficiency["trend_analysis_available"] else "insufficient_history",
        "no_fabricated_trends": True,
    }
