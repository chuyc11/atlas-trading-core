"""Developer and owner follow-up evidence packages."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_recovery_evidence.evidence_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_developer_follow_up_evidence_package(*, as_of_date: str = DEFAULT_AS_OF_DATE, recovery_plan: dict[str, Any], execution_tracker: dict[str, Any], quality_tracker: dict[str, Any]) -> dict[str, Any]:
    quality_by_id = {item.get("follow_up_id"): item for item in quality_tracker.get("items", [])}
    execution_by_id = {item.get("follow_up_id"): item for item in execution_tracker.get("items", [])}
    items = []
    for item in recovery_plan.get("items", []):
        follow_up_id = item.get("follow_up_id")
        quality_item = quality_by_id.get(follow_up_id, {})
        execution_item = execution_by_id.get(follow_up_id, {})
        actual_available = execution_item.get("evidence_available") is True
        items.append(
            {
                "follow_up_id": follow_up_id,
                "source_exception_id": item.get("source_exception_id"),
                "developer_action_required": True,
                "expected_evidence": item.get("completion_evidence_required", []),
                "actual_evidence_available": actual_available,
                "evidence_artifacts": [],
                "evidence_quality": "none" if not actual_available else "partial",
                "safe_audit_only_commands": item.get("safe_audit_only_commands") or quality_item.get("safe_audit_only_commands", []),
                "forbidden_actions": item.get("forbidden_actions") or quality_item.get("forbidden_actions", []),
                "status": "planned" if not actual_available else "evidence_available",
                "remaining_developer_gap": "updated quality explanation and audit-only verification evidence required" if not actual_available else "",
            }
        )
    return {
        "package_id": "A-SHARE-DEVELOPER-FOLLOW-UP-EVIDENCE-PACKAGE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "follow_up_count": len(items),
        "actual_evidence_available_count": sum(1 for item in items if item["actual_evidence_available"]),
        "forbidden_owner_developer_actions_detected": [],
        "items": items,
    }


def build_owner_follow_up_evidence_package(*, as_of_date: str = DEFAULT_AS_OF_DATE, owner_plan: dict[str, Any], execution_tracker: dict[str, Any]) -> dict[str, Any]:
    items = []
    for index, item in enumerate(owner_plan.get("items", []), start=1):
        items.append(
            {
                "follow_up_id": f"OWNER-FOLLOW-UP-{index:03d}",
                "action": item.get("action"),
                "allowed_evidence_types": [
                    "owner_review_note",
                    "owner_acknowledgement_note",
                    "owner_no_trade_confirmation",
                    "owner_request_for_developer_follow_up",
                    "owner_wait_for_more_history_confirmation",
                ],
                "owner_evidence_available": False,
                "owner_follow_up_status": "waiting_for_owner",
                "evidence_artifacts": [],
                "evidence_quality": "none",
                "trade_related": item.get("trade_related", False),
                "broker_related": item.get("broker_related", False),
                "order_related": item.get("order_related", False),
            }
        )
    return {
        "package_id": "A-SHARE-OWNER-FOLLOW-UP-EVIDENCE-PACKAGE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "owner_follow_up_count": len(items),
        "owner_evidence_available": False,
        "owner_follow_up_status": "waiting_for_owner",
        "does_not_require_personal_account_data": True,
        "does_not_require_broker_access": True,
        "does_not_imply_trading_decision": True,
        "items": items,
    }

