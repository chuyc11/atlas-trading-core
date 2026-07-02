from __future__ import annotations

from pathlib import Path

from a_share_v12_test_utils import make_v12_paths, v12_json
from trading_core.equity_v12_continuous_ops.builder import run_a_share_v12_continuous_ops


def test_v12_benchmark_claim_guard_continuity_blocks_unsupported_claims(tmp_path: Path) -> None:
    paths = make_v12_paths(tmp_path)
    result = run_a_share_v12_continuous_ops(paths=paths, simulation_only=True)
    benchmark = v12_json(paths, "v12_benchmark_claim_guard_continuity_result")

    assert result["benchmark_claim_guard_continuity_generated"] is True
    assert benchmark["cash_benchmark_assumption_history"] == "zero_return_cash_baseline"
    assert benchmark["equal_weight_universe_coverage_history"] == 1.0
    assert benchmark["benchmark_relative_claim_allowed"] is False
    assert benchmark["real_performance_claim_allowed"] is False
    assert benchmark["unsupported_benchmark_relative_claim_blocked"] is True
    assert benchmark["fabricated_excess_return"] is False
    assert benchmark["fabricated_tracking_error"] is False
    assert benchmark["fabricated_relative_drawdown"] is False
    assert benchmark["owner_dashboard_claim_guard_status_visible"] is True
