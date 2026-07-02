from __future__ import annotations

from pathlib import Path

from a_share_v14_test_utils import make_v14_paths, v14_json
from trading_core.equity_v14_portfolio_risk_lab.builder import run_a_share_v14_portfolio_risk_lab


def test_v14_multi_strategy_portfolio_integrates_v13_quality_without_real_active(tmp_path: Path) -> None:
    paths = make_v14_paths(tmp_path)
    result = run_a_share_v14_portfolio_risk_lab(paths=paths, simulation_only=True)
    multi = v14_json(paths, "v14_multi_strategy_portfolio_result")

    assert result["multi_strategy_portfolio_result_generated"] is True
    assert multi["strategy_eligibility_inputs_from_v13_quality_gates"] is True
    assert multi["strategy_inclusion_decision"] == "blocked_for_simulated_allocation"
    assert multi["strategy_freeze_decision"] == "freeze_simulated_allocation"
    assert multi["strategy_real_trading_active_state_present"] is False
    assert multi["copy_to_real_account_allowed"] is False
    assert multi["simulation_only_label_preserved"] is True
