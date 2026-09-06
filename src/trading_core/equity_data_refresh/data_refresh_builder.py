"""Build v0.8.0 A-share daily data refresh artifacts."""

from __future__ import annotations

from typing import Any

from trading_core.equity_data_quality.common import json_safe, utc_now, write_json
from trading_core.equity_data_refresh.coverage_summary import build_dataset_coverage_summary
from trading_core.equity_data_refresh.data_gap_report import build_data_gap_report
from trading_core.equity_data_refresh.data_refresh_boundary import build_data_refresh_boundary_check
from trading_core.equity_data_refresh.data_refresh_config import (
    DEFAULT_AS_OF_DATE,
    VALIDATE_EXISTING_DATA,
    DataRefreshConfig,
    data_refresh_artifact_paths,
    data_refresh_data_dir,
    data_refresh_output_dir,
    validate_data_refresh_config,
)
from trading_core.equity_data_refresh.data_refresh_manifest import build_data_refresh_manifest, build_data_refresh_summary
from trading_core.equity_data_refresh.data_refresh_report import write_data_refresh_reports
from trading_core.equity_data_refresh.data_refresh_source_trace import build_data_refresh_source_trace
from trading_core.equity_data_refresh.dataset_contracts import dataset_source_paths, resolve_column
from trading_core.equity_data_refresh.dataset_refresh_plan import build_dataset_refresh_plan
from trading_core.equity_data_refresh.dataset_refresh_result import build_dataset_refresh_result
from trading_core.equity_data_refresh.date_resolution import resolve_data_refresh_date
from trading_core.equity_data_refresh.freshness_validation import build_dataset_freshness_validation
from trading_core.equity_data_refresh.provider_execution import build_provider_execution_log
from trading_core.equity_data_refresh.provider_fallback_report import build_provider_fallback_report
from trading_core.equity_data_refresh.provider_health import build_provider_health_check
from trading_core.equity_data_refresh.provider_registry import build_provider_registry_snapshot, validate_provider_registry
from trading_core.equity_data_refresh.schema_validation import build_dataset_schema_validation
from trading_core.equity_data_refresh.validation_core import load_dataset_snapshots
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


def build_a_share_daily_data_refresh(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    mode: str = VALIDATE_EXISTING_DATA,
    resolve_latest_completed_trading_day: bool = False,
    allow_network_providers: bool = False,
    allow_public_providers: bool = False,
    allow_intraday_research_refresh: bool = False,
    allow_non_trading_day: bool = False,
    allow_partial_refresh: bool = False,
    allow_latest_available_if_exact_missing: bool = False,
    allow_research_workflow_after_refresh: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    config = DataRefreshConfig(
        as_of_date=as_of_date,
        requested_date_mode="latest_completed_trading_day" if resolve_latest_completed_trading_day else "explicit_as_of_date",
        mode=mode,
        resolve_latest_completed_trading_day=resolve_latest_completed_trading_day,
        allow_network_providers=allow_network_providers,
        allow_public_providers=allow_public_providers,
        allow_intraday_research_refresh=allow_intraday_research_refresh,
        allow_non_trading_day=allow_non_trading_day,
        allow_partial_refresh=allow_partial_refresh,
        allow_latest_available_if_exact_missing=allow_latest_available_if_exact_missing,
        allow_research_workflow_after_refresh=allow_research_workflow_after_refresh,
    )
    issues = validate_data_refresh_config(config)
    if issues:
        raise ValueError("; ".join(issues))
    date_resolution = resolve_data_refresh_date(
        paths=paths,
        as_of_date=as_of_date,
        resolve_latest_completed_trading_day=resolve_latest_completed_trading_day,
        allow_intraday_research_refresh=allow_intraday_research_refresh,
        allow_non_trading_day=allow_non_trading_day,
    )
    if not date_resolution["overall_passed"] and not allow_non_trading_day:
        raise ValueError("; ".join(date_resolution["blocking_reasons"]))
    resolved_as_of_date = date_resolution["resolved_as_of_date"]
    generated_at = utc_now()
    data_dir = data_refresh_data_dir(paths, resolved_as_of_date)
    output_dir = data_refresh_output_dir(paths, resolved_as_of_date)
    data_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    artifacts = data_refresh_artifact_paths(paths, resolved_as_of_date)

    registry = build_provider_registry_snapshot(allow_network_providers=allow_network_providers, allow_public_providers=allow_public_providers)
    registry_issues = validate_provider_registry(registry)
    provider_health = build_provider_health_check(paths=paths, registry=registry)
    provider_execution = build_provider_execution_log(mode=mode)
    snapshots = load_dataset_snapshots(paths)
    schema_validation = build_dataset_schema_validation(as_of_date=resolved_as_of_date, snapshots=snapshots)
    trading_dates = _trading_dates(snapshots)
    freshness_validation = build_dataset_freshness_validation(as_of_date=resolved_as_of_date, snapshots=snapshots, trading_dates=trading_dates)
    coverage_summary = build_dataset_coverage_summary(as_of_date=resolved_as_of_date, snapshots=snapshots)
    refresh_plan = build_dataset_refresh_plan(as_of_date=resolved_as_of_date, mode=mode)
    refresh_result = build_dataset_refresh_result(
        as_of_date=resolved_as_of_date,
        snapshots=snapshots,
        schema_validation=schema_validation,
        freshness_validation=freshness_validation,
        coverage_summary=coverage_summary,
    )
    fallback_report = build_provider_fallback_report(as_of_date=resolved_as_of_date, provider_execution_log=provider_execution)
    gap_report = build_data_gap_report(
        as_of_date=resolved_as_of_date,
        schema_validation=schema_validation,
        freshness_validation=freshness_validation,
        coverage_summary=coverage_summary,
        provider_health=provider_health,
    )
    warnings = _warnings(refresh_result, registry_issues)
    blocking = list(registry_issues)
    if schema_validation["schema_validation_status"] != "passed":
        blocking.append("schema_validation_failed")
    if freshness_validation["freshness_validation_status"] != "passed":
        blocking.append("freshness_validation_failed")
    if coverage_summary["coverage_validation_status"] != "passed":
        blocking.append("coverage_validation_failed")
    boundary = build_data_refresh_boundary_check(as_of_date=resolved_as_of_date, warnings=warnings, blocking_reasons=blocking)
    manifest = build_data_refresh_manifest(
        paths=paths,
        as_of_date=resolved_as_of_date,
        generated_at=generated_at,
        mode=mode,
        resolved_as_of_date=resolved_as_of_date,
        artifacts=artifacts,
        dataset_refresh_result=refresh_result,
        provider_registry=registry,
        schema_validation=schema_validation,
        freshness_validation=freshness_validation,
        coverage_summary=coverage_summary,
        boundary=boundary,
    )
    summary = build_data_refresh_summary(
        as_of_date=resolved_as_of_date,
        mode=mode,
        resolved_as_of_date=resolved_as_of_date,
        provider_registry=registry,
        dataset_refresh_result=refresh_result,
        schema_validation=schema_validation,
        freshness_validation=freshness_validation,
        coverage_summary=coverage_summary,
        data_gap_report=gap_report,
        fallback_report=fallback_report,
        boundary=boundary,
        warnings=warnings,
    )

    core_payloads = {
        "date_resolution": date_resolution,
        "provider_registry_snapshot": registry,
        "provider_health_check": provider_health,
        "provider_execution_log": provider_execution,
        "dataset_refresh_plan": refresh_plan,
        "dataset_refresh_result": refresh_result,
        "dataset_schema_validation": schema_validation,
        "dataset_freshness_validation": freshness_validation,
        "dataset_coverage_summary": coverage_summary,
        "data_gap_report": gap_report,
        "provider_fallback_report": fallback_report,
        "data_refresh_manifest": manifest,
        "data_refresh_boundary_check": boundary,
        "data_refresh_summary": summary,
    }
    write_json(artifacts["data_refresh_config"], config.to_dict())
    for key, payload in core_payloads.items():
        write_json(artifacts[key], payload)

    source_trace = build_data_refresh_source_trace(
        paths=paths,
        as_of_date=resolved_as_of_date,
        generated_at=generated_at,
        input_paths=dataset_source_paths(paths),
        output_artifacts=artifacts,
        provider_registry=registry,
        fallback_report=fallback_report,
        stale_decisions=[row for row in freshness_validation["datasets"] if row["freshness_status"] != "fresh"],
        schema_fallback_decisions=_schema_fallback_decisions(snapshots),
    )
    write_json(artifacts["data_refresh_source_trace"], source_trace)
    payload = {
        "builder_id": "A-SHARE-DAILY-DATA-REFRESH-BUILDER",
        "target_version": config.to_dict()["target_version"],
        "as_of_date": resolved_as_of_date,
        "generated_at": generated_at,
        "data_refresh_config": config.to_dict(),
        **core_payloads,
        "data_refresh_source_trace": source_trace,
        "artifacts": {key: relative(path, paths.project_root) for key, path in artifacts.items()},
    }
    reports = write_data_refresh_reports(output_dir, payload)
    source_trace = build_data_refresh_source_trace(
        paths=paths,
        as_of_date=resolved_as_of_date,
        generated_at=generated_at,
        input_paths=dataset_source_paths(paths),
        output_artifacts=artifacts,
        provider_registry=registry,
        fallback_report=fallback_report,
        stale_decisions=[row for row in freshness_validation["datasets"] if row["freshness_status"] != "fresh"],
        schema_fallback_decisions=_schema_fallback_decisions(snapshots),
    )
    write_json(artifacts["data_refresh_source_trace"], source_trace)
    payload["data_refresh_source_trace"] = source_trace
    payload["reports"] = reports
    return json_safe(payload)


def _trading_dates(snapshots: dict[str, Any]) -> list[str]:
    snapshot = snapshots["trading_calendar"]
    column = resolve_column(snapshot.frame, snapshot.contract, "trade_date")
    if column is None:
        return []
    return sorted(set(snapshot.frame[column].astype(str).str[:10]))


def _schema_fallback_decisions(snapshots: dict[str, Any]) -> list[dict[str, str]]:
    decisions = []
    for dataset_id, snapshot in snapshots.items():
        for canonical, _aliases in snapshot.contract.aliases.items():
            resolved = resolve_column(snapshot.frame, snapshot.contract, canonical)
            if resolved is not None and resolved != canonical:
                decisions.append({"dataset_id": dataset_id, "canonical_field": canonical, "resolved_field": resolved, "fallback_type": "schema_alias"})
    return decisions


def _warnings(refresh_result: dict[str, Any], registry_issues: list[str]) -> list[str]:
    warnings: list[str] = []
    for row in refresh_result.get("datasets", []):
        warnings.extend(f"{row['dataset_id']}:{item}" for item in row.get("warnings", []))
    warnings.extend(registry_issues)
    return sorted(set(warnings))
