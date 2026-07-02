from __future__ import annotations

from pathlib import Path

from a_share_v17_test_utils import make_v17_paths, v17_json
from trading_core.equity_v17_strategy_validation_lab.builder import run_a_share_v17_strategy_validation_lab


def test_v17_strategy_backtest_validation_reuses_v16_trust_layer(tmp_path: Path) -> None:
    paths = make_v17_paths(tmp_path)
    result = run_a_share_v17_strategy_validation_lab(paths=paths, simulation_only=True)
    backtest = v17_json(paths, "v17_strategy_backtest_validation_result")

    assert result["strategy_backtest_validation_result_generated"] is True
    assert backtest["event_driven_replay_used"] is True
    assert backtest["a_share_market_rules_used"] is True
    assert backtest["virtual_broker_rules_used"] is True
    assert backtest["transaction_cost_adjustment_used"] is True
    assert backtest["slippage_adjustment_used"] is True
    assert backtest["backtest_results_fabricated"] is False
    assert backtest["not_real_order"] is True
