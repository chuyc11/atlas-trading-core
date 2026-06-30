"""Blocked-state preservation check."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_readiness_recovery.recovery_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_blocked_state_preservation_check(*, as_of_date: str = DEFAULT_AS_OF_DATE, intake: dict[str, Any]) -> dict[str, Any]:
    passed = intake.get("source_gate_decision") == "blocked" and intake.get("blocked_state_preserved") is True and intake.get("owner_operationally_acceptable") is False
    return {
        "check_id": "A-SHARE-BLOCKED-STATE-PRESERVATION-CHECK",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_gate_decision": intake.get("source_gate_decision"),
        "blocked_gate_decision_preserved": intake.get("blocked_state_preserved"),
        "owner_operationally_acceptable": intake.get("owner_operationally_acceptable"),
        "recovery_plan_changes_gate_decision": False,
        "recovery_plan_marks_acceptable": False,
        "threshold_lowered": False,
        "auto_waiver_allowed": False,
        "manual_waiver_approval_recorded": False,
        "overall_passed": passed,
        "blocking_reasons": [] if passed else ["blocked_state_not_preserved"],
        "warnings": [],
    }
