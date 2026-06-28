"""Coverage summary artifact builder."""

from __future__ import annotations

from typing import Any

from trading_core.equity_data_refresh.data_refresh_config import TARGET_VERSION
from trading_core.equity_data_refresh.validation_core import DatasetSnapshot, coverage_metrics


def build_dataset_coverage_summary(*, as_of_date: str, snapshots: dict[str, DatasetSnapshot]) -> dict[str, Any]:
    metrics = coverage_metrics(snapshots, as_of_date)
    return {
        "coverage_id": "A-SHARE-DATASET-COVERAGE-SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "coverage_validation_status": "passed" if metrics["critical_missing_count"] == 0 else "failed",
        **metrics,
    }
