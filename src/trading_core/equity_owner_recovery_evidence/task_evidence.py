"""Recovery task evidence collection."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_recovery_evidence.evidence_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_recovery_task_evidence_collection(*, as_of_date: str = DEFAULT_AS_OF_DATE, backlog: dict[str, Any], evidence_registry: dict[str, Any], status_tracker: dict[str, Any]) -> dict[str, Any]:
    registry_by_task = {}
    for record in evidence_registry.get("records", []):
        registry_by_task.setdefault(record.get("source_task_id"), []).append(record)
    status_by_task = {item.get("task_id"): item for item in status_tracker.get("items", [])}
    items = []
    forbidden = []
    for task in backlog.get("tasks", []):
        task_id = task.get("task_id")
        records = registry_by_task.get(task_id, [])
        evidence_available = any(row.get("evidence_available") is True for row in records)
        grade = _grade_records(records)
        status = status_by_task.get(task_id, {})
        proposed_status = status.get("status", task.get("status", "planned"))
        if evidence_available and proposed_status == "planned":
            proposed_status = "evidence_available"
        completion_allowed = evidence_available and grade in {"strong", "audit_verified"} and status.get("completed") is True
        for row in records:
            if row.get("evidence_type") in {"broker_connected", "order_submitted", "trade_executed", "buy_signal_generated", "sell_signal_generated", "real_account_checked"}:
                forbidden.append(row.get("evidence_type"))
        items.append(
            {
                "task_id": task_id,
                "task_title": task.get("title_zh") or task.get("title") or task_id,
                "source_exception_id": task.get("source_exception_id"),
                "expected_evidence": task.get("evidence_required", []),
                "actual_evidence_records": records,
                "evidence_available": evidence_available,
                "evidence_quality": grade,
                "evidence_confidence": "none" if grade == "none" else "low" if grade in {"weak", "partial"} else "medium",
                "supports_status_change": evidence_available and proposed_status != task.get("status"),
                "proposed_status": proposed_status,
                "completion_claim_allowed": completion_allowed,
                "completion_claim_reason": "completion evidence absent or not audit verified" if not completion_allowed else "audit evidence supports completion",
                "remaining_gap": "" if completion_allowed else "completion evidence still required",
            }
        )
    return {
        "collection_id": "A-SHARE-RECOVERY-TASK-EVIDENCE-COLLECTION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "task_count": len(items),
        "evidence_record_count": sum(len(item["actual_evidence_records"]) for item in items),
        "evidence_available_count": sum(1 for item in items if item["evidence_available"]),
        "completion_claim_allowed_count": sum(1 for item in items if item["completion_claim_allowed"]),
        "task_completion_not_fabricated": all(item["completion_claim_allowed"] is False for item in items if item["evidence_quality"] in {"none", "weak", "partial"}),
        "forbidden_evidence_types_detected": sorted(set(forbidden)),
        "items": items,
    }


def _grade_records(records: list[dict[str, Any]]) -> str:
    if not records or not any(row.get("evidence_available") for row in records):
        return "none"
    if any(row.get("evidence_type") == "audit_passed" and row.get("evidence_available") for row in records):
        return "audit_verified"
    if any(row.get("evidence_type") in {"source_trace_complete", "boundary_clean"} and row.get("evidence_available") for row in records):
        return "strong"
    return "partial"

