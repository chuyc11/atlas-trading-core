"""Manifest and summary builders for data refresh."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_data_refresh.data_refresh_config import RECOMMENDED_NEXT_VERSION, TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import relative


def build_data_refresh_manifest(*, paths: ProjectPaths, as_of_date: str, generated_at: str, mode: str, resolved_as_of_date: str, artifacts: dict[str, Path], dataset_refresh_result: dict[str, Any], provider_registry: dict[str, Any], schema_validation: dict[str, Any], freshness_validation: dict[str, Any], coverage_summary: dict[str, Any], boundary: dict[str, Any]) -> dict[str, Any]:
    return {
        "manifest_id": "A-SHARE-DAILY-DATA-REFRESH-MANIFEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "generated_at": generated_at,
        "mode": mode,
        "resolved_as_of_date": resolved_as_of_date,
        "datasets": {row["dataset_id"]: row for row in dataset_refresh_result.get("datasets", [])},
        "providers": {row["provider_id"]: row for row in provider_registry.get("providers", [])},
        "output_artifacts": {key: relative(path, paths.project_root) for key, path in artifacts.items()},
        "source_artifacts": {},
        "schema_validation_status": schema_validation.get("schema_validation_status"),
        "freshness_validation_status": freshness_validation.get("freshness_validation_status"),
        "coverage_validation_status": coverage_summary.get("coverage_validation_status"),
        "boundary": boundary,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def build_data_refresh_summary(*, as_of_date: str, mode: str, resolved_as_of_date: str, provider_registry: dict[str, Any], dataset_refresh_result: dict[str, Any], schema_validation: dict[str, Any], freshness_validation: dict[str, Any], coverage_summary: dict[str, Any], data_gap_report: dict[str, Any], fallback_report: dict[str, Any], boundary: dict[str, Any], warnings: list[str]) -> dict[str, Any]:
    return {
        "summary_id": "A-SHARE-DAILY-DATA-REFRESH-SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "mode": mode,
        "resolved_as_of_date": resolved_as_of_date,
        "provider_summary": {
            "registered": len(provider_registry.get("providers", [])),
            "enabled": [row["provider_id"] for row in provider_registry.get("providers", []) if row.get("enabled")],
        },
        "dataset_status": {row["dataset_id"]: row["status"] for row in dataset_refresh_result.get("datasets", [])},
        "schema_validation_status": schema_validation.get("schema_validation_status"),
        "freshness_validation_status": freshness_validation.get("freshness_validation_status"),
        "coverage_validation_status": coverage_summary.get("coverage_validation_status"),
        "data_gaps": {
            "missing_datasets": data_gap_report.get("missing_datasets", []),
            "stale_datasets": data_gap_report.get("stale_datasets", []),
            "lagged_datasets": data_gap_report.get("lagged_datasets", []),
        },
        "fallback_used": fallback_report.get("fallback_used"),
        "boundary": boundary,
        "warnings": warnings,
        "blocking_reasons": boundary.get("blocking_reasons", []),
        "disclaimer": "Data refresh success is research data readiness only and is not live trading readiness.",
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }
