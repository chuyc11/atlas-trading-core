from a_share_v3x_release_test_utils import build_through, make_v3x_paths


def test_v35_owner_final_dashboard_keeps_owner_readiness_blocked(tmp_path):
    paths = make_v3x_paths(tmp_path)
    result = build_through(paths, "v35")

    assert result["owner_final_v3x_dashboard_generated"] is True
    assert result["owner_readiness_state"] == "blocked"
    assert result["owner_operationally_acceptable"] is False
    assert result["source_readiness_score"] == 54
    assert result["minimum_owner_readiness_score"] == 75
    assert result["score_gap"] == 21
