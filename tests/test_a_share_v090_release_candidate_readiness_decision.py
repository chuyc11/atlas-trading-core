from tests.a_share_owner_closeout_review_test_utils import make_paths, seed_closeout_outputs, closeout_data


def test_v090_release_candidate_readiness_decision_consistent(tmp_path):
    paths = make_paths(tmp_path)
    seed_closeout_outputs(paths)
    decision = closeout_data(paths, "v090_release_candidate_readiness_decision.json")
    assert decision["decision"] == "ready_with_known_blocked_owner_readiness_state"
    assert decision["owner_readiness_remains_blocked"] is True
    assert decision["owner_operationally_acceptable"] is False
