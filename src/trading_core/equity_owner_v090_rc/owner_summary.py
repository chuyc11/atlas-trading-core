"""Owner-facing summary payload for v0.9.0 RC."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_v090_rc.v090_config import DEFAULT_AS_OF_DATE, RECOMMENDED_NEXT_VERSION, TARGET_VERSION


def build_owner_release_summary(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    availability: dict[str, Any],
    full_pytest: dict[str, Any],
    audit_sweep: dict[str, Any],
    boundary_sweep: dict[str, Any],
    source_trace_sweep: dict[str, Any],
    documentation_freeze: dict[str, Any],
    disclosure: dict[str, Any],
    decision: dict[str, Any],
) -> dict[str, Any]:
    return {
        "summary_id": "A-SHARE-OWNER-V090-RC-RELEASE-SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_gate_decision": availability.get("source_gate_decision"),
        "known_owner_readiness_state": "blocked",
        "owner_operationally_acceptable": availability.get("owner_operationally_acceptable"),
        "previous_readiness_score": availability.get("previous_readiness_score"),
        "minimum_owner_readiness_score": availability.get("minimum_owner_readiness_score"),
        "score_gap": availability.get("score_gap"),
        "blocked_state_intentional": availability.get("blocked_state_intentional"),
        "blocked_state_audited": availability.get("blocked_state_audited"),
        "blocked_state_misrepresented_as_acceptable": availability.get("blocked_state_misrepresented_as_acceptable"),
        "blocks_owner_readiness_acceptance": disclosure.get("blocks_owner_readiness_acceptance"),
        "blocks_v090_rc": disclosure.get("blocks_v090_rc"),
        "full_pytest_run": full_pytest.get("full_pytest_run"),
        "full_pytest_passed": full_pytest.get("overall_passed"),
        "full_pytest_passed_count": full_pytest.get("passed_count"),
        "full_pytest_failed_count": full_pytest.get("failed_count"),
        "full_pytest_skipped_count": full_pytest.get("skipped_count"),
        "audit_sweep_run": audit_sweep.get("audit_sweep_run"),
        "audit_sweep_passed": audit_sweep.get("audit_sweep_passed"),
        "audit_sweep_item_count": audit_sweep.get("audit_sweep_item_count"),
        "failed_audit_sweep_items": audit_sweep.get("failed_audit_sweep_items"),
        "boundary_sweep_passed": boundary_sweep.get("boundary_sweep_passed"),
        "source_trace_sweep_passed": source_trace_sweep.get("source_trace_sweep_passed"),
        "documentation_freeze_passed": documentation_freeze.get("documentation_freeze_passed"),
        "v090_release_candidate_decision": decision.get("decision"),
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
        "rerun_owner_readiness_gate": False,
        "rerun_build_from_existing_data": False,
        "rerun_daily_pack": False,
        "threshold_lowered": False,
        "auto_waiver_allowed": False,
        "manual_waiver_approval_recorded": False,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }
