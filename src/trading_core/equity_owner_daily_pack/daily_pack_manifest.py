"""Manifest and summary for owner daily pack."""

from __future__ import annotations

from datetime import UTC, datetime

from trading_core.equity_owner_daily_pack.daily_pack_config import RECOMMENDED_NEXT_VERSION, TARGET_VERSION
from trading_core.system.common import relative


def build_manifest(*, as_of_date: str, mode: str, payloads: dict, source_trace: dict, boundary: dict, output_artifacts: dict, source_artifacts: dict, paths) -> dict:
    status = payloads["owner_daily_status_brief"]
    decision = payloads["owner_operations_decision_pack"]
    return {
        "manifest_id": "A-SHARE-OWNER-DAILY-PACK-MANIFEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "source_workflow_mode": "build_from_existing_data",
        "mode": mode,
        "daily_pack_generated": True,
        "owner_daily_runbook_generated": True,
        "owner_operations_decision_pack_generated": True,
        "not_investment_decision_pack": decision.get("not_investment_decision_pack", False),
        "business_output_drift_count": status.get("business_output_drift_count"),
        "protected_path_modifications_detected": status.get("protected_path_modifications_detected"),
        "automatic_action_count": status.get("automatic_action_count"),
        "execute_remediation_actions": False,
        "external_notifications_sent": False,
        "overall_status": status.get("overall_status"),
        "blocking_reasons": boundary.get("blocking_reasons", []),
        "warnings": boundary.get("warnings", []),
        "output_artifacts": {k: relative(v, paths.project_root) for k, v in output_artifacts.items()},
        "source_artifacts": {k: relative(v, paths.project_root) for k, v in source_artifacts.items()},
        "boundary": boundary,
        "source_trace_complete": source_trace.get("source_trace_complete", False),
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def build_summary(*, as_of_date: str, mode: str, manifest: dict, input_availability: dict, decision_pack: dict) -> dict:
    return {
        "summary_id": "A-SHARE-OWNER-DAILY-PACK-SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "mode": mode,
        "source_workflow_mode": "build_from_existing_data",
        "overall_passed": not manifest.get("blocking_reasons", []),
        "overall_status": manifest.get("overall_status"),
        "blocking_reasons": manifest.get("blocking_reasons", []),
        "warnings": manifest.get("warnings", []),
        "daily_pack_generated": manifest.get("daily_pack_generated", False),
        "owner_daily_runbook_generated": manifest.get("owner_daily_runbook_generated", False),
        "owner_operations_decision_pack_generated": manifest.get("owner_operations_decision_pack_generated", False),
        "not_investment_decision_pack": manifest.get("not_investment_decision_pack", False),
        "build_output_ops_refresh_audit_passed": input_availability.get("build_output_ops_refresh_audit_passed", False),
        "build_output_dashboard_audit_passed": input_availability.get("build_output_dashboard_audit_passed", False),
        "repeatability_audit_passed": input_availability.get("repeatability_audit_passed", False),
        "gated_build_audit_passed": input_availability.get("gated_build_audit_passed", False),
        "business_output_drift_count": manifest.get("business_output_drift_count"),
        "protected_path_modifications_detected": manifest.get("protected_path_modifications_detected"),
        "automatic_action_count": manifest.get("automatic_action_count"),
        "execute_remediation_actions": False,
        "external_notifications_sent": False,
        "forbidden_decision_categories_detected": decision_pack.get("forbidden_decision_categories_detected", []),
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }

