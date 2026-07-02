from __future__ import annotations

from pathlib import Path

from a_share_v16_test_utils import make_v16_paths, v16_json
from trading_core.equity_v16_pit_backtest_market_rules.builder import run_a_share_v16_pit_backtest_market_rules


def test_v16_event_driven_replay_does_not_fabricate_results(tmp_path: Path) -> None:
    paths = make_v16_paths(tmp_path)
    result = run_a_share_v16_pit_backtest_market_rules(paths=paths, simulation_only=True)
    replay = v16_json(paths, "v16_event_driven_replay_result")

    assert result["event_driven_replay_result_generated"] is True
    assert replay["replay_mode"] == "simulation_only_no_real_orders"
    assert result["backtest_results_fabricated"] is False
    assert result["simulated_fills_fabricated"] is False
    assert replay["unsupported_real_performance_claims_blocked"] is True
