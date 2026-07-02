from __future__ import annotations

from pathlib import Path

from a_share_v11_test_utils import make_v11_paths, v11_json
from trading_core.equity_v11_owner_ops_platform.builder import run_a_share_v11_owner_ops_platform


def test_v11_rl_simulated_lab_governance_cannot_hit_real_account_or_order(tmp_path: Path) -> None:
    paths = make_v11_paths(tmp_path)
    result = run_a_share_v11_owner_ops_platform(paths=paths, simulation_only=True)
    rl = v11_json(paths, "v11_rl_simulated_lab_governance_result")

    assert result["rl_simulated_lab_governance_generated"] is True
    assert set(rl["allowed_action_targets"]) == {"rl_shadow_strategy", "rl_simulated_account", "rl_virtual_portfolio"}
    assert rl["baseline_policy_evaluation_generated"] is True
    assert rl["random_simple_policy_comparison_generated"] is True
    assert rl["risk_penalty_report_generated"] is True
    assert rl["transaction_cost_sensitivity_generated"] is True
    assert rl["rl_can_hit_real_account"] is False
    assert rl["rl_can_create_real_order"] is False
