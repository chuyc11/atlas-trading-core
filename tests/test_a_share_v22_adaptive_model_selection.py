from __future__ import annotations

from pathlib import Path

from a_share_v22_test_utils import make_v22_paths, v22_json
from trading_core.equity_v22_ensemble_meta_strategy.builder import run_a_share_v22_ensemble_meta_strategy


def test_v22_adaptive_model_selection_has_no_real_account_action(tmp_path: Path) -> None:
    paths = make_v22_paths(tmp_path)
    result = run_a_share_v22_ensemble_meta_strategy(paths=paths, simulation_only=True)
    adaptive = v22_json(paths, "v22_adaptive_model_selection_result")

    assert result["adaptive_model_selection_result_generated"] is True
    assert adaptive["strategy_auto_promoted"] is False
    assert adaptive["adaptive_selection_generates_buy_sell_signal"] is False
    assert adaptive["adaptive_selection_changes_real_account"] is False
    assert result["adaptive_model_selection_results_fabricated"] is False
