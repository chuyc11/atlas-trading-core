from __future__ import annotations

from pathlib import Path

from a_share_v21_test_utils import make_v21_paths, v21_json
from trading_core.equity_v21_data_source_benchmark_hardening.builder import run_a_share_v21_data_source_benchmark_hardening


def test_v21_benchmark_claim_guard_blocks_real_and_unsupported_claims(tmp_path: Path) -> None:
    paths = make_v21_paths(tmp_path)
    result = run_a_share_v21_data_source_benchmark_hardening(paths=paths, simulation_only=True)
    guard = v21_json(paths, "v21_benchmark_claim_guard_rehardening_result")

    assert result["benchmark_claim_guard_rehardening_result_generated"] is True
    assert guard["claim_guard_audit_generated"] is True
    assert guard["benchmark_relative_claim_allowed"] is False
    assert guard["real_performance_claim_allowed"] is False
    assert guard["live_trading_claim_allowed"] is False
    assert guard["investment_advice_claim_allowed"] is False
    assert guard["fabricated_benchmark_relative_metrics"] is False
