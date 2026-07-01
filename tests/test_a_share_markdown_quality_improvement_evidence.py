from tests.a_share_recovery_evidence_test_utils import recovery_evidence_data, make_paths, seed_recovery_evidence_outputs


def test_markdown_quality_improvement_evidence_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_recovery_evidence_outputs(paths)
    evidence = recovery_evidence_data(paths, "markdown_quality_improvement_evidence.json")
    assert evidence["evidence_id"] == "A-SHARE-MARKDOWN-QUALITY-IMPROVEMENT-EVIDENCE"
    assert evidence["forbidden_wording_positive_hits"] == []

