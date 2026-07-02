from __future__ import annotations

from pathlib import Path

from a_share_v16_test_utils import make_v16_paths, v16_json
from trading_core.equity_v16_pit_backtest_market_rules.builder import run_a_share_v16_pit_backtest_market_rules


def test_v16_a_share_market_rules_covered(tmp_path: Path) -> None:
    paths = make_v16_paths(tmp_path)
    result = run_a_share_v16_pit_backtest_market_rules(paths=paths, simulation_only=True)
    rules = v16_json(paths, "v16_a_share_market_rule_registry")

    assert result["a_share_market_rule_registry_generated"] is True
    assert result["a_share_market_rules_covered"] is True
    assert result["t_plus_one_rule_checked"] is True
    assert result["price_limit_rule_checked"] is True
    assert result["suspension_rule_checked"] is True
    assert result["lot_size_rule_checked"] is True
    assert rules["rule_set"]["lot_size"] == "A-share round lot 100 shares"
