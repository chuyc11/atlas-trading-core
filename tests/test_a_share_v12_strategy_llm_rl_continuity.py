from __future__ import annotations

from pathlib import Path

from a_share_v12_test_utils import make_v12_paths, v12_json
from trading_core.equity_v12_continuous_ops.builder import run_a_share_v12_continuous_ops


def test_v12_strategy_llm_rl_and_shadow_canary_continuity(tmp_path: Path) -> None:
    paths = make_v12_paths(tmp_path)
    result = run_a_share_v12_continuous_ops(paths=paths, simulation_only=True)
    strategy = v12_json(paths, "v12_strategy_governance_continuity_result")
    llm_rl = v12_json(paths, "v12_llm_rl_continuous_governance_result")

    assert result["strategy_governance_continuity_generated"] is True
    assert result["llm_rl_continuous_governance_generated"] is True
    assert strategy["strategy_registry_connected"] is True
    assert strategy["experiment_registry_connected"] is True
    assert strategy["real_trading_active_allowed"] is False
    assert strategy["simulated_promotion_generates_real_buy_sell_signal"] is False
    assert llm_rl["llm_proposal_can_modify_simulated_active_directly"] is False
    assert llm_rl["rl_action_can_hit_real_account"] is False
    assert llm_rl["rl_action_can_create_real_order"] is False
