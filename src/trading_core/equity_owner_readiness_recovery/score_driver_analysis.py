"""Score driver analysis for owner readiness recovery."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_readiness_recovery.recovery_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_score_driver_analysis(*, as_of_date: str = DEFAULT_AS_OF_DATE, gap: dict[str, Any], source_gap_analysis: dict[str, Any], classification: dict[str, Any]) -> dict[str, Any]:
    penalties = []
    for item in source_gap_analysis.get("largest_score_penalties", []):
        penalties.append({"driver": item, "evidence_source": "v0.8.14 owner_readiness_gap_analysis", "confidence": "high"})
    exception_drivers = [
        {"exception_id": row["exception_id"], "category": row["category"], "evidence_source": "v0.8.14 quality_exception_classification", "confidence": "high"}
        for row in classification.get("classifications", [])
    ]
    return {
        "analysis_id": "A-SHARE-SCORE-DRIVER-ANALYSIS",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_score": gap["actual_owner_readiness_score"],
        "threshold_score": gap["minimum_owner_readiness_score"],
        "score_gap": gap["readiness_score_gap"],
        "score_penalty_components": penalties,
        "exception_drivers": exception_drivers,
        "warning_drivers": [row for row in exception_drivers if row["category"] == "warning_issue_threshold_issue"],
        "history_drivers": [row for row in exception_drivers if row["category"] == "insufficient_history"],
        "completeness_drivers": [],
        "source_trace_drivers": [],
        "boundary_drivers": [],
        "manual_review_drivers": exception_drivers,
        "largest_recoverable_penalties": penalties,
        "non_recoverable_or_wait_for_history_penalties": [row for row in exception_drivers if row["category"] == "insufficient_history"],
        "does_not_recalculate_source_score": True,
    }
