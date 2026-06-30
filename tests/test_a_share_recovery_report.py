from tests.a_share_owner_readiness_recovery_test_utils import AS_OF_DATE, make_paths, seed_owner_readiness_recovery_outputs


def test_a_share_recovery_reports_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_readiness_recovery_outputs(paths)
    report_dir = paths.outputs_dir / "equity_owner_readiness_recovery" / "daily" / AS_OF_DATE
    reports = [
        "A_SHARE_OWNER_READINESS_RECOVERY_PLAN.md",
        "A_SHARE_READINESS_GAP_SUMMARY.md",
        "A_SHARE_QUALITY_IMPROVEMENT_TASK_BACKLOG.md",
        "A_SHARE_DEVELOPER_RECOVERY_FOLLOW_UP.md",
        "A_SHARE_GATE_REEVALUATION_READINESS_CHECKLIST.md",
        "A_SHARE_RECOVERY_SOURCE_TRACE.md",
    ]
    assert all((report_dir / name).exists() for name in reports)
