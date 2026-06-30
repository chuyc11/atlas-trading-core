from trading_core.equity_owner_controlled_gate_reevaluation.controlled_config import ControlledReevaluationConfig, TARGET_VERSION, validate_config


def test_controlled_gate_reevaluation_config_defaults():
    config = ControlledReevaluationConfig().to_dict(source_gate_decision="blocked", minimum_score=75, actual_score=54)
    assert config["target_version"] == TARGET_VERSION
    assert config["mode"] == "record_reevaluation_skip_decision"
    assert config["rerun_owner_readiness_gate"] is False
    assert config["record_skip_decision_when_not_ready"] is True
    assert config["does_not_auto_waive"] is True


def test_controlled_gate_reevaluation_config_rejects_invalid_mode():
    assert validate_config(ControlledReevaluationConfig(mode="bad"))

