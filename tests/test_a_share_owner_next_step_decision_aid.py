from tests.a_share_operator_experience_test_utils import make_paths, operator_data, seed_operator_outputs


def test_owner_next_step_decision_aid_excludes_trading_actions(tmp_path):
    paths = make_paths(tmp_path)
    seed_operator_outputs(paths)
    aid = operator_data(paths, "owner_next_step_decision_aid.json")
    forbidden = {row["step_id"]: row for row in aid["forbidden_next_steps"]}
    assert forbidden["place_order"]["allowed"] is False
    assert aid["recommended_next_step"] == "review_known_blocked_state"
