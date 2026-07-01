from tests.a_share_final_closeout_test_utils import final_json, seed_v095_and_build_v096


def test_final_closeout_request_disallows_controlled_reevaluation(tmp_path):
    paths, _ = seed_v095_and_build_v096(tmp_path)
    request = final_json(paths, "closeout_request")

    assert request["expected_branch"] == "final_not_ready_closeout"
    assert request["allow_controlled_reevaluation_if_ready"] is False
    assert request["allow_owner_readiness_gate_rerun"] is False
    assert request["allow_new_gate_score"] is False
    assert request["allow_new_gate_decision"] is False
