from trading_core.equity_ops_history.ops_history_config import DEFAULT_AS_OF_DATE, OpsHistoryConfig, validate_ops_history_config


def test_ops_history_config_defaults_are_v086_baseline():
    config = OpsHistoryConfig()
    payload = config.to_dict()
    assert config.as_of_date == DEFAULT_AS_OF_DATE
    assert payload["append_only_history"] is True
    assert payload["allow_synthetic_history"] is False
    assert payload["broker_enabled"] is False
    assert validate_ops_history_config(config) == []

