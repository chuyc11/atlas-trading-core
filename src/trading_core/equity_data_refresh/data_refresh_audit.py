"""Audit v0.8.0 A-share daily data refresh artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import sha256_file, write_json, write_report
from trading_core.equity_data_refresh.data_refresh_config import (
    CRITICAL_DATASETS,
    DATASET_IDS,
    DEFAULT_AS_OF_DATE,
    FORBIDDEN_POSITIVE_WORDING,
    RECOMMENDED_NEXT_VERSION,
    REFRESH_BOUNDARY,
    REMEDIATION_VERSION,
    REQUIRED_INDEX_IDS,
    TARGET_VERSION,
    data_refresh_artifact_paths,
)
from trading_core.equity_data_refresh.data_refresh_report import render_audit
from trading_core.equity_data_refresh.data_refresh_source_trace import forbidden_source_path_hits, update_trace_with_audit_artifacts
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


REQUIRED_ARTIFACTS = [
    "data_refresh_config",
    "date_resolution",
    "provider_registry_snapshot",
    "provider_health_check",
    "provider_execution_log",
    "dataset_refresh_plan",
    "dataset_refresh_result",
    "dataset_schema_validation",
    "dataset_freshness_validation",
    "dataset_coverage_summary",
    "data_gap_report",
    "provider_fallback_report",
    "data_refresh_source_trace",
    "data_refresh_manifest",
    "data_refresh_boundary_check",
    "data_refresh_summary",
]


def audit_a_share_daily_data_refresh(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    artifacts = data_refresh_artifact_paths(paths, as_of_date)
    payloads = {key: _load_dict(artifacts[key]) for key in REQUIRED_ARTIFACTS}
    checks = _checks(paths=paths, artifacts=artifacts, payloads=payloads, as_of_date=as_of_date)
    blocking = [f"{name}=false" for name, passed in checks.items() if not passed]
    dataset_status = {row["dataset_id"]: row["status"] for row in payloads["dataset_refresh_result"].get("datasets", [])}
    execution = payloads["provider_execution_log"]
    boundary = payloads["data_refresh_boundary_check"]
    audit = {
        "audit_id": "A-SHARE-DAILY-DATA-REFRESH-AUDIT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "mode": payloads["data_refresh_config"].get("mode"),
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": _warnings(payloads),
        "dataset_checks": {dataset_id: dataset_status.get(dataset_id, "missing") for dataset_id in DATASET_IDS},
        "provider_checks": {
            "providers_registered": bool(payloads["provider_registry_snapshot"].get("providers")),
            "provider_health_checked": bool(payloads["provider_health_check"].get("providers")),
            "fallbacks_recorded": "fallbacks" in payloads["provider_fallback_report"],
            "broker_provider_used": bool(execution.get("broker_provider_used")),
            "real_account_provider_used": bool(execution.get("real_account_provider_used")),
            "order_provider_used": bool(execution.get("order_provider_used")),
        },
        "validation_checks": {
            "schema_validation_passed": payloads["dataset_schema_validation"].get("schema_validation_status") == "passed",
            "freshness_validation_passed": payloads["dataset_freshness_validation"].get("freshness_validation_status") == "passed",
            "coverage_validation_passed": payloads["dataset_coverage_summary"].get("coverage_validation_status") == "passed",
            "critical_datasets_available": all(dataset_status.get(dataset_id) in {"passed", "warning"} for dataset_id in CRITICAL_DATASETS),
        },
        "checks": checks,
        "boundary": {key: boundary.get(key) for key in REFRESH_BOUNDARY},
        "recommended_next_version": RECOMMENDED_NEXT_VERSION if not blocking else REMEDIATION_VERSION,
    }
    result = write_report(artifacts["data_refresh_audit_json"], audit, artifacts["data_refresh_audit_report"], render_audit(audit))
    trace = payloads.get("data_refresh_source_trace", {})
    if trace:
        updated = update_trace_with_audit_artifacts(
            paths=paths,
            trace=trace,
            audit_json=artifacts["data_refresh_audit_json"],
            audit_report=artifacts["data_refresh_audit_report"],
        )
        write_json(artifacts["data_refresh_source_trace"], updated)
    return result


def _checks(*, paths: ProjectPaths, artifacts: dict[str, Path], payloads: dict[str, Any], as_of_date: str) -> dict[str, bool]:
    result = payloads["dataset_refresh_result"]
    schema = payloads["dataset_schema_validation"]
    freshness = payloads["dataset_freshness_validation"]
    coverage = payloads["dataset_coverage_summary"]
    source_trace = payloads["data_refresh_source_trace"]
    manifest = payloads["data_refresh_manifest"]
    boundary = payloads["data_refresh_boundary_check"]
    registry = payloads["provider_registry_snapshot"]
    execution = payloads["provider_execution_log"]
    dataset_status = {row["dataset_id"]: row for row in result.get("datasets", [])}
    index_ids = set(coverage.get("index_price_ids", []))
    checks = {
        "all_required_artifacts_exist": all(artifacts[key].exists() for key in REQUIRED_ARTIFACTS),
        "target_version_matches": all(payload.get("target_version") == TARGET_VERSION for payload in payloads.values()),
        "all_required_datasets_present": set(dataset_status) == set(DATASET_IDS),
        "critical_datasets_passed": all(dataset_status.get(dataset_id, {}).get("status") in {"passed", "warning"} for dataset_id in CRITICAL_DATASETS),
        "schema_validation_passed": schema.get("schema_validation_status") == "passed",
        "freshness_validation_passed": freshness.get("freshness_validation_status") == "passed",
        "coverage_validation_passed": coverage.get("coverage_validation_status") == "passed",
        "trading_calendar_covers_as_of_date": dataset_status.get("trading_calendar", {}).get("as_of_date_available") is True,
        "daily_price_fresh_enough": dataset_status.get("daily_price", {}).get("freshness_status") == "fresh",
        "adjusted_price_fresh_enough": dataset_status.get("adjusted_price", {}).get("freshness_status") in {"fresh", "lagged_allowed", "stale_warning"},
        "index_price_contains_required_ids": set(REQUIRED_INDEX_IDS).issubset(index_ids),
        "no_forbidden_provider_used": not execution.get("broker_provider_used") and not execution.get("real_account_provider_used") and not execution.get("order_provider_used"),
        "provider_fallback_recorded": "fallbacks" in payloads["provider_fallback_report"],
        "registry_rejects_broker_provider": not registry.get("broker_provider") and not registry.get("account_provider") and not registry.get("order_provider"),
        "source_trace_complete": source_trace.get("source_trace_complete") is True,
        "source_trace_no_forbidden_paths": not forbidden_source_path_hits(source_trace.get("source_artifacts", [])),
        "source_trace_hashes_match": _source_hashes_match(paths, source_trace),
        "boundary_fields_clean": all(boundary.get(key) is expected for key, expected in REFRESH_BOUNDARY.items()),
        "boundary_overall_passed": boundary.get("overall_passed") is True,
        "no_forbidden_artifacts_generated": not boundary.get("forbidden_artifacts_present"),
        "no_forbidden_positive_wording": not _forbidden_wording_hits(artifacts),
        "manifest_generated": manifest.get("manifest_id") == "A-SHARE-DAILY-DATA-REFRESH-MANIFEST",
    }
    return checks


def _source_hashes_match(paths: ProjectPaths, source_trace: dict[str, Any]) -> bool:
    for group in ["source_artifacts", "output_artifacts"]:
        records = source_trace.get(group, {})
        iterable = records.values() if isinstance(records, dict) else records
        for row in iterable:
            path = Path(row.get("path", ""))
            if not path.is_absolute():
                path = paths.project_root / path
            if path.exists() and row.get("sha256") and sha256_file(path) != row.get("sha256"):
                return False
    return True


def _forbidden_wording_hits(artifacts: dict[str, Path]) -> list[str]:
    hits = []
    for path in artifacts.values():
        if path.exists() and path.is_file():
            text = path.read_text(encoding="utf-8", errors="ignore")
            for phrase in FORBIDDEN_POSITIVE_WORDING:
                if phrase in text:
                    hits.append(f"{path}:{phrase}")
    return hits


def _warnings(payloads: dict[str, Any]) -> list[str]:
    warnings = []
    for row in payloads["dataset_refresh_result"].get("datasets", []):
        warnings.extend(f"{row['dataset_id']}:{item}" for item in row.get("warnings", []))
    return sorted(set(warnings))


def _load_dict(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))
