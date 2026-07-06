from a_share_v3x_release_test_utils import build_through, make_v3x_paths


def test_v36_owner_security_dashboard_preserves_blocked_state(tmp_path):
    paths = make_v3x_paths(tmp_path)
    result = build_through(paths, "v36")

    assert result["owner_security_dashboard_generated"] is True
    assert result["owner_readiness_state"] == "blocked"
    assert result["owner_operationally_acceptable"] is False
    assert result["live_trading_ready"] is False
