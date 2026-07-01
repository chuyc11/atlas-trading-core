from tests.a_share_owner_closeout_review_test_utils import make_paths, seed_closeout_outputs, closeout_data


def test_unresolved_blocker_register_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_closeout_outputs(paths)
    register = closeout_data(paths, "unresolved_blocker_register.json")
    categories = {item["category"] for item in register["blockers"]}
    assert register["unresolved_blocker_count"] == 7
    assert "v090_rc_known_blocked_state" in categories
    assert register["blockers_that_block_v090_rc"] == 0
