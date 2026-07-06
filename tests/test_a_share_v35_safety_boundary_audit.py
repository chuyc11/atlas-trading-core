from a_share_v3x_release_test_utils import assert_common_boundary, build_through, make_v3x_paths


def test_v35_safety_boundary_and_release_decision(tmp_path):
    paths = make_v3x_paths(tmp_path)
    result = build_through(paths, "v35")

    assert result["release_decision"] == "released_as_research_only_simulation_platform_v3x_closeout"
    assert result["artifact_integrity_sweep_passed"] is True
    assert result["protected_path_sweep_passed"] is True
    assert result["safety_boundary_sweep_passed"] is True
    assert result["live_trading_ready"] is False
    assert_common_boundary(result)
