from __future__ import annotations

from pathlib import Path

from a_share_v22_test_utils import make_v22_paths, v22_json
from trading_core.equity_v22_ensemble_meta_strategy.builder import run_a_share_v22_ensemble_meta_strategy


def test_v22_ensemble_validation_records_unavailable_oos_walkforward(tmp_path: Path) -> None:
    paths = make_v22_paths(tmp_path)
    result = run_a_share_v22_ensemble_meta_strategy(paths=paths, simulation_only=True)
    validation = v22_json(paths, "v22_ensemble_validation_result")

    assert result["ensemble_validation_result_generated"] is True
    assert validation["ensemble_oos_evaluation"] == "not_available_warning"
    assert validation["ensemble_walk_forward_evaluation"] == "not_available_warning"
    assert validation["validation_claims_live_effectiveness"] is False
    assert result["ensemble_oos_results_fabricated"] is False
    assert result["ensemble_walkforward_results_fabricated"] is False
