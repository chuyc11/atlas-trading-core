"""Data gap report builder."""

from __future__ import annotations

from typing import Any

from trading_core.equity_data_refresh.data_refresh_config import TARGET_VERSION


def build_data_gap_report(*, as_of_date: str, schema_validation: dict[str, Any], freshness_validation: dict[str, Any], coverage_summary: dict[str, Any], provider_health: dict[str, Any]) -> dict[str, Any]:
    missing_datasets = []
    missing_fields = []
    stale_datasets = []
    lagged_datasets = []
    provider_failures = []
    for row in schema_validation.get("datasets", []):
        if row.get("record_count", 0) == 0:
            missing_datasets.append(row["dataset_id"])
        for field in row.get("missing_required_fields", []):
            missing_fields.append({"dataset_id": row["dataset_id"], "field": field})
    for row in freshness_validation.get("datasets", []):
        if row.get("freshness_status") == "stale_blocking":
            stale_datasets.append(row["dataset_id"])
        elif row.get("freshness_status") in {"stale_warning", "lagged_allowed"}:
            lagged_datasets.append(row["dataset_id"])
    for row in provider_health.get("providers", []):
        if row.get("enabled") and row.get("current_attempt_status") == "disabled_or_unavailable":
            provider_failures.append({"provider_id": row["provider_id"], "error_message": row.get("error_message")})
    coverage_failures = [
        {"dataset_id": dataset_id, "threshold": row.get("threshold"), "coverage_vs_equity_master": row.get("coverage_vs_equity_master")}
        for dataset_id, row in coverage_summary.get("datasets", {}).items()
        if not row.get("threshold_passed")
    ]
    return {
        "gap_report_id": "A-SHARE-DATA-GAP-REPORT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "missing_datasets": missing_datasets,
        "missing_dates": [row["dataset_id"] for row in freshness_validation.get("datasets", []) if not row.get("as_of_date_available")],
        "missing_fields": missing_fields,
        "lagged_datasets": lagged_datasets,
        "stale_datasets": stale_datasets,
        "provider_failures": provider_failures,
        "coverage_failures": coverage_failures,
        "recommended_data_fixes": _fixes(missing_datasets, missing_fields, stale_datasets, coverage_failures),
    }


def _fixes(missing_datasets: list[str], missing_fields: list[dict[str, str]], stale_datasets: list[str], coverage_failures: list[dict[str, Any]]) -> list[str]:
    fixes = []
    if missing_datasets:
        fixes.append("restore missing local dataset panels before running current-day research workflow")
    if missing_fields:
        fixes.append("repair provider schema mapping or enable explicit schema fallback for noncritical fields")
    if stale_datasets:
        fixes.append("refresh stale critical panels from local or public research providers")
    if coverage_failures:
        fixes.append("improve provider coverage or fail closed for critical dataset gaps")
    return fixes
