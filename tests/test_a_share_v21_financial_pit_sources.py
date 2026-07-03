from __future__ import annotations

from pathlib import Path

from a_share_v21_test_utils import make_v21_paths, v21_json
from trading_core.equity_v21_data_source_benchmark_hardening.builder import run_a_share_v21_data_source_benchmark_hardening


def test_v21_financial_pit_source_review_blocks_visible_date_fabrication(tmp_path: Path) -> None:
    paths = make_v21_paths(tmp_path)
    result = run_a_share_v21_data_source_benchmark_hardening(paths=paths, simulation_only=True)
    financial = v21_json(paths, "v21_financial_statement_pit_result")

    assert result["financial_statement_pit_result_generated"] is True
    assert financial["fabricated_financial_pit_visibility"] is False
    assert financial["report_period_treated_as_visible_date"] is False
    assert financial["future_financial_features_used"] is False
    assert financial["trusted_model_claims_allowed"] is False
