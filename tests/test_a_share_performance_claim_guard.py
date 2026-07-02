from __future__ import annotations

from pathlib import Path

from a_share_benchmark_claim_hardening_test_utils import claim_json, make_claim_paths, write_claim_base_inputs
from trading_core.equity_benchmark_claim_hardening.builder import build_a_share_benchmark_claim_hardening


def test_performance_claim_guard_blocks_real_live_and_advice_claims(tmp_path: Path) -> None:
    paths = make_claim_paths(tmp_path)
    write_claim_base_inputs(paths)

    result = build_a_share_benchmark_claim_hardening(paths=paths)
    guard = claim_json(paths, "performance_claim_guard_result")

    assert result["real_performance_claim_allowed"] is False
    assert guard["real_performance_claim_allowed"] is False
    assert guard["live_trading_claim_allowed"] is False
    assert guard["investment_advice_claim_allowed"] is False


def test_performance_claim_guard_blocks_unverified_benchmark_relative_claims(tmp_path: Path) -> None:
    paths = make_claim_paths(tmp_path)
    write_claim_base_inputs(paths, with_index=False)

    result = build_a_share_benchmark_claim_hardening(paths=paths)
    guard = claim_json(paths, "performance_claim_guard_result")

    assert result["benchmark_relative_claim_allowed"] is False
    assert guard["benchmark_relative_claim_allowed"] is False
    assert any(row["category"] == "blocked_unverified_benchmark_claim" and row["allowed"] is False for row in guard["classifications"])


def test_simulation_only_performance_text_allowed_with_disclaimer(tmp_path: Path) -> None:
    paths = make_claim_paths(tmp_path)
    write_claim_base_inputs(paths)

    result = build_a_share_benchmark_claim_hardening(paths=paths)
    guard = claim_json(paths, "performance_claim_guard_result")

    assert result["simulated_performance_claim_allowed_with_disclaimer"] is True
    assert guard["simulation_only_disclaimer_required"] is True
    assert guard["simulated_performance_claim_allowed_with_disclaimer"] is True
