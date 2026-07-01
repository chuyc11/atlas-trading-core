from tests.a_share_recovery_evidence_test_utils import recovery_evidence_data, make_paths, seed_recovery_evidence_outputs


def test_source_trace_improvement_evidence_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_recovery_evidence_outputs(paths)
    evidence = recovery_evidence_data(paths, "source_trace_improvement_evidence.json")
    assert evidence["evidence_id"] == "A-SHARE-SOURCE-TRACE-IMPROVEMENT-EVIDENCE"
    assert evidence["completeness_ratio"] == 1
    assert evidence["evidence_available"] is True

