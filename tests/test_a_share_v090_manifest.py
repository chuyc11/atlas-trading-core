from tests.a_share_v090_rc_test_utils import make_paths, seed_v090_outputs, v090_data


def test_v090_manifest_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_v090_outputs(paths)
    manifest = v090_data(paths, "v090_manifest.json")
    assert manifest["manifest_id"] == "A-SHARE-OWNER-V090-RC-MANIFEST"
    assert manifest["known_owner_readiness_state"] == "blocked"
    assert manifest["new_gate_decision_generated"] is False
