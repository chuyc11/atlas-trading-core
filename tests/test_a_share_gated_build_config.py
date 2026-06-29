from trading_core.equity_current_day_builds.gated_build_config import GatedBuildConfig, validate_gated_build_config


def test_gated_build_config_defaults_are_research_only():
    payload = GatedBuildConfig().to_dict()
    assert payload["to_workflow_mode"] == "build_from_existing_data"
    assert payload["allow_broker"] is False
    assert payload["allow_real_orders"] is False
    assert validate_gated_build_config(GatedBuildConfig()) == []


def test_gated_build_config_rejects_broker():
    assert validate_gated_build_config(GatedBuildConfig(allow_broker=True))

