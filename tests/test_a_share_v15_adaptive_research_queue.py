from __future__ import annotations

from pathlib import Path

from a_share_v15_test_utils import make_v15_paths, v15_json
from trading_core.equity_v15_market_regime_lab.builder import run_a_share_v15_market_regime_lab


def test_v15_adaptive_research_queue_cannot_trade(tmp_path: Path) -> None:
    paths = make_v15_paths(tmp_path)
    result = run_a_share_v15_market_regime_lab(paths=paths, simulation_only=True)
    queue = v15_json(paths, "v15_adaptive_research_queue_result")

    assert result["adaptive_research_queue_generated"] is True
    assert queue["experiment_registry_written"] is True
    assert queue["priority_directly_modifies_active_strategy"] is False
    assert queue["adaptive_queue_generates_trade_instruction"] is False
    assert result["adaptive_queue_generates_trade_instruction"] is False
