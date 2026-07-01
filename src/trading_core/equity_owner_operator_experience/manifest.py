"""Manifest for owner/operator experience."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from trading_core.equity_owner_operator_experience.operator_config import DEFAULT_AS_OF_DATE, RECOMMENDED_NEXT_VERSION, SOURCE_RELEASE_CANDIDATE, TARGET_VERSION


def build_operator_manifest(
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
        "manifest_id": "A-SHARE-OWNER-OPERATOR-EXPERIENCE-MANIFEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "source_release_candidate": SOURCE_RELEASE_CANDIDATE,
        "known_owner_readiness_state": "blocked",
        "owner_operationally_acceptable": summary.get("owner_operationally_acceptable"),
        "readiness_score": summary.get("readiness_score"),
        "minimum_owner_readiness_score": summary.get("minimum_owner_readiness_score"),
        "score_gap": summary.get("score_gap"),
        "operator_experience_only": True,
        "known_blocked_state_hardening_only": True,
        "owner_daily_status_generated": True,
        "known_blocked_state_banner_generated": True,
        "operator_action_menu_generated": True,
        "artifact_navigation_index_generated": True,
        "full_pytest_run": False,
        "targeted_pytest_required": True,
        "v090_full_pytest_passed": summary.get("v090_full_pytest_passed"),
        "v090_audit_sweep_passed": summary.get("v090_audit_sweep_passed"),
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
        "rerun_owner_readiness_gate": False,
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
