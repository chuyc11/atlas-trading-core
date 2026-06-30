"""Manifest and summary for controlled gate reevaluation."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from trading_core.equity_owner_controlled_gate_reevaluation.controlled_config import DEFAULT_AS_OF_DATE, RECOMMENDED_NEXT_VERSION, SOURCE_WORKFLOW_MODE, TARGET_VERSION


def build_controlled_reevaluation_manifest(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    output_artifacts: dict[str, Path],
    source_artifacts: dict[str, Path],
    source_summary: dict[str, Any],
    guard: dict[str, Any],
    skip_decision: dict[str, Any],
    controlled_decision: dict[str, Any],
    boundary: dict[str, Any],
) -> dict[str, Any]:
    return {
        "manifest_id": "A-SHARE-OWNER-CONTROLLED-GATE-REEVALUATION-MANIFEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "source_workflow_mode": SOURCE_WORKFLOW_MODE,
        "source_gate_decision": source_summary.get("source_gate_decision"),
        "blocked_gate_decision_preserved": source_summary.get("blocked_gate_decision_preserved"),
        "minimum_owner_readiness_score": source_summary.get("minimum_owner_readiness_score"),
        "actual_owner_readiness_score": source_summary.get("actual_owner_readiness_score"),
        "readiness_score_gap": source_summary.get("readiness_score_gap"),
        "readiness_guard_passed": guard.get("readiness_guard_passed"),
        "reevaluation_allowed": guard.get("reevaluation_allowed"),
        "reevaluation_skipped": skip_decision.get("reevaluation_skipped"),
        "controlled_reevaluation_decision": controlled_decision.get("decision"),
        "gate_reevaluation_executed": False,
        "threshold_lowered": False,
        "auto_waiver_allowed": False,
        "manual_waiver_approval_recorded": False,
        "output_artifacts": {key: str(path) for key, path in output_artifacts.items()},
        "source_artifacts": {key: str(path) for key, path in source_artifacts.items()},
        "boundary": boundary,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def build_controlled_reevaluation_summary(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    source_summary: dict[str, Any],
    guard: dict[str, Any],
    skip_decision: dict[str, Any],
    controlled_decision: dict[str, Any],
) -> dict[str, Any]:
    return {
        "summary_id": "A-SHARE-OWNER-CONTROLLED-GATE-REEVALUATION-SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": SOURCE_WORKFLOW_MODE,
        "source_gate_decision": source_summary.get("source_gate_decision"),
        "blocked_gate_decision_preserved": source_summary.get("blocked_gate_decision_preserved"),
        "minimum_owner_readiness_score": source_summary.get("minimum_owner_readiness_score"),
        "actual_owner_readiness_score": source_summary.get("actual_owner_readiness_score"),
        "readiness_score_gap": source_summary.get("readiness_score_gap"),
        "readiness_guard_passed": guard.get("readiness_guard_passed"),
        "reevaluation_allowed": guard.get("reevaluation_allowed"),
        "reevaluation_skipped": skip_decision.get("reevaluation_skipped"),
        "reevaluation_skip_reason": skip_decision.get("reevaluation_skip_reason"),
        "controlled_reevaluation_decision": controlled_decision.get("decision"),
        "gate_reevaluation_executed": False,
        "threshold_lowered": False,
        "auto_waiver_allowed": False,
        "manual_waiver_approval_recorded": False,
        "owner_operationally_acceptable": False,
        "not_investment_advice": True,
        "not_order_instruction": True,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }

