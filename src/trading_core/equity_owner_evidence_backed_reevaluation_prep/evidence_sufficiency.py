"""Evidence sufficiency decision for controlled gate reevaluation prep."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_evidence_backed_reevaluation_prep.prep_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_evidence_sufficiency_decision(*, as_of_date: str = DEFAULT_AS_OF_DATE, availability: dict[str, Any], quality: dict[str, Any], blockers: dict[str, Any]) -> dict[str, Any]:
    overall_quality = quality.get("overall_evidence_quality", availability.get("overall_evidence_quality", "none"))
    remaining_blockers = int(blockers.get("blocker_count", availability.get("blocking_gap_count") or 0) or 0)
    strong = int(quality.get("strong_evidence_count", availability.get("strong_evidence_count") or 0) or 0)
    audit_verified = int(quality.get("audit_verified_evidence_count", availability.get("audit_verified_evidence_count") or 0) or 0)
    missing = int(quality.get("missing_evidence_count", availability.get("missing_evidence_count") or 0) or 0)
    prerequisites = {
        "source_gate_decision_preserved": availability.get("source_gate_decision_preserved") is True,
        "threshold_not_lowered": availability.get("threshold_lowered") is False,
        "auto_waiver_not_allowed": availability.get("auto_waiver_allowed") is False,
        "manual_waiver_not_recorded": availability.get("manual_waiver_approval_recorded") is False,
        "new_gate_score_not_generated": availability.get("new_gate_score_generated") is False,
        "new_gate_decision_not_generated": availability.get("new_gate_decision_generated") is False,
        "evidence_ready_flag_true": availability.get("evidence_ready_for_next_reevaluation_prep") is True,
        "quality_is_strong_or_audit_verified": overall_quality in {"strong", "audit_verified"},
        "no_remaining_blockers": remaining_blockers == 0,
        "no_missing_evidence": missing == 0,
        "strong_or_audit_verified_evidence_present": strong > 0 or audit_verified > 0,
    }
    ready = all(prerequisites.values())
    blocking = [key for key, passed in prerequisites.items() if not passed]
    if overall_quality in {"none", "weak"} and "evidence_quality_too_low" not in blocking:
        blocking.append("evidence_quality_too_low")
    if remaining_blockers > 0 and "remaining_blockers_present" not in blocking:
        blocking.append("remaining_blockers_present")
    return {
        "decision_id": "A-SHARE-EVIDENCE-SUFFICIENCY-FOR-REEVALUATION-DECISION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_gate_decision": availability.get("source_gate_decision"),
        "source_gate_decision_preserved": availability.get("source_gate_decision_preserved"),
        "evidence_record_count": availability.get("evidence_record_count"),
        "strong_evidence_count": strong,
        "audit_verified_evidence_count": audit_verified,
        "missing_evidence_count": missing,
        "overall_evidence_quality": overall_quality,
        "remaining_blocker_count": remaining_blockers,
        "evidence_sufficient_for_controlled_gate_reevaluation": ready,
        "ready_for_controlled_gate_reevaluation": ready,
        "eligibility_decision": "eligible" if ready else "not_eligible",
        "decision_reason": "evidence_sufficient" if ready else "evidence_insufficient_or_blocked",
        "prerequisite_checks": prerequisites,
        "blocking_reasons": sorted(set(blocking)),
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
        "reevaluation_executed": False,
        "threshold_lowered": False,
        "auto_waiver_allowed": False,
        "manual_waiver_approval_recorded": False,
    }

