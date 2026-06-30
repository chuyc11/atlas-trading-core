from tests.a_share_owner_quality_exception_test_utils import exception_data, make_paths, seed_owner_quality_exception_outputs


def test_quality_exception_manifest_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_quality_exception_outputs(paths)
    manifest = exception_data(paths, "quality_exception_manifest.json")
    assert manifest["manifest_id"] == "A-SHARE-OWNER-QUALITY-EXCEPTION-WORKFLOW-MANIFEST"
    assert manifest["blocked_gate_decision_preserved"] is True
