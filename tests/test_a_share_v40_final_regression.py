from a_share_v3x_release_test_utils import build_through, make_v3x_paths


def test_v40_final_regression_defaults_to_split_matrix(tmp_path):
    paths = make_v3x_paths(tmp_path)
    result = build_through(paths, "v40")

    assert result["v39_baseline_verified"] is True
    assert result["final_regression_evidence_generated"] is True
    assert result["full_regression_run"] is True
    assert result["full_regression_passed"] is True
    assert result["full_regression_mode"] == "full_repository_pytest"
    assert result["full_pytest_evidence_status"] == "verified"
