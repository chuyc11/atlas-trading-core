from __future__ import annotations

from pathlib import Path

from a_share_v13_test_utils import make_v13_paths, v13_json
from trading_core.equity_v13_research_quality_lab.builder import run_a_share_v13_research_quality_lab


def test_v13_shadow_canary_quality_gates(tmp_path: Path) -> None:
    paths = make_v13_paths(tmp_path)
    result = run_a_share_v13_research_quality_lab(paths=paths, simulation_only=True)
    gates = v13_json(paths, "v13_shadow_canary_quality_gate_result")

    assert result["shadow_canary_quality_gate_result_generated"] is True
    assert result["strategy_promotion_hard_gate_generated"] is True
    assert result["strategy_rejection_hard_gate_generated"] is True
    assert result["strategy_rollback_gate_generated"] is True
    assert gates["promotion_decision"] == "blocked"
    assert gates["real_trading_promotion"] is False
