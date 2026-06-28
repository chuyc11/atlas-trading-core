"""Schema validation artifact builder."""

from __future__ import annotations

from typing import Any

from trading_core.equity_data_refresh.data_refresh_config import TARGET_VERSION
from trading_core.equity_data_refresh.validation_core import DatasetSnapshot, validate_schema


def build_dataset_schema_validation(*, as_of_date: str, snapshots: dict[str, DatasetSnapshot]) -> dict[str, Any]:
    records = [validate_schema(snapshot, as_of_date) for snapshot in snapshots.values()]
    return {
        "validation_id": "A-SHARE-DATASET-SCHEMA-VALIDATION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "schema_validation_status": "passed" if all(row["schema_status"] == "passed" for row in records) else "failed",
        "datasets": records,
    }
