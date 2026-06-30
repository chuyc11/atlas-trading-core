from tests.a_share_owner_readiness_recovery_test_utils import make_paths, recovery_data, seed_owner_readiness_recovery_outputs


def test_a_share_recovery_task_backlog_is_planned_and_clean(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_readiness_recovery_outputs(paths)
    backlog = recovery_data(paths, "recovery_task_backlog.json")
    assert backlog["task_count"] == 3
    assert backlog["tasks_marked_complete_by_default"] is False
    assert backlog["forbidden_recovery_task_categories_detected"] == []
    assert all(task["status"] == "planned" for task in backlog["tasks"])
