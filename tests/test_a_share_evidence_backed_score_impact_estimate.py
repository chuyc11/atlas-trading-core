from tests.a_share_recovery_evidence_test_utils import recovery_evidence_data, make_paths, seed_recovery_evidence_outputs


def test_evidence_backed_score_impact_estimate_not_gate_score(tmp_path):
    paths = make_paths(tmp_path)
    seed_recovery_evidence_outputs(paths)
    estimate = recovery_evidence_data(paths, "evidence_backed_score_impact_estimate.json")
    assert estimate["not_a_gate_score"] is True
    assert estimate["evidence_supported_score_delta_estimate"] == 0
    assert estimate["projected_score_if_evidence_accepted"] == estimate["source_readiness_score"] + estimate["evidence_supported_score_delta_estimate"]
