from tests.a_share_operator_experience_test_utils import make_paths, operator_data, seed_operator_outputs


def test_known_blocked_state_explanation_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_operator_outputs(paths)
    explanation = operator_data(paths, "known_blocked_state_explanation.json")
    assert explanation["owner_readiness_state"] == "blocked"
    assert "broker connection" in explanation["what_is_not_allowed"]
