from trading_core.equity_owner_readiness_gate.quality_gates import build_owner_next_step_quality_gate


def test_owner_next_step_gate_excludes_trade_categories():
    gate = build_owner_next_step_quality_gate(next_step={"forbidden_next_step_hits": ["place_order"], "owner_next_steps_not_trade_related": False})
    assert gate["passed"] is False
    assert "forbidden_owner_next_step_detected" in gate["blocking_reasons"]
