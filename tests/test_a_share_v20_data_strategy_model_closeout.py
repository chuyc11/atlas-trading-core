from __future__ import annotations

from pathlib import Path

from a_share_v20_test_utils import make_v20_paths, v20_json
from trading_core.equity_v20_platform_closeout.builder import run_a_share_v20_platform_closeout


def test_v20_data_strategy_research_db_and_model_closeouts(tmp_path: Path) -> None:
    paths = make_v20_paths(tmp_path)
    result = run_a_share_v20_platform_closeout(paths=paths, simulation_only=True)
    data = v20_json(paths, "v20_data_backtest_trust_closeout")
    strategy = v20_json(paths, "v20_strategy_validation_closeout")
    research_db = v20_json(paths, "v20_research_db_ml_lab_closeout")
    model = v20_json(paths, "v20_ml_model_risk_closeout")

    assert result["data_backtest_trust_closeout_generated"] is True
    assert data["lookahead_bias_guard_passed"] is True
    assert data["leakage_blocker_count"] == 0
    assert strategy["strategy_validation_closeout_generated"] is True
    assert strategy["candidate_validation_generates_buy_sell_signal"] is False
    assert research_db["research_db_ml_lab_closeout_generated"] is True
    assert research_db["predictions_are_trade_signals"] is False
    assert model["ml_model_risk_closeout_generated"] is True
    assert model["research_portfolio_is_real_portfolio"] is False
