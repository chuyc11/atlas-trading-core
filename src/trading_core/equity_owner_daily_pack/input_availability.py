"""Input availability for owner daily pack."""

from __future__ import annotations

import json
from pathlib import Path

from trading_core.equity_owner_daily_pack.daily_pack_config import BASELINE_VERSION, RECOMMENDED_NEXT_VERSION, TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


REQUIRED_INPUTS = {
    "build_output_ops_refresh_audit": "data/equity_data_quality/a_share_build_output_ops_refresh_audit.json",
    "build_output_ops_refresh_config": "data/equity_build_output_ops_refresh/daily/{as_of_date}/build_output_ops_refresh_config.json",
    "build_output_ops_input_availability": "data/equity_build_output_ops_refresh/daily/{as_of_date}/build_output_ops_input_availability.json",
    "build_output_ops_source_resolution": "data/equity_build_output_ops_refresh/daily/{as_of_date}/build_output_ops_source_resolution.json",
    "build_output_ops_date_alignment": "data/equity_build_output_ops_refresh/daily/{as_of_date}/build_output_ops_date_alignment.json",
    "build_output_monitoring_refresh": "data/equity_build_output_ops_refresh/daily/{as_of_date}/build_output_monitoring_refresh.json",
    "build_output_alert_summary_refresh": "data/equity_build_output_ops_refresh/daily/{as_of_date}/build_output_alert_summary_refresh.json",
    "build_output_remediation_refresh": "data/equity_build_output_ops_refresh/daily/{as_of_date}/build_output_remediation_refresh.json",
    "build_output_safe_action_refresh": "data/equity_build_output_ops_refresh/daily/{as_of_date}/build_output_safe_action_refresh.json",
    "build_output_ops_center_refresh": "data/equity_build_output_ops_refresh/daily/{as_of_date}/build_output_ops_center_refresh.json",
    "build_output_ops_history_refresh": "data/equity_build_output_ops_refresh/daily/{as_of_date}/build_output_ops_history_refresh.json",
    "build_output_health_score_refresh": "data/equity_build_output_ops_refresh/daily/{as_of_date}/build_output_health_score_refresh.json",
    "build_output_module_status_matrix_refresh": "data/equity_build_output_ops_refresh/daily/{as_of_date}/build_output_module_status_matrix_refresh.json",
    "build_output_issue_summary_refresh": "data/equity_build_output_ops_refresh/daily/{as_of_date}/build_output_issue_summary_refresh.json",
    "build_output_action_summary_refresh": "data/equity_build_output_ops_refresh/daily/{as_of_date}/build_output_action_summary_refresh.json",
    "build_output_owner_next_steps_refresh": "data/equity_build_output_ops_refresh/daily/{as_of_date}/build_output_owner_next_steps_refresh.json",
    "original_ops_vs_build_output_ops_comparison": "data/equity_build_output_ops_refresh/daily/{as_of_date}/original_ops_vs_build_output_ops_comparison.json",
    "build_output_ops_artifact_navigation": "data/equity_build_output_ops_refresh/daily/{as_of_date}/build_output_ops_artifact_navigation.json",
    "build_output_ops_source_trace": "data/equity_build_output_ops_refresh/daily/{as_of_date}/build_output_ops_source_trace.json",
    "build_output_ops_boundary_check": "data/equity_build_output_ops_refresh/daily/{as_of_date}/build_output_ops_boundary_check.json",
    "build_output_ops_manifest": "data/equity_build_output_ops_refresh/daily/{as_of_date}/build_output_ops_manifest.json",
    "build_output_ops_summary": "data/equity_build_output_ops_refresh/daily/{as_of_date}/build_output_ops_summary.json",
    "build_output_dashboard_summary": "data/equity_build_output_dashboard/daily/{as_of_date}/build_output_dashboard_summary.json",
    "build_output_executive_status_card": "data/equity_build_output_dashboard/daily/{as_of_date}/build_output_executive_status_card.json",
    "build_output_research_output_card": "data/equity_build_output_dashboard/daily/{as_of_date}/build_output_research_output_card.json",
    "build_output_candidate_summary_card": "data/equity_build_output_dashboard/daily/{as_of_date}/build_output_candidate_summary_card.json",
    "build_output_portfolio_summary_card": "data/equity_build_output_dashboard/daily/{as_of_date}/build_output_portfolio_summary_card.json",
    "build_output_repeatability_card": "data/equity_build_output_dashboard/daily/{as_of_date}/build_output_repeatability_card.json",
    "build_output_protected_path_card": "data/equity_build_output_dashboard/daily/{as_of_date}/build_output_protected_path_card.json",
    "build_output_warning_and_blocker_card": "data/equity_build_output_dashboard/daily/{as_of_date}/build_output_warning_and_blocker_card.json",
    "build_output_artifact_navigation": "data/equity_build_output_dashboard/daily/{as_of_date}/build_output_artifact_navigation.json",
    "build_output_dashboard_boundary_check": "data/equity_build_output_dashboard/daily/{as_of_date}/build_output_dashboard_boundary_check.json",
    "build_output_owner_dashboard_audit": "data/equity_data_quality/a_share_build_output_owner_dashboard_audit.json",
    "repeatability_summary": "data/equity_build_repeatability/daily/{as_of_date}/repeatability_summary.json",
    "repeatability_drift_summary": "data/equity_build_repeatability/daily/{as_of_date}/repeatability_drift_summary.json",
    "protected_path_modification_check": "data/equity_build_repeatability/daily/{as_of_date}/protected_path_modification_check.json",
    "repeatability_boundary_check": "data/equity_build_repeatability/daily/{as_of_date}/repeatability_boundary_check.json",
    "repeatability_audit": "data/equity_data_quality/a_share_build_repeatability_audit.json",
    "gated_build_summary": "data/equity_current_day_builds/daily/{as_of_date}/gated_build_summary.json",
    "build_from_existing_data_workflow_result": "data/equity_current_day_builds/daily/{as_of_date}/build_from_existing_data_workflow_result.json",
    "gated_build_warning_summary": "data/equity_current_day_builds/daily/{as_of_date}/gated_build_warning_summary.json",
    "gated_build_boundary_check": "data/equity_current_day_builds/daily/{as_of_date}/gated_build_boundary_check.json",
    "gated_build_audit": "data/equity_data_quality/a_share_gated_build_from_existing_data_audit.json",
    "data_refresh_summary": "data/equity_data_refresh/daily/{as_of_date}/data_refresh_summary.json",
    "dataset_freshness_validation": "data/equity_data_refresh/daily/{as_of_date}/dataset_freshness_validation.json",
    "dataset_coverage_summary": "data/equity_data_refresh/daily/{as_of_date}/dataset_coverage_summary.json",
    "data_refresh_boundary_check": "data/equity_data_refresh/daily/{as_of_date}/data_refresh_boundary_check.json",
    "data_refresh_audit": "data/equity_data_quality/a_share_daily_data_refresh_audit.json",
}


def build_input_availability(*, paths: ProjectPaths | None, as_of_date: str) -> dict:
    paths = default_paths(paths)
    payloads: dict[str, dict] = {}
    entries = []
    blocking = []
    for artifact_id, template in REQUIRED_INPUTS.items():
        path = paths.project_root / template.format(as_of_date=as_of_date)
        payload = load_json(path)
        if payload:
            payloads[artifact_id] = payload
        if not path.exists():
            blocking.append(f"missing_required_input:{artifact_id}")
        entries.append({
            "artifact_id": artifact_id,
            "path": relative(path, paths.project_root),
            "exists": path.exists(),
            "required": True,
            "as_of_date": payload.get("as_of_date") or payload.get("resolved_as_of_date"),
            "overall_passed": payload.get("overall_passed"),
            "target_version": payload.get("target_version"),
        })

    ops_audit = payloads.get("build_output_ops_refresh_audit", {})
    ops_summary = payloads.get("build_output_ops_summary", {})
    dashboard_audit = payloads.get("build_output_owner_dashboard_audit", {})
    repeat_audit = payloads.get("repeatability_audit", {})
    gated_audit = payloads.get("gated_build_audit", {})
    refresh_audit = payloads.get("data_refresh_audit", {})
    protected = payloads.get("protected_path_modification_check", {})
    if ops_audit.get("overall_passed") is not True:
        blocking.append("build_output_ops_refresh_audit_not_passed")
    if ops_audit.get("target_version") != BASELINE_VERSION:
        blocking.append("build_output_ops_refresh_target_version_mismatch")
    if ops_audit.get("recommended_next_version") != TARGET_VERSION:
        blocking.append("build_output_ops_refresh_recommended_next_version_mismatch")
    if dashboard_audit.get("overall_passed") is not True:
        blocking.append("build_output_dashboard_audit_not_passed")
    if repeat_audit.get("overall_passed") is not True:
        blocking.append("repeatability_audit_not_passed")
    if gated_audit.get("overall_passed") is not True:
        blocking.append("gated_build_audit_not_passed")
    if refresh_audit.get("overall_passed") is not True:
        blocking.append("data_refresh_audit_not_passed")
    if ops_summary.get("source_workflow_mode") != "build_from_existing_data":
        blocking.append("source_workflow_mode_not_build_from_existing_data")
    if ops_summary.get("business_output_drift_count", 1) != 0:
        blocking.append("business_output_drift_count_nonzero")
    if protected.get("protected_path_modifications_detected", True) is not False:
        blocking.append("protected_path_modifications_detected")
    return {
        "availability_id": "A-SHARE-OWNER-DAILY-PACK-INPUT-AVAILABILITY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": not blocking,
        "blocking_reasons": sorted(set(blocking)),
        "warnings": [],
        "entries": entries,
        "build_output_ops_refresh_audit_passed": ops_audit.get("overall_passed") is True,
        "build_output_dashboard_audit_passed": dashboard_audit.get("overall_passed") is True,
        "repeatability_audit_passed": repeat_audit.get("overall_passed") is True,
        "gated_build_audit_passed": gated_audit.get("overall_passed") is True,
        "data_refresh_audit_passed": refresh_audit.get("overall_passed") is True,
        "source_workflow_mode": ops_summary.get("source_workflow_mode"),
        "business_output_drift_count": ops_summary.get("business_output_drift_count"),
        "protected_path_modifications_detected": protected.get("protected_path_modifications_detected"),
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}

