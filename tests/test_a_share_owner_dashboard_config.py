from trading_core.equity_owner_dashboard.dashboard_config import OwnerDashboardConfig, validate_dashboard_config


def test_owner_dashboard_config_defaults_are_valid():
    config = OwnerDashboardConfig()
    payload = config.to_dict()
    assert payload["owner_facing"] is True
    assert payload["broker_enabled"] is False
    assert validate_dashboard_config(config) == []
