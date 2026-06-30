"""Input availability checks for owner readiness gate."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_owner_readiness_gate.gate_config import BASELINE_VERSION, DEFAULT_AS_OF_DATE, SOURCE_WORKFLOW_MODE, TARGET_VERSION
from trading_core.equity_owner_readiness_gate.io import load_json
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths

HISTORY_KEYS = {
    "daily_pack_history_config": "daily_pack_history_config.json",
    "daily_pack_history_input_availability": "daily_pack_history_input_availability.json",
    "daily_pack_history_source_resolution": "daily_pack_history_source_resolution.json",
    "daily_pack_history_date_alignment": "daily_pack_history_date_alignment.json",
    "daily_pack_run_record": "daily_pack_run_record.json",
    "daily_pack_history_append_result": "daily_pack_history_append_result.json",
    "daily_pack_history_snapshot": "daily_pack_history_snapshot.json",
    "owner_readiness_score": "owner_readiness_score.json",
    "owner_readiness_history": "owner_readiness_history.json",
    "owner_readiness_trend_sufficiency": "owner_readiness_trend_sufficiency.json",
    "daily_pack_quality_baseline": "daily_pack_quality_baseline.json",
    "warning_issue_trend_baseline": "warning_issue_trend_baseline.json",
    "safe_action_trend_baseline": "safe_action_trend_baseline.json",
    "protected_path_trend_baseline": "protected_path_trend_baseline.json",
    "boundary_trend_baseline": "boundary_trend_baseline.json",
    "source_trace_quality_trend": "source_trace_quality_trend.json",
    "daily_pack_completeness_trend": "daily_pack_completeness_trend.json",
    "owner_next_step_trend": "owner_next_step_trend.json",
    "daily_pack_history_source_trace": "daily_pack_history_source_trace.json",
    "daily_pack_history_boundary_check": "daily_pack_history_boundary_check.json",
    "daily_pack_history_manifest": "daily_pack_history_manifest.json",
    "daily_pack_history_summary": "daily_pack_history_summary.json",
}

DAILY_PACK_KEYS = {
    "owner_daily_status_brief": "owner_daily_status_brief.json",
    "owner_operations_decision_pack": "owner_operations_decision_pack.json",
    "owner_next_step_checklist": "owner_next_step_checklist.json",
    "warning_issue_digest": "warning_issue_digest.json",
    "safe_action_digest": "safe_action_digest.json",
    "protected_path_digest": "protected_path_digest.json",
    "boundary_digest": "boundary_digest.json",
    "daily_pack_manifest": "daily_pack_manifest.json",
}


def input_paths(paths: ProjectPaths, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict[str, Path]:
    paths = default_paths(paths)
    history_dir = paths.data_dir / "equity_owner_daily_pack_history" / "daily" / as_of_date
    daily_pack_dir = paths.data_dir / "equity_owner_daily_pack" / "daily" / as_of_date
    sources = {key: history_dir / name for key, name in HISTORY_KEYS.items()}
    sources.update({key: daily_pack_dir / name for key, name in DAILY_PACK_KEYS.items()})
    sources["owner_daily_pack_history_audit"] = paths.data_dir / "equity_data_quality" / "a_share_owner_daily_pack_history_audit.json"
    sources["owner_daily_pack_audit"] = paths.data_dir / "equity_data_quality" / "a_share_owner_daily_pack_audit.json"
    return sources


def build_input_availability(*, paths: ProjectPaths | None = None, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict[str, Any]:
    paths = default_paths(paths)
    sources = input_paths(paths, as_of_date)
    missing = sorted(key for key, path in sources.items() if not path.exists())
    history_audit = load_json(sources["owner_daily_pack_history_audit"])
    daily_pack_audit = load_json(sources["owner_daily_pack_audit"])
    history_manifest = load_json(sources["daily_pack_history_manifest"])
    history_boundary = load_json(sources["daily_pack_history_boundary_check"])
    blocking: list[str] = []
    if missing:
        blocking.append("required_inputs_missing")
    if history_audit.get("overall_passed") is not True:
        blocking.append("owner_daily_pack_history_audit_not_passed")
    if daily_pack_audit.get("overall_passed") is not True:
        blocking.append("owner_daily_pack_audit_not_passed")
    if history_audit.get("recommended_next_version") != TARGET_VERSION:
        blocking.append("owner_daily_pack_history_recommended_next_version_mismatch")
    if history_manifest.get("target_version") != BASELINE_VERSION:
        blocking.append("owner_daily_pack_history_manifest_version_mismatch")
    if history_boundary.get("overall_passed") is not True:
        blocking.append("owner_daily_pack_history_boundary_not_clean")
    return {
        "availability_id": "A-SHARE-OWNER-READINESS-GATE-INPUT-AVAILABILITY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": SOURCE_WORKFLOW_MODE,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
        "missing_required_inputs": missing,
        "owner_daily_pack_history_audit_passed": history_audit.get("overall_passed") is True,
        "owner_daily_pack_audit_passed": daily_pack_audit.get("overall_passed") is True,
        "boundary_clean": history_boundary.get("overall_passed") is True,
        "source_artifacts": {key: str(path) for key, path in sources.items()},
    }
