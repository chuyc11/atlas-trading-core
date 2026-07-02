from __future__ import annotations

from pathlib import Path

from a_share_v18_test_utils import make_v18_paths, v18_json
from trading_core.equity_v18_research_db_feature_ml_lab.builder import run_a_share_v18_research_db_feature_ml_lab


def test_v18_owner_ml_dashboard_keeps_readiness_blocked(tmp_path: Path) -> None:
    paths = make_v18_paths(tmp_path)
    result = run_a_share_v18_research_db_feature_ml_lab(paths=paths, simulation_only=True)
    dashboard = v18_json(paths, "v18_owner_ml_dashboard_result")

    assert result["owner_ml_dashboard_generated"] is True
    assert dashboard["owner_readiness_blocked_displayed"] is True
    assert dashboard["not_live_trading_ready_displayed"] is True
    assert dashboard["copy_to_real_account_blocked"] is True
    assert dashboard["buy_sell_advice_output"] is False
    assert dashboard["real_performance_claim_output"] is False
    assert dashboard["owner_operationally_acceptable"] is False
