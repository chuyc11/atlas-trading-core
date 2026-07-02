from __future__ import annotations

from pathlib import Path

from a_share_v17_test_utils import make_v17_paths, v17_json
from trading_core.equity_v17_strategy_validation_lab.builder import run_a_share_v17_strategy_validation_lab


def test_v17_experiment_validation_registry_governs_without_trade_instruction(tmp_path: Path) -> None:
    paths = make_v17_paths(tmp_path)
    result = run_a_share_v17_strategy_validation_lab(paths=paths, simulation_only=True)
    registry = v17_json(paths, "v17_experiment_validation_registry")

    assert result["experiment_validation_registry_generated"] is True
    assert registry["experiment_count"] == 3
    assert registry["experiment_duplication_detection"] == "passed"
    assert registry["experiment_auto_changes_simulated_active"] is False
    assert registry["experiment_generates_trade_instruction"] is False
    assert registry["experiment_enters_real_account"] is False
    assert registry["research_only"] is True
