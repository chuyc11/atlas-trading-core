from tests.a_share_owner_readiness_recovery_test_utils import make_paths, recovery_data, seed_owner_readiness_recovery_outputs


def test_a_share_recovery_score_impact_model_is_estimate(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_readiness_recovery_outputs(paths)
    model = recovery_data(paths, "recovery_score_impact_model.json")
    assert model["does_not_rewrite_source_score"] is True
    assert model["does_not_claim_recovery_succeeded"] is True
    assert model["projection_confidence"] == "medium_estimate"
    assert all(item["estimate"] for item in model["task_level_expected_score_impact"])
