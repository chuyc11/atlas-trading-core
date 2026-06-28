"""Provider registry for A-share data refresh."""

from __future__ import annotations

from typing import Any

from trading_core.equity_data_refresh.data_refresh_config import DATASET_IDS, TARGET_VERSION


def build_provider_registry_snapshot(*, allow_network_providers: bool = False, allow_public_providers: bool = False) -> dict[str, Any]:
    providers = [
        _provider("local_file_provider", "Local file provider", "local_file_provider", True, 1, False, False, DATASET_IDS),
        _provider("cached_panel_provider", "Cached panel provider", "cached_panel_provider", True, 2, False, False, DATASET_IDS),
        _provider("eastmoney_public_provider", "Eastmoney public provider", "public_http_provider", allow_public_providers, 10, True, False, ["daily_price", "daily_basic", "index_price"]),
        _provider("akshare_provider", "AkShare public provider", "akshare_provider", allow_public_providers, 20, True, False, ["equity_master", "daily_price", "adjusted_price", "daily_basic", "index_price", "industry_classification"]),
        _provider("qstock_provider", "QStock public provider", "qstock_provider", allow_public_providers, 30, True, False, ["daily_price", "daily_basic"]),
        _provider("baostock_provider", "BaoStock public provider", "baostock_provider", allow_public_providers, 40, True, False, ["daily_price", "adjusted_price", "index_price"]),
        _provider("tushare_provider", "Tushare public provider", "tushare_provider", False, 50, True, True, ["equity_master", "daily_price", "daily_basic", "financial_indicators"]),
    ]
    for provider in providers:
        if provider["requires_network"] and not allow_network_providers:
            provider["enabled"] = False
            provider["disabled_reason"] = "network providers require explicit opt-in"
    return {
        "registry_id": "A-SHARE-DATA-REFRESH-PROVIDER-REGISTRY",
        "target_version": TARGET_VERSION,
        "allow_network_providers": allow_network_providers,
        "allow_public_providers": allow_public_providers,
        "broker_provider": False,
        "real_trading_provider": False,
        "account_provider": False,
        "order_provider": False,
        "providers": providers,
        "rejected_providers": [],
    }


def validate_provider_registry(registry: dict[str, Any]) -> list[str]:
    issues = []
    for provider in registry.get("providers", []):
        if provider.get("requires_broker_account"):
            issues.append(f"provider_requires_broker_account:{provider.get('provider_id')}")
        if provider.get("provider_type") in {"broker_provider", "account_provider", "order_provider"}:
            issues.append(f"forbidden_provider_type:{provider.get('provider_id')}")
    return issues


def _provider(provider_id: str, name: str, provider_type: str, enabled: bool, priority: int, requires_network: bool, requires_token: bool, supported: list[str]) -> dict[str, Any]:
    return {
        "provider_id": provider_id,
        "provider_name": name,
        "provider_type": provider_type,
        "enabled": enabled,
        "priority": priority,
        "supports_equity_master": "equity_master" in supported,
        "supports_daily_price": "daily_price" in supported,
        "supports_adjusted_price": "adjusted_price" in supported,
        "supports_daily_basic": "daily_basic" in supported,
        "supports_index_price": "index_price" in supported,
        "supports_industry": "industry_classification" in supported,
        "supports_financials": "financial_indicators" in supported,
        "requires_network": requires_network,
        "requires_token": requires_token,
        "requires_broker_account": False,
        "timeout_seconds": 20,
        "max_retries": 2,
        "rate_limit_policy": "disabled_in_validate_existing_data" if requires_network else "local_file_read",
    }
