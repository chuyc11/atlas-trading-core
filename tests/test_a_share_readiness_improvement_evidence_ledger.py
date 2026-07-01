from tests.a_share_recovery_evidence_test_utils import recovery_evidence_data, make_paths, seed_recovery_evidence_outputs


def test_readiness_improvement_evidence_ledger_does_not_rewrite_score(tmp_path):
    paths = make_paths(tmp_path)
    seed_recovery_evidence_outputs(paths)
    ledger = recovery_evidence_data(paths, "readiness_improvement_evidence_ledger.json")
    assert isinstance(ledger["source_readiness_score"], int)
    assert ledger["actual_audited_score_changed"] is False
    assert ledger["new_audited_score"] is None
