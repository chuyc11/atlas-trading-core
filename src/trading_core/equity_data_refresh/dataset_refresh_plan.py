"""Dataset refresh plan builder."""

from __future__ import annotations

from typing import Any

from trading_core.equity_data_refresh.data_refresh_config import CRITICAL_DATASETS, DATASET_IDS, REFRESH_FROM_PUBLIC_PROVIDERS, TARGET_VERSION
from trading_core.equity_data_refresh.dataset_contracts import dataset_contracts


def build_dataset_refresh_plan(*, as_of_date: str, mode: str) -> dict[str, Any]:
    contracts = dataset_contracts()
    records = []
    for dataset_id in DATASET_IDS:
        contract = contracts[dataset_id]
        records.append(
            {
                "dataset_id": dataset_id,
                "required": True,
                "primary_provider": "local_file_provider" if mode != REFRESH_FROM_PUBLIC_PROVIDERS else "public_provider_registry",
                "fallback_providers": ["cached_panel_provider"],
                "target_as_of_date": as_of_date,
                "required_fields": list(contract.required_fields),
                "criticality": "critical" if dataset_id in CRITICAL_DATASETS else "important",
                "refresh_action": "validate_existing" if mode == "validate_existing_data" else "refresh_from_local" if mode == "refresh_from_local_sources" else "refresh_from_public_provider",
            }
        )
    return {
        "plan_id": "A-SHARE-DATASET-REFRESH-PLAN",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "mode": mode,
        "datasets": records,
    }
