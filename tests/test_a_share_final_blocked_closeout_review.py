from tests.a_share_owner_closeout_review_test_utils import make_paths, seed_closeout_outputs, closeout_data


def test_final_blocked_closeout_review_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_closeout_outputs(paths)
    review = closeout_data(paths, "final_blocked_closeout_review.json")
    assert review["closeout_review_passed"] is True
    assert review["blocked_state_intentional"] is True
    assert review["blocked_state_misrepresented_as_acceptable"] is False
    assert review["new_gate_score_generated"] is False
