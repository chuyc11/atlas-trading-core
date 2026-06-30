from trading_core.equity_owner_readiness_gate.quality_gates import build_trend_sufficiency_quality_gate
from trading_core.equity_owner_readiness_gate.threshold_policy import build_owner_readiness_threshold_policy


def test_insufficient_history_allowed_only_if_correctly_flagged():
    policy = build_owner_readiness_threshold_policy()
    gate = build_trend_sufficiency_quality_gate(sufficiency={"trend_analysis_available": False, "insufficient_history_correctly_flagged": True}, policy=policy)
    assert gate["passed"] is True
    failed = build_trend_sufficiency_quality_gate(sufficiency={"trend_analysis_available": False, "insufficient_history_correctly_flagged": False}, policy=policy)
    assert failed["passed"] is False
