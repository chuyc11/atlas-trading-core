from a_share_v3x_release_test_utils import build_through, make_v3x_paths


def test_v36_filesystem_and_network_boundaries_are_safe(tmp_path):
    paths = make_v3x_paths(tmp_path)
    result = build_through(paths, "v36")

    assert result["filesystem_path_safety_result_generated"] is True
    assert result["network_boundary_result_generated"] is True
    assert result["unsafe_file_delete_detected"] is False
    assert result["broker_network_path_detected"] is False
    assert result["account_network_path_detected"] is False
    assert result["order_api_endpoint_detected"] is False
