from __future__ import annotations

from pathlib import Path

from a_share_v23_test_utils import make_v23_paths, v23_json
from trading_core.equity_v23_operator_ux_journal.audit import audit_a_share_v23_operator_ux_journal
from trading_core.equity_v23_operator_ux_journal.builder import run_a_share_v23_operator_ux_journal


def test_v23_sweeps_and_audit_pass_then_fail_on_real_order_flag(tmp_path: Path) -> None:
    paths = make_v23_paths(tmp_path)
    result = run_a_share_v23_operator_ux_journal(paths=paths, simulation_only=True)
    audit = audit_a_share_v23_operator_ux_journal(paths=paths)

    assert result["artifact_integrity_sweep_passed"] is True
    assert result["protected_path_sweep_passed"] is True
    assert result["safety_boundary_sweep_passed"] is True
    assert result["full_pytest_run"] is False
    assert audit["overall_passed"] is True

    result_path = paths.data_dir / "equity_v23_operator_ux_journal" / "daily" / "2026-07-01" / "v23_operator_ux_journal_result.json"
    text = result_path.read_text(encoding="utf-8").replace('"real_orders_placed": false', '"real_orders_placed": true', 1)
    result_path.write_text(text, encoding="utf-8")
    blocked = audit_a_share_v23_operator_ux_journal(paths=paths)
    assert blocked["overall_passed"] is False
    assert "required_false_not_false:real_orders_placed" in blocked["blocking_reasons"]


def test_v23_ux_safety_sweep_reports_no_hard_wording_hits(tmp_path: Path) -> None:
    paths = make_v23_paths(tmp_path)
    run_a_share_v23_operator_ux_journal(paths=paths, simulation_only=True)
    sweep = v23_json(paths, "v23_ux_safety_boundary_sweep")

    assert sweep["ux_safety_boundary_sweep_generated"] is True
    assert sweep["hard_boundary_wording_hits"] == []
    assert sweep["safety_boundary_sweep_passed"] is True
