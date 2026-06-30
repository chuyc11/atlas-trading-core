"""Prerequisite validation for controlled gate reevaluation."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_controlled_gate_reevaluation.controlled_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_reevaluation_prerequisite_validation(*, as_of_date: str = DEFAULT_AS_OF_DATE, guard: dict[str, Any]) -> dict[str, Any]:
    met = guard.get("reevaluation_allowed") is True
    return {
        "validation_id": "A-SHARE-OWNER-REEVALUATION-PREREQUISITE-VALIDATION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "reevaluation_prerequisites_met": met,
        "readiness_guard_passed": guard.get("readiness_guard_passed"),
        "required_action": "record_skip_decision" if not met else "controlled_gate_reevaluation_allowed",
        "failed_prerequisites": list(guard.get("block_reasons", [])),
        "gate_reevaluation_executed": False,
        "overall_passed": True,
        "blocking_reasons": [],
    }

