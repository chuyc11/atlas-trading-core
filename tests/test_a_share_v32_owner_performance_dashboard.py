from a_share_v3x_release_test_utils import build_through, make_v3x_paths


def test_v32_owner_dashboard_keeps_performance_separate_from_readiness(tmp_path):
    paths = make_v3x_paths(tmp_path)
    result = build_through(paths, "v32")

    assert result["owner_performance_dashboard_generated"] is True
    assert result["performance_score_is_owner_readiness_score"] is False
    assert result["owner_readiness_state"] == "blocked"
    assert result["owner_operationally_acceptable"] is False
