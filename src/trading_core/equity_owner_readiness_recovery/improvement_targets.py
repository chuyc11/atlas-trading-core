"""Quality improvement target policy."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_readiness_recovery.recovery_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_quality_improvement_target_policy(*, as_of_date: str = DEFAULT_AS_OF_DATE, minimum_score: int = 75) -> dict[str, Any]:
    return {
        "policy_id": "A-SHARE-QUALITY-IMPROVEMENT-TARGET-POLICY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "target_owner_readiness_score": max(minimum_score, 75),
        "target_owner_readiness_grade": "B",
        "target_business_output_drift_count": 0,
        "target_protected_path_modifications_detected": False,
        "target_automatic_action_count": 0,
        "target_source_trace_complete": True,
        "target_boundary_clean": True,
        "target_forbidden_wording_hits": 0,
        "target_required_artifact_completeness": 1.0,
        "target_required_markdown_completeness": 1.0,
        "does_not_lower_v0813_gates": True,
        "requires_trading_actions": False,
        "requires_broker_connection": False,
    }
