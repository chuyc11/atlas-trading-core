from trading_core.equity_owner_monitoring.monitoring_config import OwnerMonitoringConfig, validate_monitoring_config


def test_owner_monitoring_config_defaults_are_safe():
    config = OwnerMonitoringConfig()
    payload = config.to_dict()
    assert payload["send_external_notifications"] is False
    assert payload["local_alert_artifacts_only"] is True
    assert validate_monitoring_config(config) == []
