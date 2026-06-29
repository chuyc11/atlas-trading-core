from tests.a_share_current_day_test_utils import AS_OF_DATE
from trading_core.equity_current_day.current_day_stage_manifest import STAGE_DEFINITIONS, build_current_day_stage_manifest


def test_current_day_stage_manifest_has_required_stages():
    manifest = build_current_day_stage_manifest(
        as_of_date=AS_OF_DATE,
        resolved_as_of_date=AS_OF_DATE,
        mode="run_research_from_existing_refresh",
        workflow_mode="validate_existing_artifacts",
        generated_at="2026-06-28T00:00:00Z",
        artifact_paths={},
        readiness={"overall_passed": True, "warnings": [], "blocking_reasons": []},
        workflow_execution={"status": "passed", "workflow_audit_overall_passed": True, "warnings": [], "blocking_reasons": []},
        warnings=[],
        blocking_reasons=[],
    )
    assert [stage["stage_id"] for stage in manifest["stages"]] == [stage_id for stage_id, _ in STAGE_DEFINITIONS]

