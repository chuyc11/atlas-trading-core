from a_share_v3x_release_test_utils import assert_common_boundary, build_through, make_v3x_paths


def test_v39_owner_handoff_dashboard_and_safety_boundary(tmp_path):
    paths = make_v3x_paths(tmp_path)
    result = build_through(paths, "v39")

    assert result["owner_handoff_dashboard_generated"] is True
    assert result["documentation_fabricated"] is False
    assert result["full_pytest_run"] is False
    assert_common_boundary(result)
