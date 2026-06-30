from tests.a_share_recovery_execution_test_utils import make_paths, execution_data, seed_recovery_execution_outputs


def test_recovery_task_evidence_registry_records_missing_evidence(tmp_path):
    paths = make_paths(tmp_path)
    seed_recovery_execution_outputs(paths)
    registry = execution_data(paths, "recovery_task_evidence_registry.json")
    assert registry["evidence_record_count"] == 3
    assert registry["evidence_available_count"] == 0
    assert registry["task_existence_alone_is_completion_evidence"] is False
    assert all(row["evidence_available"] is False for row in registry["records"])
