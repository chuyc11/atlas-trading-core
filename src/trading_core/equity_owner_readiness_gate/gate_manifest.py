"""Manifest and summary for owner readiness gate."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from trading_core.equity_owner_readiness_gate.gate_config import DEFAULT_AS_OF_DATE, RECOMMENDED_NEXT_VERSION, SOURCE_WORKFLOW_MODE, TARGET_VERSION


def build_manifest(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    output_artifacts: dict[str, Path],
    source_artifacts: dict[str, Path],
    decision: dict[str, Any],
    score: dict[str, Any],
    boundary: dict[str, Any],
    exceptions: dict[str, Any],
) -> dict[str, Any]:
    return {
        "manifest_id": "A-SHARE-OWNER-READINESS-GATE-MANIFEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "source_workflow_mode": SOURCE_WORKFLOW_MODE,
        "decision": decision["decision"],
        "owner_operationally_acceptable": decision["owner_operationally_acceptable"],
        "minimum_owner_readiness_score": decision["minimum_owner_readiness_score"],
        "actual_owner_readiness_score": score.get("score"),
        "actual_owner_readiness_grade": score.get("grade"),
        "required_gates_passed": decision["required_gates_passed"],
        "quality_exception_candidate_count": exceptions.get("candidate_count", 0),
        "business_output_drift_count": score.get("business_output_drift_count", 0),
        "protected_path_modifications_detected": boundary.get("protected_path_modifications_detected", False),
        "automatic_action_count": score.get("automatic_action_count", 0),
        "blocking_reasons": decision["blocking_reasons"],
        "warnings": decision["warnings"],
        "output_artifacts": {key: str(path) for key, path in output_artifacts.items()},
        "source_artifacts": {key: str(path) for key, path in source_artifacts.items()},
        "boundary": boundary,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def build_summary(*, as_of_date: str, decision: dict[str, Any], recommendation: dict[str, Any], audit_ready: bool) -> dict[str, Any]:
    return {
        "summary_id": "A-SHARE-OWNER-READINESS-GATE-SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": SOURCE_WORKFLOW_MODE,
        "decision": decision["decision"],
        "owner_operationally_acceptable": decision["owner_operationally_acceptable"],
        "blocking_reasons": decision["blocking_reasons"],
        "warnings": decision["warnings"],
        "owner_release_recommendation": recommendation["recommendation"],
        "audit_ready": audit_ready,
        "not_investment_decision": True,
        "not_trade_instruction": True,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }
