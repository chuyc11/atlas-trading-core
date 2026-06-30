from trading_core.equity_owner_readiness_gate.quality_gates import build_boundary_quality_gate
from trading_core.equity_owner_readiness_gate.threshold_policy import build_owner_readiness_threshold_policy


def test_boundary_violation_blocks_gate():
    gate = build_boundary_quality_gate(boundary={"boundary_clean": False, "boundary_trend_clean": False}, policy=build_owner_readiness_threshold_policy())
    assert gate["passed"] is False
    assert "boundary_not_clean" in gate["blocking_reasons"]
