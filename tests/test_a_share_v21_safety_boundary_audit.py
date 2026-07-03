from __future__ import annotations

from pathlib import Path

from a_share_v21_test_utils import make_v21_paths
from trading_core.equity_v21_data_source_benchmark_hardening.audit import audit_a_share_v21_data_source_benchmark_hardening
from trading_core.equity_v21_data_source_benchmark_hardening.builder import run_a_share_v21_data_source_benchmark_hardening


def test_v21_audit_passes_and_blocks_forbidden_order_preview(tmp_path: Path) -> None:
    paths = make_v21_paths(tmp_path)
    result = run_a_share_v21_data_source_benchmark_hardening(paths=paths, simulation_only=True)
    audit = audit_a_share_v21_data_source_benchmark_hardening(paths=paths)

    assert result["artifact_integrity_sweep_passed"] is True
    assert result["protected_path_sweep_passed"] is True
    assert result["safety_boundary_sweep_passed"] is True
    assert audit["overall_passed"] is True

    result_path = paths.data_dir / "equity_v21_data_source_benchmark_hardening" / "daily" / "2026-07-01" / "v21_data_source_benchmark_hardening_result.json"
    text = result_path.read_text(encoding="utf-8").replace('"real_order_preview_generated": false', '"real_order_preview_generated": true', 1)
    result_path.write_text(text, encoding="utf-8")

    blocked = audit_a_share_v21_data_source_benchmark_hardening(paths=paths)
    assert blocked["overall_passed"] is False
    assert "required_false_not_false:real_order_preview_generated" in blocked["blocking_reasons"]
