"""Manifest and summary for owner quality exception workflow."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from trading_core.equity_owner_quality_exceptions.exception_workflow_config import DEFAULT_AS_OF_DATE, RECOMMENDED_NEXT_VERSION, SOURCE_WORKFLOW_MODE, TARGET_VERSION


def build_manifest(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    output_artifacts: dict[str, Path],
    source_artifacts: dict[str, Path],
    intake: dict[str, Any],
    registry: dict[str, Any],
    developer_tracker: dict[str, Any],
    owner_checklist: dict[str, Any],
    waiver_record: dict[str, Any],
    boundary: dict[str, Any],
) -> dict[str, Any]:
    return {
        "manifest_id": "A-SHARE-OWNER-QUALITY-EXCEPTION-WORKFLOW-MANIFEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "source_workflow_mode": SOURCE_WORKFLOW_MODE,
        "source_gate_decision": intake["source_gate_decision"],
        "blocked_gate_decision_preserved": intake["blocked_state_preserved"],
        "minimum_owner_readiness_score": intake["minimum_owner_readiness_score"],
        "actual_owner_readiness_score": intake["actual_owner_readiness_score"],
        "readiness_score_gap": intake["readiness_score_gap"],
        "quality_exception_count": registry.get("exception_count", 0),
        "developer_follow_up_count": developer_tracker.get("follow_up_count", 0),
        "owner_follow_up_count": owner_checklist.get("owner_follow_up_count", 0),
        "manual_waiver_decision_status": waiver_record["manual_waiver_decision_status"],
        "manual_waiver_approval_recorded": waiver_record["manual_waiver_approval_recorded"],
        "auto_waiver_allowed": waiver_record["auto_waiver_allowed"],
        "waiver_changes_gate_decision": waiver_record["waiver_changes_gate_decision"],
        "external_notifications_sent": False,
        "execute_remediation_actions": False,
        "blocking_reasons": [],
        "warnings": intake.get("warnings", []),
        "output_artifacts": {key: str(path) for key, path in output_artifacts.items()},
        "source_artifacts": {key: str(path) for key, path in source_artifacts.items()},
        "boundary": boundary,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def build_summary(*, as_of_date: str, intake: dict[str, Any], registry: dict[str, Any], waiver_record: dict[str, Any]) -> dict[str, Any]:
    return {
        "summary_id": "A-SHARE-OWNER-QUALITY-EXCEPTION-WORKFLOW-SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": SOURCE_WORKFLOW_MODE,
        "source_gate_decision": intake["source_gate_decision"],
        "blocked_gate_decision_preserved": intake["blocked_state_preserved"],
        "quality_exception_count": registry.get("exception_count", 0),
        "manual_waiver_decision_status": waiver_record["manual_waiver_decision_status"],
        "manual_waiver_approval_recorded": waiver_record["manual_waiver_approval_recorded"],
        "auto_waiver_allowed": waiver_record["auto_waiver_allowed"],
        "waiver_changes_gate_decision": waiver_record["waiver_changes_gate_decision"],
        "not_investment_advice": True,
        "not_trade_instruction": True,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }
