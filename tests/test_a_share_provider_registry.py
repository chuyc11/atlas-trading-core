from __future__ import annotations

from trading_core.equity_data_refresh.provider_registry import build_provider_registry_snapshot, validate_provider_registry


def test_provider_registry_rejects_broker_provider() -> None:
    registry = build_provider_registry_snapshot()
    registry["providers"].append({"provider_id": "bad", "provider_type": "broker_provider", "requires_broker_account": True})
    assert validate_provider_registry(registry)
