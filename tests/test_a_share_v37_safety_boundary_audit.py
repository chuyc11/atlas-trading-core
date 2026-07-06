from a_share_v3x_release_test_utils import assert_common_boundary, build_through, make_v3x_paths


def test_v37_safety_boundary_and_health_score_separation(tmp_path):
    paths = make_v3x_paths(tmp_path)
    result = build_through(paths, "v37")

    assert result["health_status_result_generated"] is True
    assert result["health_status_fabricated"] is False
    assert result["health_score_is_owner_readiness_score"] is False
    assert result["health_pass_means_live_trading_ready"] is False
    assert result["full_pytest_run"] is False
    assert_common_boundary(result)
