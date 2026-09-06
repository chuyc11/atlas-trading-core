"""Runner for v0.7.9 A-share daily research workflow orchestration."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any
from collections.abc import Callable

from trading_core.equity_briefings.briefing_audit import audit_a_share_daily_stock_selection_briefing
from trading_core.equity_briefings.daily_stock_selection_briefing import build_a_share_daily_stock_selection_briefing
from trading_core.equity_data_quality.common import json_safe, utc_now, write_json
from trading_core.equity_features.feature_audit import audit_a_share_multi_horizon_features
from trading_core.equity_features.multi_horizon import build_a_share_multi_horizon_features
from trading_core.equity_portfolio_tracking.tracking_audit import audit_a_share_virtual_portfolio_tracking
from trading_core.equity_portfolio_tracking.tracking_builder import build_a_share_virtual_portfolio_tracking
from trading_core.equity_portfolios.virtual_portfolio_audit import audit_a_share_virtual_portfolios
from trading_core.equity_portfolios.virtual_portfolio_builder import build_a_share_virtual_portfolios
from trading_core.equity_scoring.component_scores import build_a_share_scores
from trading_core.equity_scoring.scoring_audit import audit_a_share_scores
from trading_core.equity_selection.candidate_generation_audit import audit_a_share_candidates
from trading_core.equity_selection.candidate_generator import generate_a_share_candidates
from trading_core.equity_selection.filter_config import TradableUniverseFilterConfig
from trading_core.equity_selection.tradable_universe_audit import audit_a_share_tradable_universe
from trading_core.equity_selection.tradable_universe_filter import build_a_share_tradable_universe
from trading_core.equity_workflows.workflow_config import (
    BUILD_FROM_EXISTING_DATA,
    DEFAULT_AS_OF_DATE,
    RECOMMENDED_NEXT_VERSION,
    TARGET_VERSION,
    VALIDATE_EXISTING_ARTIFACTS,
    WORKFLOW_BOUNDARY,
    WORKFLOW_FLAGS,
    WorkflowConfig,
    required_input_artifacts,
    stage_definitions,
    validate_workflow_config,
    workflow_artifact_paths,
    workflow_output_dir,
)
from trading_core.equity_workflows.workflow_manifest import (
    build_boundary_check,
    build_run_manifest,
    build_stage_manifest,
    build_workflow_summary,
    load_json,
)
from trading_core.equity_workflows.workflow_preflight import preflight_a_share_daily_workflow
from trading_core.equity_workflows.workflow_report import write_workflow_reports
from trading_core.equity_workflows.workflow_source_trace import build_workflow_source_trace
from trading_core.equity_workflows.workflow_stage import blocked_stage_record, make_stage_record, utc_now as stage_now
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


StageExecutor = Callable[[dict[str, Any], WorkflowConfig, ProjectPaths], dict[str, Any]]


def run_a_share_daily_research_workflow(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    mode: str = VALIDATE_EXISTING_ARTIFACTS,
    allow_latest_artifact_date: bool = False,
    allow_public_data_refresh: bool = False,
    allow_build_timestamp_drift: bool = True,
    fail_on_build_timestamp_drift: bool = False,
    allow_version_shim_warning: bool = False,
    paths: ProjectPaths | None = None,
    stage_executor: StageExecutor | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    config = WorkflowConfig(
        as_of_date=as_of_date,
        mode=mode,
        allow_public_data_refresh=allow_public_data_refresh,
        allow_latest_artifact_date=allow_latest_artifact_date,
        allow_build_timestamp_drift=allow_build_timestamp_drift,
        fail_on_build_timestamp_drift=fail_on_build_timestamp_drift,
        allow_version_shim_warning=allow_version_shim_warning,
    )
    issues = validate_workflow_config(config)
    if issues:
        raise ValueError("; ".join(issues))
    artifacts = workflow_artifact_paths(paths, as_of_date)
    artifacts["workflow_config"].parent.mkdir(parents=True, exist_ok=True)
    workflow_output_dir(paths, as_of_date).mkdir(parents=True, exist_ok=True)
    started_at = utc_now()
    write_json(artifacts["workflow_config"], config.to_dict())

    preflight = preflight_a_share_daily_workflow(
        as_of_date=as_of_date,
        mode=mode,
        allow_latest_artifact_date=allow_latest_artifact_date,
        allow_public_data_refresh=allow_public_data_refresh,
        allow_build_timestamp_drift=allow_build_timestamp_drift,
        fail_on_build_timestamp_drift=fail_on_build_timestamp_drift,
        allow_version_shim_warning=allow_version_shim_warning,
        paths=paths,
    )
    definitions = stage_definitions(paths, as_of_date)
    stages: list[dict[str, Any]] = []
    blocking_reasons: list[str] = []
    warnings: list[str] = []
    executor = stage_executor or _execute_build_stage

    for definition in definitions:
        if blocking_reasons and definition["stage_id"] not in {"stage_09_workflow_audit", "stage_10_owner_summary"}:
            stages.append(blocked_stage_record(definition=definition, mode=mode, paths=paths, reason="previous critical stage failed").to_dict())
            continue
        record = _run_stage(
            definition=definition,
            mode=mode,
            paths=paths,
            config=config,
            preflight=preflight,
            executor=executor,
            has_prior_blocking=bool(blocking_reasons),
        )
        stages.append(record)
        warnings.extend(record.get("warnings", []))
        if record["status"] in {"failed", "blocked"}:
            blocking_reasons.extend(record.get("blocking_reasons", []))

    finished_at = utc_now()
    duration = _duration_seconds(started_at, finished_at)
    stage_manifest = build_stage_manifest(as_of_date=as_of_date, mode=mode, stages=stages, generated_at=finished_at)
    run_manifest = build_run_manifest(
        as_of_date=as_of_date,
        mode=mode,
        started_at=started_at,
        finished_at=finished_at,
        duration_seconds=duration,
        stages=stages,
        warnings=sorted(set(warnings)),
        blocking_reasons=sorted(set(blocking_reasons)),
    )
    boundary_check = build_boundary_check(paths=paths, as_of_date=as_of_date, warnings=sorted(set(warnings)), blocking_reasons=sorted(set(blocking_reasons)))
    write_json(artifacts["workflow_stage_manifest"], stage_manifest)
    write_json(artifacts["workflow_run_manifest"], run_manifest)
    write_json(artifacts["workflow_boundary_check"], boundary_check)
    source_trace = build_workflow_source_trace(
        paths=paths,
        as_of_date=as_of_date,
        mode=mode,
        stages=stages,
        workflow_artifacts=artifacts,
        generated_at=finished_at,
    )
    write_json(artifacts["workflow_source_trace"], source_trace)
    workflow_summary = build_workflow_summary(
        paths=paths,
        as_of_date=as_of_date,
        mode=mode,
        run_manifest=run_manifest,
        source_trace=source_trace,
        boundary_check=boundary_check,
    )
    write_json(artifacts["workflow_summary"], workflow_summary)
    payload = {
        "workflow_id": "A-SHARE-DAILY-RESEARCH-WORKFLOW-RUNNER",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "mode": mode,
        "workflow_config": config.to_dict(),
        "workflow_preflight": preflight,
        "workflow_stage_manifest": stage_manifest,
        "workflow_run_manifest": run_manifest,
        "workflow_source_trace": source_trace,
        "workflow_boundary_check": boundary_check,
        "workflow_summary": workflow_summary,
        "artifacts": {key: relative(path, paths.project_root) for key, path in artifacts.items()},
        **WORKFLOW_FLAGS,
        "boundary": dict(WORKFLOW_BOUNDARY),
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }
    payload["reports"] = write_workflow_reports(workflow_output_dir(paths, as_of_date), payload)
    return json_safe(payload)


def _run_stage(
    *,
    definition: dict[str, Any],
    mode: str,
    paths: ProjectPaths,
    config: WorkflowConfig,
    preflight: dict[str, Any],
    executor: StageExecutor,
    has_prior_blocking: bool,
) -> dict[str, Any]:
    started = stage_now()
    status = "passed"
    blocking: list[str] = []
    warnings: list[str] = []
    command = str(definition["validate_command"] if mode == VALIDATE_EXISTING_ARTIFACTS else definition["build_command"])
    if definition["stage_id"] == "stage_00_preflight":
        status = "passed" if preflight.get("overall_passed") else "failed"
        blocking = list(preflight.get("blocking_reasons", []))
        warnings = list(preflight.get("warnings", []))
    elif definition["stage_id"] == "stage_01_data_readiness":
        ok, missing = _data_readiness(paths, config)
        status = "passed" if ok else "failed"
        blocking = [] if ok else [f"missing_required_artifacts:{missing}"]
    elif definition["stage_id"] in {"stage_09_workflow_audit", "stage_10_owner_summary"}:
        if has_prior_blocking:
            status = "blocked"
            blocking = ["previous critical stage failed"]
        else:
            status = "passed"
    elif mode == VALIDATE_EXISTING_ARTIFACTS:
        ok, stage_warnings, stage_blocking = _validate_existing_stage(definition)
        status = "passed" if ok else "failed"
        warnings = stage_warnings
        blocking = stage_blocking
    else:
        result = executor(definition, config, paths)
        status = "passed" if result.get("overall_passed", False) else "failed"
        warnings = [str(item) for item in result.get("warnings", []) if item]
        blocking = [str(item) for item in result.get("blocking_reasons", []) if item]
        if not blocking and status == "failed":
            blocking = [f"{definition['stage_id']}_build_or_audit_failed"]
    finished = stage_now()
    return make_stage_record(
        definition=definition,
        mode=mode,
        command=command,
        status=status,
        paths=paths,
        started_at=started,
        finished_at=finished,
        blocking_reasons=blocking,
        warnings=warnings,
    ).to_dict()


def _data_readiness(paths: ProjectPaths, config: WorkflowConfig) -> tuple[bool, list[str]]:
    required = required_input_artifacts(paths, config.as_of_date)
    if config.mode == VALIDATE_EXISTING_ARTIFACTS:
        missing = [relative(path, paths.project_root) for path in required.values() if not path.exists()]
        return not missing, missing
    build_required = [required["history_dir"]]
    missing = [relative(path, paths.project_root) for path in build_required if not path.exists()]
    return not missing, missing


def _validate_existing_stage(definition: dict[str, Any]) -> tuple[bool, list[str], list[str]]:
    warnings = []
    blocking = []
    for path in definition.get("input_artifacts", []):
        if isinstance(path, Path) and not path.exists():
            blocking.append(f"missing_input_artifact:{path}")
    for path in definition.get("audit_artifacts", []):
        if not isinstance(path, Path):
            continue
        audit = load_json(path)
        if not path.exists():
            blocking.append(f"missing_audit_artifact:{path}")
        elif audit.get("overall_passed") is not True:
            blocking.append(f"upstream_audit_not_passed:{path}")
        warnings.extend(str(item) for item in audit.get("warnings", []) if item)
    return not blocking, sorted(set(warnings)), blocking


def _execute_build_stage(definition: dict[str, Any], config: WorkflowConfig, paths: ProjectPaths) -> dict[str, Any]:
    stage_id = definition["stage_id"]
    as_of_date = config.as_of_date
    if stage_id == "stage_02_tradable_universe":
        tradable_config = TradableUniverseFilterConfig(as_of_date=as_of_date)
        build_a_share_tradable_universe(paths=paths, config=tradable_config)
        return audit_a_share_tradable_universe(
            paths=paths,
            as_of_date=as_of_date,
            min_listing_trading_days=tradable_config.min_listing_trading_days,
            min_avg_amount_20d=tradable_config.min_avg_amount_20d,
            min_avg_amount_60d=tradable_config.min_avg_amount_60d,
            min_total_mv=tradable_config.min_total_mv,
            min_circ_mv=tradable_config.min_circ_mv,
            min_close_price=tradable_config.min_close_price,
            allow_previous_trading_day=tradable_config.allow_previous_trading_day,
        )
    if stage_id == "stage_03_feature_engineering":
        build_a_share_multi_horizon_features(paths=paths, as_of_date=as_of_date, allow_latest_tradable_universe=config.allow_latest_artifact_date)
        return audit_a_share_multi_horizon_features(paths=paths, as_of_date=as_of_date, allow_latest_tradable_universe=config.allow_latest_artifact_date)
    if stage_id == "stage_04_scoring":
        build_a_share_scores(paths=paths, as_of_date=as_of_date, allow_latest_feature_date=config.allow_latest_artifact_date)
        return audit_a_share_scores(
            paths=paths,
            as_of_date=as_of_date,
            allow_latest_feature_date=config.allow_latest_artifact_date,
            allow_existing_downstream_artifacts=config.mode == BUILD_FROM_EXISTING_DATA,
        )
    if stage_id == "stage_05_candidate_generation":
        generate_a_share_candidates(paths=paths, as_of_date=as_of_date, allow_latest_score_date=config.allow_latest_artifact_date)
        return audit_a_share_candidates(
            paths=paths,
            as_of_date=as_of_date,
            allow_latest_score_date=config.allow_latest_artifact_date,
            allow_existing_downstream_artifacts=config.mode == BUILD_FROM_EXISTING_DATA,
        )
    if stage_id == "stage_06_virtual_portfolio_construction":
        build_a_share_virtual_portfolios(paths=paths, as_of_date=as_of_date, allow_latest_candidate_date=config.allow_latest_artifact_date)
        return audit_a_share_virtual_portfolios(paths=paths, as_of_date=as_of_date, allow_latest_candidate_date=config.allow_latest_artifact_date)
    if stage_id == "stage_07_daily_briefing":
        build_a_share_daily_stock_selection_briefing(paths=paths, as_of_date=as_of_date, allow_latest_artifact_date=config.allow_latest_artifact_date)
        return audit_a_share_daily_stock_selection_briefing(paths=paths, as_of_date=as_of_date, allow_latest_artifact_date=config.allow_latest_artifact_date)
    if stage_id == "stage_08_virtual_portfolio_tracking":
        build_a_share_virtual_portfolio_tracking(paths=paths, as_of_date=as_of_date)
        return audit_a_share_virtual_portfolio_tracking(paths=paths, as_of_date=as_of_date)
    return {"overall_passed": True, "blocking_reasons": [], "warnings": []}


def _duration_seconds(started_at: str, finished_at: str) -> float:
    started = datetime.fromisoformat(started_at)
    finished = datetime.fromisoformat(finished_at)
    return max((finished - started).total_seconds(), 0.0)
