from tests.a_share_historical_backfill_test_utils import build_v097, closeout_json, seed_v096_with_historical_inputs


def test_go_no_go_after_historical_backfill_is_not_owner_gate_decision(tmp_path, monkeypatch):
    paths = seed_v096_with_historical_inputs(tmp_path)
    build_v097(paths, monkeypatch)
    decision = closeout_json(paths, "go_no_go_after_backfill")
    precheck = closeout_json(paths, "reevaluation_readiness_precheck")

    assert decision["decision"] == "no_go_additional_evidence_required"
    assert decision["decision_type"] == "future_controlled_reevaluation_prep_decision"
    assert decision["not_owner_readiness_gate_decision"] is True
    assert decision["owner_readiness_gate_executed"] is False
    assert decision["controlled_reevaluation_executed"] is False
    assert decision["new_gate_score_generated"] is False
    assert decision["new_gate_decision_generated"] is False
    assert precheck["precheck_status"] == "not_ready"
