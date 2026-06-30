from tests.a_share_owner_readiness_gate_test_utils import make_paths, seed_owner_readiness_gate_inputs
from trading_core.equity_owner_readiness_gate.gate_builder import build_a_share_owner_readiness_gate
from trading_core.equity_owner_readiness_gate.owner_readiness_gate_audit import audit_a_share_owner_readiness_gate


def test_owner_readiness_gate_audit_passes_for_correct_blocked_state(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_readiness_gate_inputs(paths)
    build_a_share_owner_readiness_gate(paths=paths, minimum_owner_readiness_score=100)
    audit = audit_a_share_owner_readiness_gate(paths=paths)
    assert audit["overall_passed"] is True
    assert audit["gate_checks"]["decision"] == "blocked"
    assert audit["gate_checks"]["blocked_state_represented_correctly"] is True


def test_owner_readiness_gate_audit_fails_when_decision_inconsistent(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_readiness_gate_inputs(paths)
    build_a_share_owner_readiness_gate(paths=paths, minimum_owner_readiness_score=100)
    decision_path = paths.data_dir / "equity_owner_readiness_gate" / "daily" / "2026-06-26" / "owner_readiness_gate_decision.json"
    import json

    payload = json.loads(decision_path.read_text(encoding="utf-8"))
    payload["decision"] = "owner_operationally_acceptable"
    decision_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    audit = audit_a_share_owner_readiness_gate(paths=paths)
    assert audit["overall_passed"] is False
    assert "gate_decision_consistent" in audit["blocking_reasons"]
