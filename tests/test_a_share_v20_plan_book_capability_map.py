from __future__ import annotations

from pathlib import Path

from a_share_v20_test_utils import make_v20_paths, v20_json
from trading_core.equity_v20_platform_closeout.builder import run_a_share_v20_platform_closeout


def test_v20_plan_book_capability_map_p0_to_p5(tmp_path: Path) -> None:
    paths = make_v20_paths(tmp_path)
    result = run_a_share_v20_platform_closeout(paths=paths, simulation_only=True)
    capability = v20_json(paths, "v20_plan_book_capability_map")

    assert result["plan_book_capability_map_generated"] is True
    assert result["plan_book_p0_trusted_research_status"] == "complete_or_partial_with_limitations"
    assert result["plan_book_p1_strategy_validation_status"] == "complete_or_partial_with_limitations"
    assert result["plan_book_p2_portfolio_risk_status"] == "complete_or_partial_with_limitations"
    assert result["plan_book_p3_ml_research_status"] == "complete_or_partial_with_limitations"
    assert result["plan_book_p4_llm_governance_status"] == "complete_or_partial_with_limitations"
    assert result["plan_book_p5_rl_autonomous_simulation_status"] == "complete_or_partial_with_limitations"
    assert {item["phase"] for item in capability["plan_book_capabilities"]} == {"P0", "P1", "P2", "P3", "P4", "P5"}
