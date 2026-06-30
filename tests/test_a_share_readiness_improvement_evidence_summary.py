from tests.a_share_recovery_execution_test_utils import make_paths, execution_data, seed_recovery_execution_outputs


def test_readiness_improvement_evidence_does_not_claim_improvement(tmp_path):
    paths = make_paths(tmp_path)
    seed_recovery_execution_outputs(paths)
    summary = execution_data(paths, "readiness_improvement_evidence_summary.json")
    assert summary["readiness_improvement_claimed"] is False
    assert summary["ready_for_score_reassessment"] is False
    assert summary["does_not_claim_improvement_without_audit_evidence"] is True
