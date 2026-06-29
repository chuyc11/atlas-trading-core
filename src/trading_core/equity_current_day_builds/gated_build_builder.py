"""Builder orchestrator for v0.8.7 gated build-from-existing-data dry-run."""

from __future__ import annotations

import json

from trading_core.equity_current_day_builds.artifact_drift import build_artifact_drift_summary
from trading_core.equity_current_day_builds.artifact_index import build_gated_build_artifact_index
from trading_core.equity_current_day_builds.date_alignment import build_gated_build_date_alignment
from trading_core.equity_current_day_builds.execution_plan import build_gated_build_execution_plan
from trading_core.equity_current_day_builds.execution_record import execute_gated_build_and_record
from trading_core.equity_current_day_builds.gated_build_boundary import build_gated_build_boundary_check
from trading_core.equity_current_day_builds.gated_build_config import (
    AUDIT_EXISTING_GATED_BUILD,
    ALLOWED_MODES,
    COMPARE_VALIDATE_VS_BUILD_OUTPUTS,
    DEFAULT_AS_OF_DATE,
    EVALUATE_PREFLIGHT_GATE,
    GATED_BUILD_FILES,
    GATED_BUILD_REPORTS,
    RUN_GATED_BUILD_FROM_EXISTING_DATA,
    TARGET_VERSION,
    VALIDATE_GATED_BUILD_INPUTS,
    GatedBuildConfig,
    gated_build_artifact_paths,
    gated_build_data_dir,
    validate_gated_build_config,
)
from trading_core.equity_current_day_builds.gated_build_manifest import (
    build_gated_build_manifest,
    build_gated_build_summary,
)
from trading_core.equity_current_day_builds.gated_build_report import (
    render_comparison_report,
    render_dry_run_report,
    render_drift_report,
    render_preflight_report,
    render_source_trace_report,
)
from trading_core.equity_current_day_builds.gated_build_source_trace import build_gated_build_source_trace
from trading_core.equity_current_day_builds.input_availability import build_gated_build_input_availability
from trading_core.equity_current_day_builds.preflight_gate import build_preflight_gate
from trading_core.equity_current_day_builds.validate_vs_build_comparison import (
    build_validate_vs_build_comparison,
)
from trading_core.equity_current_day_builds.warning_summary import build_gated_build_warning_summary
from trading_core.equity_current_day_builds.workflow_result import build_audit_link, build_workflow_result
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def validate_a_share_gated_build_inputs(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    paths: ProjectPaths | None = None,
) -> dict:
    paths = default_paths(paths)
    input_availability = build_gated_build_input_availability(paths=paths, as_of_date=as_of_date)

    return {
        "builder_id": "A-SHARE-GATED-BUILD-INPUT-VALIDATOR",
        "overall_passed": input_availability["overall_passed"],
        "blocking_reasons": input_availability["blocking_reasons"],
        "warnings": input_availability["warnings"],
        "ops_history_audit_passed": _upstream_audit(paths, "a_share_ops_history_baseline_audit.json"),
        "ops_center_audit_passed": _upstream_audit(paths, "a_share_daily_ops_center_audit.json"),
        "current_day_audit_passed": _upstream_audit(paths, "a_share_current_day_research_run_audit.json"),
        "data_refresh_audit_passed": _upstream_audit(paths, "a_share_daily_data_refresh_audit.json"),
    }


def build_a_share_gated_build(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    mode: str = RUN_GATED_BUILD_FROM_EXISTING_DATA,
    allow_date_mismatch: bool = False,
    minimum_ops_health_score: int = 60,
    allow_public_network_refresh: bool = False,
    allow_full_research_run: bool = False,
    allow_broker: bool = False,
    allow_real_orders: bool = False,
    allow_order_preview: bool = False,
    allow_buy_sell_signals: bool = False,
    allow_old_run_daily: bool = False,
    paths: ProjectPaths | None = None,
) -> dict:
    paths = default_paths(paths)

    config = GatedBuildConfig(
        as_of_date=as_of_date,
        mode=mode,
        allow_date_mismatch=allow_date_mismatch,
        minimum_ops_health_score=minimum_ops_health_score,
        allow_public_network_refresh=allow_public_network_refresh,
        allow_full_research_run=allow_full_research_run,
        allow_broker=allow_broker,
        allow_real_orders=allow_real_orders,
        allow_order_preview=allow_order_preview,
        allow_buy_sell_signals=allow_buy_sell_signals,
        allow_old_run_daily=allow_old_run_daily,
    )

    config_issues = validate_gated_build_config(config)
    if config_issues:
        raise ValueError(f"invalid gated build config: {config_issues}")

    artifact_paths = gated_build_artifact_paths(paths, as_of_date)
    data_dir = gated_build_data_dir(paths, as_of_date)
    data_dir.mkdir(parents=True, exist_ok=True)

    # 1. Input availability
    input_availability = build_gated_build_input_availability(paths=paths, as_of_date=as_of_date)

    # 2. Date alignment
    date_alignment = build_gated_build_date_alignment(
        paths=paths, as_of_date=as_of_date, allow_date_mismatch=allow_date_mismatch
    )

    # 3. Preflight gate
    preflight_gate = build_preflight_gate(
        paths=paths,
        as_of_date=as_of_date,
        input_availability=input_availability,
        date_alignment=date_alignment,
        minimum_ops_health_score=minimum_ops_health_score,
    )

    # 4. Execution plan
    execution_plan = build_gated_build_execution_plan(
        as_of_date=as_of_date, preflight_gate=preflight_gate
    )

    validate_snapshot = _current_day_snapshot(paths, as_of_date)

    # 5. Execute (unless input validation / preflight failed)
    if mode == RUN_GATED_BUILD_FROM_EXISTING_DATA and preflight_gate.get("overall_passed"):
        execution_record = execute_gated_build_and_record(
            paths=paths,
            as_of_date=as_of_date,
            preflight_gate=preflight_gate,
            execution_plan=execution_plan,
        )
    else:
        execution_record = {
            "execution_id": "A-SHARE-GATED-BUILD-FROM-EXISTING-DATA-EXECUTION",
            "target_version": TARGET_VERSION,
            "as_of_date": as_of_date,
            "workflow_mode": "build_from_existing_data",
            "command": execution_plan.get("workflow_command", ""),
            "command_executed": False,
            "exit_code": None,
            "status": "skipped",
            "started_at": None,
            "finished_at": None,
            "duration_seconds": None,
            "workflow_audit_path": "",
            "workflow_audit_overall_passed": False,
            "blocking_reasons": [] if preflight_gate.get("overall_passed") else ["preflight_skipped"],
            "warnings": [],
            "old_run_daily_called": False,
            "broker_connected": False,
            "real_orders_placed": False,
            "buy_sell_signals_generated": False,
            "order_preview_generated": False,
            "preflight_gate_passed": preflight_gate.get("overall_passed", False),
        }

    # 6. Workflow result
    workflow_result = build_workflow_result(
        paths=paths, as_of_date=as_of_date, execution_record=execution_record
    )

    # 7. Audit link
    audit_link = build_audit_link(
        paths=paths,
        as_of_date=as_of_date,
        execution_record=execution_record,
        workflow_result=workflow_result,
    )

    # 8. Artifact index
    artifact_index = build_gated_build_artifact_index(
        paths=paths, as_of_date=as_of_date, workflow_result=workflow_result
    )

    # 9. Validate vs Build comparison
    comparison = build_validate_vs_build_comparison(
        paths=paths,
        as_of_date=as_of_date,
        validate_snapshot=validate_snapshot,
    )

    # 10. Artifact drift summary
    drift_summary = build_artifact_drift_summary(
        paths=paths, as_of_date=as_of_date, comparison=comparison
    )

    # 11. Warning summary
    warning_summary = build_gated_build_warning_summary(
        as_of_date=as_of_date,
        input_availability=input_availability,
        date_alignment=date_alignment,
        preflight_gate=preflight_gate,
        execution_record=execution_record,
        comparison=comparison,
        drift_summary=drift_summary,
    )

    # 12. Source trace
    source_trace = build_gated_build_source_trace(
        paths=paths,
        as_of_date=as_of_date,
        source_artifacts=_source_artifacts(paths, as_of_date),
        output_artifacts={k: v for k, v in artifact_paths.items() if k in GATED_BUILD_FILES},
        workflow_command=execution_plan.get("workflow_command", ""),
    )

    # 13. Boundary check
    boundary = build_gated_build_boundary_check(
        paths=paths,
        as_of_date=as_of_date,
        warnings=warning_summary.get("warnings", []),
        blocking_reasons=execution_record.get("blocking_reasons", []) + drift_summary.get("blocking_reasons", []),
        execution_record=execution_record,
    )

    # 14. Manifest
    manifest = build_gated_build_manifest(
        as_of_date=as_of_date,
        mode=mode,
        preflight_gate=preflight_gate,
        execution_record=execution_record,
        workflow_result=workflow_result,
        comparison=comparison,
        drift_summary=drift_summary,
        boundary=boundary,
        output_artifacts={k: v for k, v in artifact_paths.items() if k in GATED_BUILD_FILES},
        source_artifacts=_source_artifacts(paths, as_of_date),
        paths=paths,
    )

    # 15. Summary
    summary = build_gated_build_summary(
        as_of_date=as_of_date,
        mode=mode,
        manifest=manifest,
        preflight_gate=preflight_gate,
        execution_record=execution_record,
        workflow_result=workflow_result,
        comparison=comparison,
        drift_summary=drift_summary,
        boundary=boundary,
    )

    # Write config
    config_payload = config.to_dict()
    config_payload["gated_build_execution_performed"] = execution_record.get("command_executed", False)

    # Assemble all payloads
    payloads = {
        "gated_build_config": config_payload,
        "gated_build_input_availability": input_availability,
        "gated_build_date_alignment": date_alignment,
        "preflight_gate": preflight_gate,
        "gated_build_execution_plan": execution_plan,
        "gated_build_execution_record": execution_record,
        "build_from_existing_data_workflow_result": workflow_result,
        "build_from_existing_data_audit_link": audit_link,
        "build_artifact_index": artifact_index,
        "validate_vs_build_comparison": comparison,
        "artifact_drift_summary": drift_summary,
        "gated_build_warning_summary": warning_summary,
        "gated_build_source_trace": source_trace,
        "gated_build_boundary_check": boundary,
        "gated_build_manifest": manifest,
        "gated_build_summary": summary,
    }

    # Write daily JSON artifacts
    for key, payload in payloads.items():
        path = artifact_paths.get(key)
        if path:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    # Write markdown reports
    reports = {
        "gated_build_dry_run_report": render_dry_run_report(
            as_of_date=as_of_date,
            preflight_gate=preflight_gate,
            execution_record=execution_record,
            workflow_result=workflow_result,
            comparison=comparison,
            drift_summary=drift_summary,
            boundary=boundary,
            summary=summary,
        ),
        "gated_build_preflight_report": render_preflight_report(
            as_of_date=as_of_date,
            preflight_gate=preflight_gate,
            input_availability=input_availability,
            date_alignment=date_alignment,
        ),
        "validate_vs_build_report": render_comparison_report(
            as_of_date=as_of_date, comparison=comparison, drift_summary=drift_summary
        ),
        "artifact_drift_report": render_drift_report(as_of_date=as_of_date, drift_summary=drift_summary),
        "source_trace_report": render_source_trace_report(
            as_of_date=as_of_date, source_trace=source_trace
        ),
    }
    for key, content in reports.items():
        path = artifact_paths.get(key)
        if path:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

    return {
        "builder_id": "A-SHARE-GATED-BUILD-FROM-EXISTING-DATA-BUILDER",
        "overall_passed": boundary.get("overall_passed", False),
        "blocking_reasons": boundary.get("blocking_reasons", []),
        "warnings": boundary.get("warnings", []),
        "preflight_gate_passed": preflight_gate.get("overall_passed", False),
        "gated_build_execution_performed": execution_record.get("command_executed", False),
        "workflow_status": execution_record.get("status", "unknown"),
        "workflow_audit_passed": workflow_result.get("workflow_audit_overall_passed", False),
        "workflow_mode": "build_from_existing_data",
        "comparison_completed": comparison.get("comparison_completed", False),
        "drift_status": drift_summary.get("overall_status", "unknown"),
        "gated_build_manifest": str(artifact_paths["gated_build_manifest"]),
        "gated_build_summary": str(artifact_paths["gated_build_summary"]),
        "gated_build_boundary_check": str(artifact_paths["gated_build_boundary_check"]),
        "gated_build_dry_run_report": str(artifact_paths["gated_build_dry_run_report"]),
        "exit_code": execution_record.get("exit_code", None),
        "recommended_next_version": "v0.8.8-a-share-build-from-existing-data-repeatability-and-diff-stability",
    }


def _source_artifacts(paths: ProjectPaths, as_of_date: str) -> dict:
    ops_history_dir = paths.data_dir / "equity_ops_history" / "daily" / as_of_date
    ops_center_dir = paths.data_dir / "equity_ops_center" / "daily" / as_of_date
    current_day_dir = paths.data_dir / "equity_current_day_runs" / "daily" / as_of_date
    data_refresh_dir = paths.data_dir / "equity_data_refresh" / "daily" / as_of_date
    audits_dir = paths.data_dir / "equity_data_quality"

    return {
        "ops_history_manifest": ops_history_dir / "ops_history_manifest.json",
        "ops_history_boundary_check": ops_history_dir / "ops_history_boundary_check.json",
        "ops_history_audit": audits_dir / "a_share_ops_history_baseline_audit.json",
        "ops_manifest": ops_center_dir / "ops_manifest.json",
        "ops_boundary_check": ops_center_dir / "ops_boundary_check.json",
        "ops_center_audit": audits_dir / "a_share_daily_ops_center_audit.json",
        "ops_health_score_card": ops_center_dir / "ops_health_score_card.json",
        "current_day_run_manifest": current_day_dir / "current_day_run_manifest.json",
        "current_day_boundary_check": current_day_dir / "current_day_boundary_check.json",
        "current_day_audit": audits_dir / "a_share_current_day_research_run_audit.json",
        "data_refresh_manifest": data_refresh_dir / "data_refresh_manifest.json",
        "data_refresh_boundary_check": data_refresh_dir / "data_refresh_boundary_check.json",
        "data_refresh_audit": audits_dir / "a_share_daily_data_refresh_audit.json",
    }


def _current_day_snapshot(paths: ProjectPaths, as_of_date: str) -> dict:
    current_day_dir = paths.data_dir / "equity_current_day_runs" / "daily" / as_of_date
    snapshot = {}
    for key in [
        "current_day_run_manifest",
        "current_day_workflow_execution",
        "current_day_stage_manifest",
        "current_day_artifact_index",
        "current_day_boundary_check",
        "current_day_source_trace",
        "current_day_summary",
    ]:
        path = current_day_dir / f"{key}.json"
        if path.exists():
            try:
                snapshot[key] = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                snapshot[key] = {}
    return snapshot


def _upstream_audit(paths: ProjectPaths, filename: str) -> bool:
    path = paths.data_dir / "equity_data_quality" / filename
    if not path.exists():
        return False
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload.get("overall_passed", False) is True
    except Exception:
        return False
