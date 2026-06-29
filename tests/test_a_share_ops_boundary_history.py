from trading_core.equity_ops_history.boundary_history import build_ops_boundary_history_snapshot


def test_ops_boundary_history_keeps_protected_flags_false():
    snapshot = build_ops_boundary_history_snapshot(as_of_date="2026-06-26", ops_boundary={"overall_passed": True, "broker_connected": False})
    row = snapshot["records"][0]
    assert row["boundary_clean"] is True
    assert row["broker_connected"] is False
    assert row["real_orders_placed"] is False

