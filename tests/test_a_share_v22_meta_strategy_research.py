from __future__ import annotations

from pathlib import Path

from a_share_v22_test_utils import make_v22_paths, v22_json
from trading_core.equity_v22_ensemble_meta_strategy.builder import run_a_share_v22_ensemble_meta_strategy


def test_v22_meta_strategy_is_watch_only_not_trade_instruction(tmp_path: Path) -> None:
    paths = make_v22_paths(tmp_path)
    result = run_a_share_v22_ensemble_meta_strategy(paths=paths, simulation_only=True)
    meta = v22_json(paths, "v22_meta_strategy_research_result")

    assert result["meta_strategy_research_result_generated"] is True
    assert meta["meta_strategy_decision"] == "watch_with_limitations"
    assert meta["simulated_active_changed"] is False
    assert meta["meta_strategy_generates_real_trade"] is False
    assert result["meta_strategy_results_fabricated"] is False
