from __future__ import annotations

from pathlib import Path

from a_share_v22_test_utils import make_v22_paths
from trading_core.equity_v22_ensemble_meta_strategy.audit import audit_a_share_v22_ensemble_meta_strategy
from trading_core.equity_v22_ensemble_meta_strategy.builder import run_a_share_v22_ensemble_meta_strategy


def test_v22_audit_passes_and_blocks_real_account_mutation(tmp_path: Path) -> None:
    paths = make_v22_paths(tmp_path)
    result = run_a_share_v22_ensemble_meta_strategy(paths=paths, simulation_only=True)
    audit = audit_a_share_v22_ensemble_meta_strategy(paths=paths)

    assert result["artifact_integrity_sweep_passed"] is True
    assert result["protected_path_sweep_passed"] is True
    assert result["safety_boundary_sweep_passed"] is True
    assert audit["overall_passed"] is True

    result_path = paths.data_dir / "equity_v22_ensemble_meta_strategy" / "daily" / "2026-07-01" / "v22_ensemble_meta_strategy_result.json"
    text = result_path.read_text(encoding="utf-8").replace('"real_account_data_read": false', '"real_account_data_read": true', 1)
    result_path.write_text(text, encoding="utf-8")
    blocked = audit_a_share_v22_ensemble_meta_strategy(paths=paths)
    assert blocked["overall_passed"] is False
    assert "required_false_not_false:real_account_data_read" in blocked["blocking_reasons"]
