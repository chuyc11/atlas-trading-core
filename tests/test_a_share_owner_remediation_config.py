from trading_core.equity_owner_remediation.remediation_config import OwnerRemediationConfig, validate_remediation_config


def test_owner_remediation_config_defaults_are_safe():
    payload = OwnerRemediationConfig().to_dict()
    assert payload["execute_remediation_actions"] is False
    assert payload["allow_safe_local_dry_run"] is False
    assert payload["allow_data_refresh_rerun"] is False
    assert payload["send_external_notifications"] is False
    assert payload["broker_enabled"] is False
    assert validate_remediation_config(OwnerRemediationConfig()) == []


def test_owner_remediation_config_rejects_bad_mode():
    config = OwnerRemediationConfig(mode="bad")
    assert validate_remediation_config(config)
