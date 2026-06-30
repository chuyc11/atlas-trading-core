from trading_core.equity_owner_readiness_recovery_execution.execution_config import RecoveryExecutionConfig, TARGET_VERSION, validate_config


def test_recovery_execution_config_defaults():
    config = RecoveryExecutionConfig().to_dict(source_gate_decision="blocked", minimum_score=75, actual_score=54)
    assert config["target_version"] == TARGET_VERSION
    assert config["mode"] == "prepare_gate_reevaluation"
    assert config["execute_recovery_tasks"] is False
    assert config["rerun_owner_readiness_gate"] is False
    assert config["does_not_lower_threshold"] is True


def test_recovery_execution_config_rejects_invalid_mode():
    assert validate_config(RecoveryExecutionConfig(mode="bad"))
