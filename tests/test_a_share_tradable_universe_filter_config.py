from __future__ import annotations

from trading_core.equity_selection.filter_config import TARGET_VERSION, TradableUniverseFilterConfig, parse_bool


def test_tradable_universe_filter_config_defaults() -> None:
    config = TradableUniverseFilterConfig()

    assert config.as_of_date == "2026-06-26"
    assert config.min_listing_trading_days == 120
    assert config.min_avg_amount_20d == 50_000_000
    assert config.min_avg_amount_60d == 30_000_000
    assert config.min_total_mv == 3_000_000_000
    assert config.min_circ_mv == 2_000_000_000
    assert config.min_close_price == 2.0
    assert config.to_dict()["target_version"] == TARGET_VERSION
    assert config.to_dict()["boundary"]["scores_generated"] is False


def test_parse_bool_accepts_cli_style_values() -> None:
    assert parse_bool("false") is False
    assert parse_bool("true") is True
    assert parse_bool(False) is False

