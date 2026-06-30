from trading_core.equity_owner_readiness_gate.gate_decision import build_gate_decision
from trading_core.equity_owner_readiness_gate.threshold_policy import build_owner_readiness_threshold_policy


def test_gate_decision_consistency_and_blocked_state():
    policy = build_owner_readiness_threshold_policy()
    gates = {"score": {"passed": False, "blocking_reasons": ["owner_readiness_score_below_threshold"], "warnings": []}}
    decision = build_gate_decision(gates=gates, score={"score": 54, "grade": "D"}, policy=policy, exceptions=[])
    assert decision["decision"] == "blocked"
    assert decision["owner_operationally_acceptable"] is False
    assert decision["required_gates_passed"] is False
