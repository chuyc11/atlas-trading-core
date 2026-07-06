from a_share_v3x_release_test_utils import build_through, make_v3x_paths


def test_v35_external_review_refresh_preserves_research_only_boundary(tmp_path):
    paths = make_v3x_paths(tmp_path)
    result = build_through(paths, "v35")

    assert result["external_review_package_refresh_generated"] is True
    assert result["fabricated_release_evidence"] is False
    assert result["not_live_trading_ready"] is True
    assert result["broker_connected"] is False
