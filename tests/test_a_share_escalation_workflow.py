from tests.a_share_owner_quality_exception_test_utils import exception_data, make_paths, seed_owner_quality_exception_outputs


def test_escalation_workflow_generated_without_forbidden_routes(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_quality_exception_outputs(paths)
    workflow = exception_data(paths, "escalation_workflow.json")
    assert workflow["step_count"] >= 1
    assert workflow["no_forbidden_escalation_routes"] is True
