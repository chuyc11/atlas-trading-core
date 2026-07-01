from tests.a_share_recovery_evidence_test_utils import recovery_evidence_data, make_paths, seed_recovery_evidence_outputs


def test_recovery_evidence_manifest_and_summary(tmp_path):
    paths = make_paths(tmp_path)
    seed_recovery_evidence_outputs(paths)
    manifest = recovery_evidence_data(paths, "recovery_evidence_manifest.json")
    summary = recovery_evidence_data(paths, "recovery_evidence_summary.json")
    assert manifest["manifest_id"] == "A-SHARE-OWNER-RECOVERY-EVIDENCE-MANIFEST"
    assert manifest["full_pytest_run"] is False
    assert summary["new_gate_score_generated"] is False

