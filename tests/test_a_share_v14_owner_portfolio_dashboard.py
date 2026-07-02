from __future__ import annotations

from pathlib import Path

from a_share_v14_test_utils import make_v14_paths, v14_json
from trading_core.equity_v14_portfolio_risk_lab.builder import run_a_share_v14_portfolio_risk_lab


def test_v14_owner_portfolio_dashboard_keeps_owner_blocked_and_no_real_advice(tmp_path: Path) -> None:
    paths = make_v14_paths(tmp_path)
    result = run_a_share_v14_portfolio_risk_lab(paths=paths, simulation_only=True)
    dashboard = v14_json(paths, "v14_owner_portfolio_risk_dashboard_result")

    assert result["owner_portfolio_risk_dashboard_generated"] is True
    assert dashboard["dashboard_is_simulation_only"] is True
    assert dashboard["dashboard_prohibits_real_allocation_advice"] is True
    assert dashboard["dashboard_prohibits_copy_to_real_account"] is True
    assert dashboard["dashboard_prohibits_real_performance_claims"] is True
    assert dashboard["owner_readiness_state"] == "blocked"
    assert dashboard["owner_operationally_acceptable"] is False
    assert dashboard["readiness_score"] == 54
    assert dashboard["score_gap"] == 21
