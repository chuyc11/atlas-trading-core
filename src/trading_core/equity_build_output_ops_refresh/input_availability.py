"""Input availability for build-output ops refresh."""

from __future__ import annotations

import json
from pathlib import Path

from trading_core.equity_build_output_ops_refresh.build_output_ops_config import (
    BASELINE_VERSION,
    RECOMMENDED_NEXT_VERSION,
    TARGET_VERSION,
)
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


REQUIRED_INPUTS = {
    "build_output_dashboard_audit": "data/equity_data_quality/a_share_build_output_owner_dashboard_audit.json",
    "build_output_dashboard_config": "data/equity_build_output_dashboard/daily/{as_of_date}/build_output_dashboard_config.json",
    "build_output_input_availability": "data/equity_build_output_dashboard/daily/{as_of_date}/build_output_input_availability.json",
    "build_output_source_resolution": "data/equity_build_output_dashboard/daily/{as_of_date}/build_output_source_resolution.json",
    "build_output_date_alignment": "data/equity_build_output_dashboard/daily/{as_of_date}/build_output_date_alignment.json",
    "build_output_executive_status_card": "data/equity_build_output_dashboard/daily/{as_of_date}/build_output_executive_status_card.json",
    "build_output_data_freshness_card": "data/equity_build_output_dashboard/daily/{as_of_date}/build_output_data_freshness_card.json",
    "build_output_workflow_status_card": "data/equity_build_output_dashboard/daily/{as_of_date}/build_output_workflow_status_card.json",
    "build_output_research_output_card": "data/equity_build_output_dashboard/daily/{as_of_date}/build_output_research_output_card.json",
    "build_output_repeatability_card": "data/equity_build_output_dashboard/daily/{as_of_date}/build_output_repeatability_card.json",
    "build_output_protected_path_card": "data/equity_build_output_dashboard/daily/{as_of_date}/build_output_protected_path_card.json",
    "build_output_warning_and_blocker_card": "data/equity_build_output_dashboard/daily/{as_of_date}/build_output_warning_and_blocker_card.json",
    "build_output_artifact_navigation": "data/equity_build_output_dashboard/daily/{as_of_date}/build_output_artifact_navigation.json",
    "validate_dashboard_vs_build_dashboard_comparison": "data/equity_build_output_dashboard/daily/{as_of_date}/validate_dashboard_vs_build_dashboard_comparison.json",
    "build_output_dashboard_source_trace": "data/equity_build_output_dashboard/daily/{as_of_date}/build_output_dashboard_source_trace.json",
    "build_output_dashboard_boundary_check": "data/equity_build_output_dashboard/daily/{as_of_date}/build_output_dashboard_boundary_check.json",
    "build_output_dashboard_manifest": "data/equity_build_output_dashboard/daily/{as_of_date}/build_output_dashboard_manifest.json",
    "build_output_dashboard_summary": "data/equity_build_output_dashboard/daily/{as_of_date}/build_output_dashboard_summary.json",
    "repeatability_summary": "data/equity_build_repeatability/daily/{as_of_date}/repeatability_summary.json",
    "repeatability_drift_summary": "data/equity_build_repeatability/daily/{as_of_date}/repeatability_drift_summary.json",
    "protected_path_modification_check": "data/equity_build_repeatability/daily/{as_of_date}/protected_path_modification_check.json",
    "repeatability_boundary_check": "data/equity_build_repeatability/daily/{as_of_date}/repeatability_boundary_check.json",
    "repeatability_manifest": "data/equity_build_repeatability/daily/{as_of_date}/repeatability_manifest.json",
    "repeatability_audit": "data/equity_data_quality/a_share_build_repeatability_audit.json",
    "gated_build_summary": "data/equity_current_day_builds/daily/{as_of_date}/gated_build_summary.json",
    "build_from_existing_data_workflow_result": "data/equity_current_day_builds/daily/{as_of_date}/build_from_existing_data_workflow_result.json",
    "gated_build_warning_summary": "data/equity_current_day_builds/daily/{as_of_date}/gated_build_warning_summary.json",
    "gated_build_boundary_check": "data/equity_current_day_builds/daily/{as_of_date}/gated_build_boundary_check.json",
    "gated_build_manifest": "data/equity_current_day_builds/daily/{as_of_date}/gated_build_manifest.json",
    "gated_build_audit": "data/equity_data_quality/a_share_gated_build_from_existing_data_audit.json",
    "ops_health_score_card": "data/equity_ops_center/daily/{as_of_date}/ops_health_score_card.json",
    "ops_module_status_matrix": "data/equity_ops_center/daily/{as_of_date}/ops_module_status_matrix.json",
    "ops_issue_summary": "data/equity_ops_center/daily/{as_of_date}/ops_issue_summary.json",
    "ops_action_summary": "data/equity_ops_center/daily/{as_of_date}/ops_action_summary.json",
    "ops_owner_next_steps": "data/equity_ops_center/daily/{as_of_date}/ops_owner_next_steps.json",
    "ops_boundary_check": "data/equity_ops_center/daily/{as_of_date}/ops_boundary_check.json",
    "ops_manifest": "data/equity_ops_center/daily/{as_of_date}/ops_manifest.json",
    "ops_center_audit": "data/equity_data_quality/a_share_daily_ops_center_audit.json",
    "remediation_priority_summary": "data/equity_owner_remediation/daily/{as_of_date}/remediation_priority_summary.json",
    "safe_owner_action_checklist": "data/equity_owner_remediation/daily/{as_of_date}/safe_owner_action_checklist.json",
    "non_actionable_issue_list": "data/equity_owner_remediation/daily/{as_of_date}/non_actionable_issue_list.json",
    "dry_run_remediation_plan": "data/equity_owner_remediation/daily/{as_of_date}/dry_run_remediation_plan.json",
    "remediation_boundary_check": "data/equity_owner_remediation/daily/{as_of_date}/remediation_boundary_check.json",
    "remediation_manifest": "data/equity_owner_remediation/daily/{as_of_date}/remediation_manifest.json",
    "remediation_audit": "data/equity_data_quality/a_share_owner_remediation_audit.json",
    "monitoring_status_card": "data/equity_owner_monitoring/daily/{as_of_date}/monitoring_status_card.json",
    "owner_alert_summary_card": "data/equity_owner_monitoring/daily/{as_of_date}/owner_alert_summary_card.json",
    "alert_evaluation_result": "data/equity_owner_monitoring/daily/{as_of_date}/alert_evaluation_result.json",
    "alert_event_log": "data/equity_owner_monitoring/daily/{as_of_date}/alert_event_log.json",
    "monitoring_boundary_check": "data/equity_owner_monitoring/daily/{as_of_date}/monitoring_boundary_check.json",
    "monitoring_manifest": "data/equity_owner_monitoring/daily/{as_of_date}/monitoring_manifest.json",
    "monitoring_audit": "data/equity_data_quality/a_share_owner_monitoring_audit.json",
}

OPTIONAL_INPUTS = {
    "ops_history_audit": "data/equity_data_quality/a_share_ops_history_baseline_audit.json",
    "ops_history_snapshot": "data/equity_ops_history/daily/{as_of_date}/ops_history_snapshot.json",
}


def build_input_availability(*, paths: ProjectPaths | None, as_of_date: str) -> dict:
    paths = default_paths(paths)
    payloads: dict[str, dict] = {}
    entries = []
    blocking = []
    warnings = []
    for required, mapping in [(True, REQUIRED_INPUTS), (False, OPTIONAL_INPUTS)]:
        for artifact_id, template in mapping.items():
            path = paths.project_root / template.format(as_of_date=as_of_date)
            payload = load_json(path)
            if payload:
                payloads[artifact_id] = payload
            if required and not path.exists():
                blocking.append(f"missing_required_input:{artifact_id}")
            if not required and not path.exists():
                warnings.append(f"optional_input_missing:{artifact_id}")
            entries.append({
                "artifact_id": artifact_id,
                "path": relative(path, paths.project_root),
                "exists": path.exists(),
                "required": required,
                "as_of_date": payload.get("as_of_date") or payload.get("resolved_as_of_date"),
                "overall_passed": payload.get("overall_passed"),
                "mode": payload.get("mode"),
                "target_version": payload.get("target_version"),
            })

    dashboard_audit = payloads.get("build_output_dashboard_audit", {})
    dashboard_summary = payloads.get("build_output_dashboard_summary", {})
    repeat_audit = payloads.get("repeatability_audit", {})
    gated_audit = payloads.get("gated_build_audit", {})
    monitoring_audit = payloads.get("monitoring_audit", {})
    remediation_audit = payloads.get("remediation_audit", {})
    ops_audit = payloads.get("ops_center_audit", {})
    protected = payloads.get("protected_path_modification_check", {})

    if dashboard_audit.get("overall_passed") is not True:
        blocking.append("build_output_dashboard_audit_not_passed")
    if dashboard_audit.get("recommended_next_version") != TARGET_VERSION:
        blocking.append("build_output_dashboard_recommended_next_version_mismatch")
    if dashboard_audit.get("target_version") != BASELINE_VERSION:
        blocking.append("build_output_dashboard_target_version_mismatch")
    if repeat_audit.get("overall_passed") is not True:
        blocking.append("repeatability_audit_not_passed")
    if gated_audit.get("overall_passed") is not True:
        blocking.append("gated_build_audit_not_passed")
    if monitoring_audit.get("overall_passed") is not True:
        blocking.append("original_monitoring_audit_not_passed")
    if remediation_audit.get("overall_passed") is not True:
        blocking.append("original_remediation_audit_not_passed")
    if ops_audit.get("overall_passed") is not True:
        blocking.append("original_ops_center_audit_not_passed")
    if dashboard_summary.get("source_workflow_mode") != "build_from_existing_data":
        blocking.append("source_workflow_mode_not_build_from_existing_data")
    if dashboard_summary.get("business_output_drift_count", 1) != 0:
        blocking.append("business_output_drift_count_nonzero")
    if protected.get("protected_path_modifications_detected", True) is not False:
        blocking.append("protected_path_modifications_detected")

    return {
        "availability_id": "A-SHARE-BUILD-OUTPUT-OPS-INPUT-AVAILABILITY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": not blocking,
        "blocking_reasons": sorted(set(blocking)),
        "warnings": sorted(set(warnings)),
        "entries": entries,
        "build_output_dashboard_audit_passed": dashboard_audit.get("overall_passed") is True,
        "repeatability_audit_passed": repeat_audit.get("overall_passed") is True,
        "gated_build_audit_passed": gated_audit.get("overall_passed") is True,
        "original_monitoring_audit_passed": monitoring_audit.get("overall_passed") is True,
        "original_remediation_audit_passed": remediation_audit.get("overall_passed") is True,
        "original_ops_center_audit_passed": ops_audit.get("overall_passed") is True,
        "source_workflow_mode": dashboard_summary.get("source_workflow_mode"),
        "business_output_drift_count": dashboard_summary.get("business_output_drift_count"),
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

