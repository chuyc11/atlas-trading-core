"""Build a controlled reevaluation input package without executing the gate."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_evidence_backed_reevaluation_prep.prep_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_reevaluation_input_package(*, as_of_date: str = DEFAULT_AS_OF_DATE, availability: dict[str, Any], sufficiency: dict[str, Any], mapping: dict[str, Any], source_artifacts: dict[str, str]) -> dict[str, Any]:
    return {
        "package_id": "A-SHARE-REEVALUATION-INPUT-PACKAGE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "reevaluation_input_package_generated": True,
        "ready_for_controlled_gate_reevaluation": sufficiency.get("ready_for_controlled_gate_reevaluation"),
        "eligibility_decision": sufficiency.get("eligibility_decision"),
        "source_gate_truth": {
            "source_gate_decision": availability.get("source_gate_decision"),
            "source_readiness_score": availability.get("source_readiness_score"),
            "minimum_owner_readiness_score": availability.get("minimum_owner_readiness_score"),
            "score_gap": availability.get("score_gap"),
        },
        "evidence_summary": {
            "evidence_record_count": availability.get("evidence_record_count"),
            "strong_evidence_count": availability.get("strong_evidence_count"),
            "audit_verified_evidence_count": availability.get("audit_verified_evidence_count"),
            "missing_evidence_count": availability.get("missing_evidence_count"),
            "overall_evidence_quality": availability.get("overall_evidence_quality"),
        },
        "threshold_policy": {"minimum_owner_readiness_score": availability.get("minimum_owner_readiness_score"), "threshold_lowered": False},
        "waiver_policy": {"auto_waiver_allowed": False, "manual_waiver_approval_recorded": False},
        "mapping_id": mapping.get("mapping_id"),
        "source_artifacts": source_artifacts,
        "reevaluation_executed": False,
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
        "not_order_instruction": True,
    }

