from trading_core.equity_owner_v090_rc.v090_config import RUN_FULL_REGRESSION, V090RCConfig, validate_config


def test_v090_rc_config_defaults_and_mode_validation():
    source = {
        "source_gate_decision": "blocked",
        "previous_readiness_score": 54,
        "minimum_owner_readiness_score": 75,
        "score_gap": 21,
        "owner_operationally_acceptable": False,
        "blocked_state_intentional": True,
        "blocked_state_audited": True,
        "blocked_state_misrepresented_as_acceptable": False,
    }
    payload = V090RCConfig().to_dict(source=source)
    assert payload["mode"] == RUN_FULL_REGRESSION
    assert payload["run_full_pytest"] is True
    assert payload["allow_broker"] is False
    assert validate_config(V090RCConfig(mode="bad"))[0].startswith("mode must be one of")
