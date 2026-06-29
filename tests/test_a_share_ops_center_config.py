from trading_core.equity_ops_center.ops_config import OpsCenterConfig, validate_ops_config


def test_ops_center_config_defaults_are_safe():
    payload = OpsCenterConfig().to_dict()
    assert payload["aggregate_existing_artifacts_only"] is True
    assert payload["allow_safe_validation_chain"] is False
    assert payload["commands_executed"] == []
    assert payload["broker_enabled"] is False
    assert validate_ops_config(OpsCenterConfig()) == []


def test_ops_center_config_requires_safe_chain_flag():
    config = OpsCenterConfig(mode="run_safe_ops_validation_chain")
    assert validate_ops_config(config)
