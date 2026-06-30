"""Not-ready reason summary for controlled gate reevaluation."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_controlled_gate_reevaluation.controlled_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_not_ready_reason_summary(*, as_of_date: str = DEFAULT_AS_OF_DATE, guard: dict[str, Any]) -> dict[str, Any]:
    reasons = list(guard.get("block_reasons", []))
    return {
        "summary_id": "A-SHARE-OWNER-REEVALUATION-NOT-READY-REASON-SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "not_ready": bool(reasons),
        "reason_count": len(reasons),
        "reasons": reasons,
        "evidence_available_count": guard.get("evidence_available_count"),
        "verified_by_audit_only_count": guard.get("verified_by_audit_only_count"),
        "completed_count": guard.get("completed_count"),
        "recommended_follow_up": "collect_real_recovery_evidence_before_any_future_gate_reevaluation",
    }

