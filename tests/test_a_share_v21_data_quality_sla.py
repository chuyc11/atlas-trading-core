from __future__ import annotations

from pathlib import Path

from a_share_v21_test_utils import make_v21_paths, v21_json
from trading_core.equity_v21_data_source_benchmark_hardening.builder import run_a_share_v21_data_source_benchmark_hardening


def test_v21_data_quality_sla_is_not_owner_readiness_or_live_ready(tmp_path: Path) -> None:
    paths = make_v21_paths(tmp_path)
    result = run_a_share_v21_data_source_benchmark_hardening(paths=paths, simulation_only=True)
    sla = v21_json(paths, "v21_data_quality_sla_result")

    assert result["data_quality_sla_result_generated"] is True
    assert sla["data_quality_sla_result_generated"] is True
    assert sla["data_quality_score_is_owner_readiness_score"] is False
    assert sla["data_quality_pass_means_live_trading_ready"] is False
    assert result["data_quality_score_is_owner_readiness_score"] is False
    assert result["data_quality_pass_means_live_trading_ready"] is False
