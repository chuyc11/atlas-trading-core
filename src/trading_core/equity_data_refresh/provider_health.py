"""Provider health checks for data refresh."""

from __future__ import annotations

from typing import Any

from trading_core.equity_data_refresh.data_refresh_config import TARGET_VERSION
from trading_core.equity_data_refresh.dataset_contracts import dataset_source_paths
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import relative


def build_provider_health_check(*, paths: ProjectPaths, registry: dict[str, Any]) -> dict[str, Any]:
    source_paths = dataset_source_paths(paths)
    records = []
    for provider in registry.get("providers", []):
        is_local = provider.get("provider_type") in {"local_file_provider", "cached_panel_provider"}
        local_available = all(path.exists() for path in source_paths.values()) if is_local else None
        records.append(
            {
                "provider_id": provider["provider_id"],
                "enabled": provider["enabled"],
                "reachable": False if provider.get("requires_network") and not provider.get("enabled") else None,
                "local_source_available": local_available,
                "supports_required_dataset": any(provider.get(key) for key in provider if key.startswith("supports_")),
                "schema_contract_known": True,
                "last_successful_refresh": None,
                "current_attempt_status": "available" if provider.get("enabled") and (not is_local or local_available) else "disabled_or_unavailable",
                "error_type": None if provider.get("enabled") else "disabled",
                "error_message": provider.get("disabled_reason"),
                "retry_count": 0,
                "timeout_seconds": provider.get("timeout_seconds"),
                "fallback_used": False,
                "fallback_provider_id": None,
                "source_paths": {dataset_id: relative(path, paths.project_root) for dataset_id, path in source_paths.items()} if is_local else {},
            }
        )
    return {
        "health_check_id": "A-SHARE-DATA-REFRESH-PROVIDER-HEALTH-CHECK",
        "target_version": TARGET_VERSION,
        "providers": records,
        "network_usage_summary": {
            "network_providers_enabled": [row["provider_id"] for row in records if row["enabled"] and registry_provider(registry, row["provider_id"]).get("requires_network")],
            "external_network_calls_made": False,
        },
    }


def registry_provider(registry: dict[str, Any], provider_id: str) -> dict[str, Any]:
    for provider in registry.get("providers", []):
        if provider.get("provider_id") == provider_id:
            return provider
    return {}
