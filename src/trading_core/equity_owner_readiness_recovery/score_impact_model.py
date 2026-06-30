"""Recovery score impact model."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_readiness_recovery.recovery_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_recovery_score_impact_model(*, as_of_date: str = DEFAULT_AS_OF_DATE, gap: dict[str, Any], backlog: dict[str, Any]) -> dict[str, Any]:
    impacts = [{"task_id": task["task_id"], "expected_score_impact": task["expected_score_impact"], "estimate": True, "confidence": "medium"} for task in backlog.get("tasks", [])]
    recoverable = sum(item["expected_score_impact"] for item in impacts)
    wait = sum(task["expected_score_impact"] for task in backlog.get("tasks", []) if task.get("requires_more_history"))
    projection = min(gap["actual_owner_readiness_score"] + recoverable, 100)
    return {
        "model_id": "A-SHARE-RECOVERY-SCORE-IMPACT-MODEL",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "current_score": gap["actual_owner_readiness_score"],
        "target_score": gap["minimum_owner_readiness_score"],
        "score_gap": gap["readiness_score_gap"],
        "task_level_expected_score_impact": impacts,
        "max_potential_recoverable_score": recoverable,
        "non_recoverable_until_more_history_score": wait,
        "score_projection_after_planned_tasks": projection,
        "projection_confidence": "medium_estimate",
        "does_not_rewrite_source_score": True,
        "does_not_claim_recovery_succeeded": True,
    }
