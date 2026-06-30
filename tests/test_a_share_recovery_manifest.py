from tests.a_share_owner_readiness_recovery_test_utils import make_paths, recovery_data, seed_owner_readiness_recovery_outputs


def test_a_share_recovery_manifest_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_readiness_recovery_outputs(paths)
    manifest = recovery_data(paths, "recovery_manifest.json")
    assert manifest["source_gate_decision"] == "blocked"
    assert manifest["recovery_task_count"] == 3
    assert manifest["recommended_next_version"].startswith("v0.8.16")
