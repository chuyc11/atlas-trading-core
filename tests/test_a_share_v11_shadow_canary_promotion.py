from __future__ import annotations

from pathlib import Path

from a_share_v11_test_utils import make_v11_paths, v11_json
from trading_core.equity_v11_owner_ops_platform.builder import run_a_share_v11_owner_ops_platform


def test_v11_shadow_canary_promotion_rejection_rollback_workflows(tmp_path: Path) -> None:
    paths = make_v11_paths(tmp_path)
    result = run_a_share_v11_owner_ops_platform(paths=paths, simulation_only=True)
    shadow = v11_json(paths, "v11_shadow_canary_lifecycle_result")
    promotion = v11_json(paths, "v11_strategy_promotion_rejection_rollback_result")

    assert result["shadow_canary_lifecycle_generated"] is True
    assert shadow["state_machine"] == ["research_candidate", "backtest_passed", "shadow", "simulated_canary", "simulated_active"]
    assert shadow["simulated_canary_allocation_record_generated"] is True
    assert shadow["real_trading_active_allowed"] is False
    assert promotion["promotion_rejection_rollback_workflow_generated"] is True
    assert promotion["rollback_workflow_generated"] is True
    assert promotion["cooldown_workflow_generated"] is True
