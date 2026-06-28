from __future__ import annotations

from trading_core.equity_data_refresh.provider_execution import build_provider_execution_log


def test_provider_execution_no_network_or_fallback_by_default() -> None:
    payload = build_provider_execution_log(mode="validate_existing_data")
    assert payload["external_network_calls_made"] is False
    assert payload["broker_provider_used"] is False
    assert all(row["fallback_used"] is False for row in payload["records"])
