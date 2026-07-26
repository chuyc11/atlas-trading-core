"""Builder for v0.8.12 owner daily pack history and readiness trends."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from trading_core.equity_data_quality.common import write_json
from trading_core.equity_owner_daily_pack_history.boundary_trends import build_boundary_trend_baseline
from trading_core.equity_owner_daily_pack_history.completeness_trends import build_completeness_trend
from trading_core.equity_owner_daily_pack_history.daily_pack_history_boundary import build_boundary_check
from trading_core.equity_owner_daily_pack_history.daily_pack_history_config import (
    ALLOWED_MODES,
    AUDIT_EXISTING,
    BUILD_TRENDS,
    DEFAULT_AS_OF_DATE,
    DEFAULT_BASELINE_WINDOW_OBSERVATIONS,
    DEFAULT_HISTORY_WINDOW_DAYS,
    DEFAULT_MINIMUM_REQUIRED_OBSERVATIONS,
    FILES,
    INDEX_FILES,
    REPORTS,
    DailyPackHistoryConfig,
    artifact_paths,
    data_dir,
    output_dir,
    validate_config,
)
from trading_core.equity_owner_daily_pack_history.daily_pack_history_manifest import build_manifest, build_summary
from trading_core.equity_owner_daily_pack_history.daily_pack_history_report import write_reports
from trading_core.equity_owner_daily_pack_history.daily_pack_history_source_trace import build_source_trace
from trading_core.equity_owner_daily_pack_history.date_alignment import build_date_alignment
from trading_core.equity_owner_daily_pack_history.history_append import append_daily_pack_history
from trading_core.equity_owner_daily_pack_history.history_snapshot import build_history_snapshot
from trading_core.equity_owner_daily_pack_history.input_availability import build_input_availability, input_paths, load_json
from trading_core.equity_owner_daily_pack_history.owner_next_step_trends import build_owner_next_step_trend
from trading_core.equity_owner_daily_pack_history.protected_path_trends import build_protected_path_trend_baseline
from trading_core.equity_owner_daily_pack_history.quality_baseline import build_quality_baseline
from trading_core.equity_owner_daily_pack_history.readiness_history import build_owner_readiness_history
from trading_core.equity_owner_daily_pack_history.readiness_score import build_owner_readiness_score
from trading_core.equity_owner_daily_pack_history.run_record import build_daily_pack_run_record
from trading_core.equity_owner_daily_pack_history.safe_action_trends import build_safe_action_trend_baseline
from trading_core.equity_owner_daily_pack_history.source_resolution import build_source_resolution
from trading_core.equity_owner_daily_pack_history.source_trace_quality import build_source_trace_quality_trend
from trading_core.equity_owner_daily_pack_history.trend_sufficiency import build_trend_sufficiency
from trading_core.equity_owner_daily_pack_history.warning_issue_trends import build_warning_issue_trend_baseline
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def validate_a_share_owner_daily_pack_history_inputs(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    availability = build_input_availability(paths=paths, as_of_date=as_of_date)
    return {
        "builder_id": "A-SHARE-OWNER-DAILY-PACK-HISTORY-INPUT-VALIDATOR",
        "overall_passed": availability["overall_passed"],
        "blocking_reasons": availability["blocking_reasons"],
        "warnings": len(availability["warnings"]),
        "owner_daily_pack_audit_passed": availability["owner_daily_pack_audit_passed"],
        "source_workflow_mode": availability["source_workflow_mode"],
        "not_investment_decision_pack": availability["not_investment_decision_pack"],
        "boundary_clean": availability["boundary_clean"],
    }


def build_a_share_owner_daily_pack_history(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    mode: str = BUILD_TRENDS,
    history_window_days: int = DEFAULT_HISTORY_WINDOW_DAYS,
    minimum_required_observations: int = DEFAULT_MINIMUM_REQUIRED_OBSERVATIONS,
    baseline_window_observations: int = DEFAULT_BASELINE_WINDOW_OBSERVATIONS,
    allow_date_mismatch: bool = False,
    allow_rebuild_history: bool = False,
    allow_synthetic_history: bool = False,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = default_paths(paths)
    if mode == AUDIT_EXISTING:
        from trading_core.equity_owner_daily_pack_history.daily_pack_history_audit import audit_a_share_owner_daily_pack_history

        return audit_a_share_owner_daily_pack_history(as_of_date=as_of_date, paths=paths)
    config = DailyPackHistoryConfig(
        as_of_date=as_of_date,
        mode=mode,
        history_window_days=history_window_days,
        minimum_required_observations=minimum_required_observations,
        baseline_window_observations=baseline_window_observations,
        allow_date_mismatch=allow_date_mismatch,
        allow_rebuild_history=allow_rebuild_history,
        allow_synthetic_history=allow_synthetic_history,
    )
    issues = validate_config(config)
    if issues:
        raise ValueError("; ".join(issues))
    if mode not in ALLOWED_MODES:
        raise ValueError(f"mode must be one of {ALLOWED_MODES}")

    artifacts = artifact_paths(paths, as_of_date)
    data_dir(paths, as_of_date).mkdir(parents=True, exist_ok=True)
    availability = build_input_availability(paths=paths, as_of_date=as_of_date)
    resolution = build_source_resolution(paths=paths, as_of_date=as_of_date, input_availability=availability)
    alignment = build_date_alignment(as_of_date=as_of_date, input_availability=availability, allow_date_mismatch=allow_date_mismatch)
    payloads: dict[str, Any] = {
        "daily_pack_history_config": config.to_dict(),
        "daily_pack_history_input_availability": availability,
        "daily_pack_history_source_resolution": resolution,
        "daily_pack_history_date_alignment": alignment,
    }
    _write_payloads(artifacts, payloads)
    if mode == "validate_daily_pack_history_inputs":
        return _validation_result(availability, resolution, alignment)

    sources = input_paths(paths, as_of_date)
    source_payloads = {key: load_json(path) for key, path in sources.items()}
    score = build_owner_readiness_score(
        as_of_date=as_of_date,
        payloads={
            **source_payloads,
            "input_availability": availability,
        },
    )
    run_record = build_daily_pack_run_record(
        paths=paths,
        as_of_date=as_of_date,
        input_paths=sources,
        payloads=source_payloads,
        readiness_score=score,
    )
    score["daily_pack_manifest_sha256"] = run_record["daily_pack_manifest_sha256"]
    history_index, append_result = append_daily_pack_history(
        history_path=artifacts["daily_pack_history_index"],
        run_record=run_record,
        allow_rebuild_history=allow_rebuild_history,
    )
    records = list(history_index.get("records", []))
    snapshot = build_history_snapshot(
        as_of_date=as_of_date,
        history_index=history_index,
        minimum_required_observations=minimum_required_observations,
    )
    readiness_history = build_owner_readiness_history(as_of_date=as_of_date, records=records)
    sufficiency = build_trend_sufficiency(
        as_of_date=as_of_date,
        observation_count=snapshot["daily_pack_history_observation_count"],
        minimum_required_observations=minimum_required_observations,
        baseline_window_observations=baseline_window_observations,
    )
    generated_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    early_payloads = {
        **payloads,
        "daily_pack_run_record": run_record,
        "daily_pack_history_append_result": append_result,
        "daily_pack_history_snapshot": snapshot,
        "owner_readiness_score": score,
        "owner_readiness_history": readiness_history,
        "owner_readiness_trend_sufficiency": sufficiency,
    }
    _write_payloads(artifacts, early_payloads)
    output_artifacts = {key: artifacts[key] for key in FILES}
    index_artifacts = {key: artifacts[key] for key in INDEX_FILES}
    report_artifacts = {key: artifacts[key] for key in REPORTS}
    trace = build_source_trace(
        paths=paths,
        as_of_date=as_of_date,
        generated_at=generated_at,
        source_paths=sources,
        output_paths={**output_artifacts, **index_artifacts, **report_artifacts},
        command_policy_decisions={
            "mode": mode,
            "append_only_history": True,
            "allow_rebuild_history": allow_rebuild_history,
            "allow_synthetic_history": allow_synthetic_history,
            "commands_executed": [],
        },
    )
    boundary = build_boundary_check(
        paths=paths,
        as_of_date=as_of_date,
        blocking_reasons=availability.get("blocking_reasons", []) + resolution.get("blocking_reasons", []) + alignment.get("blocking_reasons", []),
        warnings=availability.get("warnings", []) + append_result.get("warnings", []) + alignment.get("warnings", []),
        synthetic_history_used=False,
        future_dates_used=False,
    )
    trends = {
        "daily_pack_quality_baseline": build_quality_baseline(
            as_of_date=as_of_date,
            artifacts=artifacts,
            records=records,
            sufficiency=sufficiency,
            source_trace=trace,
            boundary=boundary,
            summary=source_payloads["daily_pack_summary"],
        ),
        "warning_issue_trend_baseline": build_warning_issue_trend_baseline(
            as_of_date=as_of_date,
            records=records,
            warning_digest=source_payloads["warning_issue_digest"],
            sufficiency=sufficiency,
        ),
        "safe_action_trend_baseline": build_safe_action_trend_baseline(
            as_of_date=as_of_date,
            records=records,
            safe_action_digest=source_payloads["safe_action_digest"],
            sufficiency=sufficiency,
        ),
        "protected_path_trend_baseline": build_protected_path_trend_baseline(
            as_of_date=as_of_date,
            records=records,
            protected_digest=source_payloads["protected_path_digest"],
        ),
        "boundary_trend_baseline": build_boundary_trend_baseline(
            as_of_date=as_of_date,
            records=records,
            boundary_check=boundary,
        ),
        "source_trace_quality_trend": build_source_trace_quality_trend(as_of_date=as_of_date, records=records, source_trace=trace),
        "daily_pack_completeness_trend": build_completeness_trend(as_of_date=as_of_date, artifacts=artifacts, records=records),
        "owner_next_step_trend": build_owner_next_step_trend(as_of_date=as_of_date, records=records, checklist=source_payloads["owner_next_step_checklist"]),
        "daily_pack_history_source_trace": trace,
        "daily_pack_history_boundary_check": boundary,
    }
    _write_indexes(artifacts, records, readiness_history, trends)
    manifest = build_manifest(
        paths=paths,
        as_of_date=as_of_date,
        mode=mode,
        generated_at=generated_at,
        output_artifacts={**output_artifacts, **index_artifacts, **report_artifacts},
        source_artifacts=sources,
        append_result=append_result,
        snapshot=snapshot,
        score=score,
        sufficiency=sufficiency,
        boundary=boundary,
        source_trace=trace,
    )
    summary = build_summary(
        as_of_date=as_of_date,
        mode=mode,
        availability=availability,
        append_result=append_result,
        snapshot=snapshot,
        score=score,
        sufficiency=sufficiency,
        boundary=boundary,
    )
    payloads = {
        **early_payloads,
        **trends,
        "daily_pack_history_manifest": manifest,
        "daily_pack_history_summary": summary,
    }
    _write_payloads(artifacts, payloads)
    write_reports(output_dir(paths, as_of_date), payloads)
    return {
        "builder_id": "A-SHARE-OWNER-DAILY-PACK-HISTORY-BUILDER",
        "overall_passed": summary["overall_passed"],
        "blocking_reasons": summary["blocking_reasons"],
        "warnings": len(summary["warnings"]),
        "source_workflow_mode": summary["source_workflow_mode"],
        "daily_pack_history_observation_count": summary["daily_pack_history_observation_count"],
        "minimum_required_observations": summary["minimum_required_observations"],
        "trend_analysis_available": summary["trend_analysis_available"],
        "readiness_trend_status": summary["readiness_trend_status"],
        "owner_readiness_score": summary["owner_readiness_score"],
        "owner_readiness_grade": summary["owner_readiness_grade"],
        "append_only_history": summary["append_only_history"],
        "idempotent_append": summary["idempotent_append"],
        "duplicate_detected": summary["duplicate_detected"],
        "same_date_changed_content_warning": summary["same_date_changed_content_warning"],
        "synthetic_history_used": summary["synthetic_history_used"],
        "future_dates_used": summary["future_dates_used"],
        "recommended_next_version": summary["recommended_next_version"],
        "daily_pack_history_report": str(artifacts["daily_pack_history_report"]),
    }


def _validation_result(availability: dict, resolution: dict, alignment: dict) -> dict[str, Any]:
    blocking = availability.get("blocking_reasons", []) + resolution.get("blocking_reasons", []) + alignment.get("blocking_reasons", [])
    return {
        "builder_id": "A-SHARE-OWNER-DAILY-PACK-HISTORY-BUILDER",
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": len(availability.get("warnings", []) + resolution.get("warnings", []) + alignment.get("warnings", [])),
        "source_workflow_mode": "build_from_existing_data",
        "owner_daily_pack_audit_passed": availability.get("owner_daily_pack_audit_passed", False),
    }


def _write_payloads(artifacts: dict, payloads: dict[str, Any]) -> None:
    for key, payload in payloads.items():
        path = artifacts.get(key)
        if path:
            write_json(path, payload)


def _write_indexes(artifacts: dict, records: list[dict[str, Any]], readiness_history: dict, trends: dict[str, Any]) -> None:
    indexes = {
        "owner_readiness_history_index": {**readiness_history, "index_id": "A-SHARE-OWNER-READINESS-HISTORY-INDEX"},
        "daily_pack_quality_history_index": {
            "index_id": "A-SHARE-DAILY-PACK-QUALITY-HISTORY-INDEX",
            "target_version": trends["daily_pack_quality_baseline"]["target_version"],
            "records": [{"as_of_date": row.get("as_of_date"), "boundary_clean": row.get("boundary_clean")} for row in records],
        },
        "warning_issue_history_index": {
            "index_id": "A-SHARE-WARNING-ISSUE-HISTORY-INDEX",
            "target_version": trends["warning_issue_trend_baseline"]["target_version"],
            "records": [{"as_of_date": row.get("as_of_date"), "warning_count": row.get("warning_count"), "blocking_count": row.get("blocking_count")} for row in records],
        },
        "safe_action_history_index": {
            "index_id": "A-SHARE-SAFE-ACTION-HISTORY-INDEX",
            "target_version": trends["safe_action_trend_baseline"]["target_version"],
            "records": [{"as_of_date": row.get("as_of_date"), "safe_action_count": row.get("safe_action_count"), "automatic_action_count": row.get("automatic_action_count")} for row in records],
        },
        "protected_path_history_index": {
            "index_id": "A-SHARE-PROTECTED-PATH-HISTORY-INDEX",
            "target_version": trends["protected_path_trend_baseline"]["target_version"],
            "records": [{"as_of_date": row.get("as_of_date"), "protected_path_modifications_detected": row.get("protected_path_modifications_detected")} for row in records],
        },
        "boundary_history_index": {
            "index_id": "A-SHARE-BOUNDARY-HISTORY-INDEX",
            "target_version": trends["boundary_trend_baseline"]["target_version"],
            "records": [{"as_of_date": row.get("as_of_date"), "boundary_clean": row.get("boundary_clean")} for row in records],
        },
        "source_trace_quality_history_index": {
            "index_id": "A-SHARE-SOURCE-TRACE-QUALITY-HISTORY-INDEX",
            "target_version": trends["source_trace_quality_trend"]["target_version"],
            "records": [{"as_of_date": row.get("as_of_date"), "daily_pack_manifest_sha256": row.get("daily_pack_manifest_sha256")} for row in records],
        },
    }
    for key, payload in indexes.items():
        write_json(artifacts[key], payload)
