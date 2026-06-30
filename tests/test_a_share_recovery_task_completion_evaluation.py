from tests.a_share_recovery_execution_test_utils import make_paths, execution_data, seed_recovery_execution_outputs


def test_recovery_task_completion_requires_evidence(tmp_path):
    paths = make_paths(tmp_path)
    seed_recovery_execution_outputs(paths)
    evaluation = execution_data(paths, "recovery_task_completion_evaluation.json")
    assert evaluation["task_completion_not_fabricated"] is True
    assert evaluation["completed_count"] == 0
    assert evaluation["tasks_marked_complete_by_default"] is False
