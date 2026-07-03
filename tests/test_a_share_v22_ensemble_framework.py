from __future__ import annotations

from pathlib import Path

from a_share_v22_test_utils import make_v22_paths, v22_json
from trading_core.equity_v22_ensemble_meta_strategy.builder import run_a_share_v22_ensemble_meta_strategy


def test_v22_ensemble_framework_baseline_and_boundaries(tmp_path: Path) -> None:
    paths = make_v22_paths(tmp_path)
    result = run_a_share_v22_ensemble_meta_strategy(paths=paths, simulation_only=True)
    framework = v22_json(paths, "v22_ensemble_research_framework_result")

    assert result["v21_baseline_verified"] is True
    assert result["ensemble_research_framework_generated"] is True
    assert framework["ensemble_type_taxonomy"]
    assert framework["trust_decision_is_owner_readiness_gate_decision"] is False
    assert framework["live_trading_ready_claimed"] is False
    assert result["ensemble_outputs_are_trade_signals"] is False
