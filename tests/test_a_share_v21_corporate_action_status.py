from __future__ import annotations

from pathlib import Path

from a_share_v21_test_utils import make_v21_paths, v21_json
from trading_core.equity_v21_data_source_benchmark_hardening.builder import run_a_share_v21_data_source_benchmark_hardening


def test_v21_corporate_action_adjusted_price_and_status_reviews(tmp_path: Path) -> None:
    paths = make_v21_paths(tmp_path)
    result = run_a_share_v21_data_source_benchmark_hardening(paths=paths, simulation_only=True)
    corporate = v21_json(paths, "v21_corporate_action_adjusted_price_result")
    status = v21_json(paths, "v21_suspension_delisting_st_status_result")

    assert result["corporate_action_adjusted_price_result_generated"] is True
    assert result["suspension_delisting_st_status_result_generated"] is True
    assert corporate["fabricated_corporate_action"] is False
    assert corporate["raw_adjusted_prices_silently_mixed"] is False
    assert status["fabricated_suspension_delisting_st_status"] is False
    assert status["pit_status_warning"] is True
