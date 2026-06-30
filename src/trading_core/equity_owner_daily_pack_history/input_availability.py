"""Input availability for v0.8.12 owner daily pack history."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from trading_core.equity_owner_daily_pack_history.daily_pack_history_config import BASELINE_VERSION, TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


REQUIRED_INPUTS = {
    "owner_daily_pack_audit": "data/equity_data_quality/a_share_owner_daily_pack_audit.json",
    "daily_pack_config": "data/equity_owner_daily_pack/daily/{as_of_date}/daily_pack_config.json",
    "daily_pack_input_availability": "data/equity_owner_daily_pack/daily/{as_of_date}/daily_pack_input_availability.json",
    "daily_pack_source_resolution": "data/equity_owner_daily_pack/daily/{as_of_date}/daily_pack_source_resolution.json",
    "daily_pack_date_alignment": "data/equity_owner_daily_pack/daily/{as_of_date}/daily_pack_date_alignment.json",
    "owner_daily_status_brief": "data/equity_owner_daily_pack/daily/{as_of_date}/owner_daily_status_brief.json",
    "owner_daily_runbook": "data/equity_owner_daily_pack/daily/{as_of_date}/owner_daily_runbook.json",
    "owner_operations_decision_pack": "data/equity_owner_daily_pack/daily/{as_of_date}/owner_operations_decision_pack.json",
    "owner_next_step_checklist": "data/equity_owner_daily_pack/daily/{as_of_date}/owner_next_step_checklist.json",
    "research_output_digest": "data/equity_owner_daily_pack/daily/{as_of_date}/research_output_digest.json",
    "candidate_tracking_digest": "data/equity_owner_daily_pack/daily/{as_of_date}/candidate_tracking_digest.json",
    "virtual_portfolio_digest": "data/equity_owner_daily_pack/daily/{as_of_date}/virtual_portfolio_digest.json",
    "warning_issue_digest": "data/equity_owner_daily_pack/daily/{as_of_date}/warning_issue_digest.json",
    "safe_action_digest": "data/equity_owner_daily_pack/daily/{as_of_date}/safe_action_digest.json",
    "monitoring_remediation_ops_digest": "data/equity_owner_daily_pack/daily/{as_of_date}/monitoring_remediation_ops_digest.json",
    "protected_path_digest": "data/equity_owner_daily_pack/daily/{as_of_date}/protected_path_digest.json",
    "source_trace_digest": "data/equity_owner_daily_pack/daily/{as_of_date}/source_trace_digest.json",
    "boundary_digest": "data/equity_owner_daily_pack/daily/{as_of_date}/boundary_digest.json",
    "daily_pack_artifact_navigation": "data/equity_owner_daily_pack/daily/{as_of_date}/daily_pack_artifact_navigation.json",
    "daily_pack_source_trace": "data/equity_owner_daily_pack/daily/{as_of_date}/daily_pack_source_trace.json",
    "daily_pack_boundary_check": "data/equity_owner_daily_pack/daily/{as_of_date}/daily_pack_boundary_check.json",
    "daily_pack_manifest": "data/equity_owner_daily_pack/daily/{as_of_date}/daily_pack_manifest.json",
    "daily_pack_summary": "data/equity_owner_daily_pack/daily/{as_of_date}/daily_pack_summary.json",
}

SUPPORTING_INPUTS = {
    "build_output_ops_summary": "data/equity_build_output_ops_refresh/daily/{as_of_date}/build_output_ops_summary.json",
    "build_output_ops_manifest": "data/equity_build_output_ops_refresh/daily/{as_of_date}/build_output_ops_manifest.json",
    "build_output_ops_boundary_check": "data/equity_build_output_ops_refresh/daily/{as_of_date}/build_output_ops_boundary_check.json",
    "build_output_ops_audit": "data/equity_data_quality/a_share_build_output_ops_refresh_audit.json",
    "build_output_dashboard_summary": "data/equity_build_output_dashboard/daily/{as_of_date}/build_output_dashboard_summary.json",
    "build_output_dashboard_manifest": "data/equity_build_output_dashboard/daily/{as_of_date}/build_output_dashboard_manifest.json",
    "build_output_owner_dashboard_audit": "data/equity_data_quality/a_share_build_output_owner_dashboard_audit.json",
}


def input_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    return {key: paths.project_root / value.format(as_of_date=as_of_date) for key, value in {**REQUIRED_INPUTS, **SUPPORTING_INPUTS}.items()}


def build_input_availability(*, paths: ProjectPaths | None, as_of_date: str) -> dict[str, Any]:
    paths = default_paths(paths)
    blocking: list[str] = []
    warnings: list[str] = []
    entries: list[dict[str, Any]] = []
    payloads: dict[str, dict[str, Any]] = {}
    for artifact_id, path in input_paths(paths, as_of_date).items():
        payload = load_json(path)
        if payload:
            payloads[artifact_id] = payload
        required = artifact_id in REQUIRED_INPUTS
        if required and not path.exists():
            blocking.append(f"missing_required_input:{artifact_id}")
        if not required and not path.exists():
            warnings.append(f"missing_supporting_input:{artifact_id}")
        entries.append(
            {
                "artifact_id": artifact_id,
                "path": relative(path, paths.project_root),
                "exists": path.exists(),
                "required": required,
                "as_of_date": payload.get("as_of_date") or payload.get("resolved_as_of_date"),
                "target_version": payload.get("target_version"),
                "overall_passed": payload.get("overall_passed"),
            }
        )

    audit = payloads.get("owner_daily_pack_audit", {})
    summary = payloads.get("daily_pack_summary", {})
    boundary = payloads.get("daily_pack_boundary_check", {})
    decision = payloads.get("owner_operations_decision_pack", {})
    if audit.get("overall_passed") is not True:
        blocking.append("owner_daily_pack_audit_not_passed")
    if audit.get("target_version") != BASELINE_VERSION:
        blocking.append("owner_daily_pack_audit_target_version_mismatch")
    if audit.get("recommended_next_version") != TARGET_VERSION:
        blocking.append("owner_daily_pack_recommended_next_version_mismatch")
    if summary.get("source_workflow_mode") != "build_from_existing_data":
        blocking.append("source_workflow_mode_not_build_from_existing_data")
    if summary.get("not_investment_decision_pack") is not True or decision.get("not_investment_decision_pack") is not True:
        blocking.append("not_investment_decision_pack_false")
    if boundary.get("overall_passed") is not True or boundary.get("blocking_reasons"):
        blocking.append("daily_pack_boundary_not_clean")

    return {
        "availability_id": "A-SHARE-OWNER-DAILY-PACK-HISTORY-INPUT-AVAILABILITY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "entries": entries,
        "overall_passed": not blocking,
        "blocking_reasons": sorted(set(blocking)),
        "warnings": sorted(set(warnings)),
        "owner_daily_pack_audit_passed": audit.get("overall_passed") is True,
        "source_workflow_mode": summary.get("source_workflow_mode"),
        "not_investment_decision_pack": summary.get("not_investment_decision_pack"),
        "boundary_clean": boundary.get("overall_passed") is True and not boundary.get("blocking_reasons"),
    }


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return value if isinstance(value, dict) else {}
