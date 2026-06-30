from trading_core.equity_owner_readiness_recovery.recovery_config import RecoveryPlanConfig, TARGET_VERSION, validate_config


def test_owner_readiness_recovery_config_defaults():
    config = RecoveryPlanConfig().to_dict(source_gate_decision="blocked", minimum_score=75, actual_score=54, score_gap=21)
    assert config["target_version"] == TARGET_VERSION
    assert config["source_gate_decision"] == "blocked"
    assert config["does_not_lower_threshold"] is True
    assert config["execute_recovery_tasks"] is False
    assert config["rerun_build_from_existing_data"] is False


def test_owner_readiness_recovery_config_rejects_invalid_mode():
    assert validate_config(RecoveryPlanConfig(mode="bad"))
