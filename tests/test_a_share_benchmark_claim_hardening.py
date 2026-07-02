from __future__ import annotations

from pathlib import Path

from a_share_benchmark_claim_hardening_test_utils import claim_json, make_claim_paths, write_claim_base_inputs
from trading_core.equity_benchmark_claim_hardening.builder import build_a_share_benchmark_claim_hardening


def test_cash_benchmark_uses_explicit_zero_return_assumption(tmp_path: Path) -> None:
    paths = make_claim_paths(tmp_path)
    write_claim_base_inputs(paths)

    build_a_share_benchmark_claim_hardening(paths=paths)
    cash = claim_json(paths, "cash_benchmark_result")

    assert cash["status"] == "passed"
    assert cash["cash_return_model"] == "zero_return_cash_baseline"
    assert cash["simulation_comparison_only"] is True
    assert cash["not_real_risk_free_rate"] is True
    assert {row["daily_return"] for row in cash["records"]} == {0.0}


def test_equal_weight_benchmark_constructs_from_local_universe_returns(tmp_path: Path) -> None:
    paths = make_claim_paths(tmp_path)
    write_claim_base_inputs(paths, with_prices=True)

    result = build_a_share_benchmark_claim_hardening(paths=paths)
    equal_weight = claim_json(paths, "equal_weight_universe_benchmark_result")

    assert result["equal_weight_universe_benchmark_status"] == "passed"
    assert equal_weight["checks"]["universe_source_exists"] is True
    assert equal_weight["checks"]["price_data_exists"] is True
    assert equal_weight["checks"]["return_data_exists"] is True
    assert equal_weight["checks"]["constituent_count"] == 2
    assert equal_weight["checks"]["survivorship_bias_warning"] is True
    assert equal_weight["records"]


def test_equal_weight_benchmark_warns_on_insufficient_local_data(tmp_path: Path) -> None:
    paths = make_claim_paths(tmp_path)
    write_claim_base_inputs(paths, with_prices=False)

    result = build_a_share_benchmark_claim_hardening(paths=paths)
    equal_weight = claim_json(paths, "equal_weight_universe_benchmark_result")

    assert result["equal_weight_universe_benchmark_status"] == "warning"
    assert equal_weight["checks"]["price_data_exists"] is False
    assert equal_weight["records"] == []


def test_csi_benchmark_attribution_passes_when_local_index_data_exists(tmp_path: Path) -> None:
    paths = make_claim_paths(tmp_path)
    write_claim_base_inputs(paths, with_index=True)

    result = build_a_share_benchmark_claim_hardening(paths=paths)
    csi = claim_json(paths, "csi_benchmark_attribution_result")

    assert result["csi300_benchmark_status"] == "passed"
    assert csi["benchmark_relative_metrics_generated"] is True
    assert all(row["benchmark_relative_metrics_generated"] for row in csi["benchmarks"])
    assert all(row["tracking_error"] is not None for row in csi["benchmarks"])


def test_owner_facing_report_includes_limitations(tmp_path: Path) -> None:
    paths = make_claim_paths(tmp_path)
    write_claim_base_inputs(paths)

    build_a_share_benchmark_claim_hardening(paths=paths)
    report = (
        paths.outputs_dir
        / "equity_benchmark_claim_hardening"
        / "daily"
        / "2026-07-01"
        / "A_SHARE_BENCHMARK_AND_CLAIM_HARDENING_REPORT.md"
    ).read_text(encoding="utf-8")

    assert "不是实盘交易证据" in report
    assert "owner-readiness" in report
