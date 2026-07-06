from a_share_v3x_release_test_utils import build_through, make_v3x_paths


def test_v40_final_validation_and_freeze_decision_are_research_only(tmp_path):
    paths = make_v3x_paths(tmp_path)
    result = build_through(paths, "v40")

    assert result["security_ops_data_docs_validation_generated"] is True
    assert result["external_reviewer_freeze_package_generated"] is True
    assert result["freeze_decision"] == "frozen_as_research_only_simulation_platform"
    assert result["project_frozen_as_research_only_simulation_platform"] is True
    assert result["live_trading_ready"] is False
