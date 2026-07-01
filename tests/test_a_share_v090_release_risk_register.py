from tests.a_share_owner_closeout_review_test_utils import make_paths, seed_closeout_outputs, closeout_data


def test_v090_release_risk_register_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_closeout_outputs(paths)
    register = closeout_data(paths, "v090_release_risk_register.json")
    categories = {risk["category"] for risk in register["risks"]}
    assert register["risk_count"] == 10
    assert "blocked_state_misinterpretation" in categories
