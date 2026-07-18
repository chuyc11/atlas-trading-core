from a_share_v3x_release_test_utils import build_through, component_json, make_v3x_paths


def test_v35_long_horizon_regression_is_split_matrix(tmp_path):
    paths = make_v3x_paths(tmp_path)
    result = build_through(paths, "v35")
    evidence = component_json(paths, "v35", "v35_long_horizon_regression_evidence")

    assert result["v34_baseline_verified"] is True
    assert result["long_horizon_regression_evidence_generated"] is True
    assert result["full_regression_run"] is True
    assert result["full_regression_passed"] is True
    assert result["full_regression_mode"] == "full_repository_pytest"
    assert evidence["full_regression_mode"] == "full_repository_pytest"
    assert result["full_pytest_evidence_status"] == "verified"
