"""Orchestrate v0.8.1 A-share current-day research workflow runs."""

from __future__ import annotations

from typing import Any

from trading_core.equity_attribution.attribution_audit import audit_a_share_performance_attribution
from trading_core.equity_attribution.attribution_builder import build_a_share_performance_attribution
from trading_core.equity_benchmarks.benchmark_audit import audit_a_share_benchmark_comparison
from trading_core.equity_benchmarks.benchmark_builder import build_a_share_benchmark_comparison
from trading_core.equity_current_day.current_day_artifact_index import build_current_day_artifact_index
from trading_core.equity_current_day.current_day_boundary import build_current_day_boundary_check
from trading_core.equity_current_day.current_day_config import (
    AUDIT_EXISTING_CURRENT_DAY_RUN,
    DEFAULT_AS_OF_DATE,
    REFRESH_THEN_RUN_RESEARCH,
    RUN_RESEARCH_FROM_EXISTING_REFRESH,
    TARGET_VERSION,
    VALIDATE_CURRENT_DAY_READINESS,
    CurrentDayRunConfig,
    current_day_artifact_paths,
    current_day_data_dir,
    current_day_output_dir,
    validate_current_day_config,
)
from trading_core.equity_current_day.current_day_manifest import build_current_day_run_manifest, build_current_day_summary
from trading_core.equity_current_day.current_day_readiness import build_current_day_readiness
from trading_core.equity_current_day.current_day_report import write_current_day_reports
from trading_core.equity_current_day.current_day_source_trace import build_current_day_source_trace
from trading_core.equity_current_day.current_day_stage_manifest import build_current_day_stage_manifest
from trading_core.equity_current_day.current_day_warning_summary import build_current_day_warning_summary
from trading_core.equity_current_day.data_refresh_link import build_data_refresh_link, load_json
from trading_core.equity_current_day.workflow_execution import (
    build_blocked_workflow_execution,
    build_not_run_workflow_execution,
    build_workflow_execution_record,
)
from trading_core.equity_current_day.workflow_plan import build_current_day_workflow_plan
from trading_core.equity_data_quality.common import json_safe, utc_now, write_json
from trading_core.equity_data_refresh.data_refresh_audit import audit_a_share_daily_data_refresh
from trading_core.equity_data_refresh.data_refresh_builder import build_a_share_daily_data_refresh
from trading_core.equity_data_refresh.data_refresh_config import data_refresh_artifact_paths
from trading_core.equity_performance.performance_audit import audit_a_share_multi_day_performance
from trading_core.equity_performance.performance_builder import build_a_share_multi_day_performance
from trading_core.equity_workflows.workflow_audit import audit_a_share_daily_research_workflow
from trading_core.equity_workflows.workflow_runner import run_a_share_daily_research_workflow
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


def validate_a_share_current_day_readiness(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    use_data_refresh_resolved_date: bool = False,
    allow_date_mismatch: bool = False,
    workflow_mode: str = "validate_existing_artifacts",
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    return run_a_share_current_day_research(
        as_of_date=as_of_date,
        mode=VALIDATE_CURRENT_DAY_READINESS,
        workflow_mode=workflow_mode,
        use_data_refresh_resolved_date=use_data_refresh_resolved_date,
        allow_date_mismatch=allow_date_mismatch,
        paths=paths,
    )


def run_a_share_current_day_research(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    mode: str = RUN_RESEARCH_FROM_EXISTING_REFRESH,
    workflow_mode: str = "validate_existing_artifacts",
    use_data_refresh_resolved_date: bool = False,
    allow_date_mismatch: bool = False,
    allow_refresh_before_run: bool = False,
    allow_network_providers: bool = False,
    allow_public_providers: bool = False,
    run_post_workflow_modules: bool = False,
    allow_post_workflow_warnings_only: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    if mode == REFRESH_THEN_RUN_RESEARCH:
        _refresh_before_run(
            paths=paths,
            as_of_date=as_of_date,
            allow_refresh_before_run=allow_refresh_before_run,
            allow_network_providers=allow_network_providers,
            allow_public_providers=allow_public_providers,
        )
    resolved_as_of_date = _resolve_run_date(paths, as_of_date, use_data_refresh_resolved_date)
    config = CurrentDayRunConfig(
        as_of_date=as_of_date,
        resolved_as_of_date=resolved_as_of_date,
        mode=mode,
        workflow_mode=workflow_mode,
        use_data_refresh_resolved_date=use_data_refresh_resolved_date,
        allow_date_mismatch=allow_date_mismatch,
        allow_refresh_before_run=allow_refresh_before_run,
        allow_network_providers=allow_network_providers,
        allow_public_providers=allow_public_providers,
        run_post_workflow_modules=run_post_workflow_modules,
        allow_post_workflow_warnings_only=allow_post_workflow_warnings_only,
    )
    issues = validate_current_day_config(config)
    if issues:
        raise ValueError("; ".join(issues))
    artifacts = current_day_artifact_paths(paths, as_of_date)
    current_day_data_dir(paths, as_of_date).mkdir(parents=True, exist_ok=True)
    current_day_output_dir(paths, as_of_date).mkdir(parents=True, exist_ok=True)
    generated_at = utc_now()
    artifact_paths = {key: relative(path, paths.project_root) for key, path in artifacts.items()}
    refresh_artifacts = data_refresh_artifact_paths(paths, resolved_as_of_date)
    artifact_paths["data_refresh_audit_json"] = relative(refresh_artifacts["data_refresh_audit_json"], paths.project_root)

    readiness = build_current_day_readiness(
        paths=paths,
        as_of_date=as_of_date,
        resolved_as_of_date=resolved_as_of_date,
        workflow_mode=workflow_mode,
        allow_date_mismatch=allow_date_mismatch,
    )
    data_refresh_link = build_data_refresh_link(paths=paths, as_of_date=as_of_date, resolved_as_of_date=resolved_as_of_date)
    workflow_plan = build_current_day_workflow_plan(
        paths=paths,
        as_of_date=as_of_date,
        resolved_as_of_date=resolved_as_of_date,
        workflow_mode=workflow_mode,
        run_post_workflow_modules=run_post_workflow_modules,
    )
    workflow_execution = _execute_workflow(
        paths=paths,
        config=config,
        readiness=readiness,
        workflow_command=workflow_plan["workflow_command"],
    )
    warning_summary = build_current_day_warning_summary(
        as_of_date=as_of_date,
        resolved_as_of_date=resolved_as_of_date,
        data_refresh_warnings=list(data_refresh_link.get("data_refresh_warnings", [])),
        workflow_warnings=list(workflow_execution.get("workflow_warnings", [])),
        runner_warnings=[],
    )
    blocking = _blocking(readiness, workflow_execution, warning_summary)
    warnings = sorted({row["warning"] for row in warning_summary.get("warnings", [])})
    stage_manifest = build_current_day_stage_manifest(
        as_of_date=as_of_date,
        resolved_as_of_date=resolved_as_of_date,
        mode=mode,
        workflow_mode=workflow_mode,
        generated_at=generated_at,
        artifact_paths=artifact_paths,
        readiness=readiness,
        workflow_execution=workflow_execution,
        warnings=warnings,
        blocking_reasons=blocking,
    )
    boundary = build_current_day_boundary_check(paths=paths, as_of_date=as_of_date, warnings=warnings, blocking_reasons=blocking)
    _write_core(
        artifacts=artifacts,
        config=config.to_dict(),
        readiness=readiness,
        data_refresh_link=data_refresh_link,
        workflow_plan=workflow_plan,
        workflow_execution=workflow_execution,
        stage_manifest=stage_manifest,
        warning_summary=warning_summary,
        boundary=boundary,
    )
    artifact_index = build_current_day_artifact_index(paths=paths, as_of_date=as_of_date, resolved_as_of_date=resolved_as_of_date)
    write_json(artifacts["current_day_artifact_index"], artifact_index)
    source_trace = build_current_day_source_trace(
        paths=paths,
        as_of_date=as_of_date,
        resolved_as_of_date=resolved_as_of_date,
        generated_at=generated_at,
        workflow_command=workflow_plan["workflow_command"],
        data_refresh_link=data_refresh_link,
        artifact_index=artifact_index,
        warnings=warnings,
    )
    write_json(artifacts["current_day_source_trace"], source_trace)
    run_manifest = build_current_day_run_manifest(
        as_of_date=as_of_date,
        resolved_as_of_date=resolved_as_of_date,
        generated_at=generated_at,
        mode=mode,
        workflow_mode=workflow_mode,
        readiness=readiness,
        workflow_execution=workflow_execution,
        warning_summary=warning_summary,
        source_trace=source_trace,
        boundary=boundary,
        output_artifacts={key: relative(path, paths.project_root) for key, path in artifacts.items()},
        source_artifacts={row["artifact_id"]: row["path"] for row in artifact_index.get("artifacts", []) if row.get("created_by_current_day_run") is False},
    )
    current_day_summary = build_current_day_summary(
        as_of_date=as_of_date,
        resolved_as_of_date=resolved_as_of_date,
        mode=mode,
        workflow_mode=workflow_mode,
        readiness=readiness,
        workflow_execution=workflow_execution,
        stage_manifest=stage_manifest,
        artifact_index=artifact_index,
        warning_summary=warning_summary,
        boundary=boundary,
        run_manifest=run_manifest,
    )
    write_json(artifacts["current_day_run_manifest"], run_manifest)
    write_json(artifacts["current_day_summary"], current_day_summary)
    payload = {
        "runner_id": "A-SHARE-CURRENT-DAY-RESEARCH-RUNNER",
        "target_version": TARGET_VERSION,
        "current_day_run_config": config.to_dict(),
        "current_day_readiness": readiness,
        "current_day_data_refresh_link": data_refresh_link,
        "current_day_workflow_plan": workflow_plan,
        "current_day_workflow_execution": workflow_execution,
        "current_day_stage_manifest": stage_manifest,
        "current_day_artifact_index": artifact_index,
        "current_day_warning_summary": warning_summary,
        "current_day_source_trace": source_trace,
        "current_day_boundary_check": boundary,
        "current_day_run_manifest": run_manifest,
        "current_day_summary": current_day_summary,
        "artifacts": {key: relative(path, paths.project_root) for key, path in artifacts.items()},
    }
    reports = write_current_day_reports(current_day_output_dir(paths, as_of_date), payload)
    payload["reports"] = reports
    return json_safe(payload)


def _execute_workflow(
    *,
    paths: ProjectPaths,
    config: CurrentDayRunConfig,
    readiness: dict[str, Any],
    workflow_command: str,
) -> dict[str, Any]:
    if config.mode == AUDIT_EXISTING_CURRENT_DAY_RUN:
        return build_not_run_workflow_execution(
            paths=paths,
            as_of_date=config.as_of_date,
            resolved_as_of_date=config.resolved_as_of_date,
            mode=config.mode,
            workflow_mode=config.workflow_mode,
            command=workflow_command,
            warnings=list(readiness.get("warnings", [])),
        )
    if not readiness.get("overall_passed"):
        return build_blocked_workflow_execution(
            paths=paths,
            as_of_date=config.as_of_date,
            resolved_as_of_date=config.resolved_as_of_date,
            mode=config.mode,
            workflow_mode=config.workflow_mode,
            command=workflow_command,
            blocking_reasons=list(readiness.get("blocking_reasons", [])),
            warnings=list(readiness.get("warnings", [])),
        )
    if config.mode == VALIDATE_CURRENT_DAY_READINESS:
        return build_not_run_workflow_execution(
            paths=paths,
            as_of_date=config.as_of_date,
            resolved_as_of_date=config.resolved_as_of_date,
            mode=config.mode,
            workflow_mode=config.workflow_mode,
            command=workflow_command,
            warnings=list(readiness.get("warnings", [])),
        )
    started_at = utc_now()
    run_a_share_daily_research_workflow(
        as_of_date=config.resolved_as_of_date,
        mode=config.workflow_mode,
        paths=paths,
    )
    workflow_audit = audit_a_share_daily_research_workflow(
        as_of_date=config.resolved_as_of_date,
        mode=config.workflow_mode,
        paths=paths,
    )
    post_results = _run_post_workflow_modules(paths=paths, config=config) if config.run_post_workflow_modules and workflow_audit.get("overall_passed") else []
    finished_at = utc_now()
    return build_workflow_execution_record(
        paths=paths,
        as_of_date=config.as_of_date,
        resolved_as_of_date=config.resolved_as_of_date,
        mode=config.mode,
        workflow_mode=config.workflow_mode,
        command=workflow_command,
        started_at=started_at,
        finished_at=finished_at,
        exit_code=0 if workflow_audit.get("overall_passed") else 1,
        workflow_audit=workflow_audit,
        post_workflow_results=post_results,
    )


def _run_post_workflow_modules(*, paths: ProjectPaths, config: CurrentDayRunConfig) -> list[dict[str, Any]]:
    results = []
    benchmark_build = build_a_share_benchmark_comparison(as_of_date=config.resolved_as_of_date, paths=paths)
    benchmark_audit = audit_a_share_benchmark_comparison(as_of_date=config.resolved_as_of_date, paths=paths)
    results.append({"module": "benchmark", "builder_id": benchmark_build.get("builder_id"), "overall_passed": benchmark_audit.get("overall_passed"), "warnings": benchmark_audit.get("warnings", [])})
    performance_build = build_a_share_multi_day_performance(as_of_date=config.resolved_as_of_date, paths=paths)
    performance_audit = audit_a_share_multi_day_performance(as_of_date=config.resolved_as_of_date, paths=paths)
    results.append({"module": "performance", "builder_id": performance_build.get("builder_id"), "overall_passed": performance_audit.get("overall_passed"), "warnings": performance_audit.get("warnings", [])})
    attribution_build = build_a_share_performance_attribution(as_of_date=config.resolved_as_of_date, paths=paths)
    attribution_audit = audit_a_share_performance_attribution(as_of_date=config.resolved_as_of_date, paths=paths)
    results.append({"module": "attribution", "builder_id": attribution_build.get("builder_id"), "overall_passed": attribution_audit.get("overall_passed"), "warnings": attribution_audit.get("warnings", [])})
    return results


def _refresh_before_run(
    *,
    paths: ProjectPaths,
    as_of_date: str,
    allow_refresh_before_run: bool,
    allow_network_providers: bool,
    allow_public_providers: bool,
) -> None:
    if not allow_refresh_before_run:
        raise ValueError("refresh_then_run_research requires allow_refresh_before_run=true")
    refresh = build_a_share_daily_data_refresh(
        as_of_date=as_of_date,
        mode="validate_existing_data",
        allow_network_providers=allow_network_providers,
        allow_public_providers=allow_public_providers,
        paths=paths,
    )
    audit = audit_a_share_daily_data_refresh(as_of_date=refresh["as_of_date"], paths=paths)
    if not audit.get("overall_passed"):
        raise ValueError(f"data refresh audit failed: {audit.get('blocking_reasons', [])}")


def _resolve_run_date(paths: ProjectPaths, as_of_date: str, use_refresh_date: bool) -> str:
    if not use_refresh_date:
        return as_of_date
    refresh_artifacts = data_refresh_artifact_paths(paths, as_of_date)
    date_resolution = load_json(refresh_artifacts["date_resolution"])
    return str(date_resolution.get("resolved_as_of_date") or as_of_date)


def _blocking(*payloads: dict[str, Any]) -> list[str]:
    blocking: list[str] = []
    for payload in payloads:
        blocking.extend(str(item) for item in payload.get("blocking_reasons", []) if item)
    return sorted(set(blocking))


def _write_core(
    *,
    artifacts: dict[str, Any],
    config: dict[str, Any],
    readiness: dict[str, Any],
    data_refresh_link: dict[str, Any],
    workflow_plan: dict[str, Any],
    workflow_execution: dict[str, Any],
    stage_manifest: dict[str, Any],
    warning_summary: dict[str, Any],
    boundary: dict[str, Any],
) -> None:
    write_json(artifacts["current_day_run_config"], config)
    write_json(artifacts["current_day_readiness"], readiness)
    write_json(artifacts["current_day_data_refresh_link"], data_refresh_link)
    write_json(artifacts["current_day_workflow_plan"], workflow_plan)
    write_json(artifacts["current_day_workflow_execution"], workflow_execution)
    write_json(artifacts["current_day_stage_manifest"], stage_manifest)
    write_json(artifacts["current_day_warning_summary"], warning_summary)
    write_json(artifacts["current_day_boundary_check"], boundary)
