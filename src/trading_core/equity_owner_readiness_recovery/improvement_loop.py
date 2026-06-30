"""Quality improvement loop definition."""

from __future__ import annotations

from trading_core.equity_owner_readiness_recovery.recovery_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_quality_improvement_loop_definition(*, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict:
    return {
        "loop_id": "A-SHARE-QUALITY-IMPROVEMENT-LOOP-DEFINITION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "steps": [
            "inspect blocked gate",
            "classify exceptions",
            "map root causes",
            "define recovery tasks",
            "collect evidence",
            "run audit-only verification",
            "prepare gate reevaluation",
            "rerun gate only in future controlled version",
        ],
        "executes_audit_only_verification_now": False,
        "executes_gate_reevaluation_now": False,
    }
