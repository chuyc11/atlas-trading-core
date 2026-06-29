from tests.a_share_current_day_test_utils import AS_OF_DATE
from trading_core.equity_current_day.current_day_manifest import build_current_day_run_manifest


def test_current_day_manifest_generated():
    manifest = build_current_day_run_manifest(
        as_of_date=AS_OF_DATE,
        resolved_as_of_date=AS_OF_DATE,
        generated_at="2026-06-28T00:00:00Z",
        mode="run_research_from_existing_refresh",
        workflow_mode="validate_existing_artifacts",
        readiness={"overall_passed": True, "data_refresh_audit_passed": True, "warnings": [], "blocking_reasons": []},
        workflow_execution={"workflow_audit_overall_passed": True, "warnings": [], "blocking_reasons": []},
        warning_summary={"warnings": [], "blocking_reasons": []},
        source_trace={"forbidden_path_hits": []},
        boundary={"overall_passed": True, "warnings": [], "blocking_reasons": []},
        output_artifacts={},
        source_artifacts={},
    )
    assert manifest["overall_passed"] is True
    assert manifest["recommended_next_version"] == "v0.8.2-a-share-current-day-owner-briefing-and-monitoring-dashboard"

