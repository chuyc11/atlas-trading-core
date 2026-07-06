from a_share_v3x_release_test_utils import assert_common_boundary, build_through, make_v3x_paths


def test_v38_owner_dashboard_and_safety_boundary(tmp_path):
    paths = make_v3x_paths(tmp_path)
    result = build_through(paths, "v38")

    assert result["owner_microstructure_dashboard_generated"] is True
    assert result["price_volume_constraint_edge_case_result_generated"] is True
    assert result["full_pytest_run"] is False
    assert_common_boundary(result)
