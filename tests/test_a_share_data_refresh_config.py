from __future__ import annotations

from trading_core.equity_data_refresh.data_refresh_config import DataRefreshConfig, validate_data_refresh_config


def test_data_refresh_config_defaults_and_mode_validation() -> None:
    payload = DataRefreshConfig().to_dict()
    assert payload["mode"] == "validate_existing_data"
    assert payload["allow_network_providers"] is False
    assert payload["allow_research_workflow_after_refresh"] is False
    assert validate_data_refresh_config(DataRefreshConfig(mode="bad"))
