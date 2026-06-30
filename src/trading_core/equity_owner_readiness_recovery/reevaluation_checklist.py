"""Gate reevaluation readiness checklist."""

from __future__ import annotations

from trading_core.equity_owner_readiness_recovery.recovery_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_gate_reevaluation_readiness_checklist(*, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict:
    checks = {
        "required_artifacts_fixed": False,
        "source_trace_complete": True,
        "boundary_clean": True,
        "warnings_mapped": False,
        "developer_follow_up_resolved": False,
        "owner_follow_up_completed": False,
        "audit_only_verification_passed": False,
        "no_threshold_lowering": True,
        "no_auto_waiver": True,
        "ready_for_future_gate_reevaluation": False,
    }
    return {"checklist_id": "A-SHARE-GATE-REEVALUATION-READINESS-CHECKLIST", "target_version": TARGET_VERSION, "as_of_date": as_of_date, **checks}
