from a_share_v3x_release_test_utils import build_through, make_v3x_paths


def test_v36_config_governance_cannot_activate_real_trading(tmp_path):
    paths = make_v3x_paths(tmp_path)
    result = build_through(paths, "v36")

    assert result["config_governance_result_generated"] is True
    assert result["unsafe_config_override_detected"] is False
    assert result["new_gate_score_generated"] is False
    assert result["new_gate_decision_generated"] is False
