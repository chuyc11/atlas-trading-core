from tests.a_share_owner_readiness_gate_test_utils import gate_data, make_paths, seed_owner_readiness_gate_outputs


def test_owner_readiness_gate_manifest_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_readiness_gate_outputs(paths)
    manifest = gate_data(paths, "owner_readiness_gate_manifest.json")
    assert manifest["manifest_id"] == "A-SHARE-OWNER-READINESS-GATE-MANIFEST"
    assert manifest["recommended_next_version"] == "v0.8.14-a-share-owner-daily-pack-quality-exceptions-and-escalation-workflow"
