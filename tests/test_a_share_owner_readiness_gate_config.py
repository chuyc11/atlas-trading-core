
from trading_core.equity_owner_readiness_gate.gate_config import OwnerReadinessGateConfig, TARGET_VERSION, validate_config


def test_owner_readiness_gate_config_defaults():
    config = OwnerReadinessGateConfig().to_dict()
    assert config["target_version"] == TARGET_VERSION
    assert config["minimum_owner_readiness_score"] == 75
    assert config["owner_operations_gate_only"] is True
    assert config["not_investment_gate"] is True


def test_owner_readiness_gate_config_rejects_invalid_mode():
    config = OwnerReadinessGateConfig(mode="bad")
    assert validate_config(config)
