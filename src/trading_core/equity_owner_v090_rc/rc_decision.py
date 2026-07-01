"""v0.9.0 release candidate decision."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_v090_rc.v090_config import DEFAULT_AS_OF_DATE, RECOMMENDED_NEXT_VERSION, TARGET_VERSION


def build_release_candidate_decision(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    full_pytest: dict[str, Any],
    audit_sweep: dict[str, Any],
    boundary_sweep: dict[str, Any],
    source_trace_sweep: dict[str, Any],
    documentation_freeze: dict[str, Any],
    disclosure: dict[str, Any],
) -> dict[str, Any]:
    checks = {
        "full_pytest_passed": full_pytest.get("overall_passed") is True and full_pytest.get("full_pytest_run") is True,
        "audit_sweep_passed": audit_sweep.get("audit_sweep_passed") is True,
        "boundary_sweep_passed": boundary_sweep.get("boundary_sweep_passed") is True,
        "source_trace_sweep_passed": source_trace_sweep.get("source_trace_sweep_passed") is True,
        "documentation_freeze_passed": documentation_freeze.get("documentation_freeze_passed") is True,
        "known_blocked_state_disclosed": disclosure.get("overall_passed") is True,
        "blocked_state_not_misrepresented": disclosure.get("blocked_state_misrepresented_as_acceptable") is False,
    }
    if all(checks.values()):
        decision = "v090_rc_passed_with_known_blocked_owner_readiness"
        blocking: list[str] = []
    elif not checks["full_pytest_passed"]:
        decision = "v090_rc_blocked_by_regression"
        blocking = ["full_pytest_failed"]
    elif not checks["audit_sweep_passed"]:
        decision = "v090_rc_blocked_by_audit_sweep"
        blocking = ["audit_sweep_failed"]
    elif not checks["boundary_sweep_passed"]:
        decision = "v090_rc_blocked_by_boundary"
        blocking = ["boundary_sweep_failed"]
    elif not checks["documentation_freeze_passed"]:
        decision = "v090_rc_blocked_by_documentation"
        blocking = ["documentation_freeze_failed"]
    else:
        decision = "v090_rc_failed"
        blocking = ["known_blocked_state_disclosure_failed"]
    return {
        "decision_id": "A-SHARE-V090-RELEASE-CANDIDATE-DECISION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "allowed_decisions": [
            "v090_rc_passed_with_known_blocked_owner_readiness",
            "v090_rc_failed",
            "v090_rc_blocked_by_regression",
            "v090_rc_blocked_by_audit_sweep",
            "v090_rc_blocked_by_boundary",
            "v090_rc_blocked_by_documentation",
        ],
        "decision": decision,
        "checks": checks,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
    }
