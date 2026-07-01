from tests.a_share_owner_closeout_review_test_utils import make_paths, seed_closeout_outputs, closeout_data


def test_v090_full_regression_plan_generated_but_not_executed(tmp_path):
    paths = make_paths(tmp_path)
    seed_closeout_outputs(paths)
    plan = closeout_data(paths, "v090_full_regression_plan.json")
    assert plan["full_pytest_command"] == "python -m pytest"
    assert plan["full_pytest_run"] is False
    assert plan["full_pytest_required_in_v090"] is True
