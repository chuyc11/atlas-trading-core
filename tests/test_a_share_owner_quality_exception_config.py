from trading_core.equity_owner_quality_exceptions.exception_workflow_config import QualityExceptionWorkflowConfig, TARGET_VERSION, validate_config


def test_owner_quality_exception_config_defaults():
    config = QualityExceptionWorkflowConfig().to_dict()
    assert config["target_version"] == TARGET_VERSION
    assert config["allow_auto_waiver"] is False
    assert config["waiver_changes_gate_decision"] is False


def test_owner_quality_exception_config_rejects_invalid_mode():
    assert validate_config(QualityExceptionWorkflowConfig(mode="bad"))
