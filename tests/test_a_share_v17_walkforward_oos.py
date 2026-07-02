from __future__ import annotations

from pathlib import Path

from a_share_v17_test_utils import make_v17_paths, v17_json
from trading_core.equity_v17_strategy_validation_lab.builder import run_a_share_v17_strategy_validation_lab


def test_v17_walkforward_oos_outputs_watch_only_evaluation(tmp_path: Path) -> None:
    paths = make_v17_paths(tmp_path)
    result = run_a_share_v17_strategy_validation_lab(paths=paths, simulation_only=True)
    oos = v17_json(paths, "v17_walkforward_oos_evaluation_result")

    assert result["walkforward_oos_evaluation_result_generated"] is True
    assert oos["walk_forward_window_register_generated"] is True
    assert oos["walk_forward_result_matrix_generated"] is True
    assert oos["oos_result_matrix_generated"] is True
    assert oos["oos_pass_fail_decision"] == "watch_with_limitations"
    assert oos["oos_results_fabricated"] is False
    assert oos["owner_facing_oos_report_generated"] is True
