from __future__ import annotations

from pathlib import Path

from a_share_v17_test_utils import make_v17_paths, v17_json
from trading_core.equity_v17_strategy_validation_lab.builder import run_a_share_v17_strategy_validation_lab


def test_v17_owner_dashboard_keeps_readiness_blocked(tmp_path: Path) -> None:
    paths = make_v17_paths(tmp_path)
    result = run_a_share_v17_strategy_validation_lab(paths=paths, simulation_only=True)
    dashboard = v17_json(paths, "v17_owner_strategy_validation_dashboard_result")

    assert result["owner_strategy_validation_dashboard_generated"] is True
    assert dashboard["owner_readiness_blocked_displayed"] is True
    assert dashboard["not_live_trading_ready_displayed"] is True
    assert dashboard["copy_to_real_account_blocked"] is True
    assert dashboard["buy_sell_advice_output"] is False
    assert dashboard["real_performance_claim_output"] is False
    assert dashboard["owner_operationally_acceptable"] is False
