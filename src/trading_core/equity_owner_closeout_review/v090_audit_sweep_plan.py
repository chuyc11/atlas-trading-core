"""v0.9.0 audit sweep plan."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_closeout_review.closeout_config import DEFAULT_AS_OF_DATE, TARGET_VERSION

AUDITS = [
    ("v0813_owner_readiness_gate", "python -m trading_core.cli audit-a-share-owner-readiness-gate --as-of-date 2026-06-26", "data/equity_data_quality/a_share_owner_readiness_gate_audit.json"),
    ("v0814_quality_exception_workflow", "python -m trading_core.cli audit-a-share-owner-quality-exceptions --as-of-date 2026-06-26", "data/equity_data_quality/a_share_owner_quality_exception_workflow_audit.json"),
    ("v0815_recovery_plan", "python -m trading_core.cli audit-a-share-owner-readiness-recovery --as-of-date 2026-06-26", "data/equity_data_quality/a_share_owner_readiness_recovery_audit.json"),
    ("v0816_recovery_execution", "python -m trading_core.cli audit-a-share-owner-readiness-recovery-execution --as-of-date 2026-06-26", "data/equity_data_quality/a_share_owner_readiness_recovery_execution_audit.json"),
    ("v0817_controlled_reevaluation", "python -m trading_core.cli audit-a-share-owner-controlled-gate-reevaluation --as-of-date 2026-06-26", "data/equity_data_quality/a_share_owner_controlled_gate_reevaluation_audit.json"),
    ("v0818_recovery_evidence", "python -m trading_core.cli audit-a-share-owner-recovery-evidence --as-of-date 2026-06-26", "data/equity_data_quality/a_share_owner_recovery_evidence_audit.json"),
    ("v0819_evidence_backed_prep", "python -m trading_core.cli audit-a-share-owner-evidence-backed-reevaluation-prep --as-of-date 2026-06-26", "data/equity_data_quality/a_share_owner_evidence_backed_reevaluation_prep_audit.json"),
    ("v0820_gate_outcome", "python -m trading_core.cli audit-a-share-owner-v0820-gate-outcome --as-of-date 2026-06-26", "data/equity_data_quality/a_share_owner_v0820_gate_outcome_audit.json"),
    ("v0821_closeout_review", "python -m trading_core.cli audit-a-share-owner-closeout-review --as-of-date 2026-06-26", "data/equity_data_quality/a_share_owner_closeout_review_audit.json"),
]


def build_v090_audit_sweep_plan(*, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict[str, Any]:
    items = [
        {
            "audit_id": audit_id,
            "audit_command": command,
            "required_artifact": artifact,
            "expected_overall_passed": True,
            "expected_blocking_reasons": [],
            "expected_safety_boundary": "research_only_virtual_only_no_broker_no_orders_no_signals",
            "owner_visible": True,
            "blocks_v090_rc_if_failed": True,
        }
        for audit_id, command, artifact in AUDITS
    ]
    return {
        "plan_id": "A-SHARE-V090-AUDIT-SWEEP-PLAN",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": True,
        "blocking_reasons": [],
        "warnings": [],
        "audit_count": len(items),
        "audits": items,
    }
