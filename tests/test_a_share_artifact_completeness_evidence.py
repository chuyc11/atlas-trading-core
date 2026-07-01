from tests.a_share_recovery_evidence_test_utils import recovery_evidence_data, make_paths, seed_recovery_evidence_outputs


def test_artifact_completeness_evidence_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_recovery_evidence_outputs(paths)
    evidence = recovery_evidence_data(paths, "artifact_completeness_evidence.json")
    assert evidence["evidence_id"] == "A-SHARE-ARTIFACT-COMPLETENESS-EVIDENCE"
    assert evidence["missing_items"] == []

