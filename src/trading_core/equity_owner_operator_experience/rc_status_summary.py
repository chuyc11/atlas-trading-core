"""v0.9.0 RC status summary for operator view."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_operator_experience.operator_config import DEFAULT_AS_OF_DATE, SOURCE_RELEASE_CANDIDATE, TARGET_VERSION


def build_rc_status_summary(*, as_of_date: str = DEFAULT_AS_OF_DATE, audit: dict[str, Any], decision: dict[str, Any], summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "summary_id": "A-SHARE-RC-STATUS-SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_release": SOURCE_RELEASE_CANDIDATE,
        "v090_rc_audit_passed": audit.get("overall_passed") is True,
        "release_candidate_decision": decision.get("decision"),
        "v090_full_pytest_passed": summary.get("full_pytest_passed") is True,
        "v090_audit_sweep_passed": summary.get("audit_sweep_passed") is True,
        "known_owner_readiness_state": summary.get("known_owner_readiness_state"),
        "owner_operationally_acceptable": summary.get("owner_operationally_acceptable"),
        "overall_passed": audit.get("overall_passed") is True and decision.get("decision") == "v090_rc_passed_with_known_blocked_owner_readiness",
        "blocking_reasons": [],
        "warnings": [],
    }
