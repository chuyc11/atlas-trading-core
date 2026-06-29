"""Build-output owner dashboard cards."""

from __future__ import annotations

from pathlib import Path

from trading_core.equity_build_output_dashboard.build_output_dashboard_config import TARGET_VERSION
from trading_core.equity_build_output_dashboard.input_availability import load_json
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def build_executive_status_card(*, as_of_date: str, availability: dict, resolution: dict) -> dict:
    blocking = availability.get("blocking_reasons", []) + resolution.get("blocking_reasons", [])
    warning_count = len(availability.get("warnings", [])) + len(resolution.get("warnings", []))
    status = "passed" if not blocking and warning_count == 0 else "passed_with_warnings" if not blocking else "blocked"
    return {
        "card_id": "BUILD_OUTPUT_EXECUTIVE_STATUS",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": "build_from_existing_data",
        "overall_status": status,
        "build_output_available": availability.get("overall_passed", False),
        "gated_build_audit_passed": availability.get("gated_build_audit_passed", False),
        "repeatability_audit_passed": availability.get("repeatability_audit_passed", False),
        "business_output_drift_count": availability.get("business_output_drift_count", 0),
        "protected_path_modifications_detected": availability.get("protected_path_modifications_detected", True),
        "workflow_audit_passed": availability.get("repeatability_audit_passed", False),
        "blocking_count": len(blocking),
        "warning_count": warning_count,
        "research_only": True,
        "virtual_only": True,
        "not_order_instruction": True,
        "not_live_trading_ready": True,
    }


def build_data_freshness_card(*, paths: ProjectPaths | None, as_of_date: str) -> dict:
    paths = default_paths(paths)
    audit = load_json(paths.data_dir / "equity_data_quality" / "a_share_daily_data_refresh_audit.json")
    summary = load_json(paths.data_dir / "equity_data_refresh" / "daily" / as_of_date / "data_refresh_summary.json")
    return {
        "card_id": "BUILD_OUTPUT_DATA_FRESHNESS",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": "build_from_existing_data",
        "data_refresh_audit_passed": audit.get("overall_passed", False),
        "schema_validation_passed": _nested_bool(audit, "validation_checks", "schema_validation_passed"),
        "freshness_validation_passed": _nested_bool(audit, "validation_checks", "freshness_validation_passed"),
        "coverage_validation_passed": _nested_bool(audit, "validation_checks", "coverage_validation_passed"),
        "warnings": audit.get("warnings", []),
        "summary_available": bool(summary),
    }


def build_workflow_status_card(*, paths: ProjectPaths | None, as_of_date: str) -> dict:
    paths = default_paths(paths)
    record = load_json(paths.data_dir / "equity_build_repeatability" / "daily" / as_of_date / "repeat_build_execution_record.json")
    result = load_json(paths.data_dir / "equity_build_repeatability" / "daily" / as_of_date / "repeat_build_workflow_result.json")
    gated = load_json(paths.data_dir / "equity_current_day_builds" / "daily" / as_of_date / "build_from_existing_data_workflow_result.json")
    return {
        "card_id": "BUILD_OUTPUT_WORKFLOW_STATUS",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": "build_from_existing_data",
        "repeat_build_status": record.get("status"),
        "repeat_build_exit_code": record.get("exit_code"),
        "repeat_build_audit_passed": record.get("workflow_audit_overall_passed", False),
        "gated_build_audit_passed": gated.get("workflow_audit_overall_passed", False),
        "stage_count": result.get("stage_count", 0),
        "failed_stage_count": result.get("failed_stage_count", 0),
        "old_run_daily_called": record.get("old_run_daily_called", False),
    }


def build_research_output_card(*, paths: ProjectPaths | None, as_of_date: str) -> dict:
    paths = default_paths(paths)
    directories = {
        "features": paths.data_dir / "equity_features" / "daily" / as_of_date,
        "scores": paths.data_dir / "equity_scores" / "daily" / as_of_date,
        "selection": paths.data_dir / "equity_selection" / "daily" / as_of_date,
        "portfolios": paths.data_dir / "equity_portfolios" / "daily" / as_of_date,
        "briefings": paths.data_dir / "equity_briefings" / "daily" / as_of_date,
        "tracking": paths.data_dir / "equity_portfolio_tracking" / "daily" / as_of_date,
    }
    return {
        "card_id": "BUILD_OUTPUT_RESEARCH_OUTPUT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": "build_from_existing_data",
        "artifact_groups": {
            key: {"available": path.exists(), "file_count": sum(1 for _ in path.rglob("*") if _.is_file()) if path.exists() else 0}
            for key, path in directories.items()
        },
    }


def build_optional_summary_card(*, paths: ProjectPaths | None, as_of_date: str, card_id: str, source_path: Path) -> dict:
    paths = default_paths(paths)
    payload = load_json(source_path)
    return {
        "card_id": card_id,
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": "build_from_existing_data" if payload else "unavailable",
        "available": bool(payload),
        "source_path": str(source_path.relative_to(paths.project_root)) if source_path.exists() else str(source_path),
        "overall_passed": payload.get("overall_passed"),
        "blocking_reasons": payload.get("blocking_reasons", []),
        "warnings": payload.get("warnings", []),
        "summary": _summary_values(payload),
    }


def _nested_bool(payload: dict, *keys: str) -> bool | None:
    value = payload
    for key in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value if isinstance(value, bool) else None


def _summary_values(payload: dict) -> dict:
    result = {}
    for key in [
        "candidate_count",
        "long_count",
        "mid_count",
        "short_count",
        "portfolio_count",
        "benchmark_count",
        "observation_count",
        "artifact_count",
    ]:
        if key in payload:
            result[key] = payload[key]
    return result

