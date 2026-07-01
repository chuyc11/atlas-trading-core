from trading_core.equity_owner_v0820_gate_outcome.outcome_config import BUILD_AND_AUDIT, V0820OutcomeConfig, validate_config


def test_v0820_outcome_config_defaults_and_mode_validation():
    config = V0820OutcomeConfig()
    payload = config.to_dict(source_gate_decision="blocked", minimum_owner_readiness_score=75)
    assert config.mode == BUILD_AND_AUDIT
    assert payload["allow_controlled_reevaluation_if_eligible"] is True
    assert payload["allow_broker"] is False
    assert validate_config(config) == []
    assert validate_config(V0820OutcomeConfig(mode="bad_mode"))

