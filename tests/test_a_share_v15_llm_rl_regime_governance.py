from __future__ import annotations

from pathlib import Path

from a_share_v15_test_utils import make_v15_paths, v15_json
from trading_core.equity_v15_market_regime_lab.builder import run_a_share_v15_market_regime_lab


def test_v15_llm_rl_regime_governance_boundaries(tmp_path: Path) -> None:
    paths = make_v15_paths(tmp_path)
    result = run_a_share_v15_market_regime_lab(paths=paths, simulation_only=True)
    llm = v15_json(paths, "v15_llm_regime_governance_result")
    rl = v15_json(paths, "v15_rl_regime_governance_result")

    assert result["llm_regime_governance_generated"] is True
    assert llm["llm_proposal_generates_trade_instruction"] is False
    assert llm["llm_proposal_can_enter_simulated_active_directly"] is False
    assert result["rl_regime_governance_generated"] is True
    assert rl["rl_action_enters_simulated_layer_only"] is True
    assert rl["rl_action_reads_real_account"] is False
    assert rl["rl_action_creates_real_order"] is False
    assert rl["rl_action_generates_buy_sell_signal"] is False
