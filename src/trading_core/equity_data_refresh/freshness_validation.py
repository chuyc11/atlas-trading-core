"""Freshness validation artifact builder."""

from __future__ import annotations

from typing import Any

from trading_core.equity_data_refresh.data_refresh_config import TARGET_VERSION
from trading_core.equity_data_refresh.validation_core import DatasetSnapshot, validate_freshness


def build_dataset_freshness_validation(*, as_of_date: str, snapshots: dict[str, DatasetSnapshot], trading_dates: list[str]) -> dict[str, Any]:
    records = [validate_freshness(snapshot, as_of_date, trading_dates) for snapshot in snapshots.values()]
    return {
        "validation_id": "A-SHARE-DATASET-FRESHNESS-VALIDATION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "freshness_validation_status": "passed" if all(not row["blocking_reasons"] for row in records) else "failed",
        "datasets": records,
    }
