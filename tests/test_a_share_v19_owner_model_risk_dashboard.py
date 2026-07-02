from __future__ import annotations

from pathlib import Path

from a_share_v19_test_utils import make_v19_paths, v19_json
from trading_core.equity_v19_ml_validation_model_risk.builder import run_a_share_v19_ml_validation_model_risk


def test_v19_owner_model_risk_dashboard_keeps_readiness_blocked(tmp_path: Path) -> None:
    paths = make_v19_paths(tmp_path)
    result = run_a_share_v19_ml_validation_model_risk(paths=paths, simulation_only=True)
    dashboard = v19_json(paths, "v19_owner_model_risk_dashboard_result")

    assert result["owner_model_risk_dashboard_generated"] is True
    assert dashboard["owner_readiness_blocked_displayed"] is True
    assert dashboard["not_live_trading_ready_displayed"] is True
    assert dashboard["copy_to_real_account_blocked"] is True
    assert dashboard["buy_sell_advice_output"] is False
    assert dashboard["real_performance_claim_output"] is False
    assert dashboard["real_portfolio_recommendation_output"] is False
    assert dashboard["owner_operationally_acceptable"] is False
