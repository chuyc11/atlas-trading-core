from a_share_v3x_release_test_utils import build_through, component_json, make_v3x_paths


def test_v36_supply_chain_does_not_fabricate_vulnerability_coverage(tmp_path):
    paths = make_v3x_paths(tmp_path)
    result = build_through(paths, "v36")
    supply = component_json(paths, "v36", "v36_supply_chain_dependency_result")

    assert result["supply_chain_dependency_result_generated"] is True
    assert result["dependency_result_fabricated"] is False
    assert supply["vulnerability_db_status"] == "available"
    assert supply["assessment_status"] == "passed"
    assert supply["dependency_risk_score_is_owner_readiness_score"] is False
