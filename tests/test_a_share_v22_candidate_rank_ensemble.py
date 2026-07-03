from __future__ import annotations

from pathlib import Path

from a_share_v22_test_utils import make_v22_paths, v22_json
from trading_core.equity_v22_ensemble_meta_strategy.builder import run_a_share_v22_ensemble_meta_strategy


def test_v22_candidate_rank_ensemble_watchlist_not_buy_list(tmp_path: Path) -> None:
    paths = make_v22_paths(tmp_path)
    result = run_a_share_v22_ensemble_meta_strategy(paths=paths, simulation_only=True)
    candidate = v22_json(paths, "v22_candidate_rank_ensemble_result")

    assert result["candidate_rank_ensemble_result_generated"] is True
    assert candidate["candidate_ensemble_watchlist_generated"] is True
    assert candidate["candidate_ensemble_watchlist_is_buy_list"] is False
    assert candidate["candidate_rank_downgrade_is_sell_signal"] is False
    assert candidate["orders_path_written"] is False
    assert result["candidate_ensemble_generates_buy_sell_signal"] is False
