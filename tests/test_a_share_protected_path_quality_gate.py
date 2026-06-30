from trading_core.equity_owner_readiness_gate.quality_gates import build_protected_path_quality_gate
from trading_core.equity_owner_readiness_gate.threshold_policy import build_owner_readiness_threshold_policy


def test_protected_path_modification_blocks_gate():
    gate = build_protected_path_quality_gate(protected={"protected_path_modifications_detected": True, "protected_path_trend_clean": False}, policy=build_owner_readiness_threshold_policy())
    assert gate["passed"] is False
    assert "protected_path_modifications_detected" in gate["blocking_reasons"]
