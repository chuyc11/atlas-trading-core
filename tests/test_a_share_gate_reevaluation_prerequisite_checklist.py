from tests.a_share_recovery_execution_test_utils import make_paths, execution_data, seed_recovery_execution_outputs


def test_gate_reevaluation_prerequisite_checklist_not_ready(tmp_path):
    paths = make_paths(tmp_path)
    seed_recovery_execution_outputs(paths)
    checklist = execution_data(paths, "gate_reevaluation_prerequisite_checklist.json")
    assert checklist["ready_for_future_gate_reevaluation"] is False
    assert checklist["all_recovery_tasks_have_evidence"] is False
    assert checklist["no_gate_reevaluation_executed"] is True
