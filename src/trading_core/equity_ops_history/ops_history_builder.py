"""Builder for v0.8.6 A-share ops history baselines."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from trading_core.equity_data_quality.common import write_json
from trading_core.equity_ops_history.action_recurrence import build_ops_action_recurrence_baseline
from trading_core.equity_ops_history.baseline_drift import build_ops_baseline_drift_snapshot
from trading_core.equity_ops_history.boundary_history import build_ops_boundary_history_snapshot
from trading_core.equity_ops_history.health_score_baseline import build_ops_health_score_baseline
from trading_core.equity_ops_history.health_score_history import build_ops_health_score_history
from trading_core.equity_ops_history.history_append import append_ops_run_history
from trading_core.equity_ops_history.history_snapshot import build_ops_history_snapshot
from trading_core.equity_ops_history.input_availability import build_ops_history_input_availability, load_json, ops_history_input_paths
from trading_core.equity_ops_history.issue_recurrence import build_ops_issue_recurrence_baseline
from trading_core.equity_ops_history.module_reliability import build_ops_module_reliability_baseline
from trading_core.equity_ops_history.ops_history_boundary import build_ops_history_boundary_check
from trading_core.equity_ops_history.ops_history_config import (
    AUDIT_EXISTING_HISTORY_BASELINES,
    BUILD_TREND_BASELINES,
    DEFAULT_AS_OF_DATE,
    DEFAULT_BASELINE_WINDOW_OBSERVATIONS,
    DEFAULT_HISTORY_WINDOW_DAYS,
    DEFAULT_MINIMUM_REQUIRED_OBSERVATIONS,
    OPS_HISTORY_FILES,
    OPS_HISTORY_INDEX_FILES,
    OPS_HISTORY_REPORTS,
    OpsHistoryConfig,
    ops_history_artifact_paths,
    ops_history_output_dir,
    validate_ops_history_config,
)
from trading_core.equity_ops_history.ops_history_manifest import build_ops_history_manifest, build_ops_history_summary
from trading_core.equity_ops_history.ops_history_report import write_ops_history_reports
from trading_core.equity_ops_history.ops_history_source_trace import build_ops_history_source_trace
from trading_core.equity_ops_history.run_record import build_ops_run_record
from trading_core.equity_ops_history.trend_baseline_config import build_ops_trend_baseline_config
from trading_core.equity_ops_history.trend_sufficiency import build_ops_trend_sufficiency
from trading_core.equity_ops_history.warning_recurrence import build_ops_warning_recurrence_baseline
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def validate_a_share_ops_history_inputs(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    availability = build_ops_history_input_availability(paths=paths, as_of_date=as_of_date)
    return {
        "builder_id": "A-SHARE-OPS-HISTORY-INPUT-VALIDATION",
        "mode": "validate_history_inputs",
        "as_of_date": as_of_date,
        "overall_passed": availability["overall_passed"],
        "blocking_reasons": availability["blocking_reasons"],
        "warnings": availability["warnings"],
        "ops_center_audit_passed": availability["input_audit_checks"]["ops_center_audit_passed"],
    }


def build_a_share_ops_history_baseline(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    mode: str = BUILD_TREND_BASELINES,
    history_window_days: int = DEFAULT_HISTORY_WINDOW_DAYS,
    minimum_required_observations: int = DEFAULT_MINIMUM_REQUIRED_OBSERVATIONS,
    baseline_window_observations: int = DEFAULT_BASELINE_WINDOW_OBSERVATIONS,
    allow_rebuild_history: bool = False,
    allow_synthetic_history: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    if mode == AUDIT_EXISTING_HISTORY_BASELINES:
        from trading_core.equity_ops_history.ops_history_audit import audit_a_share_ops_history_baseline

        return audit_a_share_ops_history_baseline(as_of_date=as_of_date, paths=paths)
    config = OpsHistoryConfig(
        as_of_date=as_of_date,
        mode=mode,
        history_window_days=history_window_days,
        minimum_required_observations=minimum_required_observations,
        baseline_window_observations=baseline_window_observations,
        allow_rebuild_history=allow_rebuild_history,
        allow_synthetic_history=allow_synthetic_history,
    )
    issues = validate_ops_history_config(config)
    if issues:
        raise ValueError("; ".join(issues))
    availability = build_ops_history_input_availability(paths=paths, as_of_date=as_of_date)
    if not availability["overall_passed"]:
        raise ValueError("; ".join(availability["blocking_reasons"]))

    artifacts = ops_history_artifact_paths(paths, as_of_date)
    input_paths = ops_history_input_paths(paths, as_of_date)
    payloads = {key: load_json(path) for key, path in input_paths.items()}
    generated_at = datetime.now(timezone.utc).isoformat()

    run_record = build_ops_run_record(paths=paths, as_of_date=as_of_date, payloads=payloads, input_paths=input_paths)
    history_index, append_result = append_ops_run_history(
        history_path=artifacts["ops_run_history_index"],
        run_record=run_record,
        allow_rebuild_history=allow_rebuild_history,
    )
    records = list(history_index.get("records", []))
    snapshot = build_ops_history_snapshot(
        as_of_date=as_of_date,
        history_index=history_index,
        minimum_required_observations=minimum_required_observations,
    )
    trend_config = build_ops_trend_baseline_config(
        as_of_date=as_of_date,
        history_window_days=history_window_days,
        minimum_required_observations=minimum_required_observations,
        baseline_window_observations=baseline_window_observations,
    )
    sufficiency = build_ops_trend_sufficiency(
        as_of_date=as_of_date,
        observation_count=snapshot["run_history_observation_count"],
        minimum_required_observations=minimum_required_observations,
        baseline_window_observations=baseline_window_observations,
    )
    health_history = build_ops_health_score_history(as_of_date=as_of_date, records=records)
    health_baseline = build_ops_health_score_baseline(
        as_of_date=as_of_date,
        health_history=health_history,
        minimum_required_observations=minimum_required_observations,
        baseline_window_observations=baseline_window_observations,
    )
    module_baseline = build_ops_module_reliability_baseline(
        as_of_date=as_of_date,
        module_matrix=payloads["ops_module_status_matrix"],
        records=records,
        minimum_required_observations=minimum_required_observations,
    )
    warning_baseline = build_ops_warning_recurrence_baseline(
        as_of_date=as_of_date,
        issue_summary=payloads["ops_issue_summary"],
        records=records,
        minimum_required_observations=minimum_required_observations,
    )
    issue_baseline = build_ops_issue_recurrence_baseline(
        as_of_date=as_of_date,
        issue_summary=payloads["ops_issue_summary"],
        records=records,
        minimum_required_observations=minimum_required_observations,
    )
    action_baseline = build_ops_action_recurrence_baseline(
        as_of_date=as_of_date,
        action_checklist=payloads["ops_action_summary"],
        records=records,
    )
    boundary_snapshot = build_ops_boundary_history_snapshot(as_of_date=as_of_date, ops_boundary=payloads["ops_boundary_check"])
    drift = build_ops_baseline_drift_snapshot(as_of_date, snapshot["run_history_observation_count"], minimum_required_observations)
    boundary = build_ops_history_boundary_check(
        paths=paths,
        as_of_date=as_of_date,
        warnings=availability["warnings"] + append_result["warnings"],
        blocking_reasons=[],
        commands_executed=[],
        synthetic_history_used=False,
        future_dates_used=False,
    )

    index_payloads = _history_index_payloads(
        as_of_date=as_of_date,
        health_history=health_history,
        module_baseline=module_baseline,
        warning_baseline=warning_baseline,
        issue_baseline=issue_baseline,
        action_baseline=action_baseline,
        boundary_snapshot=boundary_snapshot,
    )
    for key, payload in index_payloads.items():
        write_json(artifacts[key], payload)

    output_paths = {key: artifacts[key] for key in OPS_HISTORY_FILES}
    output_paths.update({key: artifacts[key] for key in OPS_HISTORY_INDEX_FILES})
    output_paths.update({key: artifacts[key] for key in OPS_HISTORY_REPORTS})
    source_trace = build_ops_history_source_trace(
        paths=paths,
        as_of_date=as_of_date,
        generated_at=generated_at,
        source_paths=input_paths,
        output_paths=output_paths,
        command_policy_decisions={
            "mode": mode,
            "append_only_history": True,
            "allow_rebuild_history": allow_rebuild_history,
            "allow_synthetic_history": allow_synthetic_history,
            "commands_executed": [],
        },
    )
    manifest = build_ops_history_manifest(
        as_of_date=as_of_date,
        generated_at=generated_at,
        mode=mode,
        run_record=run_record,
        append_result=append_result,
        snapshot=snapshot,
        trend_sufficiency=sufficiency,
        boundary=boundary,
        output_artifacts=output_paths,
        source_artifacts=input_paths,
    )
    summary = build_ops_history_summary(as_of_date=as_of_date, mode=mode, manifest=manifest, append_result=append_result)
    payload: dict[str, Any] = {
        "ops_history_config": config.to_dict(),
        "ops_history_input_availability": availability,
        "ops_run_record": run_record,
        "ops_history_append_result": append_result,
        "ops_history_snapshot": snapshot,
        "ops_trend_baseline_config": trend_config,
        "ops_trend_sufficiency": sufficiency,
        "ops_health_score_history": health_history,
        "ops_health_score_baseline": health_baseline,
        "ops_module_reliability_baseline": module_baseline,
        "ops_warning_recurrence_baseline": warning_baseline,
        "ops_issue_recurrence_baseline": issue_baseline,
        "ops_action_recurrence_baseline": action_baseline,
        "ops_boundary_history_snapshot": boundary_snapshot,
        "ops_baseline_drift_snapshot": drift,
        "ops_history_source_trace": source_trace,
        "ops_history_boundary_check": boundary,
        "ops_history_manifest": manifest,
        "ops_history_summary": summary,
    }
    for key, value in payload.items():
        write_json(artifacts[key], value)
    write_ops_history_reports(ops_history_output_dir(paths, as_of_date), payload)
    return {
        "builder_id": "A-SHARE-OPS-HISTORY-BASELINE-BUILDER",
        "mode": mode,
        "as_of_date": as_of_date,
        "overall_passed": boundary["overall_passed"] and availability["overall_passed"],
        "blocking_reasons": boundary["blocking_reasons"],
        "warnings": boundary["warnings"],
        "run_history_observation_count": snapshot["run_history_observation_count"],
        "trend_analysis_available": sufficiency["trend_analysis_available"],
        "baseline_status": sufficiency["baseline_status"],
        "append_completed": append_result["append_completed"],
        "idempotent_append": append_result["idempotent_append"],
        "synthetic_history_used": sufficiency["synthetic_history_used"],
        "future_dates_used": sufficiency["future_dates_used"],
        "commands_executed": [],
        "ops_history_manifest_path": str(artifacts["ops_history_manifest"]),
        "ops_history_summary_path": str(artifacts["ops_history_summary"]),
        "ops_run_history_baseline_report": str(artifacts["ops_run_history_baseline_report"]),
    }


def _history_index_payloads(
    *,
    as_of_date: str,
    health_history: dict[str, Any],
    module_baseline: dict[str, Any],
    warning_baseline: dict[str, Any],
    issue_baseline: dict[str, Any],
    action_baseline: dict[str, Any],
    boundary_snapshot: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    return {
        "ops_health_score_history_index": {**health_history, "index_id": "A-SHARE-OPS-HEALTH-SCORE-HISTORY-INDEX"},
        "ops_module_status_history_index": {
            "index_id": "A-SHARE-OPS-MODULE-STATUS-HISTORY-INDEX",
            "target_version": module_baseline["target_version"],
            "as_of_date": as_of_date,
            "records": module_baseline.get("modules", []),
        },
        "ops_warning_history_index": {
            "index_id": "A-SHARE-OPS-WARNING-HISTORY-INDEX",
            "target_version": warning_baseline["target_version"],
            "as_of_date": as_of_date,
            "records": warning_baseline.get("items", []),
        },
        "ops_issue_history_index": {
            "index_id": "A-SHARE-OPS-ISSUE-HISTORY-INDEX",
            "target_version": issue_baseline["target_version"],
            "as_of_date": as_of_date,
            "records": issue_baseline.get("items", []),
        },
        "ops_action_history_index": {
            "index_id": "A-SHARE-OPS-ACTION-HISTORY-INDEX",
            "target_version": action_baseline["target_version"],
            "as_of_date": as_of_date,
            "records": action_baseline.get("items", []),
        },
        "ops_boundary_history_index": {
            "index_id": "A-SHARE-OPS-BOUNDARY-HISTORY-INDEX",
            "target_version": boundary_snapshot["target_version"],
            "as_of_date": as_of_date,
            "records": boundary_snapshot.get("records", []),
        },
    }
