from __future__ import annotations

from trading_core.equity_portfolio_tracking.tracking_config import DEFAULT_AS_OF_DATE, TARGET_VERSION, TRACKING_BOUNDARY, TrackingConfig, validate_tracking_config


def test_tracking_config_defaults_are_virtual_research_only() -> None:
    config = TrackingConfig()
    payload = config.to_dict()

    assert payload["config_id"] == "A-SHARE-VIRTUAL-PORTFOLIO-TRACKING-CONFIG"
    assert payload["target_version"] == TARGET_VERSION
    assert payload["as_of_date"] == DEFAULT_AS_OF_DATE
    assert payload["initial_virtual_capital"] == {"long": 1_000_000.0, "mid": 1_000_000.0, "short": 1_000_000.0}
    assert payload["fractional_shares_allowed"] is True
    assert payload["board_lot_execution_simulated"] is False
    assert payload["real_execution_simulated"] is False
    assert payload["virtual_only"] is True
    assert payload["research_only"] is True
    assert payload["not_investment_advice"] is True
    assert payload["not_order_instruction"] is True
    assert payload["not_real_trade"] is True
    assert payload["not_profit_guarantee"] is True
    assert payload["not_live_trading_ready"] is True
    assert payload["boundary"] == TRACKING_BOUNDARY
    assert validate_tracking_config(config) == []
