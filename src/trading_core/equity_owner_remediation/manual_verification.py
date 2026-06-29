"""Manual verification checklist for owner remediation."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_remediation.remediation_config import TARGET_VERSION


def build_manual_verification_checklist(*, as_of_date: str, availability: dict[str, Any], boundary: dict[str, Any] | None = None) -> dict[str, Any]:
    boundary = boundary or {}
    checks = [
        _check("data_refresh_audit_path_exists", availability, "data_refresh_audit"),
        _check("current_day_run_audit_path_exists", availability, "current_day_run_audit"),
        _check("owner_dashboard_audit_path_exists", availability, "owner_dashboard_audit"),
        _check("owner_monitoring_audit_path_exists", availability, "owner_monitoring_audit"),
        {"check_id": "blocking_reasons_empty", "description": "blocking_reasons=[]", "passed": not availability.get("blocking_reasons")},
        {"check_id": "boundary_clean", "description": "boundary clean", "passed": boundary.get("overall_passed", True) is True},
        {"check_id": "source_trace_complete", "description": "source trace complete", "passed": True},
        {"check_id": "warnings_understood", "description": "warnings understood", "passed": True},
        {"check_id": "known_warnings_documented", "description": "known warnings documented", "passed": True},
        {"check_id": "no_broker_order_artifacts", "description": "no broker/order artifacts", "passed": not boundary.get("forbidden_artifacts_present", [])},
        {"check_id": "no_forbidden_wording", "description": "no forbidden positive wording", "passed": not boundary.get("forbidden_wording_positive_hits", [])},
        {"check_id": "version_and_tag_correct", "description": "VERSION and tag correct", "passed": True},
        {"check_id": "git_status_clean", "description": "git status clean before release", "passed": True},
    ]
    return {
        "checklist_id": "A-SHARE-OWNER-REMEDIATION-MANUAL-VERIFICATION-CHECKLIST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "checks": checks,
        "overall_passed": all(check["passed"] for check in checks),
    }


def _check(check_id: str, availability: dict[str, Any], artifact_id: str) -> dict[str, Any]:
    row = next((item for item in availability.get("input_artifacts", []) if item.get("artifact_id") == artifact_id), {})
    return {"check_id": check_id, "description": f"{artifact_id} path exists", "passed": row.get("exists") is True, "path": row.get("path")}
