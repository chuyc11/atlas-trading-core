from tests.a_share_recovery_execution_test_utils import make_paths, execution_data, seed_recovery_execution_outputs


def test_developer_follow_up_evidence_tracker_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_recovery_execution_outputs(paths)
    tracker = execution_data(paths, "developer_follow_up_evidence_tracker.json")
    assert tracker["follow_up_count"] == 1
    assert tracker["evidence_available_count"] == 0
    assert tracker["completed_count"] == 0
