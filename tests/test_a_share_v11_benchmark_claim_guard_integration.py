from __future__ import annotations

from pathlib import Path

from a_share_v11_test_utils import make_v11_paths, v11_json
from trading_core.equity_v11_owner_ops_platform.builder import run_a_share_v11_owner_ops_platform


def test_v11_benchmark_claim_guard_integrates_v101_state(tmp_path: Path) -> None:
    paths = make_v11_paths(tmp_path)
    result = run_a_share_v11_owner_ops_platform(paths=paths, simulation_only=True)
    benchmark = v11_json(paths, "v11_benchmark_claim_guard_integration_result")

    assert result["benchmark_claim_guard_integrated"] is True
    assert benchmark["cash_benchmark_assumption"] == "zero_return_cash_baseline"
    assert benchmark["equal_weight_universe_coverage"] == 1.0
    assert set(benchmark["csi_availability"]) == {"CSI300", "CSI500", "CSI1000"}
    assert benchmark["benchmark_missing_warning_generated"] is True
    assert benchmark["markdown_text_guarded"] is True
