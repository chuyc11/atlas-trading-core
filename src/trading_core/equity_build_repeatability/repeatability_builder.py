"""Orchestrator for v0.8.8 build repeatability."""

from __future__ import annotations

import json

from trading_core.equity_build_repeatability.artifact_snapshot import build_artifact_snapshot
from trading_core.equity_build_repeatability.build_comparison import build_build_vs_build_comparison
from trading_core.equity_build_repeatability.date_alignment import build_repeatability_date_alignment
from trading_core.equity_build_repeatability.deterministic_normalization import build_deterministic_field_normalization
from trading_core.equity_build_repeatability.drift_summary import build_repeatability_drift_summary
from trading_core.equity_build_repeatability.execution_plan import build_repeat_build_execution_plan
from trading_core.equity_build_repeatability.execution_record import execute_repeat_build_and_record
from trading_core.equity_build_repeatability.input_availability import build_repeatability_input_availability
from trading_core.equity_build_repeatability.protected_path_snapshot import (
    build_protected_path_modification_check,
    build_protected_path_snapshot,
)
from trading_core.equity_build_repeatability.repeatability_boundary import build_repeatability_boundary_check
from trading_core.equity_build_repeatability.repeatability_config import (
    ALLOWED_MODES,
    DEFAULT_AS_OF_DATE,
    REPEATABILITY_FILES,
    RUN_REPEAT_BUILD_FROM_EXISTING_DATA,
    TARGET_VERSION,
    RepeatabilityConfig,
    repeatability_artifact_paths,
    repeatability_data_dir,
    validate_repeatability_config,
)
from trading_core.equity_build_repeatability.repeatability_manifest import (
    build_repeatability_manifest,
    build_repeatability_summary,
)
from trading_core.equity_build_repeatability.repeatability_report import (
    render_build_vs_build_report,
    render_drift_summary_report,
    render_protected_path_report,
    render_repeatability_report,
    render_source_trace_report,
)
from trading_core.equity_build_repeatability.repeatability_source_trace import build_repeatability_source_trace
from trading_core.equity_build_repeatability.warning_comparison import build_repeatability_warning_comparison
from trading_core.equity_build_repeatability.workflow_result import build_repeat_build_workflow_result
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def validate_a_share_build_repeatability_inputs(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    paths: ProjectPaths | None = None,
) -> dict:
    availability = build_repeatability_input_availability(paths=paths, as_of_date=as_of_date)
    return {
        "builder_id": "A-SHARE-BUILD-REPEATABILITY-INPUT-VALIDATOR",
        "overall_passed": availability["overall_passed"],
        "blocking_reasons": availability["blocking_reasons"],
        "warnings": len(availability["warnings"]),
        "gated_build_audit_passed": availability["gated_build_audit_passed"],
        "gated_build_workflow_mode": availability["gated_build_workflow_mode"],
    }


def build_a_share_build_repeatability(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    mode: str = RUN_REPEAT_BUILD_FROM_EXISTING_DATA,
    allow_date_mismatch: bool = False,
    allow_business_output_drift: bool = False,
    paths: ProjectPaths | None = None,
) -> dict:
    paths = default_paths(paths)
    config = RepeatabilityConfig(
        as_of_date=as_of_date,
        mode=mode,
        allow_date_mismatch=allow_date_mismatch,
        allow_business_output_drift=allow_business_output_drift,
    )
    issues = validate_repeatability_config(config)
    if issues:
        raise ValueError(f"invalid repeatability config: {issues}")
    if mode not in ALLOWED_MODES:
        raise ValueError(f"mode must be one of {ALLOWED_MODES}")

    artifact_paths = repeatability_artifact_paths(paths, as_of_date)
    repeatability_data_dir(paths, as_of_date).mkdir(parents=True, exist_ok=True)

    availability = build_repeatability_input_availability(paths=paths, as_of_date=as_of_date)
    date_alignment = build_repeatability_date_alignment(
        as_of_date=as_of_date,
        input_availability=availability,
        allow_date_mismatch=allow_date_mismatch,
    )
    pre_snapshot = build_protected_path_snapshot(paths=paths, as_of_date=as_of_date, snapshot_phase="pre_run")
    plan = build_repeat_build_execution_plan(as_of_date=as_of_date)
    first_snapshot = build_artifact_snapshot(
        paths=paths,
        as_of_date=as_of_date,
        snapshot_id="A-SHARE-FIRST-BUILD-ARTIFACT-SNAPSHOT",
    )

    if mode == RUN_REPEAT_BUILD_FROM_EXISTING_DATA:
        execution_record = execute_repeat_build_and_record(
            paths=paths,
            as_of_date=as_of_date,
            input_availability=availability,
            date_alignment=date_alignment,
            execution_plan=plan,
        )
    else:
        execution_record = {
            "execution_id": "A-SHARE-REPEAT-BUILD-FROM-EXISTING-DATA-EXECUTION",
            "target_version": TARGET_VERSION,
            "as_of_date": as_of_date,
            "workflow_mode": "build_from_existing_data",
            "command": plan.get("workflow_command"),
            "command_executed": False,
            "exit_code": None,
            "status": "skipped",
            "workflow_audit_path": "",
            "workflow_audit_overall_passed": False,
            "blocking_reasons": [],
            "warnings": [],
            "old_run_daily_called": False,
            "run_daily_called": False,
            "broker_connected": False,
            "real_orders_placed": False,
            "buy_sell_signals_generated": False,
            "order_preview_generated": False,
            "real_account_data_read": False,
            "public_network_refresh_run": False,
            "full_research_run": False,
        }

    workflow_result = build_repeat_build_workflow_result(
        paths=paths,
        as_of_date=as_of_date,
        execution_record=execution_record,
    )
    post_snapshot = build_protected_path_snapshot(paths=paths, as_of_date=as_of_date, snapshot_phase="post_run")
    protected_check = build_protected_path_modification_check(
        as_of_date=as_of_date,
        pre_snapshot=pre_snapshot,
        post_snapshot=post_snapshot,
    )
    second_snapshot = build_artifact_snapshot(
        paths=paths,
        as_of_date=as_of_date,
        snapshot_id="A-SHARE-SECOND-BUILD-ARTIFACT-SNAPSHOT",
    )
    comparison = build_build_vs_build_comparison(
        paths=paths,
        as_of_date=as_of_date,
        first_snapshot=first_snapshot,
        second_snapshot=second_snapshot,
        protected_check=protected_check,
        allow_business_output_drift=allow_business_output_drift,
    )
    drift_summary = build_repeatability_drift_summary(
        as_of_date=as_of_date,
        comparison=comparison,
        protected_check=protected_check,
        allow_business_output_drift=allow_business_output_drift,
    )
    normalization = build_deterministic_field_normalization(as_of_date=as_of_date)
    warning_comparison = build_repeatability_warning_comparison(
        paths=paths,
        as_of_date=as_of_date,
        execution_record=execution_record,
    )

    payloads = {
        "repeatability_config": config.to_dict(),
        "repeatability_input_availability": availability,
        "repeatability_date_alignment": date_alignment,
        "protected_path_pre_run_snapshot": pre_snapshot,
        "repeat_build_execution_plan": plan,
        "repeat_build_execution_record": execution_record,
        "repeat_build_workflow_result": workflow_result,
        "protected_path_post_run_snapshot": post_snapshot,
        "protected_path_modification_check": protected_check,
        "first_build_artifact_snapshot": first_snapshot,
        "second_build_artifact_snapshot": second_snapshot,
        "build_vs_build_comparison": comparison,
        "repeatability_drift_summary": drift_summary,
        "deterministic_field_normalization": normalization,
        "repeatability_warning_comparison": warning_comparison,
    }
    _write_json_payloads(payloads, artifact_paths)

    source_trace = build_repeatability_source_trace(
        paths=paths,
        as_of_date=as_of_date,
        source_artifacts=_source_artifacts(paths, as_of_date),
        output_artifacts={k: v for k, v in artifact_paths.items() if k in REPEATABILITY_FILES},
    )
    boundary = build_repeatability_boundary_check(
        paths=paths,
        as_of_date=as_of_date,
        execution_record=execution_record,
        protected_check=protected_check,
        comparison=comparison,
        drift_summary=drift_summary,
    )
    manifest = build_repeatability_manifest(
        as_of_date=as_of_date,
        mode=mode,
        execution_record=execution_record,
        workflow_result=workflow_result,
        comparison=comparison,
        drift_summary=drift_summary,
        protected_check=protected_check,
        source_trace=source_trace,
        boundary=boundary,
        output_artifacts={k: v for k, v in artifact_paths.items() if k in REPEATABILITY_FILES},
        source_artifacts=_source_artifacts(paths, as_of_date),
        paths=paths,
    )
    summary = build_repeatability_summary(
        as_of_date=as_of_date,
        mode=mode,
        manifest=manifest,
        execution_record=execution_record,
        workflow_result=workflow_result,
        comparison=comparison,
        drift_summary=drift_summary,
        protected_check=protected_check,
        boundary=boundary,
    )
    payloads.update({
        "repeatability_source_trace": source_trace,
        "repeatability_boundary_check": boundary,
        "repeatability_manifest": manifest,
        "repeatability_summary": summary,
    })
    _write_json_payloads(payloads, artifact_paths)
    _write_reports(
        artifact_paths=artifact_paths,
        as_of_date=as_of_date,
        execution_record=execution_record,
        comparison=comparison,
        drift_summary=drift_summary,
        protected_check=protected_check,
        warning_comparison=warning_comparison,
        source_trace=source_trace,
        boundary=boundary,
        summary=summary,
    )

    return {
        "builder_id": "A-SHARE-BUILD-REPEATABILITY-BUILDER",
        "overall_passed": boundary.get("overall_passed", False),
        "blocking_reasons": boundary.get("blocking_reasons", []),
        "warnings": len(boundary.get("warnings", [])),
        "workflow_mode": "build_from_existing_data",
        "repeat_build_execution_performed": execution_record.get("command_executed", False),
        "repeat_build_audit_passed": workflow_result.get("workflow_audit_overall_passed", False),
        "comparison_completed": comparison.get("comparison_completed", False),
        "business_output_drift_count": comparison.get("business_output_drift_count", 0),
        "timestamp_only_drift_count": comparison.get("timestamp_only_drift_count", 0),
        "metadata_hash_drift_count": comparison.get("metadata_hash_drift_count", 0),
        "missing_required_artifact_count": comparison.get("missing_required_artifact_count", 0),
        "protected_path_modifications_detected": protected_check.get("protected_path_modifications_detected", False),
        "repeatability_summary": str(artifact_paths["repeatability_summary"]),
        "repeatability_report": str(artifact_paths["repeatability_report"]),
        "recommended_next_version": "v0.8.9-a-share-current-day-build-output-owner-dashboard-refresh",
    }


def _write_json_payloads(payloads: dict, artifact_paths: dict) -> None:
    for key, payload in payloads.items():
        path = artifact_paths.get(key)
        if path:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _write_reports(**kwargs) -> None:
    artifact_paths = kwargs["artifact_paths"]
    reports = {
        "repeatability_report": render_repeatability_report(**{k: v for k, v in kwargs.items() if k != "artifact_paths"}),
        "build_vs_build_report": render_build_vs_build_report(
            as_of_date=kwargs["as_of_date"],
            comparison=kwargs["comparison"],
        ),
        "drift_summary_report": render_drift_summary_report(
            as_of_date=kwargs["as_of_date"],
            drift_summary=kwargs["drift_summary"],
        ),
        "protected_path_report": render_protected_path_report(
            as_of_date=kwargs["as_of_date"],
            protected_check=kwargs["protected_check"],
        ),
        "source_trace_report": render_source_trace_report(
            as_of_date=kwargs["as_of_date"],
            source_trace=kwargs["source_trace"],
        ),
    }
    for key, content in reports.items():
        path = artifact_paths[key]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def _source_artifacts(paths: ProjectPaths, as_of_date: str) -> dict:
    gated_dir = paths.data_dir / "equity_current_day_builds" / "daily" / as_of_date
    quality = paths.data_dir / "equity_data_quality"
    return {
        "gated_build_audit": quality / "a_share_gated_build_from_existing_data_audit.json",
        "gated_build_manifest": gated_dir / "gated_build_manifest.json",
        "gated_build_execution_record": gated_dir / "gated_build_execution_record.json",
        "gated_build_workflow_result": gated_dir / "build_from_existing_data_workflow_result.json",
        "gated_build_artifact_drift": gated_dir / "artifact_drift_summary.json",
        "gated_build_boundary_check": gated_dir / "gated_build_boundary_check.json",
        "ops_history_audit": quality / "a_share_ops_history_baseline_audit.json",
        "ops_center_audit": quality / "a_share_daily_ops_center_audit.json",
        "data_refresh_audit": quality / "a_share_daily_data_refresh_audit.json",
        "current_day_audit": quality / "a_share_current_day_research_run_audit.json",
    }

