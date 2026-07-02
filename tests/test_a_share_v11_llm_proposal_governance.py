from __future__ import annotations

from pathlib import Path

from a_share_v11_test_utils import make_v11_paths, v11_json
from trading_core.equity_v11_owner_ops_platform.builder import run_a_share_v11_owner_ops_platform


def test_v11_llm_proposal_governance_blocks_direct_strategy_and_trade_instruction(tmp_path: Path) -> None:
    paths = make_v11_paths(tmp_path)
    result = run_a_share_v11_owner_ops_platform(paths=paths, simulation_only=True)
    llm = v11_json(paths, "v11_llm_proposal_governance_result")

    assert result["llm_proposal_governance_generated"] is True
    assert set(["hypothesis", "risk_note", "expected_effect", "required_data", "experiment_plan"]).issubset(llm["required_fields"])
    assert llm["can_modify_active_simulated_strategy_directly"] is False
    assert llm["can_generate_trade_instruction"] is False
    assert llm["must_pass_experiment_runner_before_strategy_candidate"] is True
