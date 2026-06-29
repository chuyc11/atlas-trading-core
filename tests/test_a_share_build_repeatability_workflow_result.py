from tests.a_share_build_repeatability_test_utils import AS_OF_DATE, make_paths, write_json
from trading_core.equity_build_repeatability.workflow_result import build_repeat_build_workflow_result


def test_repeatability_workflow_result_reads_audit(tmp_path):
    paths = make_paths(tmp_path)
    write_json(paths.data_dir / "equity_data_quality" / "a_share_current_day_research_run_audit.json", {"overall_passed": True, "blocking_reasons": [], "warnings": []})
    result = build_repeat_build_workflow_result(
        paths=paths,
        as_of_date=AS_OF_DATE,
        execution_record={"status": "passed", "exit_code": 0, "blocking_reasons": [], "warnings": []},
    )
    assert result["workflow_audit_overall_passed"] is True

