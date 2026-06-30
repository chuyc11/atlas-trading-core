from tests.a_share_owner_readiness_recovery_test_utils import make_paths, recovery_data, seed_owner_readiness_recovery_outputs


def test_a_share_score_driver_analysis_has_evidence_and_confidence(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_readiness_recovery_outputs(paths)
    analysis = recovery_data(paths, "score_driver_analysis.json")
    assert analysis["score_gap"] == analysis["threshold_score"] - analysis["source_score"]
    assert all(item["evidence_source"] and item["confidence"] for item in analysis["score_penalty_components"])
    assert all(item["evidence_source"] and item["confidence"] for item in analysis["exception_drivers"])
