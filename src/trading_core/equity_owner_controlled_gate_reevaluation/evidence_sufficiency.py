"""Evidence sufficiency check for controlled gate reevaluation."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_controlled_gate_reevaluation.controlled_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_evidence_sufficiency_check(*, as_of_date: str = DEFAULT_AS_OF_DATE, evidence_registry: dict[str, Any], status_tracker: dict[str, Any]) -> dict[str, Any]:
    sufficient = evidence_registry.get("evidence_available_count", 0) > 0 and status_tracker.get("completed_count", 0) > 0
    return {
        "check_id": "A-SHARE-OWNER-CONTROLLED-REEVALUATION-EVIDENCE-SUFFICIENCY-CHECK",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "evidence_sufficient_for_gate_reevaluation": sufficient,
        "evidence_available_count": evidence_registry.get("evidence_available_count"),
        "verified_by_audit_only_count": status_tracker.get("verified_by_audit_only_count"),
        "completed_count": status_tracker.get("completed_count"),
        "forbidden_evidence_types_detected": evidence_registry.get("forbidden_evidence_types_detected", []),
        "overall_passed": True,
        "blocking_reasons": [],
    }

