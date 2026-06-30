from tests.a_share_recovery_execution_test_utils import AS_OF_DATE, make_paths, seed_recovery_execution_outputs


def test_recovery_execution_reports_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_recovery_execution_outputs(paths)
    report_dir = paths.outputs_dir / "equity_owner_readiness_recovery_execution" / "daily" / AS_OF_DATE
    reports = [
        "A_SHARE_RECOVERY_EXECUTION_TRACKER.md",
        "A_SHARE_RECOVERY_TASK_EVIDENCE.md",
        "A_SHARE_GATE_REEVALUATION_PREP.md",
        "A_SHARE_CONTROLLED_REEVALUATION_PLAN.md",
        "A_SHARE_RECOVERY_EXECUTION_SOURCE_TRACE.md",
    ]
    assert all((report_dir / name).exists() for name in reports)
