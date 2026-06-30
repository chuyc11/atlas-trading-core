from tests.a_share_controlled_gate_reevaluation_test_utils import controlled_data, make_paths, seed_controlled_gate_reevaluation_outputs


def test_controlled_gate_reevaluation_manifest_and_summary(tmp_path):
    paths = make_paths(tmp_path)
    seed_controlled_gate_reevaluation_outputs(paths)
    manifest = controlled_data(paths, "controlled_reevaluation_manifest.json")
    summary = controlled_data(paths, "controlled_reevaluation_summary.json")
    assert manifest["manifest_id"] == "A-SHARE-OWNER-CONTROLLED-GATE-REEVALUATION-MANIFEST"
    assert summary["controlled_reevaluation_decision"] == "skipped_not_ready"
    assert summary["gate_reevaluation_executed"] is False

