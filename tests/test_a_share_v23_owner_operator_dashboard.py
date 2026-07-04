from __future__ import annotations

from pathlib import Path

from a_share_v23_test_utils import make_v23_paths, v23_json
from trading_core.equity_v23_operator_ux_journal.builder import run_a_share_v23_operator_ux_journal


def test_v23_owner_operator_dashboard_shows_required_safety_state(tmp_path: Path) -> None:
    paths = make_v23_paths(tmp_path)
    result = run_a_share_v23_operator_ux_journal(paths=paths, simulation_only=True)
    dashboard = v23_json(paths, "v23_owner_operator_dashboard_result")

    assert result["owner_operator_dashboard_generated"] is True
    assert dashboard["owner_readiness_blocked_displayed"] is True
    assert dashboard["not_live_trading_ready_displayed"] is True
    assert dashboard["not_investment_advice_displayed"] is True
    assert dashboard["not_buy_sell_signal_displayed"] is True
    assert dashboard["copy_to_real_account_blocked"] is True
    assert dashboard["real_portfolio_recommendation_output"] is False
