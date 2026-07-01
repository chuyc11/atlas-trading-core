"""Owner-readiness lineage review from v0.8.13 through v0.8.20."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_closeout_review.closeout_config import DEFAULT_AS_OF_DATE, RECOMMENDED_NEXT_VERSION, TARGET_VERSION

STAGES = [
    ("v0813_owner_readiness_gate_audit", "v0.8.13", "owner readiness gate"),
    ("v0814_quality_exception_workflow_audit", "v0.8.14", "quality exceptions"),
    ("v0815_recovery_plan_audit", "v0.8.15", "recovery plan"),
    ("v0816_recovery_execution_audit", "v0.8.16", "recovery execution tracker"),
    ("v0817_controlled_reevaluation_audit", "v0.8.17", "controlled reevaluation guard"),
    ("v0818_recovery_evidence_audit", "v0.8.18", "recovery evidence collection"),
    ("v0819_evidence_backed_prep_audit", "v0.8.19", "evidence-backed reevaluation prep"),
    ("v0820_gate_outcome_audit", "v0.8.20", "final blocked closeout"),
]


def build_lineage_review(*, as_of_date: str = DEFAULT_AS_OF_DATE, payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    stages = [_stage_row(key, version, label, payloads) for key, version, label in STAGES]
    blocking = []
    if any(row["audit_overall_passed"] is not True for row in stages):
        blocking.append("lineage_contains_unpassed_audit")
    if any(row["source_gate_decision"] not in ("blocked", None) for row in stages):
        blocking.append("lineage_contains_non_blocked_source_gate_decision")
    return {
        "lineage_id": "A-SHARE-V0813-TO-V0820-LINEAGE-REVIEW",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
        "stage_count": len(stages),
        "stages": stages,
        "blocked_state_visible": True,
        "readiness_score_visible": any(row["readiness_score_if_available"] is not None for row in stages),
        "minimum_threshold_visible": any(row["minimum_owner_readiness_score"] is not None for row in stages),
        "score_gap_visible": any(row["score_gap_if_available"] is not None for row in stages),
        "readiness_score_54_visible": any(row["readiness_score_if_available"] == 54 for row in stages),
        "minimum_threshold_75_visible": any(row["minimum_owner_readiness_score"] == 75 for row in stages),
        "score_gap_21_visible": any(row["score_gap_if_available"] == 21 for row in stages),
        "new_gate_score_generated_anywhere": any(row["new_gate_score_generated"] is True for row in stages),
        "new_gate_decision_generated_anywhere": any(row["new_gate_decision_generated"] is True for row in stages),
        "threshold_lowered_anywhere": any(row["threshold_lowered"] is True for row in stages),
        "auto_waiver_allowed_anywhere": any(row["auto_waiver_allowed"] is True for row in stages),
        "manual_waiver_approval_recorded_anywhere": any(row["manual_waiver_approval_recorded"] is True for row in stages),
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def lineage_stage_rows(payloads: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return [_stage_row(key, version, label, payloads) for key, version, label in STAGES]


def _stage_row(key: str, version: str, label: str, payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    payload = payloads.get(key, {})
    missing: dict[str, str] = {}
    row = {
        "source_artifact_key": key,
        "version": version,
        "stage": label,
        "audit_id": payload.get("audit_id"),
        "audit_overall_passed": payload.get("overall_passed"),
        "blocking_reasons": payload.get("blocking_reasons"),
        "source_gate_decision": _extract(payload, missing, "source_gate_decision", [
            ("input_checks", "source_gate_decision"),
            ("gate_checks", "decision"),
            ("outcome_checks", "source_gate_decision"),
        ]),
        "readiness_score_if_available": _extract(payload, missing, "readiness_score_if_available", [
            ("gate_checks", "actual_owner_readiness_score"),
            ("exception_checks", "actual_owner_readiness_score"),
            ("recovery_checks", "actual_owner_readiness_score"),
            ("outcome_checks", "previous_readiness_score"),
        ]),
        "minimum_owner_readiness_score": _extract(payload, missing, "minimum_owner_readiness_score", [
            ("gate_checks", "minimum_owner_readiness_score"),
            ("exception_checks", "minimum_owner_readiness_score"),
            ("recovery_checks", "minimum_owner_readiness_score"),
            ("outcome_checks", "minimum_owner_readiness_score"),
        ]),
        "score_gap_if_available": _extract(payload, missing, "score_gap_if_available", [
            ("exception_checks", "readiness_score_gap"),
            ("recovery_checks", "readiness_score_gap"),
            ("outcome_checks", "score_gap"),
        ]),
        "new_gate_score_generated": _extract(payload, missing, "new_gate_score_generated", [
            ("reevaluation_checks", "new_gate_score_generated"),
            ("evidence_checks", "new_gate_score_generated"),
            ("prep_checks", "new_gate_score_generated"),
            ("outcome_checks", "new_controlled_readiness_score_generated"),
            ("boundary", "new_gate_score_generated"),
        ]),
        "new_gate_decision_generated": _extract(payload, missing, "new_gate_decision_generated", [
            ("reevaluation_checks", "new_gate_decision_generated"),
            ("evidence_checks", "new_gate_decision_generated"),
            ("prep_checks", "new_gate_decision_generated"),
            ("outcome_checks", "new_controlled_gate_decision_generated"),
            ("boundary", "new_gate_decision_generated"),
        ]),
        "threshold_lowered": _extract(payload, missing, "threshold_lowered", [
            ("recovery_checks", "threshold_lowered"),
            ("execution_checks", "threshold_lowered"),
            ("reevaluation_checks", "threshold_lowered"),
            ("prep_checks", "threshold_lowered"),
            ("outcome_checks", "threshold_lowered"),
            ("boundary", "threshold_lowered"),
        ]),
        "auto_waiver_allowed": _extract(payload, missing, "auto_waiver_allowed", [
            ("exception_checks", "auto_waiver_allowed"),
            ("recovery_checks", "auto_waiver_allowed"),
            ("execution_checks", "auto_waiver_allowed"),
            ("reevaluation_checks", "auto_waiver_allowed"),
            ("prep_checks", "auto_waiver_allowed"),
            ("outcome_checks", "auto_waiver_allowed"),
            ("boundary", "auto_waiver_allowed"),
        ]),
        "manual_waiver_approval_recorded": _extract(payload, missing, "manual_waiver_approval_recorded", [
            ("exception_checks", "manual_waiver_approval_recorded"),
            ("recovery_checks", "manual_waiver_approval_recorded"),
            ("execution_checks", "manual_waiver_approval_recorded"),
            ("reevaluation_checks", "manual_waiver_approval_recorded"),
            ("prep_checks", "manual_waiver_approval_recorded"),
            ("outcome_checks", "manual_waiver_approval_recorded"),
            ("boundary", "manual_waiver_approval_recorded"),
        ]),
        "broker_connected": _extract(payload, missing, "broker_connected", [("boundary", "broker_connected")]),
        "real_orders_placed": _extract(payload, missing, "real_orders_placed", [("boundary", "real_orders_placed")]),
        "buy_sell_signals_generated": _extract(payload, missing, "buy_sell_signals_generated", [("boundary", "buy_sell_signals_generated")]),
        "order_preview_generated": _extract(payload, missing, "order_preview_generated", [("boundary", "order_preview_generated")]),
        "evidence_status": _evidence_status(payload),
        "recommended_next_version": payload.get("recommended_next_version"),
    }
    if missing:
        row["source_missing_reason"] = missing
    return row


def _extract(payload: dict[str, Any], missing: dict[str, str], output_key: str, paths: list[tuple[str, str]]) -> Any:
    for section, key in paths:
        section_value = payload.get(section, {})
        if isinstance(section_value, dict) and key in section_value:
            return section_value.get(key)
    missing[output_key] = "source_field_not_present"
    return None


def _evidence_status(payload: dict[str, Any]) -> str | None:
    for section, key in [
        ("execution_checks", "gate_reevaluation_readiness_decision"),
        ("reevaluation_checks", "controlled_reevaluation_decision"),
        ("evidence_checks", "evidence_ready_for_next_reevaluation_prep"),
        ("prep_checks", "eligibility_decision"),
        ("gate_checks", "decision"),
    ]:
        section_value = payload.get(section, {})
        if isinstance(section_value, dict) and key in section_value:
            return str(section_value[key])
    return None
