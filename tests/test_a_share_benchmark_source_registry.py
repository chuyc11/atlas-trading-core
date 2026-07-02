from __future__ import annotations

from pathlib import Path

from a_share_benchmark_claim_hardening_test_utils import claim_json, make_claim_paths, write_claim_base_inputs
from trading_core.equity_benchmark_claim_hardening.builder import build_a_share_benchmark_claim_hardening


def test_benchmark_source_registry_generation_records_missing_csi_without_fabrication(tmp_path: Path) -> None:
    paths = make_claim_paths(tmp_path)
    write_claim_base_inputs(paths, with_index=False)

    result = build_a_share_benchmark_claim_hardening(paths=paths)
    registry = claim_json(paths, "benchmark_source_registry")
    csi = claim_json(paths, "csi_benchmark_attribution_result")

    assert result["benchmark_source_registry_generated"] is True
    assert {row["benchmark_id"] for row in registry["records"]} == {"CSI300", "CSI500", "CSI1000", "CASH", "EQUAL_WEIGHT_TRADABLE_UNIVERSE"}
    assert [row["available"] for row in registry["records"] if row["benchmark_id"].startswith("CSI")] == [False, False, False]
    assert csi["benchmark_relative_metrics_generated"] is False
    assert csi["fabricated_excess_return"] is False
    assert all(row["excess_return"] is None for row in csi["benchmarks"])


def test_benchmark_source_registry_marks_csi_usable_when_local_data_aligns(tmp_path: Path) -> None:
    paths = make_claim_paths(tmp_path)
    write_claim_base_inputs(paths, with_index=True)

    build_a_share_benchmark_claim_hardening(paths=paths)
    registry = claim_json(paths, "benchmark_source_registry")
    csi_rows = [row for row in registry["records"] if row["benchmark_id"].startswith("CSI")]

    assert all(row["available"] for row in csi_rows)
    assert all(row["usable_for_simulated_relative_metrics"] for row in csi_rows)
