
from trading_core.equity_owner_operator_experience.operator_config import BUILD_STATUS, OperatorExperienceConfig, validate_config


def test_operator_experience_config_defaults_and_mode_validation():
    config = OperatorExperienceConfig()
    payload = config.to_dict(source={"owner_operationally_acceptable": False, "previous_readiness_score": 54, "minimum_owner_readiness_score": 75, "score_gap": 21})
    assert payload["mode"] == BUILD_STATUS
    assert payload["run_full_pytest"] is False
    assert payload["rerun_owner_readiness_gate"] is False
    assert payload["allow_broker"] is False
    assert validate_config(config) == []
    assert "mode must be one of" in validate_config(OperatorExperienceConfig(mode="bad"))[0]
