from __future__ import annotations

from pathlib import Path

from a_share_v21_test_utils import make_v21_paths, v21_json
from trading_core.equity_v21_data_source_benchmark_hardening.builder import run_a_share_v21_data_source_benchmark_hardening


def test_v21_index_constituent_review_does_not_infer_membership(tmp_path: Path) -> None:
    paths = make_v21_paths(tmp_path)
    result = run_a_share_v21_data_source_benchmark_hardening(paths=paths, simulation_only=True)
    constituents = v21_json(paths, "v21_index_constituent_source_result")

    assert result["index_constituent_source_result_generated"] is True
    assert constituents["index_constituent_source_result_generated"] is True
    assert constituents["fabricated_index_constituents"] is False
    assert constituents["membership_inferred_without_evidence"] is False
    assert constituents["constituent_based_claims_allowed"] is False
    assert constituents["survivorship_bias_warning"] is True
