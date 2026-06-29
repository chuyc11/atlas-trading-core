from trading_core.equity_current_day.current_day_config import (
    RUN_RESEARCH_FROM_EXISTING_REFRESH,
    VALIDATE_EXISTING_ARTIFACTS,
    CurrentDayRunConfig,
    validate_current_day_config,
)


def test_current_day_config_defaults():
    config = CurrentDayRunConfig()
    payload = config.to_dict()
    assert payload["target_version"] == "v0.8.1-a-share-current-day-research-workflow-runner"
    assert payload["mode"] == RUN_RESEARCH_FROM_EXISTING_REFRESH
    assert payload["workflow_mode"] == VALIDATE_EXISTING_ARTIFACTS
    assert payload["broker_enabled"] is False
    assert payload["real_order_enabled"] is False


def test_current_day_config_rejects_date_mismatch_without_waiver():
    config = CurrentDayRunConfig(as_of_date="2026-06-26", resolved_as_of_date="2026-06-25")
    assert "resolved_as_of_date differs from as_of_date; pass allow_date_mismatch to proceed" in validate_current_day_config(config)

