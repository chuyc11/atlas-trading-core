"""Audit v0.7.9 A-share daily research workflow orchestration artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import json_safe, write_report
from trading_core.equity_workflows.workflow_config import (
    DEFAULT_AS_OF_DATE,
    FORBIDDEN_POSITIVE_WORDING,
    RECOMMENDED_NEXT_VERSION,
    REMEDIATION_VERSION,
    TARGET_VERSION,
    WORKFLOW_BOUNDARY,
    WORKFLOW_FLAGS,
    stage_definitions,
    upstream_audit_artifacts,
    workflow_artifact_paths,
)
from trading_core.equity_workflows.workflow_manifest import load_json, stage_counts
from trading_core.equity_workflows.workflow_preflight import read_version_checks
from trading_core.equity_workflows.workflow_report import render_workflow_audit
from trading_core.equity_workflows.workflow_source_trace import source_trace_has_forbidden_paths
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def audit_a_share_daily_research_workflow(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    mode: str | None = None,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    artifacts = workflow_artifact_paths(paths, as_of_date)
    config = load_json(artifacts["workflow_config"])
    preflight = load_json(artifacts["workflow_preflight"])
    stage_manifest = load_json(artifacts["workflow_stage_manifest"])
    run_manifest = load_json(artifacts["workflow_run_manifest"])
    source_trace = load_json(artifacts["workflow_source_trace"])
    boundary_check = load_json(artifacts["workflow_boundary_check"])
    summary = load_json(artifacts["workflow_summary"])
    effective_mode = mode or str(config.get("mode") or run_manifest.get("mode") or "validate_existing_artifacts")
    stages = stage_manifest.get("stages") if isinstance(stage_manifest.get("stages"), list) else []
    required_status = {stage["stage_id"]: stage.get("status") for stage in stages if isinstance(stage, dict) and "stage_id" in stage}
    counts = stage_counts(stages)
    version_checks = read_version_checks(paths=paths)
    upstream_audits = _upstream_audit_status(paths)
    forbidden_wording_hits = _forbidden_wording_hits(
        [
            artifacts["workflow_summary_report"],
            artifacts["workflow_stage_report"],
            artifacts["workflow_source_trace_report"],
        ]
    )
    checks = _checks(
        artifacts=artifacts,
        config=config,
        preflight=preflight,
        stage_manifest=stage_manifest,
        run_manifest=run_manifest,
        source_trace=source_trace,
        boundary_check=boundary_check,
        summary=summary,
        stages=stages,
        required_status=required_status,
        version_checks=version_checks,
        upstream_audits=upstream_audits,
        forbidden_wording_hits=forbidden_wording_hits,
        as_of_date=as_of_date,
        paths=paths,
    )
    blocking = [f"{name}=false" for name, passed in checks.items() if not passed]
    warnings = sorted(set(_collect_warnings(preflight, run_manifest, boundary_check, summary, source_trace)))
    payload = {
        "audit_id": "A-SHARE-DAILY-WORKFLOW-AUDIT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "mode": effective_mode,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": warnings,
        "stage_counts": counts,
        "required_stage_status": required_status,
        "version_checks": version_checks,
        "checks": checks,
        "upstream_audit_status": upstream_audits,
        "source_trace_complete": bool(source_trace.get("source_trace_complete")),
        "source_trace_forbidden_path_hits": source_trace_has_forbidden_paths(source_trace),
        "forbidden_wording_positive_hits": forbidden_wording_hits,
        "build_timestamp_non_strict_idempotency": bool(summary.get("build_timestamp_non_strict_idempotency") or run_manifest.get("build_timestamp_non_strict_idempotency")),
        "benchmark_placeholder_deferred_to_v0_7_10": True,
        "boundary": dict(WORKFLOW_BOUNDARY),
        **WORKFLOW_FLAGS,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION if not blocking else REMEDIATION_VERSION,
    }
    return write_report(
        artifacts["workflow_audit_json"],
        json_safe(payload),
        artifacts["workflow_audit_report"],
        render_workflow_audit(payload),
    )


def _checks(**kwargs: Any) -> dict[str, bool]:
    artifacts: dict[str, Path] = kwargs["artifacts"]
    stages = kwargs["stages"]
    required_status = kwargs["required_status"]
    stage_defs = stage_definitions(kwargs["paths"], kwargs["as_of_date"])
    required_ids = [definition["stage_id"] for definition in stage_defs]
    status_ok = all(required_status.get(stage_id) == "passed" for stage_id in required_ids)
    ordering_ok = [stage.get("stage_id") for stage in sorted(stages, key=lambda item: int(item.get("stage_order", -1)))] == required_ids
    boundary = kwargs["boundary_check"]
    run_manifest = kwargs["run_manifest"]
    source_trace = kwargs["source_trace"]
    preflight = kwargs["preflight"]
    summary = kwargs["summary"]
    return {
        "workflow_config_exists": artifacts["workflow_config"].exists(),
        "workflow_preflight_exists": artifacts["workflow_preflight"].exists(),
        "workflow_run_manifest_exists": artifacts["workflow_run_manifest"].exists(),
        "workflow_stage_manifest_exists": artifacts["workflow_stage_manifest"].exists(),
        "workflow_source_trace_exists": artifacts["workflow_source_trace"].exists(),
        "workflow_boundary_check_exists": artifacts["workflow_boundary_check"].exists(),
        "workflow_summary_exists": artifacts["workflow_summary"].exists(),
        "workflow_summary_report_exists": artifacts["workflow_summary_report"].exists(),
        "all_required_stages_present": set(required_status) == set(required_ids),
        "stage_ordering_correct": ordering_ok,
        "required_stages_passed": status_ok,
        "source_trace_complete": bool(source_trace.get("source_trace_complete")),
        "source_trace_has_no_forbidden_paths": not source_trace_has_forbidden_paths(source_trace),
        "input_artifacts_exist": all(record.get("exists") for record in source_trace.get("sources", []) if _is_input_source(str(record.get("path") or ""))),
        "upstream_audits_passed": all(record.get("overall_passed") is True for record in kwargs["upstream_audits"].values()),
        "root_import_shim_version_consistent": bool(kwargs["version_checks"].get("version_consistent")),
        "preflight_passed": bool(preflight.get("overall_passed")),
        "boundary_check_passed": bool(boundary.get("overall_passed")),
        "summary_passed": bool(summary.get("overall_passed")),
        "no_old_run_daily_called": _boundary_false(boundary, run_manifest, "call_old_run_daily") and _boundary_false(boundary, run_manifest, "run_daily_called"),
        "official_forward_dry_run_status_unchanged": _boundary_true(boundary, run_manifest, "official_forward_dry_run_status_unchanged"),
        "day2_not_executed": _boundary_false(boundary, run_manifest, "day2_executed"),
        "broker_not_connected": _boundary_false(boundary, run_manifest, "broker_connected"),
        "real_orders_not_placed": _boundary_false(boundary, run_manifest, "real_orders_placed"),
        "buy_sell_signals_not_generated": _boundary_false(boundary, run_manifest, "buy_sell_signals_generated"),
        "order_preview_not_generated": _boundary_false(boundary, run_manifest, "order_preview_generated"),
        "no_order_preview_artifact_generated": not _forbidden_name_present(kwargs["paths"], kwargs["as_of_date"], {"ORDER_PREVIEW.md", "order_preview.json"}),
        "no_buy_sell_signal_artifacts_generated": not _forbidden_name_present(kwargs["paths"], kwargs["as_of_date"], {"BUY_LIST.md", "SELL_LIST.md", "buy_list.json", "sell_list.json"}),
        "no_broker_order_generated": not _forbidden_name_present(kwargs["paths"], kwargs["as_of_date"], {"BROKER_ORDER.json", "broker_order.json"}),
        "no_real_order_generated": not _forbidden_name_present(kwargs["paths"], kwargs["as_of_date"], {"REAL_ORDER.json", "real_order.json"}),
        "no_forbidden_positive_wording": not kwargs["forbidden_wording_hits"],
        "model_profit_not_guaranteed": _boundary_false(boundary, run_manifest, "model_profit_guaranteed"),
        "live_trading_not_ready": _boundary_false(boundary, run_manifest, "live_trading_ready"),
        "build_timestamp_non_strict_idempotency_recorded": bool(kwargs["summary"].get("build_timestamp_non_strict_idempotency") or kwargs["run_manifest"].get("build_timestamp_non_strict_idempotency")),
    }


def _upstream_audit_status(paths: ProjectPaths) -> dict[str, dict[str, Any]]:
    return {
        key: {
            "path": str(path),
            "exists": path.exists(),
            "overall_passed": load_json(path).get("overall_passed") if path.exists() else None,
            "warnings": load_json(path).get("warnings", []) if path.exists() else [],
        }
        for key, path in upstream_audit_artifacts(paths).items()
    }


def _collect_warnings(*payloads: dict[str, Any]) -> list[str]:
    warnings = []
    for payload in payloads:
        warnings.extend(str(item) for item in payload.get("warnings", []) if item)
    return warnings


def _forbidden_wording_hits(paths: list[Path]) -> list[str]:
    hits = []
    for path in paths:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8").lower()
        for phrase in FORBIDDEN_POSITIVE_WORDING:
            lowered = phrase.lower()
            if lowered in text and not _is_negative_context(text, lowered):
                hits.append(f"{path.name}:{phrase}")
    return sorted(set(hits))


def _is_negative_context(text: str, phrase: str) -> bool:
    index = text.find(phrase)
    if index < 0:
        return False
    prefix = text[max(0, index - 8) : index]
    return any(marker in prefix for marker in ["不", "无", "未", "no ", "not "])


def _boundary_false(boundary: dict[str, Any], run_manifest: dict[str, Any], key: str) -> bool:
    return boundary.get(key) is False and run_manifest.get(key) is False


def _boundary_true(boundary: dict[str, Any], run_manifest: dict[str, Any], key: str) -> bool:
    return boundary.get(key) is True and run_manifest.get(key) is True


def _forbidden_name_present(paths: ProjectPaths, as_of_date: str, names: set[str]) -> bool:
    roots = [
        paths.data_dir / "equity_workflows" / "daily" / as_of_date,
        paths.outputs_dir / "equity_workflows" / "daily" / as_of_date,
        paths.data_dir / "orders",
        paths.outputs_dir / "orders",
    ]
    for root in roots:
        if not root.exists():
            continue
        for item in root.rglob("*"):
            if item.name in names:
                return True
    return False


def _is_input_source(path: str) -> bool:
    return path.startswith("data/equity_") and "equity_workflows" not in path
