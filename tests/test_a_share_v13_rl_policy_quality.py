from __future__ import annotations

from pathlib import Path

from a_share_v13_test_utils import make_v13_paths, v13_json
from trading_core.equity_v13_research_quality_lab.builder import run_a_share_v13_research_quality_lab


def test_v13_rl_policy_quality_review_is_simulation_only(tmp_path: Path) -> None:
    paths = make_v13_paths(tmp_path)
    result = run_a_share_v13_research_quality_lab(paths=paths, simulation_only=True)
    rl = v13_json(paths, "v13_rl_policy_quality_result")

    assert result["rl_policy_quality_result_generated"] is True
    assert result["rl_actions_are_real_account_actions"] is False
    assert result["rl_actions_are_real_orders"] is False
    assert rl["reward_hacking_warning_recorded"] is True
    assert rl["decision"] == "quality_blocked_for_research_review"
