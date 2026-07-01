"""Manifest for v0.9.0 RC."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from trading_core.equity_owner_v090_rc.v090_config import DEFAULT_AS_OF_DATE, RECOMMENDED_NEXT_VERSION, SOURCE_WORKFLOW_MODE, TARGET_VERSION


def build_manifest(*, as_of_date: str = DEFAULT_AS_OF_DATE, output_artifacts: dict[str, Path], source_artifacts: dict[str, Path], summary: dict[str, Any], boundary: dict[str, Any], blocking_reasons: list[str], warnings: list[str]) -> dict[str, Any]:
    return {
        "manifest_id": "A-SHARE-OWNER-V090-RC-MANIFEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "source_workflow_mode": SOURCE_WORKFLOW_MODE,
        "source_gate_decision": summary.get("source_gate_decision"),
        "known_owner_readiness_state": summary.get("known_owner_readiness_state"),
        "previous_readiness_score": summary.get("previous_readiness_score"),
        "minimum_owner_readiness_score": summary.get("minimum_owner_readiness_score"),
        "score_gap": summary.get("score_gap"),
        "owner_operationally_acceptable": summary.get("owner_operationally_acceptable"),
        "blocked_state_intentional": summary.get("blocked_state_intentional"),
        "blocked_state_audited": summary.get("blocked_state_audited"),
        "blocked_state_misrepresented_as_acceptable": summary.get("blocked_state_misrepresented_as_acceptable"),
        "full_pytest_run": summary.get("full_pytest_run"),
        "full_pytest_passed": summary.get("full_pytest_passed"),
        "full_pytest_passed_count": summary.get("full_pytest_passed_count"),
        "full_pytest_skipped_count": summary.get("full_pytest_skipped_count"),
        "audit_sweep_run": summary.get("audit_sweep_run"),
        "audit_sweep_passed": summary.get("audit_sweep_passed"),
        "boundary_sweep_passed": summary.get("boundary_sweep_passed"),
        "documentation_freeze_passed": summary.get("documentation_freeze_passed"),
        "v090_release_candidate_decision": summary.get("v090_release_candidate_decision"),
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
        "threshold_lowered": False,
        "auto_waiver_allowed": False,
        "manual_waiver_approval_recorded": False,
        "blocking_reasons": blocking_reasons,
        "warnings": warnings,
        "output_artifacts": {key: str(path) for key, path in output_artifacts.items()},
        "source_artifacts": {key: str(path) for key, path in source_artifacts.items()},
        "boundary": boundary,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }
