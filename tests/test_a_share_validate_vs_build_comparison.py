from tests.a_share_owner_dashboard_test_utils import AS_OF_DATE, make_paths, write_json
from trading_core.equity_current_day_builds.validate_vs_build_comparison import build_validate_vs_build_comparison


def test_validate_vs_build_comparison_blocks_missing_required_artifact(tmp_path):
    paths = make_paths(tmp_path)
    write_json(paths.data_dir / "equity_current_day_runs" / "daily" / AS_OF_DATE / "current_day_workflow_execution.json", {"exit_code": 0, "status": "passed"})
    comparison = build_validate_vs_build_comparison(paths=paths, as_of_date=AS_OF_DATE, validate_snapshot={"current_day_run_manifest": {"overall_passed": True}})
    assert comparison["comparison_completed"] is True
    assert comparison["missing_required_artifacts"]

