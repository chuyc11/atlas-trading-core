from __future__ import annotations

from trading_core.equity_data_refresh.dataset_contracts import contract_payload, dataset_contracts


def test_dataset_contracts_required_fields() -> None:
    contracts = dataset_contracts()
    assert "daily_price" in contracts
    assert "trade_date" in contracts["daily_price"].required_fields
    assert contract_payload()["trading_calendar"]["aliases"]["trade_date"] == ["trade_date", "date"]
