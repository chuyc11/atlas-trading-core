from trading_core.equity_owner_readiness_gate.quality_gates import build_safe_action_quality_gate
from trading_core.equity_owner_readiness_gate.threshold_policy import build_owner_readiness_threshold_policy


def test_safe_action_quality_gate_rejects_automatic_and_trade_action():
    policy = build_owner_readiness_threshold_policy()
    failed = build_safe_action_quality_gate(safe={"automatic_action_count": 1, "forbidden_safe_action_hits": ["broker"], "safe_actions_not_trade_related": False}, policy=policy)
    assert "automatic_action_count_exceeded" in failed["blocking_reasons"]
    assert "forbidden_safe_action_detected" in failed["blocking_reasons"]
