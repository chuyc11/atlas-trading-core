from __future__ import annotations

from pathlib import Path

from a_share_v15_test_utils import make_v15_paths, v15_json
from trading_core.equity_v15_market_regime_lab.builder import run_a_share_v15_market_regime_lab


def test_v15_owner_regime_dashboard_keeps_owner_blocked(tmp_path: Path) -> None:
    paths = make_v15_paths(tmp_path)
    result = run_a_share_v15_market_regime_lab(paths=paths, simulation_only=True)
    dashboard = v15_json(paths, "v15_owner_regime_dashboard_result")

    assert result["owner_regime_dashboard_generated"] is True
    assert dashboard["owner_readiness_state"] == "blocked"
    assert dashboard["owner_operationally_acceptable"] is False
    assert dashboard["readiness_score"] == 54
    assert dashboard["score_gap"] == 21
    assert dashboard["not_live_trading_ready"] is True
    assert dashboard["copy_to_real_account_prohibited"] is True
    assert dashboard["real_trade_advice_generated"] is False
