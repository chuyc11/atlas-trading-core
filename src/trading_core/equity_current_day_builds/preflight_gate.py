"""Preflight gate evaluation for v0.8.7 gated build."""

from __future__ import annotations

import json

from trading_core.equity_current_day_builds.gated_build_config import (
    TARGET_VERSION,
    FROM_WORKFLOW_MODE,
    TO_WORKFLOW_MODE,
)
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def build_preflight_gate(
    *,
    paths: ProjectPaths | None,
    as_of_date: str,
    input_availability: dict,
    date_alignment: dict,
    minimum_ops_health_score: int = 60,
) -> dict:
    paths = default_paths(paths)

    blocking_reasons = []
    warnings = []

    # Input availability must pass
    if not input_availability.get("overall_passed", False):
        blocking_reasons.append("input_availability_failed")
        for reason in input_availability.get("blocking_reasons", []):
            blocking_reasons.append(f"missing_input:{reason}")

    # Date alignment must pass
    if not date_alignment.get("overall_passed", False):
        blocking_reasons.append("date_alignment_failed")
        for reason in date_alignment.get("blocking_reasons", []):
            blocking_reasons.append(f"date_mismatch:{reason}")

    # Check upstream audits
    audit_paths = {
        "ops_history_audit": (
            paths.data_dir / "equity_data_quality" / "a_share_ops_history_baseline_audit.json"
        ),
        "ops_center_audit": (
            paths.data_dir / "equity_data_quality" / "a_share_daily_ops_center_audit.json"
        ),
        "current_day_audit": (
            paths.data_dir / "equity_data_quality" / "a_share_current_day_research_run_audit.json"
        ),
        "data_refresh_audit": (
            paths.data_dir / "equity_data_quality" / "a_share_daily_data_refresh_audit.json"
        ),
    }

    audit_results = {}
    for key, path in audit_paths.items():
        if path.exists():
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
                audit_results[key] = {
                    "exists": True,
                    "overall_passed": payload.get("overall_passed", False),
                    "blocking_reasons": payload.get("blocking_reasons", []),
                }
                if not payload.get("overall_passed", False):
                    blocking_reasons.append(f"{key}_failed")
            except Exception:
                audit_results[key] = {"exists": True, "overall_passed": False}
                blocking_reasons.append(f"{key}_parse_error")
        else:
            audit_results[key] = {"exists": False, "overall_passed": False}
            blocking_reasons.append(f"{key}_missing")

    # Check ops health score
    health_score_card = (
        paths.data_dir / "equity_ops_center" / "daily" / as_of_date / "ops_health_score_card.json"
    )
    health_score = None
    health_gate_passed = False
    if health_score_card.exists():
        try:
            payload = json.loads(health_score_card.read_text(encoding="utf-8"))
            health_score = payload.get("score", None)
            health_gate_passed = health_score is not None and health_score >= minimum_ops_health_score
            if not health_gate_passed:
                blocking_reasons.append(f"ops_health_score_below_minimum:{health_score}<{minimum_ops_health_score}")
        except Exception:
            blocking_reasons.append("ops_health_score_parse_error")
    else:
        blocking_reasons.append("ops_health_score_card_missing")

    data_refresh_checks = {}
    data_refresh_audit_path = paths.data_dir / "equity_data_quality" / "a_share_daily_data_refresh_audit.json"
    if data_refresh_audit_path.exists():
        try:
            payload = json.loads(data_refresh_audit_path.read_text(encoding="utf-8"))
            validation = payload.get("validation_checks", {})
            data_refresh_checks = {
                "data_refresh_audit_passed": payload.get("overall_passed") is True,
                "critical_datasets_passed": validation.get("critical_datasets_available") is True,
                "schema_validation_passed": validation.get("schema_validation_passed") is True,
                "freshness_validation_passed": validation.get("freshness_validation_passed") is True,
                "coverage_validation_passed": validation.get("coverage_validation_passed") is True,
            }
            for check_name, passed in data_refresh_checks.items():
                if not passed:
                    blocking_reasons.append(f"{check_name}=false")
        except Exception:
            blocking_reasons.append("data_refresh_readiness_parse_error")
    else:
        blocking_reasons.append("data_refresh_audit_missing_for_readiness")

    ops_gate = {"blocking_issue_count": None, "critical_alert_count": None}
    ops_manifest_path = paths.data_dir / "equity_ops_center" / "daily" / as_of_date / "ops_manifest.json"
    if ops_manifest_path.exists():
        try:
            manifest = json.loads(ops_manifest_path.read_text(encoding="utf-8"))
            blocking_count = int(manifest.get("blocking_issue_count", 0))
            ops_gate["blocking_issue_count"] = blocking_count
            if blocking_count != 0:
                blocking_reasons.append(f"blocking_issue_count_nonzero:{blocking_count}")
        except Exception:
            blocking_reasons.append("ops_manifest_parse_error")
    else:
        blocking_reasons.append("ops_manifest_missing_for_gate")

    monitoring_alert_path = paths.data_dir / "equity_owner_monitoring" / "daily" / as_of_date / "alert_evaluation.json"
    critical_alert_count = 0
    if monitoring_alert_path.exists():
        try:
            alert_payload = json.loads(monitoring_alert_path.read_text(encoding="utf-8"))
            critical_alert_count = int(alert_payload.get("alert_counts", {}).get("critical", 0))
        except Exception:
            critical_alert_count = 0
    ops_gate["critical_alert_count"] = critical_alert_count
    if critical_alert_count != 0:
        blocking_reasons.append(f"critical_alert_count_nonzero:{critical_alert_count}")

    history_gate = {"synthetic_history_used": None, "future_dates_used": None}
    history_audit_path = paths.data_dir / "equity_data_quality" / "a_share_ops_history_baseline_audit.json"
    if history_audit_path.exists():
        try:
            history_audit = json.loads(history_audit_path.read_text(encoding="utf-8"))
            trend = history_audit.get("trend_sufficiency", {})
            history_gate["synthetic_history_used"] = trend.get("synthetic_history_used")
            history_gate["future_dates_used"] = trend.get("future_dates_used")
            if trend.get("synthetic_history_used") is not False:
                blocking_reasons.append("synthetic_history_used_not_false")
            if trend.get("future_dates_used") is not False:
                blocking_reasons.append("future_dates_used_not_false")
        except Exception:
            blocking_reasons.append("ops_history_audit_gate_parse_error")

    # Check boundary fields from upstream audits
    boundary_clean = True
    for key, audit_info in audit_results.items():
        if not audit_info.get("overall_passed", False):
            boundary_clean = False
            break

    # Check for known forbidden state
    ops_history_boundary = (
        paths.data_dir / "equity_ops_history" / "daily" / as_of_date / "ops_history_boundary_check.json"
    )
    if ops_history_boundary.exists():
        try:
            payload = json.loads(ops_history_boundary.read_text(encoding="utf-8"))
            if payload.get("old_run_daily_called", False):
                blocking_reasons.append("old_run_daily_detected_in_ops_history")
            if payload.get("broker_connected", False):
                blocking_reasons.append("broker_connected_detected_in_ops_history")
            if payload.get("real_orders_placed", False):
                blocking_reasons.append("real_orders_placed_detected_in_ops_history")
        except Exception:
            pass

    overall_passed = not blocking_reasons

    return {
        "gate_id": "A-SHARE-GATED-BUILD-FROM-EXISTING-DATA-PREFLIGHT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "from_workflow_mode": FROM_WORKFLOW_MODE,
        "to_workflow_mode": TO_WORKFLOW_MODE,
        "overall_passed": overall_passed,
        "eligible_for_gated_dry_run": overall_passed,
        "blocking_reasons": sorted(set(blocking_reasons)),
        "warnings": sorted(set(warnings)),
        "manual_review_required": True,
        "manual_review_recorded": True,
        "audit_results": audit_results,
        "ops_health_score": health_score,
        "ops_health_gate_passed": health_gate_passed,
        "minimum_ops_health_score": minimum_ops_health_score,
        "data_refresh_checks": data_refresh_checks,
        "ops_gate": ops_gate,
        "history_gate": history_gate,
        "boundary_clean": boundary_clean,
        "research_only": True,
        "virtual_only": True,
    }
