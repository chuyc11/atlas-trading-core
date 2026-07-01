from tests.a_share_operator_experience_test_utils import make_paths, operator_data, seed_operator_outputs


def test_audit_and_test_status_summary_defers_v091_full_pytest(tmp_path):
    paths = make_paths(tmp_path)
    seed_operator_outputs(paths)
    summary = operator_data(paths, "audit_and_test_status_summary.json")
    assert summary["full_pytest_passed_in_source_release"] is True
    assert summary["v091_full_pytest_run"] is False
    assert summary["current_stage_test_policy"] == "targeted_pytest_only"
