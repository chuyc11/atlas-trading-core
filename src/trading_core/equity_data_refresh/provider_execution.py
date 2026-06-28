"""Provider execution log for data refresh."""

from __future__ import annotations

from typing import Any

from trading_core.equity_data_refresh.data_refresh_config import DATASET_IDS, TARGET_VERSION


def build_provider_execution_log(*, mode: str, provider_id: str = "local_file_provider") -> dict[str, Any]:
    return {
        "execution_log_id": "A-SHARE-DATA-REFRESH-PROVIDER-EXECUTION-LOG",
        "target_version": TARGET_VERSION,
        "mode": mode,
        "network_providers_used": [],
        "external_network_calls_made": False,
        "broker_provider_used": False,
        "real_account_provider_used": False,
        "order_provider_used": False,
        "records": [
            {
                "dataset_id": dataset_id,
                "provider_id": provider_id,
                "attempted": True,
                "action": "validate_existing" if mode == "validate_existing_data" else "refresh_from_local",
                "status": "passed",
                "request_metadata": {
                    "requires_network": False,
                    "requires_token": False,
                    "requires_broker_account": False,
                    "timeout_seconds": 20,
                    "max_retries": 2,
                    "rate_limit_policy": "local_file_read",
                },
                "fallback_used": False,
                "fallback_provider_id": None,
            }
            for dataset_id in DATASET_IDS
        ],
    }
