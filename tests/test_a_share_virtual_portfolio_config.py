from __future__ import annotations

from trading_core.equity_portfolios.portfolio_config import PORTFOLIO_BOUNDARY, RECOMMENDED_NEXT_VERSION, TARGET_VERSION, PortfolioConstructionConfig, validate_portfolio_config


def test_virtual_portfolio_config_defaults() -> None:
    config = PortfolioConstructionConfig()
    payload = config.to_dict()

    assert payload["target_version"] == TARGET_VERSION
    assert config.long_holdings == 30
    assert config.mid_holdings == 30
    assert config.short_holdings == 20
    assert config.long_max_single_weight == 0.05
    assert config.short_max_industry_weight == 0.30
    assert payload["boundary"] == PORTFOLIO_BOUNDARY
    assert RECOMMENDED_NEXT_VERSION == "v0.7.7-a-share-daily-stock-selection-briefing"
    assert validate_portfolio_config(config) == []


def test_virtual_portfolio_config_rejects_bad_values() -> None:
    config = PortfolioConstructionConfig(long_holdings=0, long_max_single_weight=2.0)
    issues = validate_portfolio_config(config)

    assert "long_holdings must be positive" in issues
    assert "long_max_single_weight must be within (0, 1]" in issues

