from a_share_v3x_release_test_utils import build_through, make_v3x_paths


def test_v37_recovery_runbook_and_dashboard_are_dry_run_only(tmp_path):
    paths = make_v3x_paths(tmp_path)
    result = build_through(paths, "v37")

    assert result["recovery_rehearsal_result_generated"] is True
    assert result["owner_operations_runbook_generated"] is True
    assert result["owner_observability_dashboard_generated"] is True
    assert result["scheduler_installed"] is False
    assert result["daemon_installed"] is False
