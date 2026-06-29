"""Data freshness card."""

from __future__ import annotations

from typing import Any

from trading_core.equity_owner_dashboard.dashboard_config import TARGET_VERSION
from trading_core.equity_owner_dashboard.input_availability import load_json
from trading_core.equity_data_refresh.data_refresh_config import data_refresh_artifact_paths
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def build_data_freshness_card(*, paths: ProjectPaths | None, as_of_date: str, resolved_as_of_date: str) -> dict[str, Any]:
    paths = default_paths(paths)
    artifacts = data_refresh_artifact_paths(paths, resolved_as_of_date)
    audit = load_json(artifacts["data_refresh_audit_json"])
    summary = load_json(artifacts["data_refresh_summary"])
    freshness = load_json(artifacts["dataset_freshness_validation"])
    coverage = load_json(artifacts["dataset_coverage_summary"])
    gaps = load_json(artifacts["data_gap_report"])
    return {
        "card_id": "DATA_FRESHNESS",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "resolved_as_of_date": resolved_as_of_date,
        "data_refresh_audit_passed": audit.get("overall_passed") is True,
        "critical_datasets_passed": audit.get("validation_checks", {}).get("critical_datasets_available") is True,
        "schema_validation_passed": audit.get("validation_checks", {}).get("schema_validation_passed") is True,
        "freshness_validation_passed": audit.get("validation_checks", {}).get("freshness_validation_passed") is True,
        "coverage_validation_passed": audit.get("validation_checks", {}).get("coverage_validation_passed") is True,
        "dataset_status_table": summary.get("dataset_status", audit.get("dataset_checks", {})),
        "known_warnings": list(audit.get("warnings", [])),
        "data_gaps": gaps.get("gaps", summary.get("data_gaps", [])),
        "freshness_status": freshness.get("freshness_validation_status"),
        "coverage_status": coverage.get("coverage_validation_status"),
    }

