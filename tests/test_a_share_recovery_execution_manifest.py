from tests.a_share_recovery_execution_test_utils import make_paths, execution_data, seed_recovery_execution_outputs


def test_recovery_execution_manifest_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_recovery_execution_outputs(paths)
    manifest = execution_data(paths, "recovery_execution_manifest.json")
    assert manifest["source_gate_decision"] == "blocked"
    assert manifest["task_count"] == 3
    assert manifest["recommended_next_version"].startswith("v0.8.17")
