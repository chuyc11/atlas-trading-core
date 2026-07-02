from __future__ import annotations

from pathlib import Path

from a_share_v17_test_utils import make_v17_paths, v17_json
from trading_core.equity_v17_strategy_validation_lab.builder import run_a_share_v17_strategy_validation_lab


def test_v17_llm_rl_validation_cannot_create_trade_instruction(tmp_path: Path) -> None:
    paths = make_v17_paths(tmp_path)
    result = run_a_share_v17_strategy_validation_lab(paths=paths, simulation_only=True)
    llm_rl = v17_json(paths, "v17_llm_rl_validation_result")

    assert result["llm_rl_validation_result_generated"] is True
    assert llm_rl["llm_proposal_has_falsifiable_conditions"] is True
    assert llm_rl["rl_policy_action_boundary_check"] == "passed"
    assert llm_rl["llm_rl_validation_generates_trade_instruction"] is False
    assert llm_rl["llm_rl_validation_generates_buy_sell_signal"] is False
    assert llm_rl["llm_rl_validation_auto_escalates_authority"] is False
