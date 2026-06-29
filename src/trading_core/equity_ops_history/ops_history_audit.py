"""Fail-close audit for v0.8.6 ops history baselines."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import sha256_file, write_report
from trading_core.equity_ops_history.input_availability import load_json
from trading_core.equity_ops_history.ops_history_config import (
    DEFAULT_AS_OF_DATE,
    OPS_HISTORY_BOUNDARY,
    OPS_HISTORY_FILES,
    OPS_HISTORY_INDEX_FILES,
    OPS_HISTORY_REPORTS,
    RECOMMENDED_NEXT_VERSION,
    REMEDIATION_VERSION,
    TARGET_VERSION,
    ops_history_artifact_paths,
)
from trading_core.equity_ops_history.ops_history_report import render_audit
from trading_core.equity_ops_history.ops_history_source_trace import forbidden_source_path_hits
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


REQUIRED_ARTIFACTS = list(OPS_HISTORY_FILES) + list(OPS_HISTORY_INDEX_FILES) + list(OPS_HISTORY_REPORTS)


def audit_a_share_ops_history_baseline(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    artifacts = ops_history_artifact_paths(paths, as_of_date)
    payloads = {key: load_json(path) for key, path in artifacts.items() if key in OPS_HISTORY_FILES or key in OPS_HISTORY_INDEX_FILES}
    checks = _checks(paths=paths, artifacts=artifacts, payloads=payloads)
    blocking = [f"{key}=false" for key, passed in checks.items() if not passed]
    sufficiency = payloads.get("ops_trend_sufficiency", {})
    append = payloads.get("ops_history_append_result", {})
    boundary = payloads.get("ops_history_boundary_check", {})
    audit = {
        "audit_id": "A-SHARE-OPS-HISTORY-BASELINE-AUDIT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "mode": payloads.get("ops_history_config", {}).get("mode"),
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": sorted(set(payloads.get("ops_history_input_availability", {}).get("warnings", []) + boundary.get("warnings", []))),
        "trend_sufficiency": {
            "run_history_observation_count": sufficiency.get("run_history_observation_count", sufficiency.get("history_observation_count")),
            "minimum_required_observations": sufficiency.get("minimum_required_observations"),
            "trend_analysis_available": sufficiency.get("trend_analysis_available"),
            "baseline_status": sufficiency.get("baseline_status"),
            "synthetic_history_used": sufficiency.get("synthetic_history_used"),
            "future_dates_used": sufficiency.get("future_dates_used"),
        },
        "append_result": {
            "append_completed": append.get("append_completed"),
            "idempotent_append": append.get("idempotent_append"),
            "duplicate_detected": append.get("duplicate_detected"),
            "same_date_changed_content_warning": append.get("same_date_changed_content_warning"),
            "records_before": append.get("records_before"),
            "records_after": append.get("records_after"),
        },
        "boundary": {key: boundary.get(key) for key in OPS_HISTORY_BOUNDARY},
        "checks": checks,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION if not blocking else REMEDIATION_VERSION,
    }
    return write_report(artifacts["ops_history_audit_json"], audit, artifacts["ops_history_audit_report"], render_audit(audit))


def _checks(*, paths: ProjectPaths, artifacts: dict[str, Path], payloads: dict[str, Any]) -> dict[str, bool]:
    availability = payloads.get("ops_history_input_availability", {})
    append = payloads.get("ops_history_append_result", {})
    snapshot = payloads.get("ops_history_snapshot", {})
    sufficiency = payloads.get("ops_trend_sufficiency", {})
    health = payloads.get("ops_health_score_baseline", {})
    module = payloads.get("ops_module_reliability_baseline", {})
    action = payloads.get("ops_action_recurrence_baseline", {})
    source_trace = payloads.get("ops_history_source_trace", {})
    boundary = payloads.get("ops_history_boundary_check", {})
    manifest = payloads.get("ops_history_manifest", {})
    return {
        "all_required_artifacts_exist": all(artifacts[key].exists() for key in REQUIRED_ARTIFACTS),
        "target_version_matches": all(payload.get("target_version") == TARGET_VERSION for payload in payloads.values() if payload),
        "ops_center_audit_passed": availability.get("input_audit_checks", {}).get("ops_center_audit_passed") is True,
        "input_availability_passed": availability.get("overall_passed") is True,
        "append_only_history": append.get("append_completed") is True and manifest.get("append_only_history") is True,
        "run_history_observation_count_matches": snapshot.get("run_history_observation_count") == len(payloads.get("ops_run_history_index", {}).get("records", [])),
        "trend_sufficiency_consistent": _trend_sufficiency_consistent(sufficiency),
        "no_synthetic_or_future_history": sufficiency.get("synthetic_history_used") is False and sufficiency.get("future_dates_used") is False,
        "health_baseline_consistent": _health_baseline_consistent(health, sufficiency),
        "module_reliability_insufficient_rates_null": _module_rates_consistent(module, sufficiency),
        "safe_actions_not_trade_related": all(
            item.get("automatic_action_allowed") is False and item.get("trade_related") is False and item.get("broker_related") is False and item.get("order_related") is False
            for item in action.get("items", [])
        ),
        "commands_executed_empty": boundary.get("commands_executed") == [] and manifest.get("commands_executed") == [],
        "source_trace_complete": source_trace.get("source_trace_complete") is True,
        "source_trace_no_forbidden_paths": not forbidden_source_path_hits(source_trace.get("source_artifacts", []) + source_trace.get("output_artifacts", [])),
        "source_trace_hashes_match": _source_hashes_match(paths, source_trace),
        "boundary_clean": boundary.get("overall_passed") is True,
        "boundary_fields_clean": _boundary_fields_clean(boundary),
        "no_forbidden_artifacts_generated": not boundary.get("forbidden_artifacts_present"),
        "no_forbidden_positive_wording": not boundary.get("forbidden_wording_positive_hits"),
        "manifest_generated": manifest.get("manifest_id") == "A-SHARE-OPS-HISTORY-BASELINE-MANIFEST",
        "summary_generated": payloads.get("ops_history_summary", {}).get("summary_id") == "A-SHARE-OPS-HISTORY-BASELINE-SUMMARY",
    }


def _trend_sufficiency_consistent(sufficiency: dict[str, Any]) -> bool:
    count = sufficiency.get("run_history_observation_count", sufficiency.get("history_observation_count"))
    minimum = sufficiency.get("minimum_required_observations")
    if not isinstance(count, int) or not isinstance(minimum, int):
        return False
    enough = count >= minimum
    return sufficiency.get("trend_analysis_available") is enough and sufficiency.get("baseline_status") == ("available" if enough else "insufficient_history")


def _health_baseline_consistent(health: dict[str, Any], sufficiency: dict[str, Any]) -> bool:
    enough = sufficiency.get("trend_analysis_available") is True
    if enough:
        return isinstance(health.get("average_score"), (int, float))
    return health.get("baseline_status") == "insufficient_history" and health.get("average_score") is None


def _module_rates_consistent(module: dict[str, Any], sufficiency: dict[str, Any]) -> bool:
    if sufficiency.get("trend_analysis_available") is True:
        return all(row.get("reliability_rate") is not None for row in module.get("modules", []))
    return all(row.get("reliability_rate") is None and row.get("trend_status") == "insufficient_history" for row in module.get("modules", []))


def _boundary_fields_clean(boundary: dict[str, Any]) -> bool:
    for key, expected in OPS_HISTORY_BOUNDARY.items():
        value = boundary.get(key)
        if isinstance(expected, list):
            if value != expected:
                return False
        elif value is not expected:
            return False
    return True


def _source_hashes_match(paths: ProjectPaths, trace: dict[str, Any]) -> bool:
    for row in trace.get("source_artifacts", []):
        path = Path(row.get("path", ""))
        if not path.is_absolute():
            path = paths.project_root / path
        if path.exists() and row.get("sha256") and sha256_file(path) != row.get("sha256"):
            return False
    return True
