from __future__ import annotations

from pathlib import Path

from a_share_v13_test_utils import make_v13_paths, v13_json
from trading_core.equity_v09_platform.builder import BOUNDARY_FALSE, BOUNDARY_TRUE
from trading_core.equity_v13_research_quality_lab.audit import audit_a_share_v13_research_quality_lab
from trading_core.equity_v13_research_quality_lab.builder import JSON_NAMES, MARKDOWN_NAMES, run_a_share_v13_research_quality_lab


def test_v13_safety_boundary_and_audit(tmp_path: Path) -> None:
    paths = make_v13_paths(tmp_path)
    result = run_a_share_v13_research_quality_lab(paths=paths, simulation_only=True)
    audit = audit_a_share_v13_research_quality_lab(paths=paths)
    safety = v13_json(paths, "v13_safety_boundary_sweep")

    assert audit["overall_passed"] is True
    assert audit["artifact_checks"]["json_count"] == len(JSON_NAMES)
    assert audit["artifact_checks"]["markdown_count"] == len(MARKDOWN_NAMES)
    assert safety["safety_boundary_sweep_passed"] is True
    for key, expected in BOUNDARY_TRUE.items():
        assert result[key] is expected
    for key in BOUNDARY_FALSE:
        assert result[key] is False
    assert result["llm_proposals_are_trade_instructions"] is False
    assert result["rl_actions_are_real_account_actions"] is False
    assert result["rl_actions_are_real_orders"] is False
    assert result["strategy_real_trading_active_state_present"] is False
