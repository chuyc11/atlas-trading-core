"""Owner readiness gap analysis."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_quality_exceptions.exception_workflow_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_owner_readiness_gap_analysis(*, as_of_date: str = DEFAULT_AS_OF_DATE, intake: dict[str, Any], score: dict[str, Any], evaluation: dict[str, Any], classification: dict[str, Any]) -> dict[str, Any]:
    return {
        "analysis_id": "A-SHARE-OWNER-READINESS-GAP-ANALYSIS",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "minimum_owner_readiness_score": intake["minimum_owner_readiness_score"],
        "actual_owner_readiness_score": intake["actual_owner_readiness_score"],
        "score_gap": intake["readiness_score_gap"],
        "grade": intake.get("actual_owner_readiness_grade"),
        "score_drivers": score.get("score_explanation", []),
        "largest_score_penalties": [item for item in score.get("score_explanation", []) if item.startswith("minus_")],
        "quality_gates_failed": evaluation.get("failed_gates", []),
        "quality_gates_passed": evaluation.get("passed_gates", []),
        "what_would_need_to_improve": ["Reduce warning load and manual safe-action burden enough to raise owner readiness above threshold."],
        "what_cannot_be_waived": ["broker/order/boundary violations", "protected path modifications", "trading instructions"],
        "what_can_be_reviewed_manually": [row["exception_id"] for row in classification.get("classifications", []) if row.get("waiver_candidate")],
        "owner_readiness_is_operations_readiness_only": True,
        "not_strategy_performance": True,
        "not_trading_signal": True,
    }
