from a_share_v3x_release_test_utils import build_through, make_v3x_paths


def test_v40_known_limitations_and_dashboard_keep_owner_blocked(tmp_path):
    paths = make_v3x_paths(tmp_path)
    result = build_through(paths, "v40")

    assert result["known_limitations_final_generated"] is True
    assert result["owner_final_maintenance_dashboard_generated"] is True
    assert result["known_limitations_hidden"] is False
    assert result["owner_readiness_state"] == "blocked"
    assert result["source_readiness_score"] == 54
    assert result["score_gap"] == 21
