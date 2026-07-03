from __future__ import annotations

from pathlib import Path

from a_share_v22_test_utils import make_v22_paths, v22_json
from trading_core.equity_v22_ensemble_meta_strategy.builder import run_a_share_v22_ensemble_meta_strategy


def test_v22_strategy_ensemble_not_real_strategy(tmp_path: Path) -> None:
    paths = make_v22_paths(tmp_path)
    result = run_a_share_v22_ensemble_meta_strategy(paths=paths, simulation_only=True)
    strategy = v22_json(paths, "v22_strategy_ensemble_result")

    assert result["strategy_ensemble_result_generated"] is True
    assert strategy["strategy_ensemble_is_real_strategy"] is False
    assert result["strategy_ensemble_generates_real_trade"] is False
    assert strategy["oos_weighted_strategy_research_ensemble_supported"] is False
