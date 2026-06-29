from trading_core.equity_build_output_dashboard.build_output_dashboard_config import BuildOutputDashboardConfig, validate_config


def test_build_output_dashboard_config_defaults():
    payload = BuildOutputDashboardConfig().to_dict()
    assert payload["source_workflow_mode"] == "build_from_existing_data"
    assert payload["prefer_build_output"] is True
    assert payload["allow_validate_fallback_for_required_artifacts"] is False


def test_build_output_dashboard_config_rejects_bad_mode():
    assert validate_config(BuildOutputDashboardConfig(mode="bad"))

