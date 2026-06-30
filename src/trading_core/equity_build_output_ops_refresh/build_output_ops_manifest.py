"""Manifest and summary for build-output ops refresh."""

from __future__ import annotations

from datetime import UTC, datetime

from trading_core.equity_build_output_ops_refresh.build_output_ops_config import RECOMMENDED_NEXT_VERSION, TARGET_VERSION
from trading_core.system.common import relative


def build_manifest(*, as_of_date: str, mode: str, payloads: dict, source_trace: dict, boundary: dict, output_artifacts: dict, source_artifacts: dict, paths) -> dict:
    health = payloads["build_output_health_score_refresh"]
    action = payloads["build_output_action_summary_refresh"]
    comparison = payloads["original_ops_vs_build_output_ops_comparison"]
    return {
        "manifest_id": "A-SHARE-BUILD-OUTPUT-OPS-REFRESH-MANIFEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "mode": mode,
        "source_workflow_mode": "build_from_existing_data",
        "monitoring_refresh_performed": True,
        "remediation_refresh_performed": True,
        "ops_center_refresh_performed": True,
        "ops_history_refresh_performed": True,
        "build_from_existing_data_rerun": False,
        "execute_remediation_actions": False,
        "external_notifications_sent": False,
        "automatic_action_count": action.get("automatic_action_count", 0),
        "health_score": health.get("score"),
        "health_grade": health.get("grade"),
        "overall_status": health.get("overall_status"),
        "comparison_completed": comparison.get("comparison_completed", False),
        "blocking_reasons": boundary.get("blocking_reasons", []),
        "warnings": boundary.get("warnings", []),
        "output_artifacts": {k: relative(v, paths.project_root) for k, v in output_artifacts.items()},
        "source_artifacts": {k: relative(v, paths.project_root) for k, v in source_artifacts.items()},
        "boundary": boundary,
        "source_trace_complete": source_trace.get("source_trace_complete", False),
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def build_summary(*, as_of_date: str, mode: str, manifest: dict, input_availability: dict, source_resolution: dict, comparison: dict) -> dict:
    return {
        "summary_id": "A-SHARE-BUILD-OUTPUT-OPS-REFRESH-SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "mode": mode,
        "source_workflow_mode": "build_from_existing_data",
        "overall_passed": not manifest.get("blocking_reasons", []),
        "overall_status": manifest.get("overall_status"),
        "blocking_reasons": manifest.get("blocking_reasons", []),
        "warnings": manifest.get("warnings", []),
        "build_output_dashboard_audit_passed": input_availability.get("build_output_dashboard_audit_passed", False),
        "repeatability_audit_passed": input_availability.get("repeatability_audit_passed", False),
        "gated_build_audit_passed": input_availability.get("gated_build_audit_passed", False),
        "original_monitoring_audit_passed": input_availability.get("original_monitoring_audit_passed", False),
        "original_remediation_audit_passed": input_availability.get("original_remediation_audit_passed", False),
        "original_ops_center_audit_passed": input_availability.get("original_ops_center_audit_passed", False),
        "monitoring_refresh_performed": manifest.get("monitoring_refresh_performed", False),
        "remediation_refresh_performed": manifest.get("remediation_refresh_performed", False),
        "ops_center_refresh_performed": manifest.get("ops_center_refresh_performed", False),
        "ops_history_refresh_performed": manifest.get("ops_history_refresh_performed", False),
        "build_from_existing_data_rerun": False,
        "business_output_drift_count": source_resolution.get("business_output_drift_count"),
        "protected_path_modifications_detected": source_resolution.get("protected_path_modifications_detected"),
        "execute_remediation_actions": False,
        "external_notifications_sent": False,
        "automatic_action_count": manifest.get("automatic_action_count", 0),
        "comparison_completed": comparison.get("comparison_completed", False),
        "ops_health_score": manifest.get("health_score"),
        "ops_health_grade": manifest.get("health_grade"),
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }

