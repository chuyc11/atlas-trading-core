from __future__ import annotations

from pathlib import Path

from a_share_v17_test_utils import make_v17_paths, v17_json
from trading_core.equity_v17_strategy_validation_lab.builder import run_a_share_v17_strategy_validation_lab


def test_v17_candidate_ranking_validation_is_not_trade_signal(tmp_path: Path) -> None:
    paths = make_v17_paths(tmp_path)
    result = run_a_share_v17_strategy_validation_lab(paths=paths, simulation_only=True)
    candidate = v17_json(paths, "v17_candidate_ranking_validation_result")

    assert result["candidate_ranking_validation_result_generated"] is True
    assert candidate["candidate_validation_generates_buy_sell_signal"] is False
    assert candidate["candidate_watchlist_is_buy_list"] is False
    assert candidate["candidate_downgrade_generates_sell_signal"] is False
    assert candidate["candidate_result_writes_real_order_path"] is False
    assert candidate["candidate_report_displays_not_investment_advice"] is True
    assert candidate["candidate_safety_audit_passed"] is True
