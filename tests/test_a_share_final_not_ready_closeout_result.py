from tests.a_share_final_closeout_test_utils import final_json, seed_v095_and_build_v096


def test_final_not_ready_result_preserves_blocked_state(tmp_path):
    paths, result = seed_v095_and_build_v096(tmp_path)
    closeout = final_json(paths, "final_not_ready_closeout_result")

    assert result["overall_passed"] is True
    assert closeout["selected_branch"] == "final_not_ready_closeout"
    assert closeout["final_closeout_decision"] == "not_ready_additional_evidence_required"
    assert closeout["owner_readiness_final_state"] == "blocked"
    assert closeout["source_readiness_score"] == 54
    assert closeout["minimum_owner_readiness_score"] == 75
    assert closeout["score_gap"] == 21
    assert closeout["controlled_reevaluation_executed"] is False
    assert closeout["new_gate_score_generated"] is False
    assert closeout["new_gate_decision_generated"] is False
