from __future__ import annotations

from pathlib import Path

from a_share_v21_test_utils import make_v21_paths, v21_json
from trading_core.equity_v21_data_source_benchmark_hardening.builder import run_a_share_v21_data_source_benchmark_hardening


def test_v21_benchmark_source_depth_blocks_fabricated_relative_metrics(tmp_path: Path) -> None:
    paths = make_v21_paths(tmp_path)
    result = run_a_share_v21_data_source_benchmark_hardening(paths=paths, simulation_only=True)
    benchmark = v21_json(paths, "v21_benchmark_source_depth_result")

    assert result["benchmark_source_depth_result_generated"] is True
    assert benchmark["benchmark_source_depth_result_generated"] is True
    assert {item["benchmark"] for item in benchmark["benchmark_validations"]} == {"CSI300", "CSI500", "CSI1000", "BROAD_MARKET"}
    assert result["fabricated_benchmark_data"] is False
    assert result["fabricated_benchmark_relative_metrics"] is False
    assert result["benchmark_relative_claim_allowed"] is False
