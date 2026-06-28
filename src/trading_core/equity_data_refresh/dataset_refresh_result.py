"""Dataset refresh result builder."""

from __future__ import annotations

from typing import Any

from trading_core.equity_data_refresh.data_refresh_config import TARGET_VERSION
from trading_core.equity_data_refresh.validation_core import DatasetSnapshot, dataset_summary


def build_dataset_refresh_result(*, as_of_date: str, snapshots: dict[str, DatasetSnapshot], schema_validation: dict[str, Any], freshness_validation: dict[str, Any], coverage_summary: dict[str, Any]) -> dict[str, Any]:
    records = []
    schema_by_id = {row["dataset_id"]: row for row in schema_validation["datasets"]}
    fresh_by_id = {row["dataset_id"]: row for row in freshness_validation["datasets"]}
    for dataset_id, snapshot in snapshots.items():
        summary = dataset_summary(snapshot, as_of_date)
        schema_status = schema_by_id[dataset_id]["schema_status"]
        freshness_status = fresh_by_id[dataset_id]["freshness_status"]
        coverage_status = "passed" if coverage_summary["datasets"][dataset_id]["threshold_passed"] else "failed"
        blocking = list(schema_by_id[dataset_id]["blocking_reasons"]) + list(fresh_by_id[dataset_id]["blocking_reasons"])
        if coverage_status == "failed" and dataset_id in {"trading_calendar", "daily_price", "adjusted_price", "index_price"}:
            blocking.append("coverage_threshold_failed")
        status = "failed" if blocking else "passed" if schema_status == "passed" and coverage_status == "passed" and freshness_status in {"fresh", "lagged_allowed"} else "warning"
        records.append(
            {
                **summary,
                "status": status,
                "provider_id": "local_file_provider",
                "output_path": summary["source_path"],
                "freshness_status": freshness_status,
                "schema_status": schema_status,
                "coverage_status": coverage_status,
                "blocking_reasons": blocking,
                "warnings": list(schema_by_id[dataset_id]["warnings"]) + list(fresh_by_id[dataset_id]["warnings"]),
            }
        )
    return {
        "result_id": "A-SHARE-DATASET-REFRESH-RESULT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "datasets": records,
    }
