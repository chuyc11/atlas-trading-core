from trading_core.equity_owner_daily_pack_history.daily_pack_history_config import (
    ALLOWED_MODES,
    BUILD_TRENDS,
    DailyPackHistoryConfig,
    TARGET_VERSION,
    validate_config,
)


def test_owner_daily_pack_history_config_defaults():
    config = DailyPackHistoryConfig().to_dict()
    assert config["target_version"] == TARGET_VERSION
    assert config["mode"] == BUILD_TRENDS
    assert config["append_only_history"] is True
    assert config["allow_synthetic_history"] is False
    assert config["allow_future_dates"] is False
    assert config["allowed_modes"] == ALLOWED_MODES


def test_owner_daily_pack_history_config_rejects_invalid_mode():
    assert validate_config(DailyPackHistoryConfig(mode="place_order"))
