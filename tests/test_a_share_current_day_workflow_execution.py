from tests.a_share_current_day_test_utils import AS_OF_DATE, make_paths
from trading_core.equity_current_day.workflow_execution import build_blocked_workflow_execution, build_workflow_execution_record


def test_current_day_workflow_execution_blocked_if_readiness_fails(tmp_path):
    paths = make_paths(tmp_path)
    execution = build_blocked_workflow_execution(
        paths=paths,
        as_of_date=AS_OF_DATE,
        resolved_as_of_date=AS_OF_DATE,
        mode="run_research_from_existing_refresh",
        workflow_mode="validate_existing_artifacts",
        command="python -m trading_core.cli run-and-audit-a-share-daily-research-workflow",
        blocking_reasons=["data_refresh_audit_passed=false"],
        warnings=[],
    )
    assert execution["status"] == "blocked"
    assert execution["workflow_audit_overall_passed"] is False


def test_current_day_workflow_execution_failed_if_workflow_audit_fails(tmp_path):
    paths = make_paths(tmp_path)
    execution = build_workflow_execution_record(
        paths=paths,
        as_of_date=AS_OF_DATE,
        resolved_as_of_date=AS_OF_DATE,
        mode="run_research_from_existing_refresh",
        workflow_mode="validate_existing_artifacts",
        command="cmd",
        started_at="2026-06-28T00:00:00Z",
        finished_at="2026-06-28T00:00:01Z",
        exit_code=1,
        workflow_audit={"overall_passed": False, "blocking_reasons": ["workflow_failed"], "warnings": []},
    )
    assert execution["status"] == "failed"
    assert execution["blocking_reasons"] == ["workflow_failed"]

