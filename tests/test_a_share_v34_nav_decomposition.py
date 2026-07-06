from a_share_v3x_release_test_utils import build_through, component_json, make_v3x_paths


def test_v34_nav_decomposition_is_simulation_only(tmp_path):
    paths = make_v3x_paths(tmp_path)
    result = build_through(paths, "v34")
    nav = component_json(paths, "v34", "v34_nav_return_decomposition_result")

    assert result["v33_baseline_verified"] is True
    assert result["nav_return_decomposition_generated"] is True
    assert result["nav_attribution_fabricated"] is False
    assert nav["portfolio_is_real_portfolio"] is False
