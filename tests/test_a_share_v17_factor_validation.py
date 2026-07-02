from __future__ import annotations

from pathlib import Path

from a_share_v17_test_utils import make_v17_paths, v17_json
from trading_core.equity_v17_strategy_validation_lab.builder import run_a_share_v17_strategy_validation_lab


def test_v17_factor_validation_records_unavailable_ic_without_fabrication(tmp_path: Path) -> None:
    paths = make_v17_paths(tmp_path)
    result = run_a_share_v17_strategy_validation_lab(paths=paths, simulation_only=True)
    factor = v17_json(paths, "v17_factor_validation_result")

    assert result["factor_validation_result_generated"] is True
    assert factor["factor_missingness_check"]["status"] == "passed"
    assert factor["factor_stability_check"] == "not_available_without_factor_panel"
    assert factor["factor_drift_check"] == "not_available_without_factor_panel"
    assert factor["ic_status"] == "not_available"
    assert factor["rank_ic_status"] == "not_available"
    assert factor["factor_results_fabricated"] is False
    assert factor["ic_results_fabricated"] is False
    assert factor["factor_t_stat"]["used_as_real_result"] is False
