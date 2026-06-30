from tests.a_share_recovery_execution_test_utils import make_paths, execution_data, seed_recovery_execution_outputs


def test_score_impact_evidence_does_not_rewrite_source_score(tmp_path):
    paths = make_paths(tmp_path)
    seed_recovery_execution_outputs(paths)
    assessment = execution_data(paths, "score_impact_evidence_assessment.json")
    assert assessment["score_rewritten_without_audit_evidence"] is False
    assert assessment["readiness_score_rewritten"] is False
    assert assessment["score_improvement_claimed"] is False
