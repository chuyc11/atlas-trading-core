"""Manifest for v0.8.20 owner gate outcome."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from trading_core.equity_owner_v0820_gate_outcome.outcome_config import DEFAULT_AS_OF_DATE, RECOMMENDED_NEXT_VERSION, SOURCE_WORKFLOW_MODE, TARGET_VERSION


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
        "manifest_id": "A-SHARE-OWNER-V0820-GATE-OUTCOME-MANIFEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "source_workflow_mode": SOURCE_WORKFLOW_MODE,
        "source_gate_decision": summary.get("source_gate_decision"),
        "selected_branch": summary.get("selected_branch"),
        "branch_decision_consistent": summary.get("branch_decision_consistent"),
        "controlled_reevaluation_executed": summary.get("controlled_reevaluation_executed"),
        "final_blocked_closeout_generated": summary.get("final_blocked_closeout_generated"),
        "previous_readiness_score": summary.get("previous_readiness_score"),
        "minimum_owner_readiness_score": summary.get("minimum_owner_readiness_score"),
        "new_controlled_readiness_score_generated": summary.get("new_controlled_readiness_score_generated"),
        "new_controlled_gate_decision_generated": summary.get("new_controlled_gate_decision_generated"),
        "owner_operationally_acceptable": summary.get("owner_operationally_acceptable"),
        "threshold_lowered": False,
        "auto_waiver_allowed": False,
        "manual_waiver_approval_recorded": False,
        "waiver_used_for_outcome": False,
        "full_pytest_run": False,
        "targeted_pytest_required": True,
        "blocking_reasons": blocking_reasons,
        "warnings": warnings,
        "output_artifacts": {key: str(path) for key, path in output_artifacts.items()},
        "source_artifacts": {key: str(path) for key, path in source_artifacts.items()},
        "boundary": boundary,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }

