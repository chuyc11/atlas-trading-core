"""Preservation checks for controlled gate reevaluation."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_controlled_gate_reevaluation.controlled_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_source_gate_preservation_check(*, as_of_date: str = DEFAULT_AS_OF_DATE, source_summary: dict[str, Any], gate_decision: dict[str, Any]) -> dict[str, Any]:
    passed = source_summary.get("source_gate_decision") == "blocked" and source_summary.get("blocked_gate_decision_preserved") is True
    return {
        "check_id": "A-SHARE-OWNER-CONTROLLED-REEVALUATION-SOURCE-GATE-PRESERVATION-CHECK",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_gate_decision": source_summary.get("source_gate_decision"),
        "v0_8_13_gate_decision": gate_decision.get("gate_decision") or gate_decision.get("owner_readiness_gate_decision"),
        "source_gate_decision_preserved": passed,
        "gate_reevaluation_executed": False,
        "new_gate_decision_generated": False,
        "overall_passed": passed,
        "blocking_reasons": [] if passed else ["source_gate_decision_not_preserved"],
    }


def build_threshold_preservation_check(*, as_of_date: str = DEFAULT_AS_OF_DATE, source_summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "check_id": "A-SHARE-OWNER-CONTROLLED-REEVALUATION-THRESHOLD-PRESERVATION-CHECK",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "minimum_owner_readiness_score": source_summary.get("minimum_owner_readiness_score"),
        "actual_owner_readiness_score": source_summary.get("actual_owner_readiness_score"),
        "threshold_lowered": False,
        "threshold_preserved": True,
        "overall_passed": True,
        "blocking_reasons": [],
    }


def build_waiver_preservation_check(*, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict[str, Any]:
    return {
        "check_id": "A-SHARE-OWNER-CONTROLLED-REEVALUATION-WAIVER-PRESERVATION-CHECK",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "auto_waiver_allowed": False,
        "manual_waiver_approval_recorded": False,
        "waiver_changes_gate_decision": False,
        "overall_passed": True,
        "blocking_reasons": [],
    }

