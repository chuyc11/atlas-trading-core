from tests.a_share_evidence_backed_prep_test_utils import make_paths, seed_evidence_backed_prep_outputs, prep_data


def test_evidence_backed_prep_manifest_and_summary_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_evidence_backed_prep_outputs(paths)
    manifest = prep_data(paths, "evidence_backed_prep_manifest.json")
    summary = prep_data(paths, "evidence_backed_prep_summary.json")
    assert manifest["manifest_id"] == "A-SHARE-EVIDENCE-BACKED-PREP-MANIFEST"
    assert summary["summary_id"] == "A-SHARE-EVIDENCE-BACKED-PREP-SUMMARY"
    assert summary["source_gate_decision_preserved"] is True
    assert summary["ready_for_controlled_gate_reevaluation"] is False

