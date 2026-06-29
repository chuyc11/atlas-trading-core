from tests.a_share_owner_dashboard_test_utils import AS_OF_DATE, make_paths, write_json
from trading_core.equity_current_day_builds.workflow_result import build_workflow_result


def test_gated_build_workflow_result_counts_list_stages(tmp_path):
    paths = make_paths(tmp_path)
    base = paths.data_dir / "equity_current_day_runs" / "daily" / AS_OF_DATE
    write_json(base / "current_day_run_manifest.json", {"output_artifacts": {"a": "b"}})
    write_json(base / "current_day_stage_manifest.json", {"stages": [{"status": "passed"}, {"status": "failed"}]})
    write_json(paths.data_dir / "equity_data_quality" / "a_share_current_day_research_run_audit.json", {"overall_passed": True, "blocking_reasons": [], "warnings": []})
    result = build_workflow_result(paths=paths, as_of_date=AS_OF_DATE, execution_record={"status": "passed"})
    assert result["stages_passed"] == 1
    assert result["stages_failed"] == 1

