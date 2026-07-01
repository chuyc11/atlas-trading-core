from tests.a_share_final_closeout_test_utils import final_json, seed_v095_and_build_v096


def test_branch_selection_chooses_final_not_ready_closeout(tmp_path):
    paths, _ = seed_v095_and_build_v096(tmp_path)
    branch = final_json(paths, "branch_selection_result")

    assert branch["selected_branch"] == "final_not_ready_closeout"
    assert branch["controlled_reevaluation_allowed"] is False
    assert branch["controlled_reevaluation_executed"] is False
    assert "controlled reevaluation is disallowed because v0.9.5 no-go result and precheck not_ready." in branch["selection_rationale"]
