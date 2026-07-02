from __future__ import annotations

import json
from pathlib import Path

from a_share_v12_test_utils import make_v12_paths, v12_daily_dir, v12_json
from trading_core.equity_v12_continuous_ops.audit import audit_a_share_v12_continuous_ops
from trading_core.equity_v12_continuous_ops.builder import run_a_share_v12_continuous_ops


def test_v12_safety_boundary_sweep_and_no_real_paths(tmp_path: Path) -> None:
    paths = make_v12_paths(tmp_path)
    result = run_a_share_v12_continuous_ops(paths=paths, simulation_only=True)
    safety = v12_json(paths, "v12_safety_boundary_sweep")

    assert result["safety_boundary_sweep_passed"] is True
    assert safety["silent_scheduler_installation"] is False
    assert safety["external_notifications_sent"] is False
    assert safety["broker_connected"] is False
    assert safety["real_account_data_read"] is False
    assert safety["real_orders_placed"] is False
    assert safety["real_order_preview_generated"] is False
    assert safety["buy_sell_signals_generated"] is False


def test_v12_audit_passes_and_catches_boundary_failure(tmp_path: Path) -> None:
    paths = make_v12_paths(tmp_path)
    run_a_share_v12_continuous_ops(paths=paths, simulation_only=True)
    assert audit_a_share_v12_continuous_ops(paths=paths)["overall_passed"] is True
    path = v12_daily_dir(paths) / "v12_continuous_ops_run_result.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["real_orders_placed"] = True
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    audit = audit_a_share_v12_continuous_ops(paths=paths)

    assert audit["overall_passed"] is False
    assert "forbidden_boundary_true:real_orders_placed" in audit["blocking_reasons"]
