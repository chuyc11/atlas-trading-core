"""Audit for v0.8.7 gated build-from-existing-data dry-run."""

from __future__ import annotations

import json
import hashlib
from pathlib import Path

from trading_core.equity_current_day_builds.gated_build_config import (
    GATED_BUILD_BOUNDARY,
    RECOMMENDED_NEXT_VERSION,
    TARGET_VERSION,
    gated_build_artifact_paths,
)
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, write_json_markdown


def audit_a_share_gated_build(
    *,
    as_of_date: str,
    paths: ProjectPaths | None = None,
) -> dict:
    paths = default_paths(paths)
    artifact_paths = gated_build_artifact_paths(paths, as_of_date)

    # Load payloads
    payloads = {}
    for key, path in artifact_paths.items():
        if key.endswith("_json") or key.endswith("_report"):
            continue
        if path.exists() and path.suffix == ".json":
            try:
                payloads[key] = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                payloads[key] = {}

    # Run checks
    checks = _checks(payloads, paths, as_of_date)

    blocking_reasons = [name for name, ok in checks.items() if not ok]
    warnings = []

    audit = {
        "audit_id": "A-SHARE-GATED-BUILD-FROM-EXISTING-DATA-AUDIT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "mode": "run_gated_build_from_existing_data",
        "overall_passed": not blocking_reasons,
        "blocking_reasons": sorted(set(blocking_reasons)),
        "warnings": sorted(set(warnings)),
        "preflight_checks": {
            "preflight_gate_passed": checks.get("preflight_gate_passed", False),
            "ops_history_audit_passed": checks.get("ops_history_audit_passed", False),
            "ops_center_audit_passed": checks.get("ops_center_audit_passed", False),
            "current_day_audit_passed": checks.get("current_day_audit_passed", False),
            "data_refresh_audit_passed": checks.get("data_refresh_audit_passed", False),
        },
        "execution_checks": {
            "workflow_mode": "build_from_existing_data",
            "gated_build_execution_performed": checks.get("gated_build_execution_performed", False),
            "workflow_audit_passed": checks.get("workflow_audit_passed", False),
            "old_run_daily_called": False,
        },
        "comparison_checks": {
            "comparison_completed": checks.get("comparison_completed", False),
            "missing_required_artifacts": [],
            "boundary_drift": not checks.get("boundary_drift_absent", True),
            "source_trace_missing": not checks.get("source_trace_complete", False),
            "source_trace_hashes_match": checks.get("source_trace_hashes_match", False),
        },
        "boundary": {
            "gated_build_from_existing_data_only": True,
            "research_only": True,
            "virtual_only": True,
            "real_portfolio_generated": False,
            "buy_sell_signals_generated": False,
            "order_preview_generated": False,
            "broker_connected": False,
            "real_orders_placed": False,
            "run_daily_called": False,
            "old_run_daily_called": False,
            "day2_executed": False,
            "official_forward_dry_run_status_unchanged": True,
            "external_notifications_sent": False,
            "public_network_refresh_run": False,
            "full_research_run": False,
            "model_profit_guaranteed": False,
            "live_trading_ready": False,
            "real_account_data_read": False,
            "build_result_used_as_trade_instruction": False,
        },
        "checks": checks,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }

    # Render markdown
    markdown = _render_audit_report(audit)

    write_json_markdown(
        artifact_paths["gated_build_audit_json"],
        audit,
        artifact_paths["gated_build_audit_report"],
        markdown,
    )

    return {
        "audit_id": audit["audit_id"],
        "overall_passed": audit["overall_passed"],
        "blocking_reasons": audit["blocking_reasons"],
        "warnings": len(audit["warnings"]),
        "preflight_checks": audit["preflight_checks"],
        "execution_checks": audit["execution_checks"],
        "comparison_checks": audit["comparison_checks"],
        "recommended_next_version": audit["recommended_next_version"],
        "json_path": str(artifact_paths["gated_build_audit_json"]),
        "report_path": str(artifact_paths["gated_build_audit_report"]),
    }


def _checks(payloads: dict, paths: ProjectPaths, as_of_date: str) -> dict[str, bool]:
    checks: dict[str, bool] = {}

    # Required artifacts exist
    artifact_paths = gated_build_artifact_paths(paths, as_of_date)
    required_keys = [
        "gated_build_config",
        "gated_build_input_availability",
        "gated_build_date_alignment",
        "preflight_gate",
        "gated_build_execution_plan",
        "gated_build_execution_record",
        "build_from_existing_data_workflow_result",
        "build_from_existing_data_audit_link",
        "build_artifact_index",
        "validate_vs_build_comparison",
        "artifact_drift_summary",
        "gated_build_warning_summary",
        "gated_build_source_trace",
        "gated_build_boundary_check",
        "gated_build_manifest",
        "gated_build_summary",
    ]
    for key in required_keys:
        path = artifact_paths.get(key)
        checks[f"{key}_present"] = bool(path and path.exists())

    # Markdown reports exist
    for key in [
        "gated_build_dry_run_report",
        "gated_build_preflight_report",
        "validate_vs_build_report",
        "artifact_drift_report",
        "source_trace_report",
    ]:
        path = artifact_paths.get(key)
        checks[f"{key}_present"] = bool(path and path.exists())

    # Preflight gate passed
    preflight = payloads.get("preflight_gate", {})
    checks["preflight_gate_passed"] = preflight.get("overall_passed", False) is True

    # Input audits passed
    checks["ops_history_audit_passed"] = _upstream_audit_passed(
        paths, "a_share_ops_history_baseline_audit.json"
    )
    checks["ops_center_audit_passed"] = _upstream_audit_passed(
        paths, "a_share_daily_ops_center_audit.json"
    )
    checks["current_day_audit_passed"] = _upstream_audit_passed(
        paths, "a_share_current_day_research_run_audit.json"
    )
    checks["data_refresh_audit_passed"] = _upstream_audit_passed(
        paths, "a_share_daily_data_refresh_audit.json"
    )

    # Execution checks
    execution = payloads.get("gated_build_execution_record", {})
    checks["gated_build_execution_performed"] = execution.get("command_executed", False) is True
    checks["workflow_audit_passed"] = execution.get("workflow_audit_overall_passed", False) is True
    checks["execution_old_run_daily_not_called"] = execution.get("old_run_daily_called", False) is False
    checks["workflow_mode_is_build_from_existing_data"] = execution.get("workflow_mode") == "build_from_existing_data"

    workflow_result = payloads.get("build_from_existing_data_workflow_result", {})
    checks["workflow_result_mode_correct"] = workflow_result.get("workflow_mode") == "build_from_existing_data"

    # Comparison checks
    comparison = payloads.get("validate_vs_build_comparison", {})
    checks["comparison_completed"] = comparison.get("comparison_completed", False) is True
    checks["no_missing_required_artifacts"] = len(comparison.get("missing_required_artifacts", [])) == 0

    drift = payloads.get("artifact_drift_summary", {})
    checks["boundary_drift_absent"] = "boundary_drift" not in drift.get("drift_categories_found", [])
    checks["no_missing_required_drift"] = "missing_required_artifact" not in drift.get("drift_categories_found", [])

    # Source trace
    source_trace = payloads.get("gated_build_source_trace", {})
    checks["source_trace_complete"] = source_trace.get("source_trace_complete", False) is True
    checks["source_trace_no_forbidden_paths"] = len(source_trace.get("forbidden_path_hits", [])) == 0
    checks["source_trace_hashes_match"] = _source_trace_hashes_match(paths, source_trace)

    # Boundary check
    boundary = payloads.get("gated_build_boundary_check", {})
    checks["boundary_overall_passed"] = boundary.get("overall_passed", False) is True
    checks["boundary_gated_build_from_existing_data_only"] = boundary.get(
        "gated_build_from_existing_data_only", False
    ) is True
    checks["boundary_broker_not_connected"] = boundary.get("broker_connected", True) is False
    checks["boundary_no_real_orders"] = boundary.get("real_orders_placed", True) is False
    checks["boundary_no_buy_sell_signals"] = boundary.get("buy_sell_signals_generated", True) is False
    checks["boundary_no_order_preview"] = boundary.get("order_preview_generated", True) is False
    checks["boundary_no_old_run_daily"] = boundary.get("old_run_daily_called", True) is False
    checks["boundary_no_run_daily"] = boundary.get("run_daily_called", True) is False
    checks["boundary_no_day2"] = boundary.get("day2_executed", True) is False
    checks["boundary_official_forward_dry_run_status_unchanged"] = boundary.get(
        "official_forward_dry_run_status_unchanged", False
    ) is True
    checks["boundary_no_public_network_refresh"] = boundary.get("public_network_refresh_run", True) is False
    checks["boundary_no_full_research_run"] = boundary.get("full_research_run", True) is False
    checks["boundary_no_external_notifications"] = boundary.get(
        "external_notifications_sent", True
    ) is False
    checks["boundary_research_only"] = boundary.get("research_only", False) is True
    checks["boundary_virtual_only"] = boundary.get("virtual_only", False) is True
    checks["boundary_no_live_trading_ready"] = boundary.get("live_trading_ready", True) is False
    checks["boundary_no_model_profit_guaranteed"] = boundary.get("model_profit_guaranteed", True) is False
    checks["boundary_no_real_account_data"] = boundary.get("real_account_data_read", True) is False
    checks["boundary_not_trade_instruction"] = boundary.get(
        "build_result_used_as_trade_instruction", True
    ) is False
    checks["boundary_no_forbidden_artifacts"] = len(boundary.get("forbidden_artifacts_present", [])) == 0
    checks["boundary_no_forbidden_wording"] = len(boundary.get("forbidden_wording_positive_hits", [])) == 0

    # Manifest checks
    manifest = payloads.get("gated_build_manifest", {})
    checks["manifest_present"] = manifest.get("manifest_id") == "A-SHARE-GATED-BUILD-FROM-EXISTING-DATA-MANIFEST"
    checks["manifest_research_only"] = manifest.get("research_only", False) is True
    checks["manifest_recommended_next_version"] = manifest.get("recommended_next_version") == RECOMMENDED_NEXT_VERSION

    return checks


def _upstream_audit_passed(paths: ProjectPaths, filename: str) -> bool:
    path = paths.data_dir / "equity_data_quality" / filename
    if not path.exists():
        return False
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload.get("overall_passed", False) is True
    except Exception:
        return False


def _source_trace_hashes_match(paths: ProjectPaths, source_trace: dict) -> bool:
    source_entries = [entry for entry in source_trace.get("entries", []) if entry.get("required") is True]
    if not source_entries:
        return False
    for entry in source_entries:
        recorded = entry.get("sha256")
        if not recorded:
            return False
        path_str = entry.get("path")
        if not path_str:
            return False
        path = paths.project_root / path_str
        if not path.exists():
            return False
        try:
            current = hashlib.sha256(path.read_bytes()).hexdigest()
        except Exception:
            return False
        if current != recorded:
            return False
    return True


def _render_audit_report(audit: dict) -> str:
    lines = [
        f"# A 股 Gated Build-from-Existing-Data Dry-Run Audit",
        f"",
        f"- **Audit ID**: {audit['audit_id']}",
        f"- **Target Version**: {audit['target_version']}",
        f"- **As-of Date**: {audit['as_of_date']}",
        f"- **Mode**: {audit['mode']}",
        f"- **Overall Passed**: {audit['overall_passed']}",
        f"- **Blocking Reasons**: {audit['blocking_reasons']}",
        f"- **Warnings Count**: {len(audit['warnings'])}",
        f"",
        f"## Preflight Checks",
        f"",
    ]
    for key, val in audit["preflight_checks"].items():
        lines.append(f"- {key}: {val}")
    lines.extend(["", "## Execution Checks", ""])
    for key, val in audit["execution_checks"].items():
        lines.append(f"- {key}: {val}")
    lines.extend(["", "## Comparison Checks", ""])
    for key, val in audit["comparison_checks"].items():
        lines.append(f"- {key}: {val}")
    lines.extend(["", "## Boundary", ""])
    for key, val in audit["boundary"].items():
        lines.append(f"- {key}: {val}")
    lines.extend([
        "",
        "## Disclaimer",
        "",
        "本审计为研究流程 dry-run 审计，不构成投资建议。",
        "不授权任何交易、不下单、不连接券商。",
        "",
    ])
    return "\n".join(lines)
