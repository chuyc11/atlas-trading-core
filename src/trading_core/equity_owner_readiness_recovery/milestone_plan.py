"""Recovery milestone plan."""

from __future__ import annotations

from trading_core.equity_owner_readiness_recovery.recovery_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_recovery_milestone_plan(*, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict:
    milestones = [
        "M1_exception_understanding_complete",
        "M2_developer_follow_up_defined",
        "M3_quality_fix_candidate_defined",
        "M4_audit_only_verification_ready",
        "M5_gate_reevaluation_ready",
    ]
    return {
        "plan_id": "A-SHARE-RECOVERY-MILESTONE-PLAN",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "milestones": [
            {
                "milestone_id": milestone,
                "title_zh": milestone,
                "entry_criteria": ["prior milestone evidence exists"],
                "exit_criteria": ["required evidence reviewed"],
                "required_evidence": ["audit-only evidence"],
                "status": "planned",
            }
            for milestone in milestones
        ],
    }
