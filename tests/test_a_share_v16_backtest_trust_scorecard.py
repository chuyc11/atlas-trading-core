from __future__ import annotations

from pathlib import Path

from a_share_v16_test_utils import make_v16_paths, v16_json
from trading_core.equity_v16_pit_backtest_market_rules.builder import run_a_share_v16_pit_backtest_market_rules


def test_v16_backtest_trust_scorecard_and_owner_dashboard(tmp_path: Path) -> None:
    paths = make_v16_paths(tmp_path)
    result = run_a_share_v16_pit_backtest_market_rules(paths=paths, simulation_only=True)
    trust = v16_json(paths, "v16_backtest_trust_scorecard")
    dashboard = v16_json(paths, "v16_owner_trust_dashboard_result")

    assert result["backtest_trust_scorecard_generated"] is True
    assert result["backtest_trust_decision"] == "trusted_for_simulation_research_or_usable_with_limitations"
    assert trust["trust_score"] == 78
    assert dashboard["owner_trust_dashboard_generated"] is True
    assert dashboard["owner_readiness_state"] == "blocked"
    assert dashboard["owner_operationally_acceptable"] is False
