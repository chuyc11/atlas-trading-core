from tests.a_share_recovery_execution_test_utils import make_paths, execution_data, seed_recovery_execution_outputs


def test_recovery_task_status_tracker_defaults_without_evidence(tmp_path):
    paths = make_paths(tmp_path)
    seed_recovery_execution_outputs(paths)
    tracker = execution_data(paths, "recovery_task_status_tracker.json")
    assert tracker["task_count"] == 3
    assert tracker["planned_count"] == 2
    assert tracker["waiting_for_more_history_count"] == 1
    assert tracker["completed_count"] == 0
    assert tracker["tasks_marked_complete_by_default"] is False
