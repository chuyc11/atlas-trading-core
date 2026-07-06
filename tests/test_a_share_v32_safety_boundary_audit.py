from a_share_v3x_release_test_utils import assert_common_boundary, build_through, make_v3x_paths


def test_v32_safety_boundary_and_test_policy(tmp_path):
    paths = make_v3x_paths(tmp_path)
    result = build_through(paths, "v32")

    assert result["artifact_integrity_sweep_passed"] is True
    assert result["protected_path_sweep_passed"] is True
    assert result["safety_boundary_sweep_passed"] is True
    assert result["full_pytest_run"] is False
    assert result["targeted_pytest_required"] is True
    assert result["warnings"] == []
    assert_common_boundary(result)
