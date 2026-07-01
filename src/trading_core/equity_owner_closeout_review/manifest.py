"""Manifest for v0.8.21 closeout review."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from trading_core.equity_owner_closeout_review.closeout_config import DEFAULT_AS_OF_DATE, RECOMMENDED_NEXT_VERSION, SOURCE_WORKFLOW_MODE, TARGET_VERSION


def build_manifest(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    output_artifacts: dict[str, Path],
    source_artifacts: dict[str, Path],
    summary: dict[str, Any],
    boundary: dict[str, Any],
    blocking_reasons: list[str],
    warnings: list[str],
) -> dict[str, Any]:
    return {
        "manifest_id": "A-SHARE-OWNER-CLOSEOUT-REVIEW-MANIFEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "source_workflow_mode": SOURCE_WORKFLOW_MODE,
        "source_gate_decision": summary.get("source_gate_decision"),
        "selected_v0820_branch": summary.get("selected_v0820_branch"),
        "previous_readiness_score": summary.get("previous_readiness_score"),
        "minimum_owner_readiness_score": summary.get("minimum_owner_readiness_score"),
        "score_gap": summary.get("score_gap"),
        "owner_operationally_acceptable": summary.get("owner_operationally_acceptable"),
        "blocked_state_intentional": summary.get("blocked_state_intentional"),
        "blocked_state_audited": summary.get("blocked_state_audited"),
        "v090_rc_scope_generated": summary.get("v090_rc_scope_generated"),
        "v090_full_regression_plan_generated": summary.get("v090_full_regression_plan_generated"),
        "v090_audit_sweep_plan_generated": summary.get("v090_audit_sweep_plan_generated"),
        "v090_documentation_freeze_checklist_generated": summary.get("v090_documentation_freeze_checklist_generated"),
        "v090_release_risk_register_generated": summary.get("v090_release_risk_register_generated"),
        "v090_release_candidate_readiness_decision": summary.get("v090_release_candidate_readiness_decision"),
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
        "execute_full_pytest": False,
        "threshold_lowered": False,
        "auto_waiver_allowed": False,
        "manual_waiver_approval_recorded": False,
        "full_pytest_run": False,
        "targeted_pytest_required": True,
        "blocking_reasons": blocking_reasons,
        "warnings": warnings,
        "output_artifacts": {key: str(path) for key, path in output_artifacts.items()},
        "source_artifacts": {key: str(path) for key, path in source_artifacts.items()},
        "boundary": boundary,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }
