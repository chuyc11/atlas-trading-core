"""Evidence gap and remaining blocker registers."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_recovery_evidence.evidence_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_evidence_gap_register(*, as_of_date: str = DEFAULT_AS_OF_DATE, task_evidence: dict[str, Any], developer: dict[str, Any], owner: dict[str, Any]) -> dict[str, Any]:
    gaps = []
    for item in task_evidence.get("items", []):
        if not item.get("completion_claim_allowed"):
            gaps.append(_gap(as_of_date, f"GAP:{item['task_id']}", item.get("task_id"), item.get("source_exception_id"), item.get("remaining_gap"), True))
    for item in developer.get("items", []):
        if not item.get("actual_evidence_available"):
            gaps.append(_gap(as_of_date, f"GAP:{item['follow_up_id']}", "", item.get("source_exception_id"), item.get("remaining_developer_gap"), True))
    if owner.get("owner_evidence_available") is False:
        gaps.append(_gap(as_of_date, "GAP:OWNER-FOLLOW-UP-EVIDENCE", "", "", "owner follow-up evidence not yet available", False))
    return {
        "register_id": "A-SHARE-EVIDENCE-GAP-REGISTER",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "gap_count": len(gaps),
        "items": gaps,
    }


def build_remaining_blocker_register(*, as_of_date: str = DEFAULT_AS_OF_DATE, gap_register: dict[str, Any], score_gap: int) -> dict[str, Any]:
    categories = sorted(
        set(
            ["missing_recovery_evidence", "readiness_score_gap", "threshold_preservation_required", "waiver_not_allowed"]
            + (["missing_owner_follow_up_evidence"] if gap_register.get("gap_count", 0) else [])
        )
    )
    return {
        "register_id": "A-SHARE-REMAINING-BLOCKER-REGISTER",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "blocker_count": len(categories),
        "categories": categories,
        "score_gap": score_gap,
        "items": gap_register.get("items", []),
    }


def _gap(as_of_date: str, gap_id: str, task_id: str, exception_id: str, missing: str, developer_required: bool) -> dict[str, Any]:
    return {
        "gap_id": gap_id,
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "related_task_id": task_id,
        "related_exception_id": exception_id,
        "missing_evidence": missing,
        "why_it_matters": "required before evidence-backed gate reevaluation prep",
        "owner_visible": True,
        "developer_follow_up_required": developer_required,
        "blocks_next_reevaluation_prep": True,
        "recommended_next_action": "collect real local recovery evidence and rerun audit-only verification",
    }

