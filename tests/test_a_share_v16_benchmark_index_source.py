from __future__ import annotations

from pathlib import Path

from a_share_v16_test_utils import make_v16_paths, v16_json
from trading_core.equity_v16_pit_backtest_market_rules.builder import run_a_share_v16_pit_backtest_market_rules


def test_v16_benchmark_index_source_hardening(tmp_path: Path) -> None:
    paths = make_v16_paths(tmp_path)
    result = run_a_share_v16_pit_backtest_market_rules(paths=paths, simulation_only=True)
    benchmark = v16_json(paths, "v16_benchmark_index_source_result")

    assert result["benchmark_index_source_result_generated"] is True
    assert result["benchmark_index_data_fabricated"] is False
    assert benchmark["source_registry_hardened"] is True
    assert benchmark["missing_index_data_behavior"] == "block_benchmark_relative_claims"
    assert benchmark["benchmark_claim_guard_integrated"] is True
