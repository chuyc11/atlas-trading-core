from a_share_v3x_release_test_utils import build_through, make_v3x_paths


def test_v34_owner_risk_dashboard_keeps_portfolio_virtual(tmp_path):
    paths = make_v3x_paths(tmp_path)
    result = build_through(paths, "v34")

    assert result["owner_risk_attribution_dashboard_generated"] is True
    assert result["portfolio_is_real_portfolio"] is False
    assert result["live_trading_ready"] is False
