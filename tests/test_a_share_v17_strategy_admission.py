from __future__ import annotations

from pathlib import Path

from a_share_v17_test_utils import make_v17_paths, v17_json
from trading_core.equity_v17_strategy_validation_lab.builder import run_a_share_v17_strategy_validation_lab


def test_v17_strategy_admission_is_simulation_only_watch(tmp_path: Path) -> None:
    paths = make_v17_paths(tmp_path)
    result = run_a_share_v17_strategy_validation_lab(paths=paths, simulation_only=True)
    admission = v17_json(paths, "v17_strategy_admission_decision_result")

    assert result["strategy_admission_decision_result_generated"] is True
    assert admission["admission_decision"] == "simulation_only_watch"
    assert admission["strategy_real_trading_active_state_present"] is False
    assert admission["strategy_admission_generates_real_trade"] is False
    assert admission["real_trading_active"] is False
    assert admission["watch_reason"]
    assert admission["rejection_reason"] is None
